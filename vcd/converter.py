"""
VCD (Video Content Description) library v4.3.1

Project website: http://vcd.vicomtech.org

Copyright (C) 2021, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.3.1.
VCD is distributed under MIT License. See LICENSE.

"""

import warnings
import copy

import vcd.core as core
import vcd.schema as schema
import vcd.types as types


class ConverterVCD420toOpenLabel020:
    # This class converts from VCD 4.2.0 into OpenLABEL 0.2.0

    # Main changes
    # 1) Metadata in OpenLABEL 0.2.0 is mostly inside "metadata"
    # 2) "streams" are at root and not inside "metadata"
    # 3) element_data_pointers in OpenLABEL 0.2.0 didn't exist in VCD 4.2.0
    # 4) UIDs are stored as strings in OpenLABEL 0.2.0 (e.g. ontology_uid)
    # 5) coordinate_systems

    # Other changes are implicitly managed by the VCD API

    def __init__(self, vcd_420_data, openlabel_020):
        if 'vcd' not in vcd_420_data:
            raise Exception("This is not a valid VCD 4.2.0 file")

        # While changes 1-2-3 are the only ones implemented, it is easier to just copy everything and then move things
        openlabel_020.data = copy.deepcopy(vcd_420_data)
        openlabel_020.data['openlabel'] = openlabel_020.data.pop('vcd')

        # 1) Metadata (annotator and comment were already inside metadata)
        if 'name' in openlabel_020.data['openlabel']:
            openlabel_020.data['openlabel'].setdefault('metadata', {})
            openlabel_020.data['openlabel']['metadata']['name'] = openlabel_020.data['openlabel']['name']
            del openlabel_020.data['openlabel']['name']
        if 'version' in openlabel_020.data['openlabel']:
            openlabel_020.data['openlabel'].setdefault('metadata', {})
            openlabel_020.data['openlabel']['metadata']['schema_version'] = schema.openlabel_schema_version
            del openlabel_020.data['openlabel']['version']

        # 2) Streams, no longer under "metadata"
        if 'metadata' in openlabel_020.data['openlabel']:
            if 'streams' in openlabel_020.data['openlabel']['metadata']:
                openlabel_020.data['openlabel']['streams'] = copy.deepcopy(openlabel_020.data['openlabel']['metadata']['streams'])
                del openlabel_020.data['openlabel']['metadata']['streams']

        # 3) Data pointers need to be fully computed
        self.__compute_data_pointers(openlabel_020.data)

        # 4) UIDs, when values, as strings
        for element_type in core.ElementType:
            if element_type.name + 's' in openlabel_020.data['openlabel']:
                for uid, element in openlabel_020.data['openlabel'][element_type.name + 's'].items():
                    if 'ontology_uid' in element:
                        element['ontology_uid'] = str(element['ontology_uid'])

    def __compute_data_pointers(self, openlabel_020_data):
        # WARNING! This function might be extremely slow
        # It does loop over all frames, and updates data pointers at objects, actions, etc
        # It is useful to convert from VCD 4.2.0 into OpenLABEL 0.2.0 (use converter.ConverterVCD420toOpenLABEL020)

        # Looping over frames and creating the necessary data_pointers
        if 'frame_intervals' in openlabel_020_data['openlabel']:
            fis = openlabel_020_data['openlabel']['frame_intervals']
            for fi in fis:
                for frame_num in range(fi['frame_start'], fi['frame_end'] + 1):
                    frame = openlabel_020_data['openlabel']['frames'][frame_num]  # warning: at this point, the key is str
                    for element_type in core.ElementType:
                        if element_type.name + 's' in frame:  # e.g. "objects", "actions"...
                            for uid, element in frame[element_type.name + 's'].items():
                                if element_type.name + '_data' in element:
                                    # So this element has element_data in this frame
                                    # and then we need to update the element_data_pointer at the root
                                    # we can safely assume it already exists

                                    # First, let's create a element_data_pointer at the root
                                    openlabel_020_data['openlabel'][element_type.name + 's'][uid].\
                                        setdefault(element_type.name + '_data_pointers', {})
                                    edp = openlabel_020_data['openlabel'][element_type.name + 's'][uid][element_type.name + '_data_pointers']

                                    # Let's loop over the element_data
                                    for ed_type, ed_array in element[element_type.name + '_data'].items():
                                        # e.g. ed_type is 'bbox', ed_array is the array of such bboxes content
                                        for element_data in ed_array:
                                            name = element_data['name']
                                            edp.setdefault(name, {})  # this element_data may already exist
                                            edp[name].setdefault('type', ed_type)  # e.g. 'bbox'
                                            edp[name].setdefault('frame_intervals', [])  # in case it does not exist
                                            fis_exist = core.FrameIntervals(edp[name]['frame_intervals'])
                                            fis_exist = fis_exist.union(core.FrameIntervals(frame_num))  # So, let's fuse with this frame
                                            edp[name]['frame_intervals'] = fis_exist.get_dict()  # overwrite
                                            # No need to manage attributes
