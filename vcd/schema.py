"""
VCD (Video Content Description) library v4.0.0

Project website: http://vcd.vicomtech.org

Copyright (C) 2020, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.0.0.
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
                    "type": "object",
                    "properties": {
                        "streams": {
                            "type": "object",
                            "patternProperties": {
                                "^": {"$ref": "#/definitions/stream"}
                            },
                            "additionalProperties": False
                        },
                        "properties": {
                            "type": "object",
                            "patternProperties": {
                                "^": {}
                            },
                            "additionalProperties": False
                        }
                    },
                    "additionalProperties": False
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
            "properties": {
                "description": {"type": "string"},
                "stream_properties": {"$ref": "#/definitions/stream_properties"},
                "type": {"type": "string"},
                "uri": {"type": "string"},
            },
            'additionalProperties': False
        },
        "stream_properties": {
            "type": "object",
            "patternProperties": {
                "^": {}
            },
            "additionalProperties": False
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