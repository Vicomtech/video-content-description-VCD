"""
VCD (Video Content Description) library v4.1.0

Project website: http://vcd.vicomtech.org

Copyright (C) 2020, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.1.0.
VCD is distributed under MIT License. See LICENSE.

"""

######################################
# Fully manually writing the schema
######################################
vcd_schema = {
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
                "version": {"type": "string"},
                "name": {"type": "string"},
                "frame_intervals": {
                    "type": "array",
                    "item": {"$ref": "#/definitions/frame_interval"}
                },
                "ontologies": {
                    "type": "object",
                    "patternProperties": {
                        "^[0-9]+$": {"type": "string"},
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
                "objects": {
                    "type": "object",
                    "patternProperties": {
                        "^[0-9]+$": {
                            "$ref": "#/definitions/object"
                        }
                    },
                    "additionalProperties": False
                },
                "actions": {
                    "type": "object",
                    "patternProperties": {
                        "^[0-9]+$": {
                            "$ref": "#/definitions/action"
                        }
                    },
                    "additionalProperties": False
                },
                "events": {
                    "type": "object",
                    "patternProperties": {
                        "^[0-9]+$": {
                            "$ref": "#/definitions/event"
                        }
                    },
                    "additionalProperties": False
                },
                "contexts": {
                    "type": "object",
                    "patternProperties": {
                        "^[0-9]+$": {
                            "$ref": "#/definitions/context"
                        }
                    },
                    "additionalProperties": False
                },
                "relations": {
                    "type": "object",
                    "patternProperties": {
                        "^[0-9]+$": {
                            "$ref": "#/definitions/relation"
                        }
                    },
                    "additionalProperties": False
                },
                "metadata": {"$ref": "#/definitions/metadata"},
            },
            "additionalProperties": False,
            "required": ["version"]
        },
        "frame": {
            "type": "object",
            "properties": {
                "objects": {
                    "type": "object",
                    "patternProperties": {
                        "^[0-9]+$": {"$ref": "#/definitions/object_data"}
                    },
                    "additionalProperties": False
                },
                "events": {
                    "type": "object",
                    "patternProperties": {
                        "^[0-9]+$": {}
                    },
                    "additionalProperties": False
                },
                "actions": {
                    "type": "object",
                    "patternProperties": {
                        "^[0-9]+$": {}
                    },
                    "additionalProperties": False
                },
                "contexts": {
                    "type": "object",
                    "patternProperties": {
                        "^[0-9]+$": {}
                    },
                    "additionalProperties": False
                },
                "relations": {
                    "type": "object",
                    "patternProperties": {
                        "^[0-9]+$": {}
                    },
                    "additionalProperties": False
                },
                "frame_properties": {
                    "description": "These frame_properties include frame-related information,"
                                   "including: stream information, odometry, and timestamping."
                                   "-Timestamps: the field \'timestamp\' can be used to declare a"
                                   "master timestamp for all information within thi frame."
                                   "-Streams: can host information related to specific streams, such"
                                   "as specific timestamps or instanteneous intrinsics."
                                   "-Odometry: it contains ego-motion of the entire scene (i.e."
                                   "the pose of the LCS (Local Coordinate System) wrt to WCS (World"
                                   "Coordinate System).",
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
        "metadata": {
            "type": "object",
            "properties": {
                "streams": {
                    "patternProperties":{
                        "^": {"$ref": "#/definitions/stream"},
                    },
                    "type": "object",
                    "additionalProperties": False
                },
                "properties": {
                    "type": "object",
                    "patternProperties": {
                        "^": {}
                    },
                    "additionalProperties": False
                },
                "annotator": {"type": "string"},
                "comment": {"type": "string"}
            },
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
                "ontology_uid": {"type": "integer"},
                "stream": {"type": "string"},
                "object_data": {"$ref": "#/definitions/object_data"},
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
                "ontology_uid": {"type": "integer"},
                "stream": {"type": "string"}
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
                "ontology_uid": {"type": "integer"},
                "stream": {"type": "string"}
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
                "ontology_uid": {"type": "integer"},
                "stream": {"type": "string"}
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
                "ontology_uid": {"type": "integer"},
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
            "additionalProperties": False
        },
        "rdf_agent": {
            "type": "object",
            "properties": {
                "type": {"type": "string"},
                "uid": {"type": "integer"},
            }
        },
        "object_data": {
            "type": "object",
            "properties": {
                "bbox": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/bbox"}
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
            }
        },
        "stream": {
            "type": "object",
            "description": "A stream describes the source of a data sequence, usually a sensor.",
            "properties": {
                "description": {"type": "string"},
                "stream_properties": {"$ref": "#/definitions/stream_properties"},
                "type": {
                    "type": "string",
                    "enum": ["camera", "lidar", "radar", "gps_imu", "Other"]
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
                            "comment": "This is a 3x4 camera matrix which projects "
                                       "3D homogeneous points (4x1) from Sensor Coordinate "
                                       "System (SCS) into the Image Coordinate Sysmte (ICS),"
                                       "plane points (3x1). "
                                       "This is the usual K matrix for camera projection, but"
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
                    }
                },
                "intrinsics_fisheye": {
                    "type": "object",
                    "properties": {
                        "width_px": {"type": "integer"},
                        "height_px": {"type": "integer"},
                        "fov_def": {"type": "number"},
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
                        "description": "This is the pose of the Sensor Coordinate Sysmte (SCS)"
                                       "defined for this stream (e.g. camera) with respect to"
                                       "the Local Coordinate System (LCS), e.g. the projection"
                                       "in the ground of the middle of rear-axis in a vehicle, "
                                       "as defined in ISO 8855."
                                       "It is a 4x4 homogeneous matrix, to enable transform from"
                                       "LCS to SCS easily. Note that the pose_scs_wrt_lcs_4x4 is"
                                       "the transform_lcs_to_scs_4x4:"
                                       "X_scs = pose_scs_wrt_lcs_4x4 * X_lcs"
                                       "X_scs = transform_lcs_wrt_scs_4x4 * X_lcs",
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
                "description": "This is the sync information for this Stream."
                               "If provided inside a certain frame, it can be used"
                               "to specify timestamps in ISO8601 format,"
                               "and a frame_stream of this stream."
                               "E.g. at vcd's frame 34, for stream CAM_LEFT, the sync info"
                               "contains timestamp=2020-04-09T04:57:57+00:00,"
                               "and frame_stream=36 (which means that this CAM_LEFT is shifted"
                               "2 frame with respect the vcd's master frame indexes."
                               "If provided at stream level, it can be used to specify"
                               "a frame shift, e.g. the shift of that stream wrt to the"
                               "master vcd frame count."                              
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
            "additionalProperties": False
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
            "additionalProperties": False
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
            "additionalProperties": False
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
            "additionalProperties": False
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
            "additionalProperties": False
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
            "additionalProperties": False
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
            "additionalProperties": False
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
            "additionalProperties": False
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
            "additionalProperties": False
        },
        "point2d": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "stream": {"type": "string"},
                "val": {
                    "type": "array",
                    "minItems": 2,
                    "maxItems": 2,
                    "items": {"type": "number"}
                },
                "attributes": {"$ref": "#/definitions/attributes"}
            },
            "required": ["name", "val"],
            "additionalProperties": False
        },
        "point3d": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "stream": {"type": "string"},
                "val": {
                    "type": "array",
                    "minItems": 3,
                    "maxItems": 3,
                    "items": {"type": "number"}
                },
                "attributes": {"$ref": "#/definitions/attributes"}
            },
            "required": ["name", "val"],
            "additionalProperties": False
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
            "additionalProperties": False
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
            "additionalProperties": False
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
                "stream": {"type": "string"},
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
                "additionalProperties": False
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
                "attributes": {"$ref": "#/definitions/attributes"},
                "additionalProperties": False
            }
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
                "attributes": {"$ref": "#/definitions/attributes"},
                "additionalProperties": False
            }
        },

    },
    "required": ["vcd"],
    "additionalProperties": False
}