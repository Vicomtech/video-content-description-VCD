/*
VCD (Video Content Description) library v4.3.0

Project website: http://vcd.vicomtech.org

Copyright (C) 2020, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a library to create and manage VCD content version 4.3.0.
VCD is distributed under MIT License. See LICENSE.

*/

/*######################################
# Fully manually writing the schema
######################################*/
export const vcd_schema_version = "4.3.0"
export const vcd_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "vcd": {"$ref": "#/definitions/vcd"}
    },
    "definitions": {
        "vcd": {
            "type": "object",
            "description": "This is the root VCD element.",
            "properties": {
                "schema_version": {"type": "string", "enum": [vcd_schema_version]},
                "file_version": {"type": "string"},
                "name": {"type": "string"},
                "frame_intervals": {
                    "type": "array",
                    "item": {"$ref": "#/definitions/frame_interval"}
                },
                "ontologies": {
                    "type": "object",
                    "patternProperties": {
                        "^([0-9]+|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$": {"type": "string"},
                    },
                    "additionalProperties": false
                },
                "frames": {
                    "type": "object",
                    "patternProperties": {
                        "^[0-9]+$": {
                            "$ref": "#/definitions/frame"
                        }
                    },
                    "additionalProperties": false
                },
                "objects": {
                    "type": "object",
                    "patternProperties": {
                        "^([0-9]+|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$": {
                            "$ref": "#/definitions/object"
                        }
                    },
                    "additionalProperties": false
                },
                "actions": {
                    "type": "object",
                    "patternProperties": {
                        "^([0-9]+|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$": {
                            "$ref": "#/definitions/action"
                        }
                    },
                    "additionalProperties": false
                },
                "events": {
                    "type": "object",
                    "patternProperties": {
                        "^([0-9]+|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$": {
                            "$ref": "#/definitions/event"
                        }
                    },
                    "additionalProperties": false
                },
                "contexts": {
                    "type": "object",
                    "patternProperties": {
                        "^([0-9]+|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$": {
                            "$ref": "#/definitions/context"
                        }
                    },
                    "additionalProperties": false
                },
                "relations": {
                    "type": "object",
                    "patternProperties": {
                        "^([0-9]+|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$": {
                            "$ref": "#/definitions/relation"
                        }
                    },
                    "additionalProperties": false
                },
                "metadata": {"$ref": "#/definitions/metadata"},
            },
            "additionalProperties": false,
            "required": ["schema_version"]
        },
        "frame": {
            "type": "object",
            "properties": {
                "objects": {
                    "type": "object",
                    "patternProperties": {
                        "^([0-9]+|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$": {
                            "type": "object",
                            "properties": {
                                "object_data": {"$ref": "#/definitions/object_data"},
                            },
                            "additionalProperties": false
                        }
                    },
                    "additionalProperties": false
                },
                "events": {
                    "type": "object",
                    "patternProperties": {
                        "^([0-9]+|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$": {
                            "type": "object",
                            "properties": {
                                "event_data": {"$ref": "#/definitions/event_data"},
                            },
                            "additionalProperties": false
                        }
                    },
                    "additionalProperties": false
                },
                "actions": {
                    "type": "object",
                    "patternProperties": {
                        "^([0-9]+|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$": {
                            "type": "object",
                            "properties": {
                                "action_data": {"$ref": "#/definitions/action_data"},
                            },
                            "additionalProperties": false
                        }
                    },
                    "additionalProperties": false
                },
                "contexts": {
                    "type": "object",
                    "patternProperties": {
                        "^([0-9]+|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$": {
                            "type": "object",
                            "properties": {
                                "context_data": {"$ref": "#/definitions/context_data"},
                            },
                            "additionalProperties": false
                        }
                    },
                    "additionalProperties": false
                },
                "relations": {
                    "type": "object",
                    "patternProperties": {
                        "^([0-9]+|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$": {}
                    },
                    "additionalProperties": false
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
                            "additionalProperties": false
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
                    "additionalProperties": true
                }
            },
            "additionalProperties": false
        },
        "frame_interval": {
            "type": "object",
            "properties": {
                "frame_start": {"type": "integer"},
                "frame_end": {"type": "integer"}
            },
            "additionalProperties": false
        },
        "metadata": {
            "type": "object",
            "properties": {
                "streams": {
                    "patternProperties":{
                        "^": {"$ref": "#/definitions/stream"},
                    },
                    "type": "object",
                    "additionalProperties": false
                },
                "properties": {
                    "type": "object",
                    "patternProperties": {
                        "^": {}
                    },
                    "additionalProperties": false
                },
                "annotator": {"type": "string"},
                "comment": {"type": "string"}
            },
            "additionalProperties": false
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
                "stream": {"type": "string"},
                "object_data": {"$ref": "#/definitions/object_data"},
                "object_data_pointers": {"$ref": "#/definitions/element_data_pointers"}
            },
            "required": ["name", "type"],
            "additionalProperties": false
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
                "stream": {"type": "string"},
                "action_data": {"$ref": "#/definitions/action_data"},
                "action_data_pointers": {"$ref": "#/definitions/element_data_pointers"}
            },
            "required": ["name", "type"],
            "additionalProperties": false
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
                "stream": {"type": "string"},
                "event_data": {"$ref": "#/definitions/event_data"},
                "event_data_pointers": {"$ref": "#/definitions/element_data_pointers"}
            },
            "required": ["name", "type"],
            "additionalProperties": false
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
                "stream": {"type": "string"},
                "context_data": {"$ref": "#/definitions/context_data"},
                "context_data_pointers": {"$ref": "#/definitions/element_data_pointers"}
            },
            "required": ["name", "type"],
            "additionalProperties": false
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
                "stream": {"type": "string"},
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
            "additionalProperties": false
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
            "additionalProperties": false
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
                    "enum": ["bbox", "rbbox", "num", "text", "boolean", "poly2d", "poly3d", "cuboid", "image", "mat", "binary", "point2d", "point3d", "vec", "line_reference", "area_reference", "mesh"]
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
            "additionalProperties": false
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
            "additionalProperties": false
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
            "additionalProperties": false
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
            "additionalProperties": false
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
            'additionalProperties': false
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
                                       System (SCS) into the Image Coordinate Sysmte (ICS),\
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
                    }
                },
                "intrinsics_fisheye": {
                    "type": "object",
                    "properties": {
                        "width_px": {"type": "integer"},
                        "height_px": {"type": "integer"},
                        "fov_deg": {"type": "number"},
                        "center_x_px": {"type": "number"},
                        "center_y_px": {"type": "number"},
                        "radius_x_px": {"type": "number"},
                        "radius_y_px": {"type": "number"},
                        "lens_coeffs": {
                            "type": "array",
                            "minItems": 4,
                            "maxItems": 4,
                            "items": {"type": "number"}
                        }
                    }
                }
            }],
            "extrinsics": {
                "type": "object",
                "properties": {
                    "pose_scs_wrt_lcs_4x4": {
                        "description": "This is the pose of the Sensor Coordinate Sysmte (SCS)\
                                       defined for this stream (e.g. camera) with respect to\
                                       the Local Coordinate System (LCS), e.g. the projection\
                                       in the ground of the middle of rear-axis in a vehicle, \
                                       as defined in ISO 8855.\
                                       It is a 4x4 homogeneous matrix, to enable transform from\
                                       LCS to SCS easily. Note that the pose_scs_wrt_lcs_4x4 is\
                                       the transform_lcs_to_scs_4x4:\
                                       X_scs = pose_scs_wrt_lcs_4x4 * X_lcs\
                                       X_scs = transform_lcs_wrt_scs_4x4 * X_lcs",
                        "type": "array",
                        "minItems": 16,
                        "maxItems": 16,
                        "items": {"type": "number"},
                        "example": [1.0, 0.0, 0.0, 10.0,
                                    0.0, 1.0, 0.0, 5.0,
                                    0.0, 0.0, 1.0, 1.0,
                                    0.0, 0.0, 0.0, 1.0]
                    }
                }
            },
            "sync": {
                "description": "This is the sync information for this Stream.\
                               If provided inside a certain frame, it can be used\
                               to specify timestamps in ISO8601 format,\
                               and a frame_stream of this stream.\
                               E.g. at vcd's frame 34, for stream CAM_LEFT, the sync info\
                               contains timestamp=2020-04-09T04:57:57+00:00,\
                               and frame_stream=36 (which means that this CAM_LEFT is shifted\
                               2 frame with respect the vcd's master frame indexes.\
                               If provided at stream level, it can be used to specify\
                               a frame shift, e.g. the shift of that stream wrt to the\
                               master vcd frame count.\
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
            "additionalProperties": true
        },
        "bbox": {
            "type": "object",
            "description": "A 2D bounding box is defined as a 4-dimensional vector [x, y, w, h], where [x, y] is the centre of the bounding box, and\
                            [w, h] represent the width (horizontal, x-coordinate dimension), and height (vertical, y-coordinate dimension), respectively.",
            "properties": {
                "name": {"type": "string"},
                "stream": {"type": "string"},
                "val": {
                    "type": "array",
                    "minItems": 4,
                    "maxItems": 4,
                    "items": {"type": "number"}
                },
                "attributes": {"$ref": "#/definitions/attributes"}
            },
            "required": ["name", "val"],
            "additionalProperties": false
        },
        "rbbox": {
            "type": "object",
            "description": "A 2D rotated bounding box is defined as a 5-dimensional vector [x, y, w, h, alpha], where [x, y] is the centre of the bounding box, and\
                            [w, h] represent the width (horizontal, x-coordinate dimension), and height (vertical, y-coordinate dimension), respectively.\
                            The angle alpha, in radians, represents the rotation of the rotated bounding box, and is defined as a right-handed rotation, i.e. positive from x to y axes, \
                            and with the origin of rotation placed at the center of the bounding box (i.e. [x, y]).",
            "properties": {
                "name": {"type": "string"},
                "stream": {"type": "string"},
                "val": {
                    "type": "array",
                    "minItems": 5,
                    "maxItems": 5,
                    "items": {"type": "number"}
                },
                "attributes": {"$ref": "#/definitions/attributes"}
            },
            "required": ["name", "val"],
            "additionalProperties": false
        },
        "num": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "stream": {"type": "string"},
                "val": {"type": "number"},
                "attributes": {"$ref": "#/definitions/attributes"}
            },
            "required": ["name", "val"],
            "additionalProperties": false
        },
        "text": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "stream": {"type": "string"},
                "val": {"type": "string"},
                "attributes": {"$ref": "#/definitions/attributes"}
            },
            "required": ["name", "val"],
            "additionalProperties": false
        },
        "boolean": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "stream": {"type": "string"},
                "val": {"type": "boolean"},
                "attributes": {"$ref": "#/definitions/attributes"}
            },
            "required": ["name", "val"],
            "additionalProperties": false
        },
        "cuboid": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "stream": {"type": "string"},
                "val": {
                    "type": "array",
                    "minItems": 9,
                    "maxItems": 9,
                    "items": {"type": "number"}
                },
                "attributes": {"$ref": "#/definitions/attributes"}
            },
            "required": ["name", "val"],
            "additionalProperties": false
        },
        "image": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "stream": {"type": "string"},
                "val": {"type": "string"},
                "mime_type": {"type": "string"},
                "encoding": {"type": "string"},
                "attributes": {"$ref": "#/definitions/attributes"}
            },
            "required": ["name", "val", "mime_type", "encoding"],
            "additionalProperties": false
        },
        "mat": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "stream": {"type": "string"},
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
            "additionalProperties": false
        },
        "binary": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "stream": {"type": "string"},
                "val": {"type": "string"},
                "encoding": {"type": "string"},
                "data_type": {"type": "string"},
                "attributes": {"$ref": "#/definitions/attributes"}
            },
            "required": ["name", "val", "encoding", "data_type"],
            "additionalProperties": false
        },
        "vec": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "stream": {"type": "string"},
                "val": {
                    "type": "array",
                    "item": {"type": "number"}
                },
                "attributes": {"$ref": "#/definitions/attributes"}
            },
            "required": ["name", "val"],
            "additionalProperties": false
        },
        "point2d": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "stream": {"type": "string"},
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
            "additionalProperties": false
        },
        "point3d": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "stream": {"type": "string"},
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
            "additionalProperties": false
        },
        "poly2d": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "stream": {"type": "string"},
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
            "additionalProperties": false
        },
        "poly3d": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "stream": {"type": "string"},
                "closed": {"type": "boolean"},
                "val": {
                    "type": "array",
                    "items": {"type": "number"}
                },
                "attributes": {"$ref": "#/definitions/attributes"}
            },
            "required": ["name", "val", "closed"],
            "additionalProperties": false
        },
        "attributes": {
            "type": "object",
            "additionalProperties": false,
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
                "stream": {"type": "string"},
                "point3d": {
                    "type": "object",
                    "patternProperties": {
                        "^[0-9]+$": {"$ref": "#/definitions/point3d"}
                    },
                    "additionalProperties": false
                },
                "line_reference": {
                    "type": "object",
                    "patternProperties": {
                        "^[0-9]+$": {"$ref": "#/definitions/line_reference"}
                    },
                    "additionalProperties": false
                },
                "area_reference": {
                    "type": "object",
                    "patternProperties": {
                        "^[0-9]+$": {"$ref": "#/definitions/area_reference"}
                    },
                    "additionalProperties": false
                },
                "additionalProperties": false
            }
        },
        "line_reference": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "stream": {"type": "string"},
                "val": {
                    "type": "array",
                    "items": {"type": "number"},
                    "minItems": 2,
                    "maxItems": 2,
                },
                "reference_type": {"type": "string"},
                "attributes": {"$ref": "#/definitions/attributes"}
            },
            "additionalProperties": false
        },
        "area_reference": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "stream": {"type": "string"},
                "val": {
                    "type": "array",
                    "items": {"type": "number"},
                },
                "reference_type": {"type": "string"},
                "attributes": {"$ref": "#/definitions/attributes"}
            },
            "additionalProperties": false
        },

    },
    "required": ["vcd"],
    "additionalProperties": false
}