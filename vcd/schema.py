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
openlabel_schema_version = "0.2.0"
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
                "tags": {"$ref": "#/definitions/tags"},
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
            "type": "object",
            "patternProperties": {
                "^(-?[0-9]+|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$":
                    {"type": "string"},
            },
            "additionalProperties": False
        },
        "resources": {
            "type": "object",
            "patternProperties": {
                "^(-?[0-9]+|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$":
                    {"type": "string"},
            },
            "additionalProperties": False
        },
        "resource_uid": {
            "type": "object",
            "patternProperties": {
                "^(-?[0-9]+|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$": {
                    "type": "string"
                }
            },
        },
        "tags": {
            "type": "object",
            "properties": {
                "administrative": {"type": "object"},
                "odd": {"type": "object"},
                "behaviour": {"type": "object"},
                "custom": {"type": "object"}
            },
            "additionalProperties": True,
        },
        "frame": {
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
                    "description": "These frame_properties include frame-related information,\
                                   including: stream information, odometry, and timestamping.\
                                   -Timestamps: the field \'timestamp\' can be used to declare a\
                                   master timestamp for all information within thi frame.\
                                   -Streams: can host information related to specific streams, such\
                                   as specific timestamps or instantaneous intrinsics.\
                                   -Odometry: it contains ego-motion of the entire scene (i.e.\
                                   the pose of the LCS (Local Coordinate System) wrt to WCS (World\
                                   Coordinate System).",
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
                        "odometry": {
                            "type": "object",
                            "properties": {
                                "comment": {"type": "string"},
                                "pose_lcs_wrt_wcs_4x4": {
                                    "type": "array",
                                    "minItems": 16,
                                    "maxItems": 16,
                                    "items": {"type": "number"}
                                },
                            }
                        }
                    },
                    "additionalProperties": True
                }
            },
            "additionalProperties": False
        },
        "frame_interval": {
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
            "type": "object",
            "properties": {
                "frame_intervals": {
                    "type": "array",
                    "item": {"$ref": "#/definitions/frame_interval"}
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
            "type": "object",
            "properties": {
                "frame_intervals": {
                    "type": "array",
                    "item": {"$ref": "#/definitions/frame_interval"}
                },
                "name": {"type": "string"},
                "type": {"type": "string"},
                "ontology_uid": {"type": "string"},
                "resource_uid": {"type": "string"},
                "coordinate_system": {"type": "string"},
                "action_data": {"$ref": "#/definitions/action_data"},
                "action_data_pointers": {"$ref": "#/definitions/element_data_pointers"}
            },
            "required": ["name", "type"],
            "additionalProperties": False
        },
        "event": {
            "type": "object",
            "properties": {
                "frame_intervals": {
                    "type": "array",
                    "item": {"$ref": "#/definitions/frame_interval"}
                },
                "name": {"type": "string"},
                "type": {"type": "string"},
                "ontology_uid": {"type": "string"},
                "resource_uid": {"type": "string"},
                "coordinate_system": {"type": "string"},
                "event_data": {"$ref": "#/definitions/event_data"},
                "event_data_pointers": {"$ref": "#/definitions/element_data_pointers"}
            },
            "required": ["name", "type"],
            "additionalProperties": False
        },
        "context": {
            "type": "object",
            "properties": {
                "frame_intervals": {
                    "type": "array",
                    "item": {"$ref": "#/definitions/frame_interval"}
                },
                "name": {"type": "string"},
                "type": {"type": "string"},
                "ontology_uid": {"type": "string"},
                "resource_uid": {"type": "string"},
                "coordinate_system": {"type": "string"},
                "context_data": {"$ref": "#/definitions/context_data"},
                "context_data_pointers": {"$ref": "#/definitions/element_data_pointers"}
            },
            "required": ["name", "type"],
            "additionalProperties": False
        },
        "relation": {
            "type": "object",
            "properties": {
                "frame_intervals": {
                    "type": "array",
                    "item": {"$ref": "#/definitions/frame_interval"}
                },
                "name": {"type": "string"},
                "type": {"type": "string"},
                "ontology_uid": {"type": "string"},
                "resource_uid": {"type": "string"},
                "rdf_objects": {
                    "type": "array",
                    "item": {"$ref": "#/definitions/rdf_agent"}
                },
                "rdf_subjects": {
                    "type": "array",
                    "item": {"$ref": "#/definitions/rdf_agent"}
                },
            },
            "required": ["name", "type", "rdf_objects", "rdf_subjects"],
            "additionalProperties": False
        },
        "rdf_agent": {
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
            "type": "object",
            "properties": {
                "frame_intervals": {
                    "type": "array",
                    "item": {"$ref": "#/definitions/frame_interval"}
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
        "action_data": {
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
            "description": "A coordinate_system is a 3D reference frame that act as placeholder"
                           "of annotations.",
            "properties": {
                "type": {"type": "string"},
                "parent": {"type": "string"},
                "children": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "pose_wrt_parent": {
                    "oneOf": [
                        {
                            "description": "It is a 4x4 homogeneous matrix, to enable transform from\
                                    3D Cartersian Systems easily. Note that the pose_children_wrt_parent_4x4 is\
                                    the transform_parent_to_child_4x4:\
                                    X_child = pose_child_wrt_parent_4x4 * X_parent\
                                    X_child = transform_parent_to_child_4x4 * X_parent."
                                   "NOTE: For camera or other projective systems (3D->2D) this pose is the extrinsic"
                                   "calibration, the projection itself is encoded as the intrinsic information, which"
                                   "is labeled inside the corresponding stream.",
                            "type": "array",
                            "items": {"type": "number"},
                            "example": [1.0, 0.0, 0.0, 10.0,
                                        0.0, 1.0, 0.0, 5.0,
                                        0.0, 0.0, 1.0, 1.0,
                                        0.0, 0.0, 0.0, 1.0]},
                        {
                            "type": "object",
                            "description": "A pose can be expressed in several other forms, e.g. with a rotation\
                                           and translation vector"
                        }
                    ]
                },
                "uid": {"type": "string"}
            },
            "required": ["type", "parent"],
            "additionalProperties": False
        },
        "stream": {
            "type": "object",
            "description": "A stream describes the source of a data sequence, usually a sensor.",
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
                            "comment": "This is a 3x4 camera matrix which projects  \
                                       3D homogeneous points (4x1) from Sensor Coordinate \
                                       System (SCS) into the Image Coordinate System (ICS),\
                                       plane points (3x1). \
                                       This is the usual K matrix for camera projection, but\
                                       extended from 3x3 to 3x4, to enable its usage to project\
                                       4x1 homogeneous 3D points defined in the SCS into the ICS.\
                                       The SCS follows as well the usual convention x-to-right, y-down, z-forward:\
                                       x_ics = camera_matrix * X_scs",
                            "minItems": 12,
                            "maxItems": 12,
                            "items": {"type": "number"},
                            "example": [720.0, 0.0, 320.0, 0.0,
                                        0.0, 720.0, 240.0, 0.0,
                                        0.0, 0.0, 1.0, 0.0]
                        },
                        "distortion_coeffs": {
                            "type": "array",
                            "comment": "This is the array 1xN radial and tangential distortion \
                                       coefficients. See https://docs.opencv.org/4.2.0/d9/d0c/group__calib3d.html",
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
                "description": "This is the sync information for this Stream.\
                               If provided inside a certain frame, it can be used\
                               to specify timestamps in ISO8601 format,\
                               and a frame_stream of this stream.\
                               E.g. at openlabel's frame 34, for stream CAM_LEFT, the sync info\
                               contains timestamp=2020-04-09T04:57:57+00:00,\
                               and frame_stream=36 (which means that this CAM_LEFT is shifted\
                               2 frame with respect the openlabel's master frame indexes.\
                               If provided at stream level, it can be used to specify\
                               a frame shift, e.g. the shift of that stream wrt to the\
                               master openlabel frame count.\
                               E.g. if the shift is constant for all frames, it is more compact\
                               to define the frame_shift=2 at stream level.",
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
            "description": "A 2D bounding box is defined as a 4-dimensional vector [x, y, w, h], where [x, y] is the centre of the bounding box, and\
                            [w, h] represent the width (horizontal, x-coordinate dimension), and height (vertical, y-coordinate dimension), respectively.",
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
                "attributes": {"$ref": "#/definitions/attributes"}
            },
            "required": ["name", "val"],
            "additionalProperties": True
        },
        "text": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "coordinate_system": {"type": "string"},
                "val": {"type": "string"},
                "attributes": {"$ref": "#/definitions/attributes"}
            },
            "required": ["name", "val"],
            "additionalProperties": True
        },
        "boolean": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "coordinate_system": {"type": "string"},
                "val": {"type": "boolean"},
                "attributes": {"$ref": "#/definitions/attributes"}
            },
            "required": ["name", "val"],
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
                    "item": {"type": "number"}
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
                    "item": {
                        "oneOf": [
                            {"type": "number"},
                            {"type": "string"}
                        ]
                    }
                },
                "attributes": {"$ref": "#/definitions/attributes"}
            },
            "required": ["name", "val"],
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