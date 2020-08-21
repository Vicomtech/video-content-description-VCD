"""
VCD (Video Content Description) library v4.3.0

Project website: http://vcd.vicomtech.org

Copyright (C) 2020, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.3.0.
VCD is distributed under MIT License. See LICENSE.

"""

import warnings
import copy

import vcd.core as core
import vcd.types as types


class ConverterVCD430toVCD330:
    # This class receives a VCD 4.3.0, and creates a VCD 3.3.0 payload
    # Creates a Frame-wise VCD 3.3.0 JSON payload

    # NOTE: Some features of VCD 4.3.0 are NOT supported by VCD 3.3.0
    # Therefore, some content from a VCD 4.3.0 may not be convertible to VCD 3.3.0
    # e.g. VCD 4.3.0 supports action_data, event_data, context_data,
    #      also specific intrinsics and extrinsics information

    # NOTE: This class is left here for future work.
    # the differences between VCD 4.3.0 and VCD 3.3.0 are so large that it is
    # miss-leading to have a ConverterVCD430toVCD330 class which works only partially
    # for some use cases.

    def __init__(self, vcd_430_data):       

        # Create VCD 3.3.0 container
        vcd_330_data = dict()
        vcd_330_data['VCD'] = dict()

        # Root and metadata
        if 'metadata' in vcd_430_data['vcd']:
            if 'annotator' in vcd_430_data['vcd']['metadata']:
                vcd_330_data['VCD']['annotator'] = vcd_430_data['vcd']['metadata']['annotator']
            if 'name' in vcd_430_data['vcd']['metadata']:
                vcd_330_data['VCD']['name'] = vcd_430_data['vcd']['metadata']['name']
            if 'comment' in vcd_430_data['vcd']['metadata']:
                vcd_330_data['VCD']['scdName'] = vcd_430_data['vcd']['metadata']['comment']
        
        if 'streams' in vcd_430_data['vcd']:
            vcd_330_data['VCD']['metaData'] = dict()
            for stream in vcd_430_data['vcd']['streams'].keys():
                vcd_330_data['VCD']['metaData'].setdefault('stream', [])
                if 'stream_properties' in vcd_430_data['vcd']['streams'][stream]:
                    vcd_330_data['VCD']['metaData']['stream'].append(
                        {"description": vcd_430_data['vcd']['streams'][stream]['description'],
                         "uri": vcd_430_data['vcd']['streams'][stream]['uri'],
                         "name": stream,
                         "type": vcd_430_data['vcd']['streams'][stream]['type'],
                         "streamProperties": vcd_430_data['vcd']['streams'][stream]['stream_properties']}
                    )
                else:
                    vcd_330_data['VCD']['metaData']['stream'].append(
                        {"description": vcd_430_data['vcd']['streams'][stream]['description'],
                         "uri": vcd_430_data['vcd']['streams'][stream]['uri'],
                         "name": stream,
                         "type": vcd_430_data['vcd']['streams'][stream]['type']}
                    )

        # Frame intervals (only the outer frame interval in VCD 3.3.0)
        fis = vcd_430_data['vcd']['frame_intervals']
        frameStart = 0
        frameEnd = 0
        for fi in fis:
            if fi['frame_start'] > frameStart:
                frameStart = fi['frame_start']
            if fi['frame_end'] > frameEnd:
                frameEnd = fi['frame_end']

        vcd_330_data['VCD']['frameInterval'] = {
            'frameStart': frameStart,
            'frameEnd': frameEnd
        }

        # Ontologies
        if 'ontologies' in vcd_430_data['vcd']:
            vcd_330_data['VCD']['OntologyManager'] = {}
            vcd_330_data['VCD']['OntologyManager']['ontology'] = []
            for ontology_uid in vcd_430_data['vcd']['ontologies'].keys():
                vcd_330_data['VCD']['OntologyManager']['ontology'].append(
                    vcd_430_data['vcd']['ontologies'][ontology_uid]
                )

        # StaticAttributes (objects and potentially contexts if no frame interval inside)
        if 'objects' in vcd_430_data['vcd']:
            for object_key in vcd_430_data['vcd']['objects'].keys():
                object = vcd_430_data['vcd']['objects'][object_key]

                #hasFrameIntervals = ('frame_intervals' in object)
                #if hasFrameIntervals:
                #    if len(object['frame_intervals']) == 0:
                #        hasFrameIntervals = False
                #if not hasFrameIntervals:
                if "object_data" in object:
                    # This is the static part of object
                    vcd_330_data['VCD'].setdefault('staticAttributes', dict())
                    vcd_330_data['VCD']['staticAttributes'].setdefault('objects', [])

                    obj = {}
                    obj.update({"name": object["name"]})
                    obj.update({"type": object["type"]})
                    obj.update({"uid": object_key})
                    if "ontology_uid" in object:
                        obj.update({"ontologyUID": object["ontology_uid"]})

                    # Copy object_data into ObjectDataContainer
                    self.__copy_object_data(object, obj)

                    vcd_330_data['VCD']['staticAttributes']['objects'].append(obj)
        if 'contexts' in vcd_430_data['vcd']:
            for context_key in vcd_430_data['vcd']['contexts'].keys():
                context4 = vcd_430_data['vcd']['contexts'][context_key]
                hasFrameIntervals = ('frame_intervals' in context4)
                if hasFrameIntervals:
                    if len(context4['frame_intervals']) == 0:
                        hasFrameIntervals = False

                if not hasFrameIntervals:
                    # This is the static part of object
                    vcd_330_data['VCD'].setdefault('staticAttributes', dict())
                    vcd_330_data['VCD']['staticAttributes'].setdefault('contexts', [])

                    obj = {}
                    obj.update({"name": context4["name"]})
                    obj.update({"type": context4["type"]})
                    obj.update({"uid": context_key})
                    if "ontology_uid" in context4:
                        obj.update({"ontologyUID": context4["ontology_uid"]})

                    vcd_330_data['VCD']['staticAttributes']['contexts'].append(obj)

        # Dynamic attributes
        # Actions, Events, Contexts, Objects, Relations -> create entries at 'frames'
        vcd_330_data['VCD'].setdefault('frames', [])

        for frame_num in vcd_430_data['vcd']['frames'].keys():
            frame4 = vcd_430_data['vcd']['frames'][frame_num]

            frame3 = dict()
            frame3.update({'frame': frame_num})

            for elements in frame4.keys():
                if elements == 'frame_properties':
                    if 'timestamp' in frame4['frame_properties']:
                        frame3.update({'timestamp': frame4['frame_properties']['timestamp']})
                else: #
                    frame3.setdefault(elements, [])
                    elements4 = frame4[elements]
                    for element4_id in elements4:
                        # In VCD4, within frame, we only have the uid, data is outside
                        element4_static = vcd_430_data['vcd'][elements][element4_id]
                        obj = {}
                        obj.update({"name": element4_static["name"]})
                        obj.update({"uid": element4_id})
                        obj.update({"type": element4_static["type"]})
                        if "ontology_uid" in element4_static:
                            obj.update({"ontologyUID": element4_static["ontology_uid"]})

                        element4_dynamic = elements4[element4_id]
                        if elements == 'objects':
                            # Add ObjectDataContainers
                            self.__copy_object_data(element4_dynamic, obj)

                        elif elements == 'relations':
                            obj.update({"predicate": element4_static["type"]})
                            if 'rdf_subjects' in element4_static:
                                obj.update({'rdf_subjects': element4_static['rdf_subjects']})
                            if 'rdf_objects' in element4_static:
                                obj.update({'rdf_objects': element4_static['rdf_objects']})


                        frame3[elements].append(obj)
                vcd_330_data['VCD']['frames'].append(frame3)

            return vcd_330_data

    def __add_attributes(self, src430, dst330):
        if 'attributes' in src430:
            attrib3_dict = {}
            attrib3_type = ""
            for attrib4_key in src430['attributes'].keys():
                if attrib4_key == "boolean":
                    attrib3_dict.setdefault('bool', [])
                    attrib3_type = "bool"
                elif attrib4_key == "text":
                    attrib3_dict.setdefault('text', [])
                    attrib3_type = "text"
                elif attrib4_key == "num" or attrib4_key == "vec":
                    attrib3_dict.setdefault("num", [])
                    attrib3_type = "num"

                for it4 in src430['attributes'][attrib4_key]:
                    it3 = {}
                    it3.update({"name": it4['name']})
                    if attrib4_key == "num":
                        if 'val' in it4:
                            it3.update({"val": [it4['val']]})
                    else:
                        if 'val' in it4:
                            it3.update({"val": it4['val']})
                    if "stream" in it4:
                        warnings.warn("WARNING: VCD4.3.0 allows stream info for "
                                      "bool, num, text and vec, but VCD3.3.0 does not.")
                    attrib3_dict[attrib3_type].append(it3)
            dst330.update({"attributes": attrib3_dict})

    def __copy_object_data(self, root, obj):
        odc = {}
        if 'object_data' not in root:
            return
        for object_data_key in root['object_data'].keys():
            for object_data_item in root['object_data'][object_data_key]:

                object_data_current = {}
                object_data_current.update({"name": object_data_item['name']})

                if object_data_key == "num":  # special case, because vcd4 treats num as single number, while vcd3 requires array
                    if 'val' in object_data_item:
                        object_data_current.update({"val": [object_data_item['val']]})
                else:
                    if 'val' in object_data_item:
                        object_data_current.update({"val": object_data_item['val']})
                if 'stream' in object_data_item:
                    object_data_current.update({"inStream": object_data_item['stream']})

                # Add attributes
                self.__add_attributes(object_data_item, object_data_current)

                if object_data_key == "bbox":
                    odc.setdefault('bbox', [])
                    odc['bbox'].append(object_data_current)
                elif object_data_key == "num":
                    odc.setdefault('num', [])
                    odc['num'].append(object_data_current)
                elif object_data_key == "vec":
                    odc.setdefault('num', [])
                    odc['num'].append(object_data_current)
                elif object_data_key == "boolean":
                    odc.setdefault('bool', [])
                    odc['bool'].append(object_data_current)
                elif object_data_key == "text":
                    odc.setdefault('text', [])
                    odc['text'].append(object_data_current)
                elif object_data_key == "cuboid":
                    odc.setdefault('cuboid', [])
                    odc['cuboid'].append(object_data_current)
                elif object_data_key == "poly2d":
                    object_data_current.update({"closed": object_data_item['closed']})
                    object_data_current.update({"mode": object_data_item['mode']})
                    odc.setdefault('poly2D', [])
                    odc['poly2D'].append(object_data_current)
                elif object_data_key == "poly3d":
                    object_data_current.update({"closed": object_data_item['closed']})
                    odc.setdefault('poly3D', [])
                    odc['poly3D'].append(object_data_current)
                elif object_data_key == "point2d":
                    object_data_current.update({"id": object_data_item['id']})
                    odc.setdefault('point2D', [])
                    odc['point2D'].append(object_data_current)
                elif object_data_key == "point3d":
                    object_data_current.update({"id": object_data_item['id']})
                    odc.setdefault('point3D', [])
                    odc['point3D'].append(object_data_current)
                elif object_data_key == "mat":
                    object_data_current.update({"channels": object_data_item['channels']})
                    object_data_current.update({"width": object_data_item['width']})
                    object_data_current.update({"height": object_data_item['height']})
                    object_data_current.update({"dataType": object_data_item['data_type']})
                    odc.setdefault('mat', [])
                    odc['mat'].append(object_data_current)
                elif object_data_key == "image":
                    object_data_current.update({"encoding": object_data_item['encoding']})
                    object_data_current.update({"mimeType": object_data_item['mime_type']})
                    odc.setdefault('image', [])
                    odc['image'].append(object_data_current)
                elif object_data_key == "binary":
                    object_data_current.update({"dataType": object_data_item['data_type']})
                    object_data_current.update({"encoding": object_data_item['encoding']})
                    odc.setdefault('binary', [])
                    odc['binary'].append(object_data_current)
                elif object_data_key == "mesh":
                    # Area
                    object_data_current.setdefault("areaReference", list())
                    for key, val in object_data_item['area_reference'].items():
                        ref_type430 = val['reference_type']
                        if ref_type430 == "line_reference":
                            refType330 = "lineReference"
                        elif ref_type430 == "point3d":
                            refType330 = "point3D"
                        else:
                            refType330 = ref_type430
                        if 'val' in val:
                            object_data_current["areaReference"].append(
                                {
                                    "id": key,
                                    "name": val['name'],
                                    "referenceType": refType330,
                                    "val": val.get('val')
                                }
                            )
                        else:
                            object_data_current["areaReference"].append(
                                {
                                    "id": key,
                                    "name": val['name'],
                                    "referenceType": refType330,
                                }
                            )
                        # Add attributes
                        self.__add_attributes(val, object_data_current["areaReference"][-1])

                    # Line
                    object_data_current.setdefault("lineReference", list())
                    for key, val in object_data_item['line_reference'].items():
                        ref_type430 = val['reference_type']
                        if ref_type430 == "point3d":
                            refType330 = "point3D"
                        else:
                            refType330 = ref_type430
                        if 'val' in val:
                            object_data_current["lineReference"].append(
                                {
                                    "id": key,
                                    "name": val['name'],
                                    "referenceType": refType330,
                                    "val": val.get('val')
                                }
                            )
                        else:
                            object_data_current["lineReference"].append(
                                {
                                    "id": key,
                                    "name": val['name'],
                                    "referenceType": refType330,
                                }
                            )
                        # Add attributes
                        self.__add_attributes(val, object_data_current["lineReference"][-1])

                    # point3d
                    object_data_current.setdefault("point3D", list())
                    for key, val in object_data_item['point3d'].items():
                        object_data_current['point3D'].append(
                            {
                                "id": key,
                                "name": val['name'],
                                "val": val.get('val')
                            }
                        )

                        # Add attributes
                        self.__add_attributes(val, object_data_current['point3D'][-1])

                    odc.setdefault('mesh', [])
                    odc['mesh'].append(object_data_current)
                obj.update({'objectDataContainer': odc})


class ConverterVCD330toVCD430:
    # This class converts a VCD3.3.0 into VCD4.3.0
    
    def __init__(self, vcd_330_data, vcd_430):
        # Main VCD element
        if 'VCD' not in vcd_330_data:
            raise Exception("This is not a valid VCD 3.3.0 file.")

        # Metadata and other
        # NOTE: 'scdName' field is lost as VCD 4.3.0 does not support SCD
        # NOTE: 'frameInterval' from 'VCD' is not copied, but computed from frames
        # NOTE: 'guid' in 'Object's is ignored in VCD 4.3.0
        # TODO: Apparently 'streamProperties" can exist in VCD3.3.0, although it is not in the schema
        if 'annotator' in vcd_330_data['VCD']:
            vcd_430.add_annotator(vcd_330_data['VCD']['annotator'])
        if 'name' in vcd_330_data['VCD']:
            vcd_430.add_name(vcd_330_data['VCD']['name'])
        if 'metaData' in vcd_330_data['VCD']:
            metadata = vcd_330_data['VCD']['metaData']
            streams = metadata['stream']
            for stream in streams:
                stream_type = stream['type']
                if stream_type == 'video':
                    stream_type = 'camera'
                elif stream_type == 'pointcloud' or stream_type == 'lidar':
                    stream_type = 'lidar'
                vcd_430.add_stream(
                    stream['name'], stream['uri'], stream['description'], stream_type
                )
        if 'ontologyManager' in vcd_330_data['VCD']:
            ontologyManager = vcd_330_data['VCD']['ontologyManager']
            for ontology in ontologyManager['ontology']:
                vcd_430.add_ontology(ontology)
        if 'frames' in vcd_330_data['VCD']:
            # This is Frame-wise VCD
            for frame in vcd_330_data['VCD']['frames']:
                # A frame has required "frame", and optional "streamSync", "frameProperties", "frame", "timestamp"
                # and then "objects", "actions", etc.
                frame_num = frame['frame']
                if 'timestamp' in frame:
                    vcd_430.add_frame_properties(frame_num=frame_num,
                                                  timestamp=frame['timestamp'])
                if 'frameProperties' in frame:
                    frame_properties=dict()
                    for frameProperty in frame['frameProperties']:
                        val = frameProperty['val']
                        name = frameProperty['name']
                        if frameProperty['name'] == 'timestamp':
                            vcd_430.add_frame_properties(frame_num, timestamp=val)
                        else:
                            frame_properties[name] = val
                    if frame_properties:
                        vcd_430.add_frame_properties(frame_num, timestamp=None, properties=frame_properties)
                if 'streamSync' in frame:
                    for streamSyncItem in frame['streamSync']:
                        vcd_430.add_stream_properties(
                            streamSyncItem['name'],
                            stream_sync=types.StreamSync(
                                    frame_vcd=frame_num,
                                    frame_stream=streamSyncItem['frame']
                                )
                        )

                # Now the elements
                self.__copy_elements(vcd_430, frame, frame_num)

        if 'staticAttributes' in vcd_330_data['VCD']:
            self.__copy_elements(vcd_430, vcd_330_data['VCD']['staticAttributes'])

    def __copy_elements(self, vcd_430, root, frame_num=None):
        if 'objects' in root:
            for object in root['objects']:
                uid = str(object['uid'])  # Let's convert to string here
                name = object['name']
                ontologyUID = None
                if 'ontologyUID' in object:
                    ontologyUID = str(object['ontologyUID'])  # Let's convert to string here
                typeSemantic = object.get('type', '')  # In VCD 4.3.0 type is required, but it VCD 3.3.0 seems to be not

                if not vcd_430.has(core.ElementType.object, uid):
                    vcd_430.add_object(name, typeSemantic, frame_num, uid, ontologyUID)

                if 'objectDataContainer' in object:
                    objectDataContainer = object['objectDataContainer']
                    for key, value in objectDataContainer.items():
                        for object_data in value:
                            inStream = None
                            if 'inStream' in object_data:
                                inStream = object_data['inStream']
                            if 'val' in object_data:
                                val = object_data['val']
                            currentObjectData = None

                            # Create main object_data body
                            # NOTE: in the following calls, I am using direct access to dictionary for required fields, e.g.
                            # object_data['name'], etc.
                            # For optional fields, I am using get() function, e.g. object_data.get('mode') which defaults to
                            # None
                            if key == 'num':
                                if len(val) == 1:
                                    # Single value, this is a num
                                    currentObjectData = types.num(object_data['name'], val[0], inStream)
                                else:
                                    # Multiple values, this is a vec
                                    currentObjectData = types.vec(object_data['name'], val, inStream)
                            elif key == 'bool':
                                currentObjectData = types.boolean(object_data['name'], val, inStream)
                            elif key == 'text':
                                currentObjectData = types.text(object_data['name'], val, inStream)
                            elif key == 'image':
                                currentObjectData = types.image(
                                    object_data['name'], val,
                                    object_data['mimeType'], object_data['encoding'],
                                    inStream
                                )
                            elif key == 'binary':
                                currentObjectData = types.binary(
                                    object_data['name'], val,
                                    object_data['dataType'], object_data['encoding'],
                                    inStream
                                )
                            elif key == 'vec':
                                currentObjectData = types.vec(object_data['name'], val, inStream)
                            elif key == 'bbox':
                                currentObjectData = types.bbox(object_data['name'], val, inStream)
                            elif key == 'cuboid':
                                currentObjectData = types.cuboid(object_data['name'], val, inStream)
                            elif key == 'mat':
                                currentObjectData = types.mat(
                                    object_data['name'], val,
                                    object_data['channels'], object_data['width'], object_data['height'],
                                    object_data['dataType'],
                                    inStream
                                )
                            elif key == 'point2D':
                                currentObjectData = types.point2d(object_data['name'], val, object_data.get('id'), inStream)
                            elif key == 'point3D':
                                currentObjectData = types.point3d(object_data['name'], val, object_data.get('id'), inStream)
                            elif key == "poly2D":
                                mode_int = object_data['mode']
                                currentObjectData = types.poly2d(
                                    object_data['name'], val, types.Poly2DType(mode_int), object_data['closed'], inStream
                                )
                            elif key == "poly3D":
                                currentObjectData = types.poly3d(object_data['name'], val, object_data['closed'], inStream)
                            elif key == "mesh":
                                currentObjectData = types.mesh(object_data['name'])
                                if 'point3D' in object_data:
                                    for p3d_330 in object_data['point3D']:
                                        # Create a types.point3d object and add it to the mesh
                                        id = p3d_330['id']
                                        name = p3d_330['name']
                                        val = p3d_330['val']

                                        p3d_430 = types.point3d(name, val)
                                        self.__add_attributes(p3d_330, p3d_430)
                                        currentObjectData.add_vertex(p3d_430, id)

                                if 'lineReference' in object_data:
                                    for lref_330 in object_data['lineReference']:
                                        # Create a types.line_reference object and add it to the mesh
                                        id = lref_330['id']
                                        name = lref_330['name']
                                        referenceType = lref_330['referenceType']
                                        assert(referenceType == "point3D")
                                        val = lref_330.get('val')  # defaults to None, needed for the constructor

                                        lref_430 = types.lineReference(name, val, types.ObjectDataType.point3d)
                                        self.__add_attributes(lref_330, lref_430)
                                        currentObjectData.add_edge(lref_430, id)

                                if 'areaReference' in object_data:
                                    for aref_330 in object_data['areaReference']:
                                        # Create a types.area_reference object and add it to the mesh
                                        id = aref_330['id']
                                        name = aref_330['name']
                                        referenceType = aref_330['referenceType']
                                        assert (referenceType == "point3D" or referenceType == "lineReference")
                                        val = aref_330.get('val')  # defaults to None, needed for the constructor

                                        if referenceType == "point3D":
                                            aref_430 = types.areaReference(name, val, types.ObjectDataType.point3d)
                                        else:
                                            aref_430 = types.areaReference(name, val, types.ObjectDataType.line_reference)
                                        self.__add_attributes(aref_330, aref_430)
                                        currentObjectData.add_area(aref_430, id)

                            # Add any attributes
                            self.__add_attributes(object_data, currentObjectData)

                            # Add the object_data to the object
                            if not vcd_430.has_element_data(core.ElementType.object, uid, currentObjectData):
                                vcd_430.add_object_data(uid, currentObjectData, frame_num)
                            else:
                                vcd_430.update_object_data(uid, currentObjectData, frame_num)
        if 'actions' in root:
            for action in root['actions']:
                uid = str(action['uid'])
                name = action['name']
                ontologyUID = None
                if 'ontologyUID' in action:
                    ontologyUID = str(action['ontologyUID'])
                typeSemantic = action.get('type', '')  # required in VCD 4.0, not in VCD 3.3.0

                if not vcd_430.has(core.ElementType.action, uid):
                    vcd_430.add_action(name, typeSemantic, frame_num, uid, ontologyUID)
                else:
                    vcd_430.update_action(uid, frame_num)
        if 'events' in root:
            for event in root['events']:
                uid = str(event['uid'])
                name = event['name']
                ontologyUID = None
                if 'ontologyUID' in event:
                    ontologyUID = str(event['ontologyUID'])
                typeSemantic = event.get('type', '')

                if not vcd_430.has(core.ElementType.event, uid):
                    vcd_430.add_event(name, typeSemantic, frame_num, uid, ontologyUID)
                else:
                    vcd_430.update_event(uid, frame_num)
        if 'contexts' in root:
            for context in root['contexts']:
                uid = str(context['uid'])
                name = context['name']
                ontologyUID = None
                if 'ontologyUID' in context:
                    ontologyUID = str(context['ontologyUID'])
                typeSemantic = context.get('type', '')

                if not vcd_430.has(core.ElementType.context, uid):
                    vcd_430.add_context(name, typeSemantic, frame_num, uid, ontologyUID)
                else:
                    vcd_430.update_context(uid, frame_num)
        if 'relations' in root:
            for relation in root['relations']:
                uid = str(relation['uid'])
                name = relation['name']
                ontologyUID = None
                if 'ontologyUID' in relation:
                    ontologyUID = str(relation['ontologyUID'])
                predicate = relation.get('predicate', '')
                rdf_objects = relation.get('rdf_objects', None)
                rdf_subjects = relation.get('rdf_subjects', None)

                if not vcd_430.has(core.ElementType.relation, uid):
                    vcd_430.add_relation(name, predicate, frame_value=frame_num, uid=uid, ont_uid=ontologyUID)
                    for rdf_object in rdf_objects:
                        element_type = None
                        rdf_object_type_str = rdf_object['type']
                        if rdf_object_type_str == "Object":
                            element_type = core.ElementType.object
                        elif rdf_object_type_str == "Action":
                            element_type = core.ElementType.action
                        elif rdf_object_type_str == "Event":
                            element_type = core.ElementType.event
                        elif rdf_object_type_str == "Context":
                            element_type = core.ElementType.context
                        else:
                            warnings.warn("ERROR: Unrecognized Element type. Must be Object, Action, Event or Context.")

                        vcd_430.add_rdf(uid, core.RDF.object, str(rdf_object['uid']), element_type)
                    for rdf_subject in rdf_subjects:
                        element_type = None
                        rdf_object_type_str = rdf_subject['type']
                        if rdf_object_type_str == "Object":
                            element_type = core.ElementType.object
                        elif rdf_object_type_str == "Action":
                            element_type = core.ElementType.action
                        elif rdf_object_type_str == "Event":
                            element_type = core.ElementType.event
                        elif rdf_object_type_str == "Context":
                            element_type = core.ElementType.context
                        else:
                            warnings.warn("ERROR: Unrecognized Element type. Must be Object, Action, Event or Context.")

                        vcd_430.add_rdf(uid, core.RDF.subject, str(rdf_subject['uid']), element_type)
                else:
                    vcd_430.update_relation(uid, frame_num)

    def __add_attributes(self, src330, object_data430):
        # Add any attributes
        if 'attributes' in src330:
            attributes = src330['attributes']
            for k, v in attributes.items():
                if k == "bool":
                    for od in v:
                        object_data430.add_attribute(types.boolean(od['name'], od['val']))
                elif k == "num":
                    for od in v:
                        if len(od['val']) == 1:
                            object_data430.add_attribute(types.num(od['name'], od['val'][0]))
                        else:
                            object_data430.add_attribute(types.vec(od['name'], od['val']))
                elif k == "text":
                    for od in v:
                        object_data430.add_attribute(types.text(od['name'], od['val']))


class ConverterVCD420toVCD430:
    # This class converts from VCD 4.2.0 into VCD 4.3.0

    # Main changes
    # 1) Metadata in VCD 4.3.0 is mostly inside "metadata"
    # 2) "streams" are at root and not inside "metadata"
    # 3) element_data_pointers in VCD 4.3.0 didn't exist in VCD 4.2.0
    # 4) UIDs are stored as strings in VCD 4.3.0 (e.g. ontology_uid)

    # TODO
    # 5) Cuboids use quaternions
    # 6) Arbitrary number of coordinate systems

    # Other changes are implicitly managed by the VCD 4.3.0 API

    def __init__(self, vcd_420_data, vcd_430):
        if 'vcd' not in vcd_420_data:
            raise Exception("This is not a valid VCD 4.2.0 file")

        # While changes 1-2-3 are the only ones implemented, it is easier to just copy everything and then move things
        vcd_430.data = copy.deepcopy(vcd_420_data)

        # 1) Metadata (annotator and comment were already inside metadata)
        if 'name' in vcd_430.data['vcd']:
            vcd_430.data['vcd'].setdefault('metadata', {})
            vcd_430.data['vcd']['metadata']['name'] = vcd_430.data['vcd']['name']
            del vcd_430.data['vcd']['name']
        if 'version' in vcd_430.data['vcd']:
            vcd_430.data['vcd'].setdefault('metadata', {})
            vcd_430.data['vcd']['metadata']['schema_version'] = "4.3.0"
            del vcd_430.data['vcd']['version']

        # 2) Streams, no longer under "metadata"
        if 'metadata' in vcd_430.data['vcd']:
            if 'streams' in vcd_430.data['vcd']['metadata']:
                vcd_430.data['vcd']['streams'] = copy.deepcopy(vcd_430.data['vcd']['metadata']['streams'])
                del vcd_430.data['vcd']['metadata']['streams']

        # 3) Data pointers need to be fully computed
        self.__compute_data_pointers(vcd_430.data)

        # 4) UIDs, when values, as strings
        for element_type in core.ElementType:
            if element_type.name + 's' in vcd_430.data['vcd']:
                for uid, element in vcd_430.data['vcd'][element_type.name + 's'].items():
                    if 'ontology_uid' in element:
                        element['ontology_uid'] = str(element['ontology_uid'])

    def __compute_data_pointers(self, vcd_430_data):
        # WARNING! This function might be extremely slow
        # It does loop over all frames, and updates data pointers at objects, actions, etc
        # It is useful to convert from VCD 4.2.0 into VCD 4.3.0 (use converter.ConverterVCD420toVCD430)

        # Looping over frames and creating the necessary data_pointers
        if 'frame_intervals' in vcd_430_data['vcd']:
            fis = vcd_430_data['vcd']['frame_intervals']
            for fi in fis:
                for frame_num in range(fi['frame_start'], fi['frame_end'] + 1):
                    frame = vcd_430_data['vcd']['frames'][str(frame_num)]  # warning: at this point, the key is str
                    for element_type in core.ElementType:
                        if element_type.name + 's' in frame:  # e.g. "objects", "actions"...
                            for uid, element in frame[element_type.name + 's'].items():
                                if element_type.name + '_data' in element:
                                    # So this element has element_data in this frame
                                    # and then we need to update the element_data_pointer at the root
                                    # we can safely assume it already exists

                                    # First, let's create a element_data_pointer at the root
                                    vcd_430_data['vcd'][element_type.name + 's'][uid].\
                                        setdefault(element_type.name + '_data_pointers', {})
                                    edp = vcd_430_data['vcd'][element_type.name + 's'][uid][element_type.name + '_data_pointers']

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