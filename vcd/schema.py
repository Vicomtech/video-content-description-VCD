"""
VCD (Video Content Description) library v4.3.1

Project website: http://vcd.vicomtech.org

Copyright (C) 2021, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.3.1.
VCD is distributed under MIT License. See LICENSE.

"""

######################################
# Fully manually writing the schema
######################################
from builtins import type

openlabel_schema_version = "0.3.0"
openlabel_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "openlabel": {"$ref": "#/definitions/openlabel"}
    },
    "definitions": {
        "openlabel": {
            "type": "object",
            "description": "This is the root OpenLABEL element.",
            "properties": {
                "metadata": {"$ref": "#/definitions/metadata"},
                "ontologies": {"$ref": "#/definitions/ontologies"},
                "resources": {"$ref": "#/definitions/resources"},
                "tags": {
                    "description": "Tags are a special type of labels which might be attached to any type of content, "
                                   "such as images, data containers, folders, etc. In OpenLabel its main purpose is to "
                                   "allow adding metadata to scenario descriptions.",
                    "type": "object",
                    "patternProperties": {
                        "^(-?[0-9]+|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$": {
                            "$ref": "#/definitions/tag"
                        }
                    },
                    "additionalProperties": False
                },
                "frames": {
                    "type": "object",
                    "patternProperties": {
                        "^[0-9]+$": {
                            "$ref": "#/definitions/frame"
                        }
                    },
                    "additionalProperties": False
                },
                "frame_intervals": {
                    "type": "array",
                    "item": {"$ref": "#/definitions/frame_interval"}
                },
                "objects": {
                    "type": "object",
                    "patternProperties": {
                        "^(-?[0-9]+|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$": {
                            "$ref": "#/definitions/object"
                        }
                    },
                    "additionalProperties": False
                },
                "actions": {
                    "type": "object",
                    "patternProperties": {
                        "^(-?[0-9]+|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$": {
                            "$ref": "#/definitions/action"
                        }
                    },
                    "additionalProperties": False
                },
                "events": {
                    "type": "object",
                    "patternProperties": {
                        "^(-?[0-9]+|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$": {
                            "$ref": "#/definitions/event"
                        }
                    },
                    "additionalProperties": False
                },
                "contexts": {
                    "type": "object",
                    "patternProperties": {
                        "^(-?[0-9]+|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$": {
                            "$ref": "#/definitions/context"
                        }
                    },
                    "additionalProperties": False
                },
                "relations": {
                    "type": "object",
                    "patternProperties": {
                        "^(-?[0-9]+|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$": {
                            "$ref": "#/definitions/relation"
                        }
                    },
                    "additionalProperties": False
                },
                "streams": {"$ref": "#/definitions/streams"},
                "coordinate_systems": {"$ref": "#/definitions/coordinate_systems"},
            },
            "additionalProperties": False,
            "required": ["metadata"]
        },
        "metadata": {
            "description": "This item contains information (metadata) about the annotation file itself including the "
                           "schema_version, file_version, annotator, etc.",
            "type": "object",
            "properties": {
                "schema_version": {"type": "string", "enum": [openlabel_schema_version]},
                "file_version": {"type": "string"},
                "name": {"type": "string"},
                "annotator": {"type": "string"},
                "comment": {"type": "string"},
            },
            "additionalProperties": True,
            "required": ["schema_version"]
        },
        "ontologies": {
            "description": "This item contains identifiers of ontologies as key (identifier) value (URL or URI) pairs. "
                           "Ontology identifiers can then be used within elements to declare where the element type is "
                           "defined",
            "type": "object",
            "patternProperties": {
                "^(-?[0-9]+|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$":
                    {
                        "oneOf": [{
                            "type": "string"
                        }, {
                            "type": "object",
                            "properties": {
                                "uri": {"type": "string"},
                                "subset_included": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "subset_excluded": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                }
                            },
                            "additionalProperties": True,
                            "required": ["uri"]
                        }]
                    },
            },
            "additionalProperties": False
        },
        "resources": {
            "description": "This item contains identifiers of external resources (files, URLs) that might be used to "
                           "link data of this annotation file with existing content. "
                           "E.g. \"resources\": { \"0\": \"../resources/oxdr/opendrive_file.xml\"} declares a resource "
                           "related to an OpenDrive file, with identifier \"0\"",
            "type": "object",
            "patternProperties": {
                "^(-?[0-9]+|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$":
                    {"type": "string"},
            },
            "additionalProperties": False
        },
        "resource_uid": {
            "description": "This is a unique identifier of an element in an external resource.",
            "type": "object",
            "patternProperties": {
                "^(-?[0-9]+|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$": {
                    "type": "string"
                }
            },
        },
        "tag": {
            "type": "object",
            "properties": {
                "type": {"type": "string"},
                "tag_data": {"$ref": "#/definitions/tag_data"},
                "ontology_uid": {"type": "string"},
                "resource_uid": {"$ref": "#/definitions/resource_uid"},
            },
            "additionalProperties": True,
            "required": ["type"]
        },
        "frame": {
            "description": "A frame is a container of dynamic information. It is indexed inside the OpenLabel file "
                           "by its frame number. Time information about the frame is enclosed inside its"
                           "\"frame_properties\". A frame contains dynamic information of elements, "
                           "such as \"objects\" or \"actions\", which are indexed by their UUID, so their static "
                           "information can be found at the element level.",
            "type": "object",
            "properties": {
                "objects": {
                    "type": "object",
                    "patternProperties": {
                        "^(-?[0-9]+|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$": {
                            "type": "object",
                            "properties": {
                                "object_data": {"$ref": "#/definitions/object_data"},
                            },
                            "additionalProperties": False
                        }
                    },
                    "additionalProperties": False
                },
                "events": {
                    "type": "object",
                    "patternProperties": {
                        "^(-?[0-9]+|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$": {
                            "type": "object",
                            "properties": {
                                "event_data": {"$ref": "#/definitions/event_data"},
                            },
                            "additionalProperties": False
                        }
                    },
                    "additionalProperties": False
                },
                "actions": {
                    "type": "object",
                    "patternProperties": {
                        "^(-?[0-9]+|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$": {
                            "type": "object",
                            "properties": {
                                "action_data": {"$ref": "#/definitions/action_data"},
                            },
                            "additionalProperties": False
                        }
                    },
                    "additionalProperties": False
                },
                "contexts": {
                    "type": "object",
                    "patternProperties": {
                        "^(-?[0-9]+|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$": {
                            "type": "object",
                            "properties": {
                                "context_data": {"$ref": "#/definitions/context_data"},
                            },
                            "additionalProperties": False
                        }
                    },
                    "additionalProperties": False
                },
                "relations": {
                    "type": "object",
                    "patternProperties": {
                        "^(-?[0-9]+|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$": {}
                    },
                    "additionalProperties": False
                },
                "frame_properties": {
                    "description": "These frame_properties include frame-related information,"
                                   "including: stream information, and timestamping."
                                   "-Timestamps: the field \'timestamp\' can be used to declare a"
                                   "master timestamp for all information within thi frame."
                                   "-Streams: can host information related to specific streams, such"
                                   "as specific timestamps or instantaneous intrinsics.",
                    "type": "object",
                    "properties": {
                        "timestamp": {"type": "string"},
                        "streams": {
                            "type": "object",
                            "patternProperties": {
                                "^": {"$ref": "#/definitions/stream"}
                            },
                            "additionalProperties": False
                        },
                        "transforms": {
                            "type": "object",
                            "patternProperties": {
                                "^": {"$ref": "#/definitions/transform"}
                            },
                            "additionalProperties": False
                        }
                    },
                    "additionalProperties": True
                }
            },
            "additionalProperties": False
        },
        "frame_interval": {
            "description": "A frame interval defines an starting and ending frame number, as a closed interval.",
            "type": "object",
            "properties": {
                "frame_start": {"type": "integer"},
                "frame_end": {"type": "integer"}
            },
            "additionalProperties": False
        },
        "streams": {
            "patternProperties": {
                "^": {"$ref": "#/definitions/stream"},
                },
            "type": "object",
            "additionalProperties": False
        },
        "coordinate_systems": {
            "patternProperties": {
                        "^": {"$ref": "#/definitions/coordinate_system"}
                    },
            "type": "object",
            "additionalProperties": False
        },
        "object": {
            "description": "An object is the main type of annotation element, and is designed to represent "
                           "spatio-temporal entities, such as physical objects in the real world. Objects as "
                           "any other element is identified by a UUID, and defined by its name, type, and other"
                           "properties. "
                           "All elements can have static and dynamic data. Objects are the only type of elements "
                           "that can have geometric data, such as bounding boxes, cuboids, polylines, images, etc.",
            "type": "object",
            "properties": {
                "frame_intervals": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/frame_interval"}
                },
                "name": {"type": "string"},
                "type": {"type": "string"},
                "ontology_uid": {"type": "string"},
                "resource_uid": {"$ref": "#/definitions/resource_uid"},
                "coordinate_system": {"type": "string"},
                "object_data": {"$ref": "#/definitions/object_data"},
                "object_data_pointers": {"$ref": "#/definitions/element_data_pointers"}
            },
            "required": ["name", "type"],
            "additionalProperties": False
        },
        "action": {
            "description": "An action is a type of element intended to describe temporal situations with "
                           "semantic load, such as a certain activity happening in real life, such as "
                           "crossing-zebra-cross, standing-still, playing-guitar. As such, actions are simply "
                           "defined by their type, the frame intervals in which the action happens, and any "
                           "additional action data (e.g. numbers, booleans, text as attributes of the actions)",
            "type": "object",
            "properties": {
                "frame_intervals": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/frame_interval"}
                },
                "name": {"type": "string"},
                "type": {"type": "string"},
                "ontology_uid": {"type": "string"},
                "resource_uid": {"$ref": "#/definitions/resource_uid"},
                "coordinate_system": {"type": "string"},
                "action_data": {"$ref": "#/definitions/action_data"},
                "action_data_pointers": {"$ref": "#/definitions/element_data_pointers"}
            },
            "required": ["name", "type"],
            "additionalProperties": False
        },
        "event": {
            "description": "An event is an instantaneous situation that happens without a temporal interval. "
                           "Events complement Actions providing a mechanism to specify triggers or to connect "
                           "actions and objects with causality relations.",
            "type": "object",
            "properties": {
                "frame_intervals": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/frame_interval"}
                },
                "name": {"type": "string"},
                "type": {"type": "string"},
                "ontology_uid": {"type": "string"},
                "resource_uid": {"$ref": "#/definitions/resource_uid"},
                "coordinate_system": {"type": "string"},
                "event_data": {"$ref": "#/definitions/event_data"},
                "event_data_pointers": {"$ref": "#/definitions/element_data_pointers"}
            },
            "required": ["name", "type"],
            "additionalProperties": False
        },
        "context": {
            "description": "A context is a type of element which defines any non spatial nor temporal annotation. "
                           "Contexts can be used to add richness to the contextual information of a scene, including "
                           "location, weather, application-related information",
            "type": "object",
            "properties": {
                "frame_intervals": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/frame_interval"}
                },
                "name": {"type": "string"},
                "type": {"type": "string"},
                "ontology_uid": {"type": "string"},
                "resource_uid": {"$ref": "#/definitions/resource_uid"},
                "coordinate_system": {"type": "string"},
                "context_data": {"$ref": "#/definitions/context_data"},
                "context_data_pointers": {"$ref": "#/definitions/element_data_pointers"}
            },
            "required": ["name", "type"],
            "additionalProperties": False
        },
        "relation": {
            "description": "A relation is a type of element which connects two or more other elements, using "
                           "RDF triples to structure the connection, with one or more subjects, a predicate and "
                           "one or more objects ",
            "type": "object",
            "properties": {
                "frame_intervals": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/frame_interval"}
                },
                "name": {"type": "string"},
                "type": {"type": "string"},
                "ontology_uid": {"type": "string"},
                "resource_uid": {"$ref": "#/definitions/resource_uid"},
                "rdf_objects": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/rdf_agent"}
                },
                "rdf_subjects": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/rdf_agent"}
                },
            },
            "required": ["name", "type", "rdf_objects", "rdf_subjects"],
            "additionalProperties": False
        },
        "rdf_agent": {
            "description": "This item specifies whether an RDF entry is a subject or an object in a RDF triple.",
            "type": "object",
            "properties": {
                "type": {"type": "string"},
                "uid": {"type": "string"},
            }
        },
        "element_data_pointers": {
            "type": "object",
            "patternProperties": {
                "^": {"$ref": "#/definitions/element_data_pointer"}
            },
            "additionalProperties": False
        },
        "element_data_pointer": {
            "description": "This item contains pointers to element_data of elements, indexed by name, and containing "
                           "information about the element_data type (e.g. bounding box, cuboid) and the frame intervals"
                           "in which this element_data exists within an element. "
                           "As a consequence, these pointers can be used to explore the JSON file rapidly",
            "type": "object",
            "properties": {
                "frame_intervals": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/frame_interval"}
                },
                "type": {
                    "type": "string",
                    "enum": ["bbox", "rbbox", "num", "text", "boolean", "poly2d", "poly3d", "cuboid", "image", "mat",
                             "binary", "point2d", "point3d", "vec", "line_reference", "area_reference", "mesh"]
                },
                "attribute_pointers": {
                    "type": "object",
                    "patternProperties": {
                        "^": {
                            "type": "string",
                            "enum": ["num", "text", "boolean", "vec"]
                        }
                    }
                }
            },
            "required": ["frame_intervals"]
        },
        "tag_data": {
            "oneOf": [{
                "type": "object",
                "properties": {
                    "num": {
                        "type": "array",
                        "items": {"$ref": "#/definitions/num"}
                    },
                    "vec": {
                        "type": "array",
                        "items": {"$ref": "#/definitions/vec"}
                    },
                    "text": {
                        "type": "array",
                        "items": {"$ref": "#/definitions/text"}
                    },
                    "boolean": {
                        "type": "array",
                        "items": {"$ref": "#/definitions/boolean"}
                    }
                },
                "additionalProperties": False
            }, {
                "type": "string"
            }]
        },
        "action_data": {
            "description": "Additional data to describe attributes of the action.",
            "type": "object",
            "properties": {
                "num": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/num"}
                },
                "vec": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/vec"}
                },
                "text": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/text"}
                },
                "boolean": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/boolean"}
                }
            },
            "additionalProperties": False
        },
        "event_data": {
            "description": "Additional data to describe attributes of the event.",
            "type": "object",
            "properties": {
                "num": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/num"}
                },
                "vec": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/vec"}
                },
                "text": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/text"}
                },
                "boolean": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/boolean"}
                }
            },
            "additionalProperties": False
        },
        "context_data": {
            "description": "Additional data to describe attributes of the context.",
            "type": "object",
            "properties": {
                "num": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/num"}
                },
                "vec": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/vec"}
                },
                "text": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/text"}
                },
                "boolean": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/boolean"}
                }
            },
            "additionalProperties": False
        },
        "object_data": {
            "description": "Additional data to describe attributes of the object.",
            "type": "object",
            "properties": {
                "bbox": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/bbox"}
                },
                "rbbox": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/rbbox"}
                },
                "num": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/num"}
                },
                "vec": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/vec"}
                },
                "text": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/text"}
                },
                "boolean": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/boolean"}
                },
                "poly2d": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/poly2d"}
                },
                "poly3d": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/poly3d"}
                },
                "cuboid": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/cuboid"}
                },
                "image": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/image"}
                },
                "mat": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/mat"}
                },
                "binary": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/binary"}
                },
                "point2d": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/point2d"}
                },
                "point3d": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/point3d"}
                },
                "mesh": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/mesh"}
                },
                "line_reference": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/line_reference"}
                },
                "area_reference": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/area_reference"}
                }
            },
            "additionalProperties": False
        },
        "coordinate_system": {
            "description": "A coordinate system is a 3D reference frame. Spatial information of objects and their "
                           "can be defined with respect to coordinate systems.",
            "properties": {
                "type": {"type": "string"},
                "parent": {"type": "string"},
                "children": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "pose_wrt_parent": {"$ref": "#/definitions/transform_data"},
                "uid": {"type": "string"}
            },
            "required": ["type", "parent"],
            "additionalProperties": True
        },
        "transform": {
            "type": "object",
            "properties": {
                "src": {"type": "string"},
                "dst": {"type": "string"},
                "transform_src_to_dst": {"$ref": "#/definitions/transform_data"}
            },
            "required": ["src", "dst", "transform_src_to_dst"],
            "additionalProperties": True
        },
        "transform_data": {
            "oneOf": [
                {
                    "type": "object",
                    "properties": {
                        "matrix4x4": {
                            "description": "It is a 4x4 homogeneous matrix, to enable transform from"
                                    "3D Cartersian Systems easily. Note that the pose_child_wrt_parent_4x4 is"
                                    "the transform_child_to_parent_4x4:"
                                    "X_child = (pose_child_wrt_parent_4x4)^-1 * X_parent"
                                    "X_parent = transform_child_to_child_4x4 * X_child.",
                            "type": "array",
                            "items": {"type": "number"},
                            "example": [1.0, 0.0, 0.0, 10.0,
                                        0.0, 1.0, 0.0, 5.0,
                                        0.0, 0.0, 1.0, 1.0,
                                        0.0, 0.0, 0.0, 1.0]
                        },
                    },
                    "required": ["matrix4x4"],
                    "additionalProperties": False
                },
                {
                    "description": "A transform can be defined with a quaternion (x, y, z, w) that encondes the "
                                   "rotation of a coordinate system with respect to another, "
                                   "and a translation (x, y, z)",
                    "type": "object",
                    "properties": {
                        "quaternion": {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 4,
                            "maxItems": 4
                        },
                        "translation": {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 3,
                            "maxItems": 3
                        }
                    },
                    "required": ["quaternion", "translation"],
                    "additionalProperties": False
                },
                {
                    "type": "object",
                    "properties": {
                        "euler_angles": {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 3,
                            "maxItems": 3
                        },
                        "translation": {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 3,
                            "maxItems": 3
                        },
                        "sequence": {"type": "string"}
                    },
                    "required": ["euler_angles", "translation"],
                    "additionalProperties": False
                }
            ]
        },
        "stream": {
            "description": "A stream describes the source of a data sequence, usually a sensor.",
            "type": "object",
            "properties": {
                "description": {"type": "string"},
                "stream_properties": {"$ref": "#/definitions/stream_properties"},
                "type": {
                    "type": "string",
                    "enum": ["camera", "lidar", "radar", "gps_imu", "other"]
                },
                "uri": {"type": "string"},
            },
            'additionalProperties': False
        },
        "stream_properties": {
            "type": "object",
            "oneOf": [{
                "intrinsics_pinhole": {
                    "type": "object",
                    "properties": {
                        "width_px": {"type": "integer"},
                        "height_px": {"type": "integer"},
                        "camera_matrix": {
                            "type": "array",
                            "comment": "This is a 3x4 camera matrix which projects  "
                                       "3D homogeneous points (4x1) from a sensor coordinate "
                                       "System into the image plane (3x1)"                                       
                                       "This is the usual K matrix for camera projection (as in OpenCV), but"
                                       "extended from 3x3 to 3x4, to enable its usage to project"
                                       "4x1 homogeneous 3D points defined in the SCS into the ICS."
                                       "The SCS follows as well the usual convention x-to-right, y-down, z-forward:"
                                       "x_ics = camera_matrix * X_scs",
                            "minItems": 12,
                            "maxItems": 12,
                            "items": {"type": "number"},
                            "example": [720.0, 0.0, 320.0, 0.0,
                                        0.0, 720.0, 240.0, 0.0,
                                        0.0, 0.0, 1.0, 0.0]
                        },
                        "distortion_coeffs": {
                            "type": "array",
                            "comment": "This is the array 1xN radial and tangential distortion "
                                       "coefficients. See https://docs.opencv.org/4.2.0/d9/d0c/group__calib3d.html",
                            "minItems": 5,
                            "maxItems": 14,
                            "items": {"type": "number"},
                            "example": [-4.0569640920796241e-01,
                                        1.9116055332155032e-01,
                                        0.0000000000000000000,
                                        0.0000000000000000000,
                                        -4.7033609773998064e-02]
                        }
                    },
                    "additionalProperties": True
                },
                "intrinsics_fisheye": {
                    "type": "object",
                    "properties": {
                        "width_px": {"type": "integer"},
                        "height_px": {"type": "integer"},
                        "fov_deg": {"type": ["number", "null"]},
                        "center_x_px": {"type": ["number", "null"]},
                        "center_y_px": {"type": ["number", "null"]},
                        "radius_x_px": {"type": ["number", "null"]},
                        "radius_y_px": {"type": ["number", "null"]},
                        "lens_coeffs": {
                            "type": "array",
                            "minItems": 4,
                            "maxItems": 4,
                            "items": {"type": "number"}
                        }
                    },
                    "additionalProperties": True
                },
                "intrinsics_custom": {
                    "type": "object"
                }
            }],
            "sync": {
                "description": "This is the sync information for this Stream."
                               "If provided inside a certain frame, it can be used"
                               "to specify timestamps in ISO8601 format,"
                               "and a frame_stream of this stream."
                               "E.g. at openlabel's frame 34, for stream CAM_LEFT, the sync info"
                               "contains timestamp=2020-04-09T04:57:57+00:00,"
                               "and frame_stream=36 (which means that this CAM_LEFT is shifted"
                               "2 frame with respect the openlabel's master frame indexes."
                               "If provided at stream level, it can be used to specify"
                               "a frame shift, e.g. the shift of that stream wrt to the"
                               "master openlabel frame count."
                               "E.g. if the shift is constant for all frames, it is more compact"
                               "to define the frame_shift=2 at stream level.",
                "type": "object",
                "oneOf": [{
                    "properties": {
                        "timestamp": {"type": "string"},
                        "frame_stream": {"type": "integer"},
                    },
                }, {
                    "properties": {
                        "frame_shift": {"type": "integer"}
                    }
                }
                ]
            },
            "additionalProperties": True
        },
        "bbox": {
            "type": "object",
            "description": "A 2D bounding box is defined as a 4-dimensional vector [x, y, w, h], where [x, y] "
                           "is the centre of the bounding box, and [w, h] represent the width (horizontal, "
                           "x-coordinate dimension), and height (vertical, y-coordinate dimension), respectively.",
            "properties": {
                "name": {"type": "string"},
                "coordinate_system": {"type": "string"},
                "val": {
                    "type": "array",
                    "minItems": 4,
                    "maxItems": 4,
                    "items": {"type": "number"}
                },
                "attributes": {"$ref": "#/definitions/attributes"}
            },
            "required": ["name", "val"],
            "additionalProperties": True
        },
        "rbbox": {
            "type": "object",
            "description": "A 2D rotated bounding box is defined as a 5-dimensional vector [x, y, w, h, alpha], where "
                           "[x, y] is the centre of the bounding box, and [w, h] represent the width (horizontal, "
                           "x-coordinate dimension), and height (vertical, y-coordinate dimension), respectively. The "
                           "angle alpha, in radians, represents the rotation of the rotated bounding box, and is "
                           "defined as a right-handed rotation, i.e. positive from x to y axes, and with the origin "
                           "of rotation placed at the center of the bounding box (i.e. [x, y]).",
            "properties": {
                "name": {"type": "string"},
                "coordinate_system": {"type": "string"},
                "val": {
                    "type": "array",
                    "minItems": 5,
                    "maxItems": 5,
                    "items": {"type": "number"}
                },
                "attributes": {"$ref": "#/definitions/attributes"}
            },
            "required": ["name", "val"],
            "additionalProperties": True
        },
        "num": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "coordinate_system": {"type": "string"},
                "val": {"type": "number"},
                "type": {"type": "string", "enum": ["value", "min", "max"]},
                "attributes": {"$ref": "#/definitions/attributes"}
            },
            "required": ["val"],
            "additionalProperties": True
        },
        "text": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "coordinate_system": {"type": "string"},
                "val": {"type": "string"},
                "type": {"type": "string", "enum": ["value"]},
                "attributes": {"$ref": "#/definitions/attributes"}
            },
            "required": ["val"],
            "additionalProperties": True
        },
        "boolean": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "coordinate_system": {"type": "string"},
                "val": {"type": "boolean"},
                "type": {"type": "string", "enum": ["value"]},
                "attributes": {"$ref": "#/definitions/attributes"}
            },
            "required": ["val"],
            "additionalProperties": True
        },
        "cuboid": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "coordinate_system": {"type": "string"},
                "val": {
                    "oneOf": [
                        {
                            "type": "array",
                            "minItems": 9,
                            "maxItems": 10,
                            "items": {"type": "number"}
                        },
                        {
                            "type": "null"
                        }
                    ]
                },
                "attributes": {"$ref": "#/definitions/attributes"}
            },
            "required": ["name", "val"],
            "additionalProperties": True
        },
        "image": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "coordinate_system": {"type": "string"},
                "val": {"type": "string"},
                "mime_type": {"type": "string"},
                "encoding": {"type": "string"},
                "attributes": {"$ref": "#/definitions/attributes"}
            },
            "required": ["name", "val", "mime_type", "encoding"],
            "additionalProperties": True
        },
        "mat": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "coordinate_system": {"type": "string"},
                "val": {
                    "type": "array",
                    "items": {"type": "number"}
                },
                "channels": {"type": "number"},
                "width": {"type": "number"},
                "height": {"type": "number"},
                "data_type": {"type": "string"},
                "attributes": {"$ref": "#/definitions/attributes"}
            },
            "required": ["name", "val", "channels", "width", "height", "data_type"],
            "additionalProperties": True
        },
        "binary": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "coordinate_system": {"type": "string"},
                "val": {"type": "string"},
                "encoding": {"type": "string"},
                "data_type": {"type": "string"},
                "attributes": {"$ref": "#/definitions/attributes"}
            },
            "required": ["name", "val", "encoding", "data_type"],
            "additionalProperties": True
        },
        "vec": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "coordinate_system": {"type": "string"},
                "val": {
                    "type": "array",
                    "items": {
                        "oneOf": [
                            {"type": "number"},
                            {"type": "string"}
                        ]
                    }
                },
                "type": {"type": "string", "enum": ["values", "range"]},
                "attributes": {"$ref": "#/definitions/attributes"}
            },
            "required": ["val"],
            "additionalProperties": True
        },
        "point2d": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "coordinate_system": {"type": "string"},
                "id": {"type": "integer"},
                "val": {
                    "type": "array",
                    "minItems": 2,
                    "maxItems": 2,
                    "items": {"type": "number"}
                },
                "attributes": {"$ref": "#/definitions/attributes"}
            },
            "required": ["name", "val"],
            "additionalProperties": True
        },
        "point3d": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "coordinate_system": {"type": "string"},
                "id": {"type": "integer"},
                "val": {
                    "type": "array",
                    "minItems": 3,
                    "maxItems": 3,
                    "items": {"type": "number"}
                },
                "attributes": {"$ref": "#/definitions/attributes"}
            },
            "required": ["name", "val"],
            "additionalProperties": True
        },
        "poly2d": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "coordinate_system": {"type": "string"},
                "mode": {"type": "string"},
                "closed": {"type": "boolean"},
                "val": {
                    "anyOf": [
                        {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        {
                            "type": "array",
                            "items": {"type": "number"}
                        }
                    ]
                },
                "hierarchy": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "minItems": 4,
                    "maxItems": 4,
                },
                "attributes": {"$ref": "#/definitions/attributes"}
            },
            "required": ["name", "val", "mode", "closed"],
            "additionalProperties": True
        },
        "poly3d": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "coordinate_system": {"type": "string"},
                "closed": {"type": "boolean"},
                "val": {
                    "type": "array",
                    "items": {"type": "number"}
                },
                "attributes": {"$ref": "#/definitions/attributes"}
            },
            "required": ["name", "val", "closed"],
            "additionalProperties": True
        },
        "attributes": {
            "description": "Attributes is the alias of element data that can be nested inside geometric "
                           "object data. "
                           "E.g. A certain bounding box object_data can have attributes related to its "
                           "score, visibility, etc. These values can be nested inside the bounding box as attributes",
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "num": {
                    "type": "array",
                    "items": {
                        "$ref": "#/definitions/num"
                    }
                },
                "vec": {
                    "type": "array",
                    "items": {
                        "$ref": "#/definitions/vec"
                    }
                },
                "boolean": {
                    "type": "array",
                    "items": {
                        "$ref": "#/definitions/boolean"
                    }
                },
                "text": {
                    "type": "array",
                    "items": {
                        "$ref": "#/definitions/text"
                    }
                }
            }
        },
        "mesh": {
            "description": "This is a special type of object data which encodes a point-line-area mesh. "
                           "It is intended to represent 3D meshes, where points, lines and areas composing the mesh "
                           "are interrelated, and can have their own properties",
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "coordinate_system": {"type": "string"},
                "point3d": {
                    "type": "object",
                    "patternProperties": {
                        "^[0-9]+$": {"$ref": "#/definitions/point3d"}
                    },
                    "additionalProperties": False
                },
                "line_reference": {
                    "type": "object",
                    "patternProperties": {
                        "^[0-9]+$": {"$ref": "#/definitions/line_reference"}
                    },
                    "additionalProperties": False
                },
                "area_reference": {
                    "type": "object",
                    "patternProperties": {
                        "^[0-9]+$": {"$ref": "#/definitions/area_reference"}
                    },
                    "additionalProperties": False
                },
                "additionalProperties": True
            }
        },
        "line_reference": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "coordinate_system": {"type": "string"},
                "val": {
                    "type": "array",
                    "items": {"type": "number"},
                    "minItems": 2,
                    "maxItems": 2,
                },
                "reference_type": {"type": "string"},
                "attributes": {"$ref": "#/definitions/attributes"}
            },
            "additionalProperties": True
        },
        "area_reference": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "coordinate_system": {"type": "string"},
                "val": {
                    "type": "array",
                    "items": {"type": "number"},
                },
                "reference_type": {"type": "string"},
                "attributes": {"$ref": "#/definitions/attributes"}
            },
            "additionalProperties": True
        },
    },
    "required": ["openlabel"],
    "additionalProperties": False
}