"""
VCD (Video Content Description) library v4.3.0

Project website: http://vcd.vicomtech.org

Copyright (C) 2020, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.3.0.
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


class ElementType(Enum):
    """
    Elements of VCD (Object, Action, Event, Context, Relation)
    """
    object = 1
    action = 2
    event = 3
    context = 4
    relation = 5


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
    def __init__(self, frame_value=None):
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
                    self.fis_dict = utils.fuse_frame_intervals(self.fis_dict)
                    self.fis_num = utils.as_frame_intervals_array_tuples(self.fis_dict)
                elif all(isinstance(x, dict) for x in frame_value):
                    # User provided a list of dict
                    self.fis_dict = frame_value
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
        if len(self.fis_dict) == 0 or len(self.fis_num) == 0:
            return True
        else:
            return False

    def get_dict(self):
        return self.fis_dict

    def get(self):
        return self.fis_num

    def rm_frame(self, frame_num):
        self.fis_dict = utils.rm_frame_from_frame_intervals(self.fis_dict, frame_num)
        self.fis_num = utils.as_frame_intervals_array_tuples(self.fis_dict)

    def union(self, frame_intervals):
        fis_union = utils.fuse_frame_intervals(frame_intervals.get_dict() + self.fis_dict)
        return FrameIntervals(fis_union)

    def intersection(self, frame_intervals):
        fis_int = utils.intersection_between_frame_interval_arrays(self.fis_num, frame_intervals.get())
        return FrameIntervals(fis_int)

    def get_outer(self):
        return utils.get_outer_frame_interval(self.fis_dict)

    def has_frame(self, frame_num):
        return utils.is_inside_frame_intervals(frame_num, self.fis_num)


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
                    if val.isnumeric():
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
            json_file = open(file_name)
            # In VCD 4.2.0, uids and frames were ints, so, parsing needed a lambda function to do the job
            # self.data = json.load(
            #    json_file,
            #    object_hook=lambda d: {int(k) if k.lstrip('-').isdigit() else k: v for k, v in d.items()}
            # )
            read_data = json.load(json_file)  # Open without converting strings to integers

            # Check VERSION
            if 'vcd' in read_data:
                # This is 4.x
                if 'version' in read_data['vcd']:
                    # This is 4.1-2
                    if read_data['vcd']['version'] == "4.2.0":
                        # This is VCD 4.2.0
                        self.reset()  # to init object
                        converter.ConverterVCD420toVCD430(read_data, self)  # self is modified internally

                    elif read_data['vcd']['version'] == "4.1.0":
                        # This is VCD 4.1.0
                        # TODO
                        pass
                elif 'metadata' in read_data['vcd']:
                    if 'schema_version' in read_data['vcd']['metadata']:
                        if read_data['vcd']['metadata']['schema_version'] == "4.3.0":
                            # This is VCD 4.3.0
                            self.data = read_data
                            if validation:
                                if not hasattr(self, 'schema'):
                                    self.schema = schema.vcd_schema
                                validate(instance=self.data, schema=self.schema)  # Raises errors if not validated
                                json_file.close()

                            # In VCD 4.3.0 uids are strings, because they can be numeric strings, or UUIDs
                            # but frames are still ints, so let's parse like that
                            if 'frames' in self.data['vcd']:
                                frames = self.data['vcd']['frames']
                                if frames:  # So frames is not empty
                                    self.data['vcd']['frames'] = {int(key): value for key, value in frames.items()}
                        else:
                            raise Exception("ERROR: This vcd file does not seem to be 4.3.0 nor 4.2.0")
                    else:
                        raise Exception("ERROR: This vcd file does not seem to be 4.3.0 nor 4.2.0")
            elif 'VCD' in read_data:
                # This is 3.x
                #if read_data['VCD']['version'] == "3.3.0":
                # Assuming this is VCD 3.3.0, let's load into VCD 4.3.0
                self.reset()  # to init object
                converter.ConverterVCD330toVCD430(read_data, self)  # self is modified internally

            # Close file
            json_file.close()

            # Final set-up
            self.__compute_last_uid()
        else:
            self.reset()

    def set_use_uuid(self, val):
        assert(isinstance(val, bool))
        self.use_uuid = val

    def reset(self):
        # Main VCD data
        self.data = {'vcd': {}}
        self.data['vcd']['metadata'] = {}
        self.data['vcd']['metadata']['schema_version'] = schema.vcd_schema_version

        # Schema information
        self.schema = schema.vcd_schema

        # Additional auxiliary structures
        self.__lastUID = dict()
        self.__lastUID[ElementType.object] = -1
        self.__lastUID[ElementType.action] = -1
        self.__lastUID[ElementType.event] = -1
        self.__lastUID[ElementType.context] = -1
        self.__lastUID[ElementType.relation] = -1

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
                # Let's use integers, and return a string
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
            self.data['vcd']['frame_intervals'] = frame_intervals.get_dict()

    def __update_vcd_frame_intervals(self, frame_intervals):
        # This function creates the union of existing VCD with the input frameIntervals
        assert (isinstance(frame_intervals, FrameIntervals))
        if not frame_intervals.empty():
            if 'frame_intervals' not in self.data['vcd']:
                self.data['vcd']['frame_intervals'] = []
            fis_current = FrameIntervals(self.data['vcd']['frame_intervals'])
            fis_union = fis_current.union(frame_intervals)
            self.__set_vcd_frame_intervals(fis_union)

    def __add_frame(self, frame_num):
        # self.data['vcd']['frames'].setdefault(frame_num, {}) # 3.8 secs - 10.000 times
        if 'frames' not in self.data['vcd']:
            self.data['vcd']['frames'] = {}
        if frame_num not in self.data['vcd']['frames']:
            self.data['vcd']['frames'][frame_num] = {}

    def __compute_last_uid(self):
        self.__lastUID = dict()
        # Read all objects and fill lastUID
        self.__lastUID[ElementType.object] = -1
        if 'objects' in self.data['vcd']:
            for uid in self.data['vcd']['objects']:
                if int(uid) > self.__lastUID[ElementType.object]:
                    self.__lastUID[ElementType.object] = int(uid)

        self.__lastUID[ElementType.action] = -1
        if 'actions' in self.data['vcd']:
            for uid in self.data['vcd']['actions']:
                if int(uid) > self.__lastUID[ElementType.action]:
                    self.__lastUID[ElementType.action] = int(uid)

        self.__lastUID[ElementType.event] = -1
        if 'events' in self.data['vcd']:
            for uid in self.data['vcd']['events']:
                if int(uid) > self.__lastUID[ElementType.event]:
                    self.__lastUID[ElementType.event] = int(uid)

        self.__lastUID[ElementType.context] = -1
        if 'contexts' in self.data['vcd']:
            for uid in self.data['vcd']['contexts']:
                if int(uid) > self.__lastUID[ElementType.context]:
                    self.__lastUID[ElementType.context] = int(uid)

        self.__lastUID[ElementType.relation] = -1
        if 'relations' in self.data['vcd']:
            for uid in self.data['vcd']['relations']:
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

    def __add_element(
            self, element_type, name, semantic_type, frame_intervals=None, uid=None, ont_uid=None,
            stream=None
    ):
        if uid is not None:
            assert(isinstance(uid, UID))
        else:
            uid = UID()  # so we don't have more None types
        if ont_uid is not None:
            assert(isinstance(ont_uid, UID))
        else:
            ont_uid = UID()  # so we don't have more None types

        # 0.- Check if element already exists
        element_exists = self.has(element_type, uid.as_str())  # note: public functions use int or str for uids

        # 1.- Get uid to assign
        uid_to_assign = self.__get_uid_to_assign(element_type, uid)  # note: private functions use UID type for uids

        # 2.- Update Root element (['vcd']['element']), overwrites content
        fis_old = self.get_element_frame_intervals(element_type, uid.as_str())
        self.__create_update_element(element_type, name, semantic_type, frame_intervals, uid_to_assign, ont_uid, stream)

        # 3.- Update frames entries and VCD frame intervals
        if not frame_intervals.empty():
            # 3.1.- Element with explicit frame interval argument, let's study if we need to remove or add
            if element_exists:
                # 3.1.1.- Loop over new to add it not inside old
                fis_new = frame_intervals
                for fi in fis_new.get():
                    for f in range(fi[0], fi[1]+1):
                        is_inside = fis_old.has_frame(f)
                        if not is_inside:
                            # New frame is not inside -> let's add this frame
                            fi_ = FrameIntervals(f)
                            self.__add_frames(fi_, element_type, uid)
                            self.__update_vcd_frame_intervals(fi_)
                # 3.1.2.- Remove frames: loop over old to delete old if not inside new
                for fi in fis_old.get():
                    for f in range(fi[0], fi[1]+1):
                        is_inside = fis_new.has_frame(f)
                        if not is_inside:
                            # Old frame not inside new ones -> let's remove this frame
                            elements_in_frame = self.data['vcd']['frames'][f][element_type.name +'s']
                            del elements_in_frame[uid.as_str()]
                            if len(elements_in_frame) == 0:
                                del self.data['vcd']['frames'][f][element_type.name +'s']
                                if len(self.data['vcd']['frames'][f]) == 0:
                                    self.__rm_frame(f)
            else:
                # As the element didnt exist before this call, we just need to addframes
                self.__add_frames(frame_intervals, element_type, uid_to_assign)
                self.__update_vcd_frame_intervals(frame_intervals)
        else:
            # 3.2.- This element does not have a specific frame_interval...
            vcd_frame_intervals = self.get_frame_intervals()
            if vcd_frame_intervals.empty():
                # ... but VCD has already other elements or info that have established some frame intervals
                # The element is then assumed to exist in all frames: let's add a pointer into all frames (also
                # for Relations!)
                self.__add_frames(vcd_frame_intervals, element_type, uid_to_assign)
        return uid_to_assign

    def __update_element(self, element_type, uid, frame_intervals):
        assert(isinstance(element_type, ElementType))
        assert(isinstance(uid, UID))
        assert(isinstance(frame_intervals, FrameIntervals))

        # Check if this uid exists
        if uid.as_str() not in self.data['vcd'][element_type.name + 's']:
            warnings.warn("WARNING: trying to update a non-existing Element.")
            return False

        # Read existing data about this element, so we can call __add_element
        name = self.data['vcd'][element_type.name + 's'][uid.as_str()]['name']
        semantic_type = self.data['vcd'][element_type.name + 's'][uid.as_str()]['type']
        ont_uid = None
        stream = None
        if 'ontology_uid' in self.data['vcd'][element_type.name + 's'][uid.as_str()]:
            ont_uid = UID(self.data['vcd'][element_type.name + 's'][uid.as_str()]['ontology_uid'])
        if 'stream' in self.data['vcd'][element_type.name + 's'][uid.as_str()]:
            stream = self.data['vcd'][element_type.name + 's'][uid.as_str()]['stream']

        # Call __add_element (which internally creates OR updates)
        fis_existing = self.get_element_frame_intervals(element_type, uid.as_str())
        fis_union = fis_existing.union(frame_intervals)
        self.__add_element(element_type, name, semantic_type, fis_union, uid, ont_uid, stream)

    def __modify_element(self, element_type, uid, name=None, semantic_type=None, frame_intervals=None,
                         ont_uid=None, stream=None):
        self.__add_element(element_type, name, semantic_type, frame_intervals, uid, ont_uid, stream)

    def __create_update_element(
            self, element_type, name, semantic_type, frame_intervals, uid, ont_uid, stream
    ):
        # 1.- Copy from existing or create new entry (this copies everything, including element_data)
        # element_data_pointers and frame intervals
        self.data['vcd'].setdefault(element_type.name + 's', {})
        self.data['vcd'][element_type.name + 's'].setdefault(uid.as_str(), {})
        element = self.data['vcd'][element_type.name + 's'][uid.as_str()]

        # 2.- Copy from arguments
        if name is not None:
            element['name'] = name
        if semantic_type is not None:
            element['type'] = semantic_type
        if not frame_intervals.empty():
            element['frame_intervals'] = frame_intervals.get_dict()
        if not ont_uid.is_none() and self.get_ontology(ont_uid.as_str()):
            element['ontology_uid'] = ont_uid.as_str()
        if stream is not None and self.has_stream(stream):
            element['stream'] = stream

        # 3.- Reshape element_data_poitners according to this new frame intervals
        if not frame_intervals.empty():
            if element_type.name + '_data_pointers' in element:
                edps = element[element_type.name + '_data_pointers']
                for edp_name in edps:
                    # NOW, we have to UPDATE frame intervals of pointers: NOT ADDING
                    # (to add use MODIFY_ELEMENT_DATA) BUT REMOVING
                    # If we compute the intersection frame_intervals, we can copy that into
                    # element_data_pointers frame intervals
                    fis_int = frame_intervals.intersection(FrameIntervals(edps[edp_name]['frame_intervals']))
                    if not fis_int.empty():
                        element.setdefault(element_type.name + '_data_pointers', {})
                        element[element_type.name + '_data_pointers'][edp_name] = edps[edp_name]
                        element[element_type.name + '_data_pointers'][edp_name]['frame_intervals'] = fis_int.get_dict()

    def __add_element_data(self, element_type, uid, element_data, frame_intervals):
        assert(isinstance(uid, UID))
        # 0.- Check if element
        if not self.has(element_type, uid.as_str()):
            return

        # 1.- If new frameinterval, update root element, frames and vcd
        # as this frame interval refers to an element_data, we need to NOT delete frames from element
        if frame_intervals is not None and not frame_intervals.empty():
            element = self.get_element(element_type, uid.as_str())
            ont_uid = None
            stream = None
            if 'ontology_uid' in element:
                ont_uid = UID(element['ontology_uid'])
            if 'stream' in element:
                stream = element['stream']

            # Prepare union of frame intervals to update element
            fis_element = self.get_element_frame_intervals(element_type, uid.as_str())
            fis_union = fis_element.union(frame_intervals)
            self.__add_element(element_type, element['name'], element['type'], fis_union, uid, ont_uid, stream)

        # 2.- Inject/substitute Element_data
        self.__create_update_element_data(element_type, uid, element_data, frame_intervals)

        # 3.- Update element_data_pointers
        # IMPORTANT: here we use frame_intervals, and NOT the fusion, because "add" concept is to create or modify,
        # but not to update (fuse)
        self.__create_update_element_data_pointers(element_type, uid, element_data, frame_intervals)

    def __create_update_element_data_pointers(self, element_type, uid, element_data, frame_intervals):
        assert(isinstance(uid, UID))
        self.data['vcd'][element_type.name + 's'][uid.as_str()].setdefault(element_type.name + '_data_pointers', {})
        edp = self.data['vcd'][element_type.name + 's'][uid.as_str()][element_type.name + '_data_pointers']
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

    def __create_update_element_data(self, element_type, uid, element_data, frame_intervals):
        assert(isinstance(uid, UID))
        # 0.- Check if element_data
        if 'in_stream' in element_data.data:
            if not self.has_stream(element_data.data['in_stream']):
                return

        # 1.- At root XOR frames, copy from existing or create new entry
        if frame_intervals.empty():
            # 1.1.- Static
            element = self.get_element(element_type, uid.as_str())
            if element is not None:
                element.setdefault(element_type.name + '_data', {})
                element[element_type.name + '_data'].setdefault(element_data.type.name, []) # e.g. bbox

                # Find if element_data already there, if so, replace, otherwise, append
                list_aux = element[element_type.name + '_data'][element_data.type.name]
                pos_list = [idx for idx, val in enumerate(list_aux) if val['name'] == element_data.data['name']]
                if len(pos_list) == 0:
                    # No: then, just push this new element data
                    element[element_type.name + '_data'][element_data.type.name].append(element_data.data)
                else:
                    # Yes, let's substitute
                    pos = pos_list[0]
                    element[element_type.name + '_data'][element_data.type.name][pos] = element_data.data  # TODO: Deep copy?
            else:
                warnings.warn("WARNING: trying to add objectdata to non-existing object, uid" + uid)
        else:
            # 1.2.- Dynamic (create at frames, which already exist because this function is called after add_element)
            fis = frame_intervals.get()
            for fi in fis:
                for f in range(fi[0], fi[1]+1):
                    # Add element_data entry
                    frame = self.get_frame(f)  # TODO: check deep copy
                    if frame is None:
                        #warnings.warn("WARNING: create_update_element_data reaches a frame that does not exist."
                        #              "Inner data flow may be broken!")
                        self.__add_frame(f)
                        frame = self.get_frame(f)
                    frame.setdefault(element_type.name + 's', {})
                    frame[element_type.name + 's'].setdefault(uid.as_str(), {})
                    element = frame[element_type.name + 's'][uid.as_str()]
                    element.setdefault(element_type.name + '_data', {})
                    element[element_type.name + '_data'].setdefault(element_data.type.name, [])

                    # Find if element_data already there
                    list_aux = element[element_type.name + '_data'][element_data.type.name]
                    pos_list = [idx for idx, val in enumerate(list_aux) if val['name'] == element_data.data['name']]

                    if len(pos_list) == 0:
                        # No, then just push this new element data
                        element[element_type.name + '_data'][element_data.type.name].append(element_data.data)
                    else:
                        # Ok, this is either an error, or a call from modify, let's substitute
                        pos = pos_list[0]
                        element[element_type.name + '_data'][element_data.type.name][pos] = element_data.data
        # Note: don't update here element_data_pointers, they are updated in create_update_element_data_pointers

    def __rm_frame(self, frame_num):
        # This function deletes a frame entry from frames, and updates VCD accordingly
        # NOTE: This function does not update corresponding element or element data entries for this frame
        # (use modifyElement or modifyElementData for such functionality)
        # this function is left private so users can't use it directly: they have to use modifyElement or
        # modifyElementData or other of the removal functions
        if 'frames' in self.data['vcd']:
            if frame_num in self.data['vcd']['frames']:
                del self.data['vcd']['frames'][frame_num]

                # Remove from VCD frame intervals
                if 'frame_intervals' in self.data['vcd']:
                    fis_dict = self.data['vcd']['frame_intervals']
                else:
                    fis_dict = []
                fis_dict_new = utils.rm_frame_from_frame_intervals(fis_dict, frame_num)

                # Now substitute
                self.data['vcd']['frame_intervals'] = fis_dict_new  # TODO: deep copy?

    def __compute_data_pointers(self):
        # WARNING! This function might be extremely slow
        # It does loop over all frames, and updates data pointers at objects, actions, etc
        # It is useful to convert from VCD 4.2.0 into VCD 4.3.0 (use converter.ConverterVCD420toVCD430)

        # Looping over frames and creating the necessary data_pointers
        if 'frame_intervals' in self.data['vcd']:
            fis = self.data['vcd']['frame_intervals']
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
                                    self.data['vcd'][element_type.name + 's'][uid].\
                                        setdefault(element_type.name + '_data_pointers', {})
                                    edp = self.data['vcd'][element_type.name + 's'][uid][element_type.name + '_data_pointers']

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

    ##################################################
    # Public API: add, update
    ##################################################
    def add_file_version(self, version):
        assert (type(version) is str)
        if 'metadata' not in self.data['vcd']:
            self.data['vcd']['metadata'] = {}
        self.data['vcd']['metadata']['file_version'] = version

    def add_metadata_properties(self, properties):
        assert(isinstance(properties, dict))
        prop = self.data['vcd']['metadata']
        prop.update(properties)

    def add_name(self, name):
        assert(type(name) is str)
        if 'metadata' not in self.data['vcd']:
            self.data['vcd']['metadata'] = {}
        self.data['vcd']['metadata']['name'] = name

    def add_annotator(self, annotator):
        assert(type(annotator) is str)
        if 'metadata' not in self.data['vcd']:
            self.data['vcd']['metadata'] = {}
        self.data['vcd']['metadata']['annotator'] = annotator

    def add_comment(self, comment):
        assert(type(comment) is str)
        if 'metadata' not in self.data['vcd']:
            self.data['vcd']['metadata'] = {}
        self.data['vcd']['metadata']['comment'] = comment

    def add_ontology(self, ontology_name):
        self.data['vcd'].setdefault('ontologies', dict())
        for ont_uid in self.data['vcd']['ontologies']:
            if self.data['vcd']['ontologies'][ont_uid] == ontology_name:
                warnings.warn('WARNING: adding an already existing ontology')
                return None
        length = len(self.data['vcd']['ontologies'])
        self.data['vcd']['ontologies'][str(length)] = ontology_name
        return str(length)

    def add_coordinate_system(self, name, cs_type, parent_name="", pose_wrt_parent=[], uid=None):
        assert(isinstance(cs_type, types.CoordinateSystemType))
        # Create entry
        self.data['vcd'].setdefault('coordinate_systems', {})
        self.data['vcd']['coordinate_systems'][name] = {'type': cs_type.name,
                                                        'parent': parent_name,
                                                        'pose_wrt_parent': pose_wrt_parent,
                                                        'children': []}
        if uid is not None:
            assert(isinstance(uid, str))
            self.data['vcd']['coordinate_systems'][name].update({"uid": uid})

        # Update parents
        if parent_name != "":
            found = False
            for n, cs in self.data['vcd']['coordinate_systems'].items():
                if n == parent_name:
                    found = True
                    cs['children'].append(name)
            if not found:
                warnings.warn("WARNING: Creating a coordinate system with a non-defined parent coordinate system."
                              "Coordinate systems must be introduced in order")

    def add_transform(self, frame_num, transform):
        assert (isinstance(frame_num, int))
        assert(isinstance(transform, types.Transform))

        self.__add_frame(frame_num)  # this function internally checks if the frame already exists
        self.data['vcd']['frames'][frame_num].setdefault('frame_properties', dict())
        self.data['vcd']['frames'][frame_num]['frame_properties'].setdefault('transforms', dict())
        self.data['vcd']['frames'][frame_num]['frame_properties']['transforms'].update(transform.data)

    def add_stream(self, stream_name, uri, description, stream_type):
        assert(isinstance(stream_name, str))
        assert(isinstance(uri, str))
        assert(isinstance(description, str))

        self.data['vcd'].setdefault('streams', dict())
        self.data['vcd']['streams'].setdefault(stream_name, dict())
        if isinstance(stream_type, StreamType):
            self.data['vcd']['streams'][stream_name] = {
                'description': description, 'uri': uri, 'type': stream_type.name
            }
        elif isinstance(stream_type, str):
            self.data['vcd']['streams'][stream_name] = {
                'description': description, 'uri': uri, 'type': stream_type
            }

    def add_frame_properties(self, frame_num, timestamp=None, properties=None):
        self.__add_frame(frame_num)  # this function internally checks if the frame already exists
        self.data['vcd']['frames'][frame_num].setdefault('frame_properties', dict())
        if timestamp is not None:
            assert (isinstance(timestamp, str))
            self.data['vcd']['frames'][frame_num]['frame_properties']['timestamp'] = timestamp

        if properties is not None:
            assert (isinstance(properties, dict))
            self.data['vcd']['frames'][frame_num]['frame_properties'].update(properties)

    #def add_odometry(self, frame_num, odometry):
    #    assert(isinstance(frame_num, int))
    #    assert(isinstance(odometry, types.Odometry))

    #    self.__add_frame(frame_num)  # this function internally checks if the frame already exists
    #    self.data['vcd']['frames'][frame_num].setdefault('frame_properties', dict())
    #    self.data['vcd']['frames'][frame_num]['frame_properties'].update(odometry.data)

    #def add_stream_properties(self, stream_name, properties=None, intrinsics=None, extrinsics=None, stream_sync=None):
    def add_stream_properties(self, stream_name, properties=None, intrinsics=None, stream_sync=None):
        has_arguments = False
        if intrinsics is not None:
            assert(isinstance(intrinsics, types.Intrinsics))
            has_arguments = True
        #if extrinsics is not None:
        #    assert(isinstance(extrinsics, types.Extrinsics))
        #    has_arguments = True
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
        if 'metadata' in self.data['vcd']:
            if 'streams' in self.data['vcd']:
                if stream_name in self.data['vcd']['streams']:
                    if frame_num is None:
                        # This information is static
                        self.data['vcd']['streams'][stream_name].setdefault('stream_properties', dict())
                        if properties is not None:
                            self.data['vcd']['streams'][stream_name]['stream_properties'].\
                                update(properties)
                        if intrinsics is not None:
                            self.data['vcd']['streams'][stream_name]['stream_properties'].\
                                update(intrinsics.data)
                        #if extrinsics is not None:
                        #    self.data['vcd']['streams'][stream_name]['stream_properties'].\
                        #        update(extrinsics.data)
                        if stream_sync is not None:
                            if stream_sync.data:
                                self.data['vcd']['streams'][stream_name]['stream_properties'].\
                                    update(stream_sync.data)
                    else:
                        # This is information of the stream for a specific frame
                        self.__add_frame(frame_num)  # to add the frame in case it does not exist
                        frame = self.data['vcd']['frames'][frame_num]
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
                        #if extrinsics is not None:
                        #    frame['frame_properties']['streams'][stream_name]['stream_properties'].\
                        #        update(extrinsics.data)

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
        file = open(file_name, 'w')
        file.write(string)
        file.close()

    def validate(self, stringified_vcd):
        temp = json.loads(stringified_vcd)
        if not hasattr(self, 'schema'):
            self.schema = schema.vcd_schema
        validate(instance=temp, schema=self.schema)

    def stringify(self, pretty=True, validate=True):
        if pretty:
            stringified_vcd = json.dumps(self.data, indent=4, sort_keys=False)

        else:
            stringified_vcd = json.dumps(self.data, separators=(',', ':'), sort_keys=False)
        if validate:
            self.validate(stringified_vcd)
        return stringified_vcd

    def stringify_frame(self, frame_num, dynamic_only=True, pretty=False):
        if frame_num not in self.data['vcd']['frames']:
            warnings.warn("WARNING: Trying to stringify a non-existing frame.")
            return ''

        if dynamic_only:
            if pretty:
                return json.dumps(self.data['vcd']['frames'][frame_num], indent=4, sort_keys=True)
            else:
                return json.dumps(self.data['vcd']['frames'][frame_num])

        else:
            # Need to compose dynamic and static information into a new structure
            # Copy the dynamic info first
            frame_static_dynamic = copy.deepcopy(self.data['vcd']['frames'][frame_num])  # Needs to be a copy!

            # Now the static info for objects, actions, events, contexts and relations
            # Relations can be frame-less or frame-specific
            for element_type in ElementType:
                # First, elements explicitly defined for this frame
                if element_type.name + 's' in self.data['vcd']['frames'][frame_num]:
                    for uid, content in self.data['vcd']['frames'][frame_num][element_type.name + 's'].items():
                        frame_static_dynamic[element_type.name + 's'][uid].update(
                            self.data['vcd'][element_type.name + 's'][uid]
                        )
                        # Remove frameInterval entry
                        if 'frame_intervals' in frame_static_dynamic[element_type.name + 's'][uid]:
                            del frame_static_dynamic[element_type.name + 's'][uid]['frame_intervals']

                # But also other elements without frame intervals specified, which are assumed to exist during
                # the entire sequence, except frame-less Relations which are assumed to not be associated to any frame
                if element_type.name + 's' in self.data['vcd'] and element_type.name != 'relation':
                    for uid, element in self.data['vcd'][element_type.name + 's'].items():
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

    def update_object(self, uid, frame_value):
        # This function is only needed if no add_object_data calls are used, but the object needs to be kept alive
        return self.__update_element(ElementType.object, UID(uid), FrameIntervals(frame_value))

    def update_action(self, uid, frame_value):
        return self.__update_element(ElementType.action, UID(uid), FrameIntervals(frame_value))

    def update_context(self, uid, frame_value):
        return self.__update_element(ElementType.context, UID(uid), FrameIntervals(frame_value))

    def update_relation(self, uid, frame_value):
        if self.get_relation(uid) is not None:
            if not self.relation_has_frame_intervals(uid):
                warnings.warn("WARNING: Trying to update the frame information of a Relation defined as frame-less. "
                              "Ignoring command.")
            else:
                return self.__update_element(ElementType.relation, UID(uid), FrameIntervals(frame_value))

    def add_object(self, name, semantic_type='', frame_value=None, uid=None, ont_uid=None, stream=None):
        return self.__add_element(ElementType.object, name, semantic_type, FrameIntervals(frame_value),
                                  UID(uid), UID(ont_uid), stream).as_str()

    def add_action(self, name, semantic_type='', frame_value=None, uid=None, ont_uid=None, stream=None):
        return self.__add_element(ElementType.action, name, semantic_type, FrameIntervals(frame_value),
                                  UID(uid), UID(ont_uid), stream).as_str()

    def add_event(self, name, semantic_type='', frame_value=None, uid=None, ont_uid=None, stream=None):
        return self.__add_element(ElementType.event, name, semantic_type, FrameIntervals(frame_value),
                                  UID(uid), UID(ont_uid), stream).as_str()

    def add_context(self, name, semantic_type='', frame_value=None, uid=None, ont_uid=None, stream=None):
        return self.__add_element(ElementType.context, name, semantic_type, FrameIntervals(frame_value),
                                  UID(uid), UID(ont_uid), stream).as_str()

    def add_relation(self, name, semantic_type='', frame_value=None, uid=None, ont_uid=None):
        relation_uid = self.__add_element(
            ElementType.relation, name, semantic_type, frame_intervals=FrameIntervals(frame_value),
            uid=UID(uid), ont_uid=UID(ont_uid)
        )
        return relation_uid.as_str()

    def add_rdf(self, relation_uid, rdf_type, element_uid, element_type):
        assert(isinstance(element_type, ElementType))
        assert(isinstance(rdf_type, RDF))
        rel_uid = UID(relation_uid)
        el_uid = UID(element_uid)
        if rel_uid.as_str() not in self.data['vcd']['relations']:
            warnings.warn("WARNING: trying to add RDF to non-existing Relation.")
            return
        else:
            relation = self.data['vcd']['relations'][rel_uid.as_str()]
            if el_uid.as_str() not in self.data['vcd'][element_type.name + 's']:
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
                                   ont_uid=None, frame_value=None):
        # Note: no need to wrap uids as UID, since all calls are public functions, and no access to dict is done.
        relation_uid = self.add_relation(name, semantic_type, uid=relation_uid, ont_uid=ont_uid,
                                         frame_value=frame_value)
        self.add_rdf(relation_uid=relation_uid, rdf_type=RDF.subject,
                     element_uid=object_uid, element_type=ElementType.object)
        self.add_rdf(relation_uid=relation_uid, rdf_type=RDF.object,
                     element_uid=action_uid, element_type=ElementType.action)

        return relation_uid

    def add_relation_action_action(self, name, semantic_type, action_uid_1, action_uid_2, relation_uid=None,
                                   ont_uid=None, frame_value=None):
        # Note: no need to wrap uids as UID, since all calls are public functions, and no access to dict is done.
        relation_uid = self.add_relation(name, semantic_type, uid=relation_uid, ont_uid=ont_uid,
                                         frame_value=frame_value)
        self.add_rdf(relation_uid=relation_uid, rdf_type=RDF.subject,
                     element_uid=action_uid_1, element_type=ElementType.action)
        self.add_rdf(relation_uid=relation_uid, rdf_type=RDF.object,
                     element_uid=action_uid_2, element_type=ElementType.action)

        return relation_uid

    def add_relation_object_object(self, name, semantic_type, object_uid_1, object_uid_2, relation_uid=None,
                                   ont_uid=None, frame_value=None):
        # Note: no need to wrap uids as UID, since all calls are public functions, and no access to dict is done.
        relation_uid = self.add_relation(name, semantic_type, uid=relation_uid, ont_uid=ont_uid,
                                         frame_value=frame_value)
        self.add_rdf(relation_uid=relation_uid, rdf_type=RDF.subject,
                     element_uid=object_uid_1, element_type=ElementType.object)
        self.add_rdf(relation_uid=relation_uid, rdf_type=RDF.object,
                     element_uid=object_uid_2, element_type=ElementType.object)

        return relation_uid

    def add_relation_action_object(self, name, semantic_type, action_uid, object_uid, relation_uid=None,
                                   ont_uid=None, frame_value=None):
        # Note: no need to wrap uids as UID, since all calls are public functions, and no access to dict is done.
        relation_uid = self.add_relation(name, semantic_type, uid=relation_uid, ont_uid=ont_uid,
                                         frame_value=frame_value)
        self.add_rdf(relation_uid=relation_uid, rdf_type=RDF.subject,
                     element_uid=action_uid, element_type=ElementType.action)
        self.add_rdf(relation_uid=relation_uid, rdf_type=RDF.object,
                     element_uid=object_uid, element_type=ElementType.object)

        return relation_uid

    def add_relation_subject_object(self, name, semantic_type, subject_type, subject_uid, object_type, object_uid,
                                    relation_uid, ont_uid, frame_value=None):
        # Note: no need to wrap uids as UID, since all calls are public functions, and no access to dict is done.
        relation_uid = self.add_relation(name, semantic_type, uid=relation_uid, ont_uid=ont_uid, frame_value=frame_value)
        assert(isinstance(subject_type, ElementType))
        assert(isinstance(object_type, ElementType))
        self.add_rdf(relation_uid=relation_uid, rdf_type=RDF.subject,
                     element_uid=subject_uid, element_type=subject_type)
        self.add_rdf(relation_uid=relation_uid, rdf_type=RDF.object,
                     element_uid=object_uid, element_type=object_type)

        return relation_uid

    def add_object_data(self, uid, object_data, frame_value=None):
        if self.has_element_data(ElementType.object, uid, object_data):
            warnings.warn("WARNING: This element already has an object_data with this name. "
                          "This will substitute the content. To add new object_data at new frame_intervals "
                          "use update_object_data. "
                          "To modify an existing object_data, use modify_object_data.")
        return self.__add_element_data(ElementType.object, UID(uid), object_data, FrameIntervals(frame_value))

    def add_action_data(self, uid, action_data, frame_value=None):
        if self.has_element_data(ElementType.object, uid, action_data):
            warnings.warn("WARNING: This element already has an action_data with this name. "
                          "This will substitute the content. To add new action_data at new frame_intervals "
                          "use update_action_data. "
                          "To modify an existing action_data, use modify_action_data.")
        return self.__add_element_data(ElementType.action, UID(uid), action_data, FrameIntervals(frame_value))

    def add_event_data(self, uid, event_data, frame_value=None):
        if self.has_element_data(ElementType.object, uid, event_data):
            warnings.warn("WARNING: This element already has an event_data with this name. "
                          "This will substitute the content. To add new event_data at new frame_intervals "
                          "use update_event_data. "
                          "To modify an existing event_data, use modify_event_data.")
        return self.__add_element_data(ElementType.evevt, UID(uid), event_data, FrameIntervals(frame_value))

    def add_context_data(self, uid, context_data, frame_value=None):
        if self.has_element_data(ElementType.object, uid, context_data):
            warnings.warn("WARNING: This element already has an context_data with this name. "
                          "This will substitute the content. To add new context_data at new frame_intervals "
                          "use update_context_data. "
                          "To modify an existing context_data, use modify_context_data.")
        return self.__add_element_data(ElementType.context, UID(uid), context_data, FrameIntervals(frame_value))

    def modify_action(self, uid, name=None, semantic_type=None, frame_value = None, ont_uid=None, stream=None):
        return self.__modify_element(
            ElementType.action, UID(uid), name, semantic_type, FrameIntervals(frame_value), UID(ont_uid), stream
        )

    def modify_object(self, uid, name=None, semantic_type=None, frame_value=None, ont_uid=None, stream=None):
        return self.__modify_element(
            ElementType.object, UID(uid), name, semantic_type, FrameIntervals(frame_value), UID(ont_uid), stream
        )

    def modify_event(self, uid, name=None, semantic_type=None, frame_value=None, ont_uid=None, stream=None):
        return self.__modify_element(
            ElementType.event, UID(uid), name, semantic_type, FrameIntervals(frame_value), UID(ont_uid), stream
        )

    def modify_context(self, uid, name=None, semantic_type=None, frame_value=None, ont_uid=None, stream=None):
        return self.__modify_element(
            ElementType.context, UID(uid), name, semantic_type, FrameIntervals(frame_value), UID(ont_uid), stream
        )

    def modify_relation(self, uid, name=None, semantic_type=None, frame_value=None, ont_uid=None, stream=None):
        return self.__modify_element(
            ElementType.relation, UID(uid), name, semantic_type, FrameIntervals(frame_value), UID(ont_uid), stream
        )

    def modify_action_data(self, uid, action_data, frame_value):
        return self.add_action_data(uid, action_data, frame_value)

    def modify_object_data(self, uid, object_data, frame_value):
        return self.add_object_data(uid, object_data, frame_value)

    def modify_event_data(self, uid, event_data, frame_value):
        return self.add_event_data(uid, event_data, frame_value)

    def modify_context_data(self, uid, context_data, frame_value):
        return self.add_context_data(uid, context_data, frame_value)

    def update_element_data(self, element_type, uid, element_data, frame_value=None):
        assert(isinstance(element_type, ElementType))
        assert(isinstance(element_data, types.ObjectData))
        element = self.get_element(element_type, uid)

        if frame_value is not None:
            # Dynamic
            if element is not None:
                if element_type.name + '_data_pointers' in element:
                    if element_data.data['name'] in element[element_type.name + '_data_pointers']:
                        # It is not a simple call to addElementData with the union of frame intervals
                        # We need to substitute the content for just frameValue, without modifying the rest that must
                        # stay as it was

                        # Similar to what is done in addElementData:
                        # 1.- Update Root element, farmes and VCD (just in case this call to updateElementData just
                        # adds one frame)
                        fis_existing = FrameIntervals(element['frame_intervals'])
                        fis_new = FrameIntervals(frame_value)
                        fis_union = fis_existing.union(fis_new)
                        ont_uid = None
                        stream = None
                        if 'ontology_uid' in element:
                            ont_uid = element['ontology_uid']
                        if 'stream' in element:
                            stream = element['stream']
                        self.__add_element(
                            element_type, element['name'], element['type'], fis_union, UID(uid), UID(ont_uid), stream
                        )

                        # 2.- Inject the new elementdata using the framevalue
                        # this will replace existing content at such frames, or create new entries
                        self.__create_update_element_data(element_type, UID(uid), element_data, fis_new)

                        # 3.- Update element_data_pointers
                        self.__create_update_element_data_pointers(element_type, UID(uid), element_data, fis_union)
        else:
            # Static: so wa can't fuse frame intervals, this is a substitution
            if element is not None:
                self.__add_element_data(element_type, UID(uid), element_data, FrameIntervals(frame_value))

    def update_action_data(self, uid, action_data, frame_value=None):
        return self.update_element_data(ElementType.action, uid, action_data, frame_value)

    def update_object_data(self, uid, object_data, frame_value=None):
        return self.update_element_data(ElementType.object, uid, object_data, frame_value)

    def update_event_data(self, uid, event_data, frame_value=None):
        return self.update_element_data(ElementType.event, uid, event_data, frame_value)

    def update_context_data(self, uid, context_data, frame_value=None):
        return self.update_element_data(ElementType.context, uid, context_data, frame_value)

    ##################################################
    # Get / Read
    ##################################################
    def get_data(self):
        return self.data

    def has_objects(self):
        return 'objects' in self.data['vcd']

    def has_actions(self):
        return 'actions' in self.data['vcd']

    def has_contexts(self):
        return 'contexts' in self.data['vcd']

    def has_events(self):
        return 'events' in self.data['vcd']

    def has_relations(self):
        return 'relations' in self.data['vcd']

    def has(self, element_type, uid):
        if not element_type.name + 's' in self.data['vcd']:
            return False
        else:
            uid_str = UID(uid).as_str()
            if uid_str in self.data['vcd'][element_type.name + 's']:
                return True
            else:
                return False

    def has_element_data(self, element_type, uid, element_data):
        if not self.has(element_type, uid):
            return False
        else:
            uid_str = UID(uid).as_str()
            if element_type.name + '_data_pointers' not in self.data['vcd'][element_type.name + 's'][uid_str]:
                return False
            name = element_data.data['name']
            return name in self.data['vcd'][element_type.name + 's'][uid_str][element_type.name + '_data_pointers']

    def get_all(self, element_type):
        """
        Returns all elements of the specified ElementType.
        e.g. all Object's or Context's
        """
        assert(isinstance(element_type, ElementType))
        return self.data['vcd'].get(element_type.name + 's')

    def get_element(self, element_type, uid):
        assert (isinstance(element_type, ElementType))
        if self.data['vcd'].get(element_type.name + 's') is None:
            warnings.warn("WARNING: trying to get a " + element_type.name + " but this VCD has none.")
            return None
        uid_str = UID(uid).as_str()
        if uid_str in self.data['vcd'][element_type.name + 's']:
            return self.data['vcd'][element_type.name + 's'][uid_str]
        else:
            warnings.warn("WARNING: trying to get non-existing " + element_type.name + " with uid: " + uid_str)
            return None

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

    def get_frame(self, frame_num):
        if 'frames' not in self.data['vcd']:
            return None
        else:
            frame = self.data['vcd']['frames'].get(frame_num)
            return frame

    def get_elements_of_type(self, element_type, semantic_type):
        uids_str = []
        if not element_type.name + 's' in self.data['vcd']:
            return uids_str
        for uid_str, element in self.data['vcd'][element_type.name + 's'].items():
            if element['type'] == semantic_type:
                uids_str.append(uid_str)
        return uids_str

    def get_elements_with_element_data_name(self, element_type, data_name):
        uids_str = []
        for uid_str in self.data['vcd'][element_type.name + 's']:
            element = self.data['vcd'][element_type.name + 's'][uid_str]
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
        if uid_str in self.data['vcd'][element_type.name + 's']:
            element = self.data['vcd'][element_type.name + 's'][uid_str]
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

    def get_element_data(self, element_type, uid, data_name, frame_num = None):
        uid_str = UID(uid).as_str()
        if self.has(element_type, uid):
            if frame_num is not None:
                # Dynamic info
                if not isinstance(frame_num, int):
                    warnings.warn("WARNING: Calling get_element_data with a non-integer frame_num.")
                frame = self.get_frame(frame_num)
                if frame is not None:
                    element = frame[element_type.name + 's'][uid_str]
                    for prop in element[element_type.name + '_data']:
                        val_array = element[element_type.name + '_data'][prop]
                        for val in val_array:
                            if val['name'] == data_name:
                                return val
            else:
                # Static info
                element = self.data['vcd'][element_type.name + 's'][uid_str]
                for prop in element[element_type.name + '_data']:
                    val_array = element[element_type.name + '_data'][prop]
                    for val in val_array:
                        if val['name'] == data_name:
                            return val
        else:
            warnings.warn("WARNING: Asking element data from a non-existing Element.")
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
            element = self.data['vcd'][element_type.name + 's'][uid_str]
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
        return len(self.data['vcd'][element_type.name + 's'])

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

    def get_ontology(self, ont_uid):
        ont_uid_str = UID(ont_uid).as_str()
        if 'ontologies' in self.data['vcd']:
            if ont_uid_str in self.data['vcd']['ontologies']:
                return self.data['vcd']['ontologies'][ont_uid_str]
        return None

    def get_metadata(self):
        if 'metadata' in self.data['vcd']:
            return self.data['vcd']['metadata']
        else:
            return dict()

    def has_stream(self, stream):
        md = self.get_metadata()
        if 'streams' in md:
            stream_name = StreamType[stream]
            if stream_name in self.data['vcd']['streams']:
                return True
            else:
                return False

    def get_frame_intervals(self):
        if 'frame_intervals' in self.data['vcd']:
            return FrameIntervals(self.data['vcd']['frame_intervals'])
        else:
            return FrameIntervals()

    def get_element_frame_intervals(self, element_type, uid):
        uid_str = UID(uid).as_str()
        if not element_type.name + 's' in self.data['vcd']:
            return FrameIntervals()
        else:
            if not uid_str in self.data['vcd'][element_type.name + 's']:
                return FrameIntervals()
            return FrameIntervals(self.data['vcd'][element_type.name + 's'][uid_str].get('frame_intervals'))

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
        elements = self.data['vcd'][element_type.name + 's']
        index = None

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
        elements = self.data['vcd'][element_type.name + 's']

        # Get element from summary
        if not self.has(element_type, uid):
            return

        # Remove from frames: let's read frame_intervals from summary
        element = elements[uid_str]
        for i in range(0, len(element['frame_intervals'])):
            fi = element['frame_intervals'][i]
            for frame_num in range(fi['frame_start'], fi['frame_end']+1):
                elements_in_frame = self.data['vcd']['frames'][frame_num][element_type.name + 's']
                if uid in elements_in_frame:
                    del elements_in_frame[uid_str]
                if len(elements_in_frame) == 0: # objects might have end up empty TODO: test this
                    del self.data['vcd']['frames'][frame_num][element_type.name + 's']
                    if len(self.data['vcd']['frames'][frame_num]) == 0: # this frame may have ended up being empty
                        del self.data['vcd']['frames'][frame_num]

        # Delete this element from summary
        del elements[uid_str]

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
