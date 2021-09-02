"""
VCD (Video Content Description) library v4.3.1

Project website: http://vcd.vicomtech.org

Copyright (C) 2021, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.3.1.
VCD is distributed under MIT License. See LICENSE.

"""


import copy
import json
import warnings
from jsonschema import validate
from enum import Enum

import re
import uuid

import vcd.types as types
import vcd.utils as utils
import vcd.schema as schema
import vcd.converter as converter


class TagType(Enum):
    """
    Tag's first-level categories as defined in the OpenLABEL standard
    """
    administrative = 1
    odd = 2
    behaviour = 3
    custom = 4

class ResourceUID:
    """
    This is a class to add additional UIDs to an element, according to its representation
    in another resource.
    E.g. A Lane or Road object labeled in VCD can correspond to a Lane or Road element in an
    OpenDrive file.
    Then the OpenDrive file path is added with
    res_opendrive_uidopenlabel.add_resource("../resources/xodr/multi_intersections.xodr")
    And any object added can add the elment UID at the resource using this ResourceUID class
    openlabel.add_object("road1", "road", res_uid=ResourceUID(res_opendrive_uid, 217))
    """
    def __init__(self, resource_uid, id_at_resource):
        self.resource_uid = UID(resource_uid)  # this is the UID of the resource file
        self.id_at_resource = UID(id_at_resource)  # this is the UID of the element in the resource

    def as_dict(self):
        return {self.resource_uid.as_str(): self.id_at_resource.as_str()}


class ElementType(Enum):
    """
    Elements of VCD (Object, Action, Event, Context, Relation, Tag)
    """
    object = 1
    action = 2
    event = 3
    context = 4
    relation = 5
    tag = 6


class StreamType(Enum):
    """
    Type of stream (sensor).
    """
    camera = 1
    lidar = 2
    radar = 3
    gps_imu = 4
    other = 5


class RDF(Enum):
    """
    Type of RDF agent (subject or object)
    """
    subject = 1
    object = 2


class FrameIntervals:
    """
    FrameIntervals class aims to simplify management of frame intervals
    """
    def __init__(self, frame_value=None, fuse=False):
        self.fis_dict = []
        self.fis_num = []

        if frame_value is not None:
            if isinstance(frame_value, int):
                self.fis_dict = [{'frame_start': frame_value, 'frame_end': frame_value}]
                self.fis_num = [(frame_value, frame_value)]
            elif isinstance(frame_value, list):
                if len(frame_value) == 0:
                    return
                if all(isinstance(x, tuple) for x in frame_value):
                    # Then, frame_value is an array of tuples
                    self.fis_dict = utils.as_frame_intervals_array_dict(frame_value)
                    if fuse:
                        self.fis_dict = utils.fuse_frame_intervals(self.fis_dict)
                    self.fis_num = utils.as_frame_intervals_array_tuples(self.fis_dict)
                elif all(isinstance(x, list) for x in frame_value):
                    # This is possibly a list of list, e.g. [[0, 10], [12, 15]], instead of the above case list of tupl
                    self.fis_dict = utils.as_frame_intervals_array_dict(frame_value)
                    if fuse:
                        self.fis_dict = utils.fuse_frame_intervals(self.fis_dict)
                    self.fis_num = utils.as_frame_intervals_array_tuples(self.fis_dict)
                elif all(isinstance(x, dict) for x in frame_value):
                    # User provided a list of dict
                    self.fis_dict = frame_value
                    if fuse:
                        self.fis_dict = utils.fuse_frame_intervals(self.fis_dict)
                    self.fis_num = utils.as_frame_intervals_array_tuples(self.fis_dict)
            elif isinstance(frame_value, tuple):
                # Then, frame_value is a tuple (one single frame interval)
                self.fis_num = [frame_value]
                self.fis_dict = utils.as_frame_intervals_array_dict(self.fis_num)
            elif isinstance(frame_value, dict):
                # User provided a single dict
                self.fis_dict = [frame_value]
                self.fis_num = utils.as_frame_intervals_array_tuples(self.fis_dict)
            else:
                warnings.warn("ERROR: Unsupported FrameInterval format.")

    def empty(self):
        #if len(self.fis_dict) == 0 or len(self.fis_num) == 0:
        return not self.fis_num

    def get_dict(self):
        return self.fis_dict

    def get(self):
        return self.fis_num

    def get_length(self):
        length = 0
        for fi in self.fis_num:
            length += fi[1] + 1 - fi[0]
        return length

    def rm_frame(self, frame_num):
        self.fis_dict = utils.rm_frame_from_frame_intervals(self.fis_dict, frame_num)
        self.fis_num = utils.as_frame_intervals_array_tuples(self.fis_dict)

    def union(self, frame_intervals):
        # Several quick cases
        if not self.fis_dict:
            return frame_intervals
        elif frame_intervals.get() == self.get():
            return frame_intervals       
        else:
            # Generic case
            fis_union = utils.fuse_frame_intervals(self.fis_dict + frame_intervals.get_dict())            
            return FrameIntervals(fis_union)

    def intersection(self, frame_intervals):
        fis_int = utils.intersection_between_frame_interval_arrays(self.fis_num, frame_intervals.get())
        return FrameIntervals(fis_int)

    def equals(self, frame_intervals):
        fis_int = self.intersection(frame_intervals)
        fis_union = self.union(frame_intervals)

        if fis_int.get_length() == fis_union.get_length():
            return True
        else:
            return False

    def contains(self, frame_intervals):
        fis_int = self.intersection(frame_intervals)

        if fis_int.get_length() == frame_intervals.get_length():
            return True
        else:
            return False

    def is_contained_by(self, frame_intervals):
        fis_int = self.intersection(frame_intervals)

        if fis_int.get_length() == self.get_length():
            return True
        else:
            return False

    def get_outer(self):
        return utils.get_outer_frame_interval(self.fis_dict)

    def has_frame(self, frame_num):
        return utils.is_inside_frame_intervals(frame_num, self.fis_num)

    def to_str(self):
        text = "["
        for fi in self.fis_num:
            text += "(" + str(fi[0]) + "," + str(fi[1]) + ")"
        text += "]"

        return text


class UID:
    """
    This is a helper class that simplifies management of UIDs.
    Public functions permits the user to introduce either int or string values as UIDs
    Internal functions create the UID objects to ensure the proper format is used where needed
    """
    def __init__(self, val=None):
        if val is None:
            # Void uid
            self.__set("", -1, False)
        else:
            if isinstance(val, int):
                self.__set(str(val), val, False)
            elif isinstance(val, str):
                if val == '':
                    self.__set("", -1, False)
                else:
                    if val.strip('-').isnumeric():  # this holds true for "-3" and "3"
                        self.__set(val, int(val), False)
                    elif bool(re.match(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$",
                                       val)):
                        self.__set(val, -1, True)
                    else:
                        warnings.warn("ERROR: Unsupported UID string type.")
                        self.__set("", -1, False)
            else:
                warnings.warn("ERROR: Unsupported UID type.")
                self.__set("", -1, False)

    def __set(self, uid_str=None, uid_int=None, is_uuid=False):
        self.uid_str = uid_str
        self.uid_int = uid_int
        self.uuid = is_uuid

    def is_uuid(self):
        return self.uuid

    def as_str(self):
        return self.uid_str

    def as_int(self):
        if self.is_uuid():
            warnings.warn("ERROR: This UID is not numeric, can't call getAsInt.")
        else:
            return self.uid_int

    def is_none(self):
        if self.uid_int == -1 and self.uid_str == "":
            return True
        else:
            return False


class SetMode(Enum):
    """
    The SetMode specifies how added content is inserted.
    SetMode.union is the default value,
    and determines that any new call to add functions (e.g. add_object, or add_action_data),
    actually adds content, extending the frame_intervals of the recipient container to the
    limits defined by the newly provided frame_intervals, effectively extending it to the union
    of frame_intervals (existing plus new), substituting the content which already existed
    with coincident frame (and name, uid, etc).
    SetMode.replace acts replacing old content by new, potentially removing frames if the newly
    provided frame_intervals are shorter than the existing ones.
    """
    union = 1
    replace = 2


class VCD:
    """
    VCD class as main container of VCD content. Exposes functions to
    add Elements, to get information and to remove data.
    Internally manages all information as Python dictionaries, and can map
    data into JSON strings.
    """
    ##################################################
    # Constructor
    ##################################################
    def __init__(self, file_name=None, validation=False):        
        self.use_uuid = False
        if file_name is not None:
            # Load from file
            json_file = open(file_name, encoding='utf-8')
            read_data = json.load(json_file)  # Open without converting strings to integers
            
            # Check VERSION and call converters if needed
            if 'vcd' in read_data:
                # This is 4.x
                if 'version' in read_data['vcd']:
                    # This is 4.1-2
                    if read_data['vcd']['version'] == "4.2.0":
                        # This is VCD 4.2.0
                        warnings.warn("WARNING: Converting VCD 4.2.0 to OpenLABEL 1.0.0. A full revision is recommended.")
                        # Convert frame entries to int
                        frames = read_data['vcd']['frames']
                        if frames:  # So frames is not empty
                            read_data['vcd']['frames'] = {int(key): value for key, value in frames.items()}

                        self.reset()  # to init object
                        converter.ConverterVCD420toOpenLabel100(read_data, self)  # self is modified internally

                    elif read_data['vcd']['version'] == "4.1.0":
                        # This is VCD 4.1.0
                        raise Exception("ERROR: VCD 4.1.0 to OpenLABEL 1.0.0 conversion is not implemented.")
                        pass
                elif 'metadata' in read_data['vcd']:
                    if 'schema_version' in read_data['vcd']['metadata']:
                        if read_data['vcd']['metadata']['schema_version'] == "4.3.0" or \
                                read_data['vcd']['metadata']['schema_version'] == "4.3.1":

                            # This is VCD 4.3.0 or VCD 4.3.1
                            self.data = read_data                           
                            
                            # 'vcd' content was loaded, need to change root to 'openlabel'
                            # Let's substitute the root from 'vcd' to 'openlabel', and update the schema version
                            self.data['openlabel'] = self.data.pop('vcd')
                            self.data['openlabel']['metadata']['schema_version'] = schema.openlabel_schema_version

                            if validation:
                                if not hasattr(self, 'schema'):
                                    self.schema = schema.openlabel_schema                                    
                                validate(instance=self.data, schema=self.schema)  # Raises errors if not validated
                                json_file.close()

                            # In VCD 4.3.1 uids are strings, because they can be numeric strings, or UUIDs
                            # but frames are still ints, so let's parse frame numbers as integers
                            if 'frames' in self.data['openlabel']:
                                frames = self.data['openlabel']['frames']
                                if frames:  # So frames is not empty
                                    self.data['openlabel']['frames'] = {int(key): value for key, value in frames.items()}
                        else:
                            raise Exception("ERROR: This vcd file does not seem to be 4.3.0, 4.3.1 nor 4.2.0")
                    else:
                        raise Exception("ERROR: This vcd file does not seem to be 4.3.0, 4.3.1 nor 4.2.0")
            elif 'openlabel' in read_data:
                # This is an OpenLABEL file 
                schema_version = read_data['openlabel']['metadata']['schema_version']
                if schema_version == "0.3.0" or schema_version == "1.0.0":
                    # This is OpenLABEL 0.3.0 or 1.0.0 (are equivalent)
                    self.data = read_data
                    if validation:
                        if not hasattr(self, 'schema'):
                            self.schema = schema.openlabel_schema
                        validate(instance=self.data, schema=self.schema)  # Raises errors if not validated
                        json_file.close()

                    # In OpenLABEL 0.3.0-1.0.0 uids are strings, because they can be numeric strings, or UUIDs
                    # but frames are still indexed by ints, so let's parse frame numbers as integers
                    if 'frames' in self.data['openlabel']:
                        frames = self.data['openlabel']['frames']
                        if frames:  # So frames is not empty
                            self.data['openlabel']['frames'] = {int(key): value for key, value in frames.items()}
                else:
                    Exception(
                        "ERROR: This OpenLABEL file has version different than 0.3.0 or 1.0.0. This API is incompatible.")                

            # Close file
            json_file.close()

            # Final set-up
            self.__compute_last_uid()
        else:
            # Init the VCD structures
            self.reset()

    def set_use_uuid(self, val):
        assert(isinstance(val, bool))
        self.use_uuid = val

    def reset(self):
        # Main VCD data
        self.data = {'openlabel': {}}
        self.data['openlabel']['metadata'] = {}
        self.data['openlabel']['metadata']['schema_version'] = schema.openlabel_schema_version

        # Schema information
        self.schema = schema.openlabel_schema

        # Additional auxiliary structures
        self.__lastUID = dict()
        self.__lastUID[ElementType.object] = -1
        self.__lastUID[ElementType.action] = -1
        self.__lastUID[ElementType.event] = -1
        self.__lastUID[ElementType.context] = -1
        self.__lastUID[ElementType.relation] = -1
        self.__lastUID[ElementType.tag] = -1

    def convert_to_vcd330(self):
        return converter.ConverterVCD430toVCD330(self.data)

    ##################################################
    # Private API: inner functions
    ##################################################
    def __get_uid_to_assign(self, element_type, uid):
        assert isinstance(element_type, ElementType)
        assert(isinstance(uid, UID))
        if uid.is_none():
            if self.use_uuid:
                # Let's use UUIDs
                uid_to_assign = UID(str(uuid.uuid4()))
            else:
                # Let's use integers
                self.__lastUID[element_type] += 1
                uid_to_assign = UID(self.__lastUID[element_type])
        else:
            # uid is not None
            assert(isinstance(uid, UID))
            if not uid.is_uuid():
                # Ok, user provided a number, let's proceed
                if uid.as_int() > self.__lastUID[element_type]:
                    self.__lastUID[element_type] = uid.as_int()
                    uid_to_assign = UID(self.__lastUID[element_type])
                else:
                    uid_to_assign = uid
            else:
                # This is a UUID
                self.use_uuid = True
                uid_to_assign = uid

        return uid_to_assign

    def __set_vcd_frame_intervals(self, frame_intervals):
        assert(isinstance(frame_intervals, FrameIntervals))
        if not frame_intervals.empty():
            self.data['openlabel']['frame_intervals'] = frame_intervals.get_dict()

    def __update_vcd_frame_intervals(self, frame_intervals):
        # This function creates the union of existing VCD with the input frameIntervals
        assert (isinstance(frame_intervals, FrameIntervals))
        if not frame_intervals.empty():
            if 'frame_intervals' not in self.data['openlabel']:
                self.data['openlabel']['frame_intervals'] = []
            fis_current = FrameIntervals(self.data['openlabel']['frame_intervals'])
            fis_union = fis_current.union(frame_intervals)
            self.__set_vcd_frame_intervals(fis_union)

    def __add_frame(self, frame_num):
        if 'frames' not in self.data['openlabel']:
            self.data['openlabel']['frames'] = {}
        if frame_num not in self.data['openlabel']['frames']:
            self.data['openlabel']['frames'][frame_num] = {}

    def __compute_last_uid(self):
        self.__lastUID = dict()
        # Read all objects and fill lastUID
        self.__lastUID[ElementType.object] = -1
        if 'objects' in self.data['openlabel']:
            for uid in self.data['openlabel']['objects']:
                if int(uid) > self.__lastUID[ElementType.object]:
                    self.__lastUID[ElementType.object] = int(uid)

        self.__lastUID[ElementType.action] = -1
        if 'actions' in self.data['openlabel']:
            for uid in self.data['openlabel']['actions']:
                if int(uid) > self.__lastUID[ElementType.action]:
                    self.__lastUID[ElementType.action] = int(uid)

        self.__lastUID[ElementType.event] = -1
        if 'events' in self.data['openlabel']:
            for uid in self.data['openlabel']['events']:
                if int(uid) > self.__lastUID[ElementType.event]:
                    self.__lastUID[ElementType.event] = int(uid)

        self.__lastUID[ElementType.context] = -1
        if 'contexts' in self.data['openlabel']:
            for uid in self.data['openlabel']['contexts']:
                if int(uid) > self.__lastUID[ElementType.context]:
                    self.__lastUID[ElementType.context] = int(uid)

        self.__lastUID[ElementType.relation] = -1
        if 'relations' in self.data['openlabel']:
            for uid in self.data['openlabel']['relations']:
                if int(uid) > self.__lastUID[ElementType.relation]:  # uid is a string!
                    self.__lastUID[ElementType.relation] = int(uid)

    def __add_frames(self, frame_intervals, element_type, uid):
        assert(isinstance(frame_intervals, FrameIntervals))
        assert(isinstance(element_type, ElementType))
        assert(isinstance(uid, UID))
        if frame_intervals.empty():
            return
        else:
            # Loop over frames and add
            fis = frame_intervals.get()
            for fi in fis:
                for f in range(fi[0], fi[1]+1):
                    # Add frame
                    self.__add_frame(f)
                    # Add element entry
                    frame = self.get_frame(f)
                    frame.setdefault(element_type.name + 's', {})
                    frame[element_type.name + 's'].setdefault(uid.as_str(), {})

    def __set_element(
            self, element_type, name, semantic_type, frame_intervals, uid, ont_uid,
            coordinate_system, set_mode, res_uid, **kwargs
    ):
        assert (isinstance(uid, UID))
        assert (isinstance(ont_uid, UID))
        if res_uid is not None:
            assert (isinstance(res_uid, ResourceUID))
        assert (isinstance(frame_intervals, FrameIntervals))
        assert (isinstance(set_mode, SetMode))

        fis = frame_intervals
        if set_mode == SetMode.union:
            # Union means fusion, we are calling this function to "add" content, not to remove any
            fis_existing = self.get_element_frame_intervals(element_type, uid.as_str())
            fis = fis_existing.union(frame_intervals)

        # 0.- Get uid_to_assign
        uid_to_assign = self.__get_uid_to_assign(element_type, uid)  # note: private functions use UID type for uids

        # 1.- Set the root entries and frames entries
        self.__set_element_at_root_and_frames(element_type, name, semantic_type, fis,
                                              uid_to_assign, ont_uid, coordinate_system, res_uid)

        # 2.- Kwargs
        # Add any additional custom properties
        element = self.data['openlabel'][element_type.name + 's'][uid_to_assign.as_str()]
        for key, value in kwargs.items():
            element[key] = value

        return uid_to_assign

    def __set_element_at_root_and_frames(
            self, element_type, name, semantic_type, frame_intervals, uid, ont_uid, coordinate_system, res_uid
    ):
        # 1.- Copy from existing or create new entry (this copies everything, including element_data)
        # element_data_pointers and frame intervals
        uidstr = uid.as_str()
        element_existed = self.has(element_type, uidstr)# note: public functions use int or str for uids
        self.data['openlabel'].setdefault(element_type.name + 's', {})
        self.data['openlabel'][element_type.name + 's'].setdefault(uidstr, {})
        element = self.data['openlabel'][element_type.name + 's'][uidstr]

        fis_old = FrameIntervals()
        if 'frame_intervals' in element:
            fis_old = FrameIntervals(element['frame_intervals'])

        # 2.- Copy from arguments
        if name is not None:
            element['name'] = name
        if semantic_type is not None:
            element['type'] = semantic_type
        if not frame_intervals.empty() or (element_existed and not fis_old.empty()):
            # So, either the newFis has something, or the fisOld had something (in which case needs to be substituted)
            # Under the previous control, no 'frame_intervals' field is added to newly created static elements
            # -> should 'frame_intervals' be mandatory
            element['frame_intervals'] = frame_intervals.get_dict()
        if not ont_uid.is_none() and self.get_ontology(ont_uid.as_str()):
            element['ontology_uid'] = ont_uid.as_str()
        if res_uid is not None:
            resource_uid = res_uid.resource_uid
            if not resource_uid.is_none() and self.get_resource(resource_uid.as_str()):
                element['resource_uid'] = res_uid.as_dict()
        if coordinate_system is not None and self.has_coordinate_system(coordinate_system):
            element['coordinate_system'] = coordinate_system

        # 2.bis.- For Relations obligue to have rdf_objects and rdf_subjects entries (to be compliant with schema)
        if element_type is ElementType.relation:
            if 'rdf_subjects' not in element:
                element['rdf_subjects'] = []
            if 'rdf_objects' not in element:
                element['rdf_objects'] = []

        # 3.- Reshape element_data_pointers according to this new frame intervals
        if element_type.name + '_data_pointers' in element:
            edps = element[element_type.name + '_data_pointers']
            for edp_name in edps:
                # NOW, we have to UPDATE frame intervals of pointers because we have modified the frame_intervals
                # of the element itself, adn
                # If we compute the intersection frame_intervals, we can copy that into
                # element_data_pointers frame intervals
                fis_int = FrameIntervals()
                if not frame_intervals.empty():
                    fis_int = frame_intervals.intersection(FrameIntervals(edps[edp_name]['frame_intervals']))

                # Update the pointers
                element.setdefault(element_type.name + '_data_pointers', {})
                element[element_type.name + '_data_pointers'][edp_name] = edps[edp_name]
                element[element_type.name + '_data_pointers'][edp_name]['frame_intervals'] = fis_int.get_dict()

        # 4.- Now set at frames
        if not frame_intervals.empty():
            # 2.1.- There is frame_intervals specified
            if not element_existed:
                # 2.1.a) Just create the new element
                self.__add_frames(frame_intervals, element_type, uid)
                self.__update_vcd_frame_intervals(frame_intervals)
            else:
                # 2.1.b) This is a substitution: depending on the new frame_intervals, we may need to delete/add frames
                # Add
                fis_new = frame_intervals
                for fi in fis_new.get():
                    for f in range(fi[0], fi[1] + 1):
                        is_inside = fis_old.has_frame(f)
                        if not is_inside:
                            # New frame is not inside -> let's add this frame
                            fi_ = FrameIntervals(f)
                            self.__add_frames(fi_, element_type, uid)
                            self.__update_vcd_frame_intervals(fi_)
                # Remove
                if element_existed and fis_old.empty():
                    # Ok, the element was originally static (thus with fisOld empty)
                    # so potentially there are pointers of the element in all frames (in case there are frames)
                    # Now the element is declared with a specific frame intervals. Then we first need to remove all
                    # element entries (pointers) in all OTHER frames
                    vcd_frame_intervals = self.get_frame_intervals()
                    if not vcd_frame_intervals.empty():
                        for fi in vcd_frame_intervals.get():
                            for f in range(fi[0], fi[1] + 1):
                                if not fis_new.has_frame(f):  # Only for those OTHER frames not those just added
                                    elements_in_frame = self.data['openlabel']['frames'][f][element_type.name + 's']
                                    if uidstr in elements_in_frame:
                                        del elements_in_frame[uidstr]
                                        if len(elements_in_frame) == 0:
                                            del self.data['openlabel']['frames'][f][element_type.name + 's']
                                            if len(self.data['openlabel']['frames'][f]) == 0:
                                                self.__rm_frame(f)

                # Next loop for is for the case fis_old wasn't empty, so we just need to remove old content
                for fi in fis_old.get():
                    for f in range(fi[0], fi[1] + 1):
                        is_inside = fis_new.has_frame(f)
                        if not is_inside:
                            # Old frame not inside new ones -> let's remove this frame
                            elements_in_frame = self.data['openlabel']['frames'][f][element_type.name + 's']
                            del elements_in_frame[uidstr]
                            if len(elements_in_frame) == 0:
                                del self.data['openlabel']['frames'][f][element_type.name + 's']
                                if len(self.data['openlabel']['frames'][f]) == 0:
                                    self.__rm_frame(f)
        else:
            # 2.2.- The element is declared as static
            if element_type is not ElementType.relation:  # frame-less relation must remain frame-less
                vcd_frame_intervals = self.get_frame_intervals()
                if not vcd_frame_intervals.empty():
                    # ... but VCD has already other elements or info that have established some frame intervals
                    # The element is then assumed to exist in all frames: let's add a pointer into all frames
                    self.__add_frames(vcd_frame_intervals, element_type, uid)

            # But, if the element existed previously, and it was dynamic, there is already information inside frames.
            # If there is element_data at frames, they are removed
            if not fis_old.empty():
                self.rm_element_data_from_frames(element_type, uid, fis_old)

                # Additionally, we need to remove element entries at frames, and frames entirely to clean-up
                for fi in fis_old.get():
                    for f in range(fi[0], fi[1] + 1):
                        elements_in_frame = self.data['openlabel']['frames'][f][element_type.name + 's']
                        del elements_in_frame[uidstr]
                        # Clean-up
                        if len(elements_in_frame) == 0:
                            del self.data['openlabel']['frames'][f][element_type.name + 's']
                            if len(self.data['openlabel']['frames'][f]) == 0:
                                self.__rm_frame(f)

    def __set_element_data(self, element_type, uid, element_data, frame_intervals, set_mode):
        assert(isinstance(uid, UID))
        assert(isinstance(frame_intervals, FrameIntervals))
        assert(isinstance(set_mode, SetMode))

        # 0.- Checks
        if not self.has(element_type, uid.as_str()):
            warnings.warn("WARNING: Trying to set element_data for a non-existing element.")
            return
        element = self.get_element(element_type, uid.as_str())

        # Read existing data about this element, so we can call __set_element
        name = element.get('name')
        semantic_type = element['type']
        ont_uid = UID(None)
        cs = None
        if 'ontology_uid' in element:
            ont_uid = UID(element['ontology_uid'])
        res_uid = None
        if 'resource_uid' in element:
            res_uid = ResourceUID(element['resource_uid'].keys()[0],
                                  element['resource_uid'].values()[0])
        if 'coordinate_system' in element:
            cs = element['coordinate_system']

        if 'coordinate_system' in element_data.data:
            if not self.has_coordinate_system(element_data.data['coordinate_system']):
                warnings.warn("WARNING: Trying to set element_data with a non-declared coordinate system.")
                return

        if frame_intervals.empty() and set_mode == SetMode.union and not isinstance(element_data, types.mesh):
            set_mode = SetMode.replace

        if set_mode == SetMode.replace:
            # Extend also the container Element just in case the frame_interval of this element_data is beyond it
            # removes/creates frames if needed
            # This call is to modify an existing element_data, which may imply removing some frames
            if not frame_intervals.empty():
                fis_existing = FrameIntervals(element['frame_intervals'])
                fis_new = frame_intervals
                fis_union = fis_existing.union(fis_new)
                self.__set_element(element_type, name, semantic_type, fis_union, uid, ont_uid, cs, set_mode, res_uid)
                self.__set_element_data_content_at_frames(element_type, uid, element_data, frame_intervals)
            else:
                # This is a static element_data. If it was declared dynamic before, let's remove it
                #self.__set_element(element_type, name, semantic_type, frame_intervals, uid, ont_uid, cs, set_mode)
                if self.has_element_data(element_type, uid.as_str(), element_data):
                    fis_old = self.get_element_data_frame_intervals(element_type, uid.as_str(), element_data.data['name'])
                    if not fis_old.empty():
                        self.rm_element_data_from_frames_by_name(element_type, uid, element_data.data['name'], fis_old)
                self.__set_element_data_content(element_type, element, element_data)
            # Set the pointers
            self.__set_element_data_pointers(element_type, uid, element_data, frame_intervals)
        else:  # set_mode = SetMode.union
            # This call is to add element_data to the element, substituting content if overlap, otherwise adding
            # First, extend also the container Element just in case the frame_interval of this element_data is beyond
            # the currently existing frame_intervals of the Element
            # internally computes the union
            self.__set_element(element_type, name, semantic_type, frame_intervals, uid, ont_uid, cs, set_mode, res_uid)

            if not frame_intervals.empty():
                fis_existing = FrameIntervals()
                if element_type.name + '_data_pointers' in element:
                    edp = element[element_type.name + '_data_pointers']
                    if element_data.data['name'] in edp:
                        fis_existing = FrameIntervals(edp[element_data.data['name']]['frame_intervals'])
                fis_new = frame_intervals
                fis_union = fis_existing.union(fis_new)

                # Dynamic
                if element is not None:
                    # It is not a simple call with the union of frame intervals
                    # We need to substitute the content for just this frame_interval, without modifying the rest
                    # that must stay as it was
                    # Loop over the specified frame_intervals to create or substitute the content
                    self.__set_element_data_content_at_frames(element_type, uid, element_data, fis_new)

                # Set the pointers (but the pointers we have to update using the union)
                self.__set_element_data_pointers(element_type, uid, element_data, fis_union)
            elif isinstance(element_data, types.mesh):
                # This is only for mesh case that can have this static part
                # (because it is an object data type which is both static and dynamic)
                self.__set_element_data_content(element_type, element, element_data)

    def __set_element_data_content_at_frames(self, element_type, uid, element_data, frame_intervals):
        # Loop over the specified frame_intervals to create or substitute the content
        # Create entries of the element_data at frames
        fis = frame_intervals.get()
        for fi in fis:
            for f in range(fi[0], fi[1] + 1):
                # Add element_data entry
                frame = self.get_frame(f)
                if frame is None:
                    self.__add_frame(f)
                    frame = self.get_frame(f)

                frame.setdefault(element_type.name + 's', {})
                frame[element_type.name + 's'].setdefault(uid.as_str(), {})
                element = frame[element_type.name + 's'][uid.as_str()]
                self.__set_element_data_content(element_type, element, element_data)

    @staticmethod
    def __set_tag_data_content(tag, tag_data):
        tag.setdefault('val', {})
        tag['val'].setdefault(tag_data.type.name, [])
        list_aux = tag['val'][tag_data.type.name]
        pos_list = [idx for idx, val in enumerate(list_aux) if val['name'] == tag_data.data['name']]
        if len(pos_list) == 0:
            tag['val'][tag_data.type.name].append(tag_data.data)
        else:
            pos = pos_list[0]
            tag['val'][tag_data.type.name][pos] = tag_data.data

    @staticmethod
    def __set_element_data_content(element_type, element, element_data):
        # Adds the element_data to the corresponding container
        # If an element_data with same name exists, it is substituted
        element.setdefault(element_type.name + '_data', {})
        element[element_type.name + '_data'].setdefault(element_data.type.name, [])

        # Find if element_data already there
        if 'name' in element_data.data:
            list_aux = element[element_type.name + '_data'][element_data.type.name]
            pos_list = [idx for idx, val in enumerate(list_aux) if val['name'] == element_data.data['name']]
        else:
            pos_list = []

        if len(pos_list) == 0:
            # Not found, then just push this new element data
            element[element_type.name + '_data'][element_data.type.name].append(element_data.data)
        else:
            # Found: let's substitute
            pos = pos_list[0]
            element[element_type.name + '_data'][element_data.type.name][pos] = element_data.data

    def __set_element_data_pointers(self, element_type, uid, element_data, frame_intervals):
        # For Tags, let's ignore element_data_pointers
        if element_type == ElementType.tag:
            return

        assert(isinstance(uid, UID))
        self.data['openlabel'][element_type.name + 's'][uid.as_str()].setdefault(element_type.name + '_data_pointers', {})
        edp = self.data['openlabel'][element_type.name + 's'][uid.as_str()][element_type.name + '_data_pointers']
        edp[element_data.data['name']] = {}
        edp[element_data.data['name']]['type'] = element_data.type.name
        if frame_intervals is None:
            edp[element_data.data['name']]['frame_intervals'] = []
        else:
            edp[element_data.data['name']]['frame_intervals'] = frame_intervals.get_dict()
        if 'attributes' in element_data.data:
            edp[element_data.data['name']]['attributes'] = {}
            for attr_type in element_data.data['attributes']:  # attr_type might be 'boolean', 'text', 'num', or 'vec'
                for attr in element_data.data['attributes'][attr_type]:
                    edp[element_data.data['name']]['attributes'][attr['name']] = attr_type

    def __rm_frame(self, frame_num):
        # This function deletes a frame entry from frames, and updates VCD accordingly
        if 'frames' in self.data['openlabel']:
            if frame_num in self.data['openlabel']['frames']:
                del self.data['openlabel']['frames'][frame_num]
            if len(self.data['openlabel']['frames']) == 0:
                del self.data['openlabel']['frames']

        # Remove from VCD frame intervals
        if 'frame_intervals' in self.data['openlabel']:
            fis_dict = self.data['openlabel']['frame_intervals']
            fis_dict_new = utils.rm_frame_from_frame_intervals(fis_dict, frame_num)

            # Now substitute
            if len(fis_dict_new) == 0:
                del self.data['openlabel']['frame_intervals']
            else:
                self.data['openlabel']['frame_intervals'] = fis_dict_new


    def __compute_data_pointers(self):
        # WARNING! This function might be extremely slow
        # It does loop over all frames, and updates data pointers at objects, actions, etc
        # It is useful to convert from VCD 4.2.0 into VCD 4.3.1 (use converter.ConverterVCD420toVCD430)

        # Looping over frames and creating the necessary data_pointers
        if 'frame_intervals' in self.data['openlabel']:
            fis = self.data['openlabel']['frame_intervals']
            for fi in fis:
                for frame_num in range(fi['frame_start'], fi['frame_end'] + 1):
                    frame = self.get_frame(frame_num)
                    for element_type in ElementType:
                        if element_type.name + 's' in frame:  # e.g. "objects", "actions"...
                            for uid, element in frame[element_type.name + 's'].items():
                                if element_type.name + '_data' in element:
                                    # So this element has element_data in this frame
                                    # and then we need to update the element_data_pointer at the root
                                    # we can safely assume it already exists

                                    # First, let's create a element_data_pointer at the root
                                    self.data['openlabel'][element_type.name + 's'][uid].\
                                        setdefault(element_type.name + '_data_pointers', {})
                                    edp = self.data['openlabel'][element_type.name + 's'][uid]
                                    [element_type.name + '_data_pointers']

                                    # Let's loop over the element_data
                                    for ed_type, ed_array in element[element_type.name + '_data'].items():
                                        # e.g. ed_type is 'bbox', ed_array is the array of such bboxes content
                                        for element_data in ed_array:
                                            name = element_data['name']
                                            edp.setdefault(name, {})  # this element_data may already exist
                                            edp[name].setdefault('type', ed_type)  # e.g. 'bbox'
                                            edp[name].setdefault('frame_intervals', [])  # in case it does not exist
                                            fis_exist = FrameIntervals(edp[name]['frame_intervals'])
                                            fis_exist.union(FrameIntervals(frame_num))  # So, let's fuse with this frame
                                            edp[name]['frame_intervals'] = fis_exist.get_dict()  # overwrite
                                            # No need to manage attributes

    def rm_element_data_from_frames_by_name(self, element_type, uid, element_data_name, frame_intervals):
        for fi in frame_intervals.get():
            for f in range(fi[0], fi[1] + 1):
                if self.has_frame(f):
                    frame = self.data['openlabel']['frames'][f]
                    if element_type.name + 's' in frame:
                        if uid.as_str() in frame[element_type.name + 's']:
                            element = frame[element_type.name + 's'][uid.as_str()]
                            if element_type.name + '_data' in element:
                                # Delete only the element_data with the specified name
                                for prop in element[element_type.name + '_data']:
                                    val_array = element[element_type.name + '_data'][prop]
                                    for i in range(0, len(val_array)):
                                        val = val_array[i]
                                        if val['name'] == element_data_name:
                                            del element[element_type.name + '_data'][prop][i]

    def rm_element_data_from_frames(self, element_type, uid, frame_intervals):
        for fi in frame_intervals.get():
            for f in range(fi[0], fi[1] + 1):
                if self.has_frame(f):
                    frame = self.data['openlabel']['frames'][f]
                    if element_type.name + 's' in frame:
                        if uid.as_str() in frame[element_type.name + 's']:
                            element = frame[element_type.name + 's'][uid.as_str()]
                            if element_type.name + '_data' in element:
                                # Delete all its former dyamic element_data entries at old fis
                                del element[element_type.name + '_data']

        # Clean-up data pointers of object_data that no longer exist!
        # Note, element_data_pointers are correctly updated, but there might be some now declared as static
        # corresponding to element_data that was dynamic but now has been removed when the element changed to static
        if self.has(element_type, uid.as_str()):
            element = self.data['openlabel'][element_type.name + 's'][uid.as_str()]
            if element_type.name + '_data_pointers' in element:
                edps = element[element_type.name + '_data_pointers']
                edp_names_to_delete = []
                for edp_name in edps:
                    fis_ed = FrameIntervals(edps[edp_name]['frame_intervals'])
                    if fis_ed.empty():
                        # Check if element_data exists
                        ed_type = edps[edp_name]['type']
                        found = False
                        if element_type.name + '_data' in element:
                            if ed_type in element[element_type.name + '_data']:
                                for ed in element[element_type.name + '_data'][ed_type]:
                                    if ed['name'] == edp_name:
                                        found = True
                                        break
                        if not found:
                            edp_names_to_delete.append(edp_name)
                for edp_name in edp_names_to_delete:
                    del element[element_type.name + '_data_pointers'][edp_name]

    ##################################################
    # Public API: add, update
    ##################################################
    def add_file_version(self, version):
        assert (type(version) is str)
        if 'metadata' not in self.data['openlabel']:
            self.data['openlabel']['metadata'] = {}
        self.data['openlabel']['metadata']['file_version'] = version

    def add_metadata_properties(self, properties):
        assert(isinstance(properties, dict))
        prop = self.data['openlabel']['metadata']
        prop.update(properties)

    def add_name(self, name):
        assert(type(name) is str)
        if 'metadata' not in self.data['openlabel']:
            self.data['openlabel']['metadata'] = {}
        self.data['openlabel']['metadata']['name'] = name

    def add_annotator(self, annotator):
        assert(type(annotator) is str)
        if 'metadata' not in self.data['openlabel']:
            self.data['openlabel']['metadata'] = {}
        self.data['openlabel']['metadata']['annotator'] = annotator

    def add_comment(self, comment):
        assert(type(comment) is str)
        if 'metadata' not in self.data['openlabel']:
            self.data['openlabel']['metadata'] = {}
        self.data['openlabel']['metadata']['comment'] = comment

    def add_ontology(self, ontology_name, subset_include=None, subset_exclude=None, **kwargs):
        self.data['openlabel'].setdefault('ontologies', dict())
        for ont_uid in self.data['openlabel']['ontologies']:
            if self.data['openlabel']['ontologies'][ont_uid] == ontology_name:
                warnings.warn('WARNING: adding an already existing ontology')
                return None
        length = len(self.data['openlabel']['ontologies'])
        if subset_include is None and subset_exclude is None and len(kwargs)==0:
            self.data['openlabel']['ontologies'][str(length)] = ontology_name
        else:
            self.data['openlabel']['ontologies'][str(length)] = {"uri": ontology_name}
            if subset_include is not None:
                self.data['openlabel']['ontologies'][str(length)]["subset_include"] = subset_include
            if subset_exclude is not None:
                self.data['openlabel']['ontologies'][str(length)]["subset_exclude"] = subset_exclude
            for key, value in kwargs.items():
                self.data['openlabel']['ontologies'][str(length)][key] = value
        return str(length)

    def add_resource(self, resource_name):
        self.data['openlabel'].setdefault('resources', dict())
        for res_uid in self.data['openlabel']['resources']:
            if self.data['openlabel']['resources'][res_uid] == resource_name:
                warnings.warn('WARNING: adding an already existing resource')
                return None
        length = len(self.data['openlabel']['resources'])
        self.data['openlabel']['resources'][str(length)] = resource_name
        return str(length)

    def add_coordinate_system(self, name, cs_type, parent_name="", pose_wrt_parent=None):
        # Argument pose_wrt_parent can be used to quickly add a list containing the 4x4 matrix
        # However, argument pose can be used to add any type of Pose object (created with types.Pose)
        assert(isinstance(cs_type, types.CoordinateSystemType))

        # Create entry
        self.data['openlabel'].setdefault('coordinate_systems', {})
        self.data['openlabel']['coordinate_systems'][name] = {'type': cs_type.name,
                                                        'parent': parent_name,
                                                        'children': []}

        # Add Pose data
        if pose_wrt_parent is not None:
            assert(isinstance(pose_wrt_parent, types.PoseData))
            self.data['openlabel']['coordinate_systems'][name].update({"pose_wrt_parent": pose_wrt_parent.data})        

        # Update parents
        if parent_name != "":
            found = False
            for n, cs in self.data['openlabel']['coordinate_systems'].items():
                if n == parent_name:
                    found = True
                    cs['children'].append(name)
            if not found:
                warnings.warn("WARNING: Creating a coordinate system with a non-defined parent coordinate system."
                              "Coordinate systems must be introduced in order")

    def add_transform(self, frame_num, transform):
        assert(isinstance(frame_num, int))
        assert(isinstance(transform, types.Transform))

        self.__add_frame(frame_num)  # this function internally checks if the frame already exists
        self.data['openlabel']['frames'][frame_num].setdefault('frame_properties', dict())
        self.data['openlabel']['frames'][frame_num]['frame_properties'].setdefault('transforms', dict())
        self.data['openlabel']['frames'][frame_num]['frame_properties']['transforms'].update(transform.data)

    def add_stream(self, stream_name, uri, description, stream_type):
        assert(isinstance(stream_name, str))
        assert(isinstance(uri, str))
        assert(isinstance(description, str))

        self.data['openlabel'].setdefault('streams', dict())
        self.data['openlabel']['streams'].setdefault(stream_name, dict())
        if isinstance(stream_type, StreamType):
            self.data['openlabel']['streams'][stream_name] = {
                'description': description, 'uri': uri, 'type': stream_type.name
            }
        elif isinstance(stream_type, str):
            self.data['openlabel']['streams'][stream_name] = {
                'description': description, 'uri': uri, 'type': stream_type
            }

    def add_frame_properties(self, frame_num, timestamp=None, properties=None):
        self.__add_frame(frame_num)  # this function internally checks if the frame already exists
        self.__update_vcd_frame_intervals(FrameIntervals(frame_num))
        self.data['openlabel']['frames'][frame_num].setdefault('frame_properties', dict())
        if timestamp is not None:
            assert (isinstance(timestamp, (str, float)))
            self.data['openlabel']['frames'][frame_num]['frame_properties']['timestamp'] = timestamp

        if properties is not None:
            assert (isinstance(properties, dict))
            self.data['openlabel']['frames'][frame_num]['frame_properties'].update(properties)

    def add_stream_properties(self, stream_name, properties=None, intrinsics=None, stream_sync=None):
        has_arguments = False
        if intrinsics is not None:
            assert(isinstance(intrinsics, types.Intrinsics))
            has_arguments = True
        if properties is not None:
            assert(isinstance(properties, dict))  # "Properties of Stream should be defined as a dictionary"
            has_arguments = True
        if stream_sync is not None:
            assert(isinstance(stream_sync, types.StreamSync))
            has_arguments = True
            if stream_sync.frame_vcd is not None:
                frame_num = stream_sync.frame_vcd
            else:
                frame_num = None
        else:
            frame_num = None

        if not has_arguments:
            return

        # This function can be used to add stream properties. If frame_num is defined, the information is embedded
        # inside 'frame_properties' of the specified frame. Otherwise, the information is embedded into
        # 'stream_properties' inside 'metadata'.

        # Find if this stream is declared
        if 'metadata' in self.data['openlabel']:
            if 'streams' in self.data['openlabel']:
                if stream_name in self.data['openlabel']['streams']:
                    if frame_num is None:
                        # This information is static
                        self.data['openlabel']['streams'][stream_name].setdefault('stream_properties', dict())
                        if properties is not None:
                            self.data['openlabel']['streams'][stream_name]['stream_properties'].\
                                update(properties)
                        if intrinsics is not None:
                            self.data['openlabel']['streams'][stream_name]['stream_properties'].\
                                update(intrinsics.data)
                        if stream_sync is not None:
                            if stream_sync.data:
                                self.data['openlabel']['streams'][stream_name]['stream_properties'].\
                                    update(stream_sync.data)
                    else:
                        # This is information of the stream for a specific frame
                        self.__add_frame(frame_num)  # to add the frame in case it does not exist
                        frame = self.data['openlabel']['frames'][frame_num]
                        frame.setdefault('frame_properties', dict())
                        frame['frame_properties'].setdefault('streams', dict())
                        frame['frame_properties']['streams'].setdefault(stream_name, dict())
                        frame['frame_properties']['streams'][stream_name].setdefault('stream_properties', dict())
                        if properties is not None:
                            frame['frame_properties']['streams'][stream_name]['stream_properties'].\
                                update(properties)
                        if intrinsics is not None:
                            frame['frame_properties']['streams'][stream_name]['stream_properties'].\
                                update(intrinsics.data)

                        if stream_sync.data:
                            frame['frame_properties']['streams'][stream_name]['stream_properties'].\
                                update(stream_sync.data)
                else:
                    warnings.warn('WARNING: Trying to add stream properties for non-existing stream. '
                                  'Use add_stream first.')

    def save_frame(self, frame_num, file_name, dynamic_only=True, pretty=False):
        string = self.stringify_frame(frame_num, dynamic_only, pretty)
        file = open(file_name, 'w')
        file.write(string)
        file.close()

    def save(self, file_name, pretty=False, validate=False):
        string = self.stringify(pretty, validate)
        file = open(file_name, 'w', encoding='utf8')
        file.write(string)
        file.close()

    def validate(self, stringified_vcd):
        temp = json.loads(stringified_vcd)
        if not hasattr(self, 'schema'):
            self.schema = schema.openlabel_schema
        validate(instance=temp, schema=self.schema)

    def stringify(self, pretty=True, validate=True):
        if pretty:
            stringified_vcd = json.dumps(self.data, indent=4, sort_keys=False, ensure_ascii=False)

        else:
            stringified_vcd = json.dumps(self.data, separators=(',', ':'), sort_keys=False, ensure_ascii=False)
        if validate:
            self.validate(stringified_vcd)
        return stringified_vcd

    def stringify_frame(self, frame_num, dynamic_only=True, pretty=False):
        if frame_num not in self.data['openlabel']['frames']:
            warnings.warn("WARNING: Trying to stringify a non-existing frame.")
            return ''

        if dynamic_only:
            if pretty:
                return json.dumps(self.data['openlabel']['frames'][frame_num], indent=4, sort_keys=True)
            else:
                return json.dumps(self.data['openlabel']['frames'][frame_num])

        else:
            # Need to compose dynamic and static information into a new structure
            # Copy the dynamic info first
            frame_static_dynamic = copy.deepcopy(self.data['openlabel']['frames'][frame_num])  # Needs to be a copy!

            # Now the static info for objects, actions, events, contexts and relations
            # Relations can be frame-less or frame-specific
            for element_type in ElementType:
                # First, elements explicitly defined for this frame
                if element_type.name + 's' in self.data['openlabel']['frames'][frame_num]:
                    for uid, content in self.data['openlabel']['frames'][frame_num][element_type.name + 's'].items():
                        frame_static_dynamic[element_type.name + 's'][uid].update(
                            self.data['openlabel'][element_type.name + 's'][uid]
                        )
                        # Remove frameInterval entry
                        if 'frame_intervals' in frame_static_dynamic[element_type.name + 's'][uid]:
                            del frame_static_dynamic[element_type.name + 's'][uid]['frame_intervals']

                # But also other elements without frame intervals specified, which are assumed to exist during
                # the entire sequence, except frame-less Relations which are assumed to not be associated to any frame
                if element_type.name + 's' in self.data['openlabel'] and element_type.name != 'relation':
                    for uid, element in self.data['openlabel'][element_type.name + 's'].items():
                        frame_intervals_dict = element.get('frame_intervals')
                        if frame_intervals_dict is None or not frame_intervals_dict:
                            # So the list of frame intervals is empty -> this element lives the entire scene
                            # Let's add it to frame_static_dynamic
                            frame_static_dynamic.setdefault(element_type.name + 's', dict()) # in case there are no
                                                                        # such type of elements already in this frame
                            frame_static_dynamic[element_type.name + 's'][uid] = dict()
                            frame_static_dynamic[element_type.name + 's'][uid] = copy.deepcopy(element)

                            # Remove frameInterval entry
                            if 'frame_intervals' in frame_static_dynamic[element_type.name + 's'][uid]:
                                del frame_static_dynamic[element_type.name + 's'][uid]['frame_intervals']

            if pretty:
                return json.dumps(frame_static_dynamic, indent=4, sort_keys=True)
            else:
                return json.dumps(frame_static_dynamic)

    def add_object(self, name, semantic_type='', frame_value=None, uid=None, ont_uid=None, coordinate_system=None,
                   set_mode=SetMode.union, res_uid=None, **kwargs):
        return self.__set_element(ElementType.object, name, semantic_type, FrameIntervals(frame_value),
                                  UID(uid), UID(ont_uid), coordinate_system, set_mode, res_uid, **kwargs).as_str()

    def add_action(self, name, semantic_type='', frame_value=None, uid=None, ont_uid=None, coordinate_system=None,
                   set_mode=SetMode.union, res_uid=None, **kwargs):
        return self.__set_element(ElementType.action, name, semantic_type, FrameIntervals(frame_value),
                                  UID(uid), UID(ont_uid), coordinate_system, set_mode, res_uid, **kwargs).as_str()

    def add_event(self, name, semantic_type='', frame_value=None, uid=None, ont_uid=None, coordinate_system=None,
                  set_mode=SetMode.union, res_uid=None, **kwargs):
        return self.__set_element(ElementType.event, name, semantic_type, FrameIntervals(frame_value),
                                  UID(uid), UID(ont_uid), coordinate_system, set_mode, res_uid, **kwargs).as_str()

    def add_context(self, name, semantic_type='', frame_value=None, uid=None, ont_uid=None, coordinate_system=None,
                    set_mode=SetMode.union, res_uid=None, **kwargs):
        return self.__set_element(ElementType.context, name, semantic_type, FrameIntervals(frame_value),
                                  UID(uid), UID(ont_uid), coordinate_system, set_mode, res_uid, **kwargs).as_str()

    def add_relation(self, name, semantic_type='', frame_value=None, uid=None, ont_uid=None,
                     set_mode=SetMode.union, res_uid=None, **kwargs):
        if set_mode == SetMode.replace and uid is not None:
            if self.has(ElementType.relation, uid):
                relation = self.data['openlabel']['relations'][UID(uid).as_str()]
                relation['rdf_subjects'] = []
                relation['rdf_objects'] = []

        relation_uid = self.__set_element(
            ElementType.relation, name, semantic_type, frame_intervals=FrameIntervals(frame_value),
            uid=UID(uid), ont_uid=UID(ont_uid), set_mode=set_mode, coordinate_system=None, res_uid=res_uid, **kwargs)
        return relation_uid.as_str()

    def add_tag(self, semantic_type='', uid=None, ont_uid=None, res_uid=None, **kwargs):
        return self.__set_element(ElementType.tag, None, semantic_type, FrameIntervals(None),
                                  UID(uid), UID(ont_uid), None, SetMode.union, res_uid, **kwargs).as_str()

    def add_element(self, element_type, name, semantic_type='', frame_value=None, uid=None, ont_uid=None, coordinate_system=None,
                    set_mode=SetMode.union, res_uid=None, **kwargs):
        return self.__set_element(element_type, name, semantic_type, FrameIntervals(frame_value),
                                  UID(uid), UID(ont_uid), coordinate_system, set_mode, res_uid, **kwargs).as_str()

    def add_rdf(self, relation_uid, rdf_type, element_uid, element_type):
        assert(isinstance(element_type, ElementType))
        assert(isinstance(rdf_type, RDF))
        rel_uid = UID(relation_uid)
        el_uid = UID(element_uid)
        if rel_uid.as_str() not in self.data['openlabel']['relations']:
            warnings.warn("WARNING: trying to add RDF to non-existing Relation.")
            return
        else:
            relation = self.data['openlabel']['relations'][rel_uid.as_str()]
            if el_uid.as_str() not in self.data['openlabel'][element_type.name + 's']:
                warnings.warn("WARNING: trying to add RDF using non-existing Element.")
                return
            else:
                if rdf_type == RDF.subject:
                    relation.setdefault('rdf_subjects', [])
                    relation['rdf_subjects'].append(
                        {'uid': el_uid.as_str(), 'type': element_type.name}
                    )
                else:
                    relation.setdefault('rdf_objects', [])
                    relation['rdf_objects'].append(
                        {'uid': el_uid.as_str(), 'type': element_type.name}
                    )

    def add_relation_object_action(self, name, semantic_type, object_uid, action_uid, relation_uid=None,
                                   ont_uid=None, frame_value=None, set_mode=SetMode.union, res_uid=None, **kwargs):
        # Note: no need to wrap uids as UID, since all calls are public functions, and no access to dict is done.
        relation_uid = self.add_relation(name, semantic_type, uid=relation_uid, ont_uid=ont_uid,
                                         frame_value=frame_value, set_mode=set_mode, res_uid=res_uid, **kwargs)
        self.add_rdf(relation_uid=relation_uid, rdf_type=RDF.subject,
                     element_uid=object_uid, element_type=ElementType.object)
        self.add_rdf(relation_uid=relation_uid, rdf_type=RDF.object,
                     element_uid=action_uid, element_type=ElementType.action)

        return relation_uid

    def add_relation_action_action(self, name, semantic_type, action_uid_1, action_uid_2, relation_uid=None,
                                   ont_uid=None, frame_value=None, set_mode=SetMode.union, res_uid=None, **kwargs):
        # Note: no need to wrap uids as UID, since all calls are public functions, and no access to dict is done.
        relation_uid = self.add_relation(name, semantic_type, uid=relation_uid, ont_uid=ont_uid,
                                         frame_value=frame_value, set_mode=set_mode, res_uid=res_uid, **kwargs)
        self.add_rdf(relation_uid=relation_uid, rdf_type=RDF.subject,
                     element_uid=action_uid_1, element_type=ElementType.action)
        self.add_rdf(relation_uid=relation_uid, rdf_type=RDF.object,
                     element_uid=action_uid_2, element_type=ElementType.action)

        return relation_uid

    def add_relation_object_object(self, name, semantic_type, object_uid_1, object_uid_2, relation_uid=None,
                                   ont_uid=None, frame_value=None, set_mode=SetMode.union, res_uid=None, **kwargs):
        # Note: no need to wrap uids as UID, since all calls are public functions, and no access to dict is done.
        relation_uid = self.add_relation(name, semantic_type, uid=relation_uid, ont_uid=ont_uid,
                                         frame_value=frame_value, set_mode=set_mode, res_uid=res_uid, **kwargs)
        self.add_rdf(relation_uid=relation_uid, rdf_type=RDF.subject,
                     element_uid=object_uid_1, element_type=ElementType.object)
        self.add_rdf(relation_uid=relation_uid, rdf_type=RDF.object,
                     element_uid=object_uid_2, element_type=ElementType.object)

        return relation_uid

    def add_relation_action_object(self, name, semantic_type, action_uid, object_uid, relation_uid=None,
                                   ont_uid=None, frame_value=None, set_mode=SetMode.union, res_uid=None, **kwargs):
        # Note: no need to wrap uids as UID, since all calls are public functions, and no access to dict is done.
        relation_uid = self.add_relation(name, semantic_type, uid=relation_uid, ont_uid=ont_uid,
                                         frame_value=frame_value, set_mode=set_mode, res_uid=res_uid, **kwargs)
        self.add_rdf(relation_uid=relation_uid, rdf_type=RDF.subject,
                     element_uid=action_uid, element_type=ElementType.action)
        self.add_rdf(relation_uid=relation_uid, rdf_type=RDF.object,
                     element_uid=object_uid, element_type=ElementType.object)

        return relation_uid

    def add_relation_subject_object(self, name, semantic_type, subject_type, subject_uid, object_type, object_uid,
                                    relation_uid=None, ont_uid=None, frame_value=None, set_mode=SetMode.union, res_uid=None, **kwargs):
        # Note: no need to wrap uids as UID, since all calls are public functions, and no access to dict is done.
        relation_uid = self.add_relation(name, semantic_type, uid=relation_uid, ont_uid=ont_uid,
                                         frame_value=frame_value, set_mode=set_mode, res_uid=res_uid, **kwargs)
        assert(isinstance(subject_type, ElementType))
        assert(isinstance(object_type, ElementType))
        self.add_rdf(relation_uid=relation_uid, rdf_type=RDF.subject,
                     element_uid=subject_uid, element_type=subject_type)
        self.add_rdf(relation_uid=relation_uid, rdf_type=RDF.object,
                     element_uid=object_uid, element_type=object_type)

        return relation_uid

    def add_object_data(self, uid, object_data, frame_value=None, set_mode=SetMode.union):
        return self.__set_element_data(ElementType.object, UID(uid), object_data, FrameIntervals(frame_value),
                                       set_mode)

    def add_action_data(self, uid, action_data, frame_value=None, set_mode=SetMode.union):
        return self.__set_element_data(ElementType.action, UID(uid), action_data, FrameIntervals(frame_value),
                                       set_mode)

    def add_event_data(self, uid, event_data, frame_value=None, set_mode=SetMode.union):
        return self.__set_element_data(ElementType.evevt, UID(uid), event_data, FrameIntervals(frame_value),
                                       set_mode)

    def add_context_data(self, uid, context_data, frame_value=None, set_mode=SetMode.union):
        return self.__set_element_data(ElementType.context, UID(uid), context_data, FrameIntervals(frame_value),
                                       set_mode)

    def add_tag_data(self, uid, tag_data, frame_value=None, set_mode=SetMode.union):
        return self.__set_element_data(ElementType.tag, UID(uid), tag_data, FrameIntervals(frame_value),
                                       set_mode)
    
    def add_element_data(self, element_type, uid, element_data, frame_value=None, set_mode=SetMode.union):
        return self.__set_element_data(element_type, UID(uid), element_data, FrameIntervals(frame_value),
                                       set_mode)

    ##################################################
    # Get / Read
    ##################################################
    def get_data(self):
        return self.data

    def get_root(self):
        return self.data['openlabel']

    def has_elements(self, element_type):
        element_type_name = element_type.name
        return element_type_name + 's' in self.data['openlabel']

    def has_objects(self):
        return 'objects' in self.data['openlabel']

    def has_actions(self):
        return 'actions' in self.data['openlabel']

    def has_contexts(self):
        return 'contexts' in self.data['openlabel']

    def has_events(self):
        return 'events' in self.data['openlabel']

    def has_relations(self):
        return 'relations' in self.data['openlabel']

    def has(self, element_type, uid):
        if not element_type.name + 's' in self.data['openlabel']:
            return False
        else:
            uid_str = UID(uid).as_str()
            if uid_str in self.data['openlabel'][element_type.name + 's']:
                return True
            else:
                return False

    def has_element_data(self, element_type, uid, element_data):
        if not self.has(element_type, uid):
            return False
        else:
            uid_str = UID(uid).as_str()
            if element_type.name + '_data_pointers' not in self.data['openlabel'][element_type.name + 's'][uid_str]:
                return False
            name = element_data.data['name']
            return name in self.data['openlabel'][element_type.name + 's'][uid_str][element_type.name + '_data_pointers']

    def has_frame(self, frame_num):
        if 'frames' not in self.data['openlabel']:
            return False
        else:
            if frame_num in self.data['openlabel']['frames']:
                return True
            else:
                return False

    def get_all(self, element_type):
        """
        Returns all elements of the specified ElementType.
        e.g. all Object's or Context's
        """
        assert(isinstance(element_type, ElementType))
        return self.data['openlabel'].get(element_type.name + 's')

    def get_element(self, element_type, uid):
        assert (isinstance(element_type, ElementType))
        if self.data['openlabel'].get(element_type.name + 's') is None:
            warnings.warn("WARNING: trying to get a " + element_type.name + " but this VCD has none.")
            return None
        uid_str = UID(uid).as_str()
        if uid_str in self.data['openlabel'][element_type.name + 's']:
            return self.data['openlabel'][element_type.name + 's'][uid_str]
        else:
            warnings.warn("WARNING: trying to get non-existing " + element_type.name + " with uid: " + uid_str)
            return None

    def get_objects(self):
        return self.data['openlabel'].get('objects')

    def get_actions(self):
        return self.data['openlabel'].get('actions')

    def get_events(self):
        return self.data['openlabel'].get('events')

    def get_contexts(self):
        return self.data['openlabel'].get('contexts')

    def get_relations(self):
        return self.data['openlabel'].get('relations')

    def get_object(self, uid):
        return self.get_element(ElementType.object, uid)

    def get_action(self, uid):
        return self.get_element(ElementType.action, uid)

    def get_event(self, uid):
        return self.get_element(ElementType.event, uid)

    def get_context(self, uid):
        return self.get_element(ElementType.context, uid)

    def get_relation(self, uid):
        return self.get_element(ElementType.relation, uid)

    def get_element_uid_by_name(self, element_type, name):
        if not self.has_elements(element_type):
            return None
        element_type_name = element_type.name
        elements = self.data['openlabel'][element_type_name + 's']
        for uid, element in elements.items():
            name_element = element['name']
            if name_element == name:
                return uid
        return None

    def get_object_uid_by_name(self, name):
        return self.get_element_uid_by_name(ElementType.object, name)

    def get_action_uid_by_name(self, name):
        return self.get_element_uid_by_name(ElementType.action, name)

    def get_context_uid_by_name(self, name):
        return self.get_element_uid_by_name(ElementType.context, name)

    def get_event_uid_by_name(self, name):
        return self.get_element_uid_by_name(ElementType.event, name)

    def get_relation_uid_by_name(self, name):
        return self.get_element_uid_by_name(ElementType.relation, name)

    def get_frame(self, frame_num):       
        return self.data['openlabel']['frames'].get(frame_num)            

    def get_elements_of_type(self, element_type, semantic_type):
        uids_str = []
        if not element_type.name + 's' in self.data['openlabel']:
            return uids_str
        for uid_str, element in self.data['openlabel'][element_type.name + 's'].items():
            if element['type'] == semantic_type:
                uids_str.append(uid_str)
        return uids_str

    def get_elements_with_element_data_name(self, element_type, data_name):
        uids_str = []
        for uid_str in self.data['openlabel'][element_type.name + 's']:
            element = self.data['openlabel'][element_type.name + 's'][uid_str]
            if element_type.name + '_data_pointers' in element:
                for name in element[element_type.name + '_data_pointers']:
                    if name == data_name:
                        uids_str.append(uid_str)
                        break
        return uids_str

    def get_objects_with_object_data_name(self, data_name):
        return self.get_elements_with_element_data_name(ElementType.object, data_name)

    def get_actions_with_action_data_name(self, data_name):
        return self.get_elements_with_element_data_name(ElementType.action, data_name)

    def get_events_with_event_data_name(self, data_name):
        return self.get_elements_with_element_data_name(ElementType.event, data_name)

    def get_contexts_with_context_data_name(self, data_name):
        return self.get_elements_with_element_data_name(ElementType.context, data_name)

    def get_frames_with_element_data_name(self, element_type, uid, data_name):
        uid_str = UID(uid).as_str()
        if uid_str in self.data['openlabel'][element_type.name + 's']:
            element = self.data['openlabel'][element_type.name + 's'][uid_str]
            if element_type.name + '_data_pointers' in element:
                for name in element[element_type.name + '_data_pointers']:
                    if name == data_name:
                        return FrameIntervals(element[element_type.name + '_data_pointers'][name]['frame_intervals'])
        return None

    def get_frames_with_object_data_name(self, uid, data_name):
        return self.get_frames_with_element_data_name(ElementType.object, uid, data_name)

    def get_frames_with_action_data_name(self, uid, data_name):
        return self.get_frames_with_element_data_name(ElementType.action, uid, data_name)

    def get_frames_with_event_data_name(self, uid, data_name):
        return self.get_frames_with_element_data_name(ElementType.event, uid, data_name)

    def get_frames_with_context_data_name(self, uid, data_name):
        return self.get_frames_with_element_data_name(ElementType.context, uid, data_name)

    def get_element_data_count_per_type(self, element_type, uid, data_type, frame_num=None):
        # Returns 0 if no such element exist or if the element does not have the data_type
        # Returns the count otherwise (e.g. how many "bbox" does this object have)
        assert(isinstance(data_type, types.ObjectDataType))
        uid_str = UID(uid).as_str()
        if self.has(element_type, uid):
            if frame_num is not None:
                # Dynamic info
                if not isinstance(frame_num, int):
                    warnings.warn("WARNING: Calling get_element_data with a non-integer frame_num.")
                frame = self.get_frame(frame_num)
                if frame is not None:
                    if element_type.name + 's' in frame:
                        if uid_str in frame[element_type.name + 's']:
                            element = frame[element_type.name + 's'][uid_str]
                            for prop in element[element_type.name + '_data']:
                                if prop == data_type.name:
                                    return len(element[element_type.name + '_data'][prop])
                        else:
                            return 0
                    else:
                        return 0
            else:
                # Static info
                element = self.data['openlabel'][element_type.name + 's'][uid_str]
                for prop in element[element_type.name + '_data']:
                    if prop == data_type.name:
                        return len(element[element_type.name + '_data'][prop])
        else:
            return 0
        return 0

    def get_element_data(self, element_type, uid, data_name, frame_num=None):
        element_exists = self.has(element_type, uid)
        vcd_has_frames = not self.get_frame_intervals().empty()

        if not element_exists:  # the element does not exist
            return None

        if not vcd_has_frames and frame_num is not None:  # don't ask for frame-specific info in a VCD without frames
            return None

        frame_num_is_number = isinstance(frame_num, int)
        uid_str = UID(uid).as_str()

        element_exists_in_this_frame = False
        if frame_num is not None and frame_num_is_number:
            # The user is asking for frame-specific attributes

            found_in_frame = False
            frame = self.get_frame(frame_num)
            if frame is not None:
                if element_type.name + 's' in frame:
                    if uid_str in frame[element_type.name + 's']:
                        element_exists_in_this_frame = True
                        element = frame[element_type.name + 's'][uid_str]
                        if element_type.name + '_data' in element:
                            for prop in element[element_type.name + '_data']:
                                val_array = element[element_type.name + '_data'][prop]
                                for val in val_array:
                                    if val['name'] == data_name:
                                        return val
            if not found_in_frame:
                # The user has asked to get an element_data for a certain frame, but there is no info about this
                # element or element_data at this frame
                if not element_exists_in_this_frame:
                    return None
                element = self.data['openlabel'][element_type.name + 's'][uid_str]  # the element exists because of prev. ctrl
                for prop in element[element_type.name + '_data']:
                    val_array = element[element_type.name + '_data'][prop]
                    for val in val_array:
                        if val['name'] == data_name:
                            return val
        else:
            # The user is asking for static attributes at the root of the element
            element = self.data['openlabel'][element_type.name + 's'][uid_str]  # the element exists because of prev. ctrl
            for prop in element[element_type.name + '_data']:
                val_array = element[element_type.name + '_data'][prop]
                for val in val_array:
                    if val['name'] == data_name:
                        return val
        return None

    def get_object_data(self, uid, data_name, frame_num=None):
        return self.get_element_data(ElementType.object, uid, data_name, frame_num)

    def get_action_data(self, uid, data_name, frame_num=None):
        return self.get_element_data(ElementType.action, uid, data_name, frame_num)

    def get_event_data(self, uid, data_name, frame_num=None):
        return self.get_element_data(ElementType.event, uid, data_name, frame_num)

    def get_context_data(self, uid, data_name, frame_num=None):
        return self.get_element_data(ElementType.context, uid, data_name, frame_num)

    def get_element_data_pointer(self, element_type, uid, data_name):
        uid_str = UID(uid).as_str()
        if self.has(element_type, uid):
            if element_type.name + 's' in self.data['openlabel']:
                if uid_str in self.data['openlabel'][element_type.name + 's']:
                    element = self.data['openlabel'][element_type.name + 's'][uid_str]
                    if element_type.name + '_data_pointers' in element:
                        if data_name in element[element_type.name + '_data_pointers']:
                            return element[element_type.name + '_data_pointers'][data_name]
        else:
            warnings.warn("WARNING: Asking element data from a non-existing Element.")
        return None

    def get_element_data_frame_intervals(self, element_type, uid, data_name):
        return FrameIntervals(self.get_element_data_pointer(element_type, uid, data_name)['frame_intervals'])

    def get_object_data_frame_intervals(self, uid, data_name):
        return self.get_element_data_frame_intervals(ElementType.object, uid, data_name)

    def get_action_data_frame_intervals(self, uid, data_name):
        return self.get_element_data_frame_intervals(ElementType.action, uid, data_name)

    def get_event_data_frame_intervals(self, uid, data_name):
        return self.get_element_data_frame_intervals(ElementType.event, uid, data_name)

    def get_context_data_frame_intervals(self, uid, data_name):
        return self.get_element_data_frame_intervals(ElementType.context, uid, data_name)

    def get_num_elements(self, element_type):
        if self.has_elements(element_type):
            return len(self.data['openlabel'][element_type.name + 's'])
        else:
            return 0

    def get_num_objects(self):
        return self.get_num_elements(ElementType.object)

    def get_num_actions(self):
        return self.get_num_elements(ElementType.action)

    def get_num_events(self):
        return self.get_num_elements(ElementType.event)

    def get_num_contexts(self):
        return self.get_num_elements(ElementType.context)

    def get_num_relations(self):
        return self.get_num_elements(ElementType.relation)

    def get_elements_uids(self, element_type: ElementType):
        if self.has_elements(element_type):
            list_of_uids = list(self.data['openlabel'][element_type.name + 's'].keys())
            return list_of_uids
        else:
            return []

    def get_ontology(self, ont_uid):
        ont_uid_str = UID(ont_uid).as_str()
        if 'ontologies' in self.data['openlabel']:
            if ont_uid_str in self.data['openlabel']['ontologies']:
                return copy.deepcopy(self.data['openlabel']['ontologies'][ont_uid_str])
        return None

    def get_resource(self, res_uid):
        res_uid_str = UID(res_uid).as_str()
        if 'resources' in self.data['openlabel']:
            if res_uid_str in self.data['openlabel']['resources']:
                return copy.deepcopy(self.data['openlabel']['resources'][res_uid_str])
        return None

    def get_metadata(self):
        if 'metadata' in self.data['openlabel']:
            return self.data['openlabel']['metadata']
        else:
            return dict()

    def has_coordinate_system(self, cs):
        if 'coordinate_systems' in self.data['openlabel']:
            if cs in self.data['openlabel']['coordinate_systems']:
                return True
        return False

    def get_coordinate_systems(self):
        if 'coordinate_systems' in self.data['openlabel']:
            return copy.deepcopy(self.data['openlabel']['coordinate_systems'])
        else:
            return []

    def get_coordinate_system(self, coordinate_system):
        if self.has_coordinate_system(coordinate_system):
            return copy.deepcopy(self.data['openlabel']['coordinate_systems'][coordinate_system])
        else:
            return None

    def has_stream(self, stream_name):
        if 'streams' in self.data['openlabel']:
            if stream_name in self.data['openlabel']['streams']:
                return True
            else:
                return False

    def get_streams(self):
        if 'streams' in self.data['openlabel']:
            return copy.deepcopy(self.data['openlabel']['streams'])
        else:
            return {}

    def get_stream(self, stream_name):
        if self.has_stream(stream_name):
            return copy.deepcopy(self.data['openlabel']['streams'][stream_name])
        else:
            return None

    def get_frame_intervals(self):
        if 'frame_intervals' in self.data['openlabel']:
            return FrameIntervals(self.data['openlabel']['frame_intervals'])
        else:
            return FrameIntervals()

    def get_element_frame_intervals(self, element_type, uid):
        uid_str = UID(uid).as_str()
        if not element_type.name + 's' in self.data['openlabel']:
            return FrameIntervals()
        else:
            if not uid_str in self.data['openlabel'][element_type.name + 's']:
                return FrameIntervals()
            return FrameIntervals(self.data['openlabel'][element_type.name + 's'][uid_str].get('frame_intervals'))

    def relation_has_frame_intervals(self, relation_uid):
        rel_uid = UID(relation_uid)
        relation = self.get_relation(relation_uid)
        if relation is None:
            warnings.warn("WARNING: Non-existing relation " + rel_uid.as_str())
        else:
            if 'frame_intervals' not in relation:
                return False
            else:
                if len(relation['frame_intervals']) == 0:
                    return False
                else:
                    return True

    ##################################################
    # Remove
    ##################################################
    def rm_element_by_type(self, element_type, semantic_type):
        elements = self.data['openlabel'][element_type.name + 's']

        # Get Element from summary
        uids_to_remove_str = []
        for uid_str, element in elements.items():
            if element['type'] == semantic_type:
                uids_to_remove_str.append(uid_str)
        for uid_str in uids_to_remove_str:
            self.rm_element(element_type, uid_str)

    def rm_object_by_type(self, semantic_type):
        self.rm_element_by_type(ElementType.object, semantic_type)

    def rm_action_by_type(self, semantic_type):
        self.rm_element_by_type(ElementType.action, semantic_type)

    def rm_event_by_type(self, semantic_type):
        self.rm_element_by_type(ElementType.event, semantic_type)

    def rm_context_by_type(self, semantic_type):
        self.rm_element_by_type(ElementType.context, semantic_type)

    def rm_relation_by_type(self, semantic_type):
        self.rm_element_by_type(ElementType.relation, semantic_type)

    def rm_element(self, element_type, uid):
        uid_str = UID(uid).as_str()
        if not self.has_elements(element_type):
            return

        # Get element from summary
        if not self.has(element_type, uid):
            return

        # Remove from frames: let's read frame_intervals from summary
        elements = self.data['openlabel'][element_type.name + 's']
        element = elements[uid_str]
        if 'frame_intervals' in element:
            for i in range(0, len(element['frame_intervals'])):
                fi = element['frame_intervals'][i]
                for frame_num in range(fi['frame_start'], fi['frame_end']+1):
                    elements_in_frame = self.data['openlabel']['frames'][frame_num][element_type.name + 's']
                    if uid in elements_in_frame:
                        del elements_in_frame[uid_str]
                    if len(elements_in_frame) == 0:  # objects might have end up empty TODO: test this
                        del self.data['openlabel']['frames'][frame_num][element_type.name + 's']
                        if len(self.data['openlabel']['frames'][frame_num]) == 0:  # this frame may have ended up being empty
                            del self.data['openlabel']['frames'][frame_num]
                            self.__rm_frame(frame_num)

        # Delete this element from summary
        del elements[uid_str]
        if len(elements) == 0:
            del self.data['openlabel'][element_type.name + 's']

    def rm_object(self, uid):
        self.rm_element(ElementType.object, uid)

    def rm_action(self, uid):
        self.rm_element(ElementType.action, uid)

    def rm_event(self, uid):
        self.rm_element(ElementType.event, uid)

    def rm_context(self, uid):
        self.rm_element(ElementType.context, uid)

    def rm_relation(self, uid):
        self.rm_element(ElementType.relation, uid)


class OpenLABEL(VCD):
    """
    This is the OpenLABEL class, which inherites from VCD class.
    """
    def __init__(self, file_name=None, validation=False):
        VCD.__init__(self, file_name, validation)
