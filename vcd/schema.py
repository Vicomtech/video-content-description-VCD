"""
VCD (Video Content Description) library v5.0.1

Project website: http://vcd.vicomtech.org

Copyright (C) 2021, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 5.0.1.
VCD is distributed under MIT License. See LICENSE.

"""

######################################
# Fully manually writing the schema
######################################
from builtins import type

openlabel_schema_version = "1.0.0"
openlabel_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "openlabel": {"$ref": "#/definitions/openlabel"}
    },
    "definitions": {
        "openlabel": {
            "type": "object",
            "description": "The OpenLABEL root JSON object, which contains all other JSON objects.",
            "properties": {
                "metadata": {"$ref": "#/definitions/metadata"},
                "ontologies": {"$ref": "#/definitions/ontologies"},
                "resources": {"$ref": "#/definitions/resources"},
                "tags": {
                    "description": "This is the JSON object of tags. Tag keys are strings containing numerical UIDs or 32 bytes UUIDs.",
                    "type": "object",
                    "patternProperties": {
                        "^(-?[0-9]+|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$": {
                            "$ref": "#/definitions/tag"
                        }
                    },
                    "additionalProperties": False
                },
                "frames": {
                    "description": "This is the JSON object of frames that contain the dynamic (time-wise) annotations. Keys are strings containing numerical frame identifiers (denoted as master frame numbers).",
                    "type": "object",
                    "patternProperties": {
                        "^[0-9]+$": {
                            "$ref": "#/definitions/frame"
                        }
                    },
                    "additionalProperties": False
                },
                "frame_intervals": {
                    "description": "This is an array of frame intervals.",
                    "type": "array",
                    "item": {"$ref": "#/definitions/frame_interval"}
                },
                "objects": {
                    "description": "This is the JSON object of OpenLABEL objects. Object keys are strings containing numerical UIDs or 32 bytes UUIDs.",
                    "type": "object",
                    "patternProperties": {
                        "^(-?[0-9]+|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$": {
                            "$ref": "#/definitions/object"
                        }
                    },
                    "additionalProperties": False
                },
                "actions": {
                    "description": "This is the JSON object of OpenLABEL actions. Action keys are strings containing numerical UIDs or 32 bytes UUIDs.",
                    "type": "object",
                    "patternProperties": {
                        "^(-?[0-9]+|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$": {
                            "$ref": "#/definitions/action"
                        }
                    },
                    "additionalProperties": False
                },
                "events": {
                    "description": "This is the JSON object of OpenLABEL events. Event keys are strings containing numerical UIDs or 32 bytes UUIDs.",
                    "type": "object",
                    "patternProperties": {
                        "^(-?[0-9]+|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$": {
                            "$ref": "#/definitions/event"
                        }
                    },
                    "additionalProperties": False
                },
                "contexts": {
                    "description": "This is the JSON object of OpenLABEL contexts. Context keys are strings containing numerical UIDs or 32 bytes UUIDs.",
                    "type": "object",
                    "patternProperties": {
                        "^(-?[0-9]+|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$": {
                            "$ref": "#/definitions/context"
                        }
                    },
                    "additionalProperties": False
                },
                "relations": {
                    "description": "This is the JSON object of OpenLABEL relations. Relation keys are strings containing numerical UIDs or 32 bytes UUIDs.",
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
            "description": "This JSON object contains information (metadata) about the annotation file itself including the schema_version, file_version, annotator, etc.",
            "type": "object",
            "properties": {
                "schema_version": {
                        "description": "Version number of the OpenLABEL schema this annotation JSON object follows.",
                        "type": "string", 
                        "enum": [openlabel_schema_version]
                    },
                "file_version": {
                    "description": "Version number of the OpenLABEL annotation content.",
                    "type": "string"
                    },
                "name": {
                    "description": "Name of the OpenLABEL annotation content.",
                    "type": "string"
                    },
                "annotator": {
                    "description": "Name or description of the annotator that created the annotations.",
                    "type": "string"
                    },
                "comment": {
                    "description": "Additional information or description about the annotation content.",
                    "type": "string"
                    },
            },
            "additionalProperties": True,
            "required": ["schema_version"]
        },
        "ontologies": {
            "description": "This is the JSON object of OpenLABEL ontologies. Ontology keys are strings containing numerical UIDs or 32 bytes UUIDs. Ontology values can be any of: strings (e.g. encoding a URI), or JSON objects containing a URI string, and optional lists of included and excluded terms.",
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
                                "boundary_list": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "boundary_mode": {
                                    "type": "string",
                                    "enum": ["include", "exclude"]
                                }
                            },
                            "additionalProperties": True,
                            "required": ["uri"],
                            "dependencies": {
                                "boundary_list": {"required": ["boundary_mode"] }
                            }
                        }]
                    },
            },
            "additionalProperties": False
        },
        "resources": {
            "description": "This is the JSON object of OpenLABEL resources. Resource keys are strings containing numerical UIDs or 32 bytes UUIDs. Resource values are strings that describe an external resource (e.g. file name, URLs) that might be used to link data of this OpenLABEL annotation content with external existing content.",
            "type": "object",
            "patternProperties": {
                "^(-?[0-9]+|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$":
                    {"type": "string"},
            },
            "additionalProperties": False
        },
        "resource_uid": {
            "description": "This is a JSON object that contains links to external resources. Resource_uid keys are strings containing numerical UIDs or 32 bytes UUIDs. Resource_uid values are strings describing the identifier of the element in the external resource.",
            "type": "object",
            "patternProperties": {
                "^(-?[0-9]+|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$": {
                    "type": "string"
                }
            },
        },
        "tag": {
            "description": "A tag is a special type of label that can be attached to any type of content, "
                           "such as images, data containers, folders, etc. In OpenLABEL its main purpose is to "
                           "allow adding metadata to scenario descriptions.",
            "type": "object",
            "properties": {
                "type": {
                        "description": "The type of a tag defines the class the tag corresponds to.",
                        "type": "string"
                    },
                "tag_data": {"$ref": "#/definitions/tag_data"},
                "ontology_uid": {
                        "description": "This is the UID of the ontology where the type of this tag is defined.",
                        "type": "string"
                    },
                "resource_uid": {"$ref": "#/definitions/resource_uid"},
            },
            "additionalProperties": True,
            "required": ["type"]
        },
        "frame": {
            "description": "A frame is a container of dynamic (time-wise) information.",
            "type": "object",
            "properties": {
                "objects": {
                    "description": "This is a JSON object that contains dynamic information of OpenLABEL objects. Object keys are strings containing numerical UIDs or 32 bytes UUIDs. Object values may contain an \"object_data\" JSON object.",
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
                    "description": "This is a JSON object that contains dynamic information of OpenLABEL events. Event keys are strings containing numerical UIDs or 32 bytes UUIDs. Event values may contain an \"event_data\" JSON object.",
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
                    "description": "This is a JSON object that contains dynamic information of OpenLABEL actions. Action keys are strings containing numerical UIDs or 32 bytes UUIDs. Action values may contain an \"action_data\" JSON object.",
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
                    "description": "This is a JSON object that contains dynamic information of OpenLABEL contexts. Context keys are strings containing numerical UIDs or 32 bytes UUIDs. Context values may contain an \"context_data\" JSON object.",
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
                    "description": "This is a JSON object that contains dynamic information of OpenLABEL relations. Relation keys are strings containing numerical UIDs or 32 bytes UUIDs. Relation values are empty. The presence of a key-value relation pair indicates the specified relation exists in this frame.",
                    "type": "object",
                    "patternProperties": {
                        "^(-?[0-9]+|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$": {}
                    },
                    "additionalProperties": False
                },
                "frame_properties": {
                    "description": "This is a JSON object which contains information about this frame.",
                    "type": "object",
                    "properties": {
                        "timestamp": {
                            "description": "The timestamp indicates a time instant as a string or numerical value to describe this frame.",
                            "anyOf": [{"type": "string"}, {"type": "number"}]
                            },
                        "streams": {
                            "description": "Streams is a JSON object which contains OpenLABEL streams, with specific information for this frame. Stream keys can be any string (e.g. friendly stream name).",
                            "type": "object",
                            "patternProperties": {
                                "^": {"$ref": "#/definitions/stream"}
                            },
                            "additionalProperties": False
                        },
                        "transforms": {
                            "description": "Transforms is a JSON object which contains OpenLABEL transforms specific for this frame. Transform keys can be any string (e.g. friendly name of a transform).",
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
            "description": "A frame interval defines an starting and ending frame number, as a closed interval (i.e. the interval includes the limit frame numbers).",
            "type": "object",
            "properties": {
                "frame_start": {
                    "description": "Initial frame number of the interval.",
                    "type": "integer"
                    },
                "frame_end": {
                    "description": "Ending frame number of the interval.",
                    "type": "integer"
                    }
            },
            "additionalProperties": False
        },
        "streams": {
            "description": "This is a JSON object which contains OpenLABEL streams. Stream keys can be any string (e.g. friendly stream name).",
            "patternProperties": {
                "^": {"$ref": "#/definitions/stream"},
                },
            "type": "object",
            "additionalProperties": False
        },
        "coordinate_systems": {
            "description": "This is a JSON object which contains OpenLABEL coordinate systems. Coordinate system keys can be any string (e.g. friendly coordinate system name).",
            "patternProperties": {
                        "^": {"$ref": "#/definitions/coordinate_system"}
                    },
            "type": "object",
            "additionalProperties": False
        },
        "object": {
            "description": "An object is the main type of annotation element, and is designed to represent "
                           "spatio-temporal entities, such as physical objects in the real world. Objects must have a name and type."                           
                           "Objects can have static and dynamic data. Objects are the only type of elements "
                           "that can have geometric data, such as bounding boxes, cuboids, polylines, images, etc.",
            "type": "object",
            "properties": {
                "frame_intervals": {
                    "description": "The array of frame intervals where this object exists or is defined.",
                    "type": "array",
                    "items": {"$ref": "#/definitions/frame_interval"}
                },
                "name": {
                    "description": "Name of the object (it is a friendly name, not used for indexing).",
                    "type": "string"
                    },
                "type": {
                    "description": "The type of an object defines the class the object corresponds to.",
                    "type": "string"
                    },
                "ontology_uid": {
                    "description": "This is the UID of the ontology where the type of this object is defined.",
                    "type": "string"
                    },
                "resource_uid": {"$ref": "#/definitions/resource_uid"},
                "coordinate_system": {
                    "description": "This is the string key of the coordinate system this object is referenced with respect to.",
                    "type": "string"
                    },
                "object_data": {"$ref": "#/definitions/object_data"},
                "object_data_pointers": {"$ref": "#/definitions/element_data_pointers"}
            },
            "required": ["name", "type"],
            "additionalProperties": False
        },
        "action": {
            "description": "An action is a type of element intended to describe temporal situations with "
                           "semantic load, as a certain activity happening in real life, such as "
                           "crossing-zebra-cross, standing-still, playing-guitar, etc. As such, actions are simply "
                           "defined by their type, the frame intervals in which the action happens, and any "
                           "additional action data (e.g. numbers, booleans, text as attributes of the actions)",
            "type": "object",
            "properties": {
                "frame_intervals": {
                    "description": "The array of frame intervals where this action exists or is defined.",
                    "type": "array",
                    "items": {"$ref": "#/definitions/frame_interval"}
                },
                "name": {"type": "string", "description": "Name of the action (it is a friendly name, not used for indexing)."},
                "type": {"type": "string", "description": "The type of an action defines the class the action corresponds to."},
                "ontology_uid": {"description": "This is the UID of the ontology where the type of this action is defined.", "type": "string"},
                "resource_uid": {"$ref": "#/definitions/resource_uid"},                
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
                    "description": "The array of frame intervals where this event exists or is defined. Note that events are thought to be instantaneous, therefore usually they will be defined for a single frame interval where the starting and ending frames are the same.",
                    "type": "array",
                    "items": {"$ref": "#/definitions/frame_interval"}
                },
                "name": {"description": "Name of the event (it is a friendly name, not used for indexing).", "type": "string"},
                "type": {"description": "The type of an event defines the class the event corresponds to.", "type": "string"},
                "ontology_uid": {"description": "This is the UID of the ontology where the type of this event is defined.", "type": "string"},
                "resource_uid": {"$ref": "#/definitions/resource_uid"},                
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
                    "description": "The array of frame intervals where this context exists or is defined.",
                    "type": "array",
                    "items": {"$ref": "#/definitions/frame_interval"}
                },
                "name": {"description": "Name of the context (it is a friendly name, not used for indexing).", "type": "string"},
                "type": {"description": "The type of a context defines the class the context corresponds to.", "type": "string"},
                "ontology_uid": {"description": "This is the UID of the ontology where the type of this context is defined.", "type": "string"},
                "resource_uid": {"$ref": "#/definitions/resource_uid"},                
                "context_data": {"$ref": "#/definitions/context_data"},
                "context_data_pointers": {"$ref": "#/definitions/element_data_pointers"}
            },
            "required": ["name", "type"],
            "additionalProperties": False
        },
        "relation": {
            "description": "A relation is a type of element which connects two or more other elements (e.g. objects, actions, contexts or events), using "
                           "RDF triples to structure the connection, with one or more subjects, a predicate and "
                           "one or more semantic objects ",
            "type": "object",
            "properties": {
                "frame_intervals": {
                    "description": "The array of frame intervals where this relation exists or is defined.",
                    "type": "array",
                    "items": {"$ref": "#/definitions/frame_interval"}
                },
                "name": {"description": "Name of the relation (it is a friendly name, not used for indexing).", "type": "string"},
                "type": {"description": "The type of a relation defines the class the predicated of the relation corresponds to.", "type": "string"},
                "ontology_uid": {"description": "This is the UID of the ontology where the type of this relation is defined.", "type": "string"},
                "resource_uid": {"$ref": "#/definitions/resource_uid"},
                "rdf_objects": {
                    "description": "This is the list of RDF semantic objects of this relation.",
                    "type": "array",
                    "items": {"$ref": "#/definitions/rdf_agent"}
                },
                "rdf_subjects": {
                    "description": "This is the list of RDF semantic subjects of this relation.",
                    "type": "array",
                    "items": {"$ref": "#/definitions/rdf_agent"}
                },
            },
            "required": ["name", "type", "rdf_objects", "rdf_subjects"],
            "additionalProperties": False
        },
        "rdf_agent": {
            "description": "An RDF agent is either an RDF semantic object or subject.",
            "type": "object",
            "properties": {
                "type": {
                    "description": "The OpenLABEL type of element.",
                    "type": "string",
                    "enum": ["object", "action", "event", "context"]
                    },
                "uid": {
                    "description": "The element UID this RDF agent refers to.",
                    "type": "string"
                    },
            }
        },
        "element_data_pointers": {
            "description": "This is a JSON object which contains OpenLABEL element data pointers. Element data pointer keys shall be the \"name\" of the element data this pointer points to.",
            "type": "object",
            "patternProperties": {
                "^": {"$ref": "#/definitions/element_data_pointer"}
            },
            "additionalProperties": False
        },
        "element_data_pointer": {
            "description": "This item contains pointers to element data of elements, indexed by \"name\", and containing "
                           "information about the element data type (e.g. bounding box, cuboid) and the frame intervals"
                           "in which this element_data exists within an element. "
                           "As a consequence, these pointers can be used to explore element data dynamic information within the JSON content.",
            "type": "object",
            "properties": {
                "frame_intervals": {
                    "description": "List of frame intervals of the element data pointed by this pointer",
                    "type": "array",
                    "items": {"$ref": "#/definitions/frame_interval"}
                },
                "type": {
                    "description": "Type of the element data pointed by this pointer.",
                    "type": "string",
                    "enum": ["bbox", "rbbox", "num", "text", "boolean", "poly2d", "poly3d", "cuboid", "image", "mat",
                             "binary", "point2d", "point3d", "vec", "line_reference", "area_reference", "mesh"]
                },
                "attribute_pointers": {
                    "description": "This is a JSON object which contains pointers to the attributes of the element data pointed by this pointer. The attribute pointers keys shall be the \"name\" of the attribute of the element data this pointer points to.",
                    "type": "object",
                    "patternProperties": {
                        "^": {
                            "description": "The attribute pointer values are strings which define the type of the attribute.",
                            "type": "string",
                            "enum": ["num", "text", "boolean", "vec"]
                        }
                    }
                }
            },
            "required": ["frame_intervals"]
        },
        "tag_data": {
            "description": "Tag data can be a JSON object or a string which contains additional information about this tag.",
            "oneOf": [{
                "type": "object",
                "properties": {
                    "num": {
                        "description": "List of \"num\" that describe this tag.",
                        "type": "array",
                        "items": {"$ref": "#/definitions/num"}
                    },
                    "vec": {
                        "description": "List of \"vec\" that describe this tag.",
                        "type": "array",
                        "items": {"$ref": "#/definitions/vec"}
                    },
                    "text": {
                        "description": "List of \"text\" that describe this tag.",
                        "type": "array",
                        "items": {"$ref": "#/definitions/text"}
                    },
                    "boolean": {
                        "description": "List of \"boolean\" that describe this tag.",
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
                    "description": "List of \"num\" that describe this action.",
                    "type": "array",
                    "items": {"$ref": "#/definitions/num"}
                },
                "vec": {
                    "description": "List of \"vec\" that describe this action.",
                    "type": "array",
                    "items": {"$ref": "#/definitions/vec"}
                },
                "text": {
                    "description": "List of \"text\" that describe this action.",
                    "type": "array",
                    "items": {"$ref": "#/definitions/text"}
                },
                "boolean": {
                    "description": "List of \"boolean\" that describe this action.",
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
                    "description": "List of \"num\" that describe this event.",
                    "type": "array",
                    "items": {"$ref": "#/definitions/num"}
                },
                "vec": {
                    "description": "List of \"vec\" that describe this event.",
                    "type": "array",
                    "items": {"$ref": "#/definitions/vec"}
                },
                "text": {
                    "description": "List of \"text\" that describe this event.",
                    "type": "array",
                    "items": {"$ref": "#/definitions/text"}
                },
                "boolean": {
                    "description": "List of \"boolean\" that describe this event.",
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
                    "description": "List of \"num\" that describe this context.",
                    "type": "array",
                    "items": {"$ref": "#/definitions/num"}
                },
                "vec": {
                    "description": "List of \"vec\" that describe this context.",
                    "type": "array",
                    "items": {"$ref": "#/definitions/vec"}
                },
                "text": {
                    "description": "List of \"text\" that describe this context.",
                    "type": "array",
                    "items": {"$ref": "#/definitions/text"}
                },
                "boolean": {
                    "description": "List of \"boolean\" that describe this context.",
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
                    "description": "List of \"bbox\" that describe this object.",
                    "type": "array",
                    "items": {"$ref": "#/definitions/bbox"}
                },
                "rbbox": {
                    "description": "List of \"rbbox\" that describe this object.",
                    "type": "array",
                    "items": {"$ref": "#/definitions/rbbox"}
                },
                "num": {
                    "description": "List of \"num\" that describe this object.",
                    "type": "array",
                    "items": {"$ref": "#/definitions/num"}
                },
                "vec": {
                    "description": "List of \"vec\" that describe this object.",
                    "type": "array",
                    "items": {"$ref": "#/definitions/vec"}
                },
                "text": {
                    "description": "List of \"text\" that describe this object.",
                    "type": "array",
                    "items": {"$ref": "#/definitions/text"}
                },
                "boolean": {
                    "description": "List of \"boolean\" that describe this object.",
                    "type": "array",
                    "items": {"$ref": "#/definitions/boolean"}
                },
                "poly2d": {
                    "description": "List of \"poly2d\" that describe this object.",
                    "type": "array",
                    "items": {"$ref": "#/definitions/poly2d"}
                },
                "poly3d": {
                    "description": "List of \"poly3d\" that describe this object.",
                    "type": "array",
                    "items": {"$ref": "#/definitions/poly3d"}
                },
                "cuboid": {
                    "description": "List of \"cuboid\" that describe this object.",
                    "type": "array",
                    "items": {"$ref": "#/definitions/cuboid"}
                },
                "image": {
                    "description": "List of \"image\" that describe this object.",
                    "type": "array",
                    "items": {"$ref": "#/definitions/image"}
                },
                "mat": {
                    "description": "List of \"mat\" that describe this object.",
                    "type": "array",
                    "items": {"$ref": "#/definitions/mat"}
                },
                "binary": {
                    "description": "List of \"binary\" that describe this object.",
                    "type": "array",
                    "items": {"$ref": "#/definitions/binary"}
                },
                "point2d": {
                    "description": "List of \"point2d\" that describe this object.",
                    "type": "array",
                    "items": {"$ref": "#/definitions/point2d"}
                },
                "point3d": {
                    "description": "List of \"point3d\" that describe this object.",
                    "type": "array",
                    "items": {"$ref": "#/definitions/point3d"}
                },
                "mesh": {
                    "description": "List of \"mesh\" that describe this object.",
                    "type": "array",
                    "items": {"$ref": "#/definitions/mesh"}
                },
                "line_reference": {
                    "description": "List of \"line_reference\" that describe this object.",
                    "type": "array",
                    "items": {"$ref": "#/definitions/line_reference"}
                },
                "area_reference": {
                    "description": "List of \"area_reference\" that describe this object.",
                    "type": "array",
                    "items": {"$ref": "#/definitions/area_reference"}
                }
            },
            "additionalProperties": False
        },
        "coordinate_system": {
            "description": "A coordinate system is a 3D reference frame. Spatial information of objects and their properties"
                           "can be defined with respect to coordinate systems.",
            "properties": {
                "type": {
                    "description": "This is a string that describes the type of the coordinate system (e.g. \"local\", \"geo\").",
                    "type": "string"
                    },
                "parent": {
                    "description": "This is the string UID of the parent coordinate system this coordinate system is refered to.",
                    "type": "string"
                    },
                "children": {
                    "description": "List of children of this coordinate system.",
                    "type": "array",
                    "items": {
                        "description": "This is the string UID of this child coordinate system.",
                        "type": "string"
                        },
                },
                "pose_wrt_parent": {"$ref": "#/definitions/transform_data"},                
            },
            "required": ["type", "parent"],
            "additionalProperties": True
        },
        "transform": {
            "description": "This is a JSON object with information about this transform.",
            "type": "object",
            "properties": {
                "src": {
                    "description": "The string UID (name) of the source coordinate system of geometrical data this transform converts.",
                    "type": "string"
                    },
                "dst": {
                    "description": "The string UID (name) of the destination coordinate system for geometric data converted with this transform.",
                    "type": "string"
                    },
                "transform_src_to_dst": {"$ref": "#/definitions/transform_data"}
            },
            "required": ["src", "dst", "transform_src_to_dst"],
            "additionalProperties": True
        },
        "transform_data": {
            "description": "JSON object containing the transform data.",
            "oneOf": [
                {                    
                    "type": "object",
                    "properties": {
                        "matrix4x4": {
                            "description": "Flattened list of 16 entries encoding a 4x4 homogeneous matrix, to enable transform 3D column homogeneous vectors 4x1 using right-multiplication of matrices: X_dst = matrix_4x4 * X_src.",
                            "type": "array",
                            "items": {"type": "number"},                            
                        },
                    },
                    "required": ["matrix4x4"],
                    "additionalProperties": False
                },
                {
                    "description": "A transform can be defined with a quaternion to encodes the "
                                   "rotation of a coordinate system with respect to another, "
                                   "and a translation.",
                    "type": "object",
                    "properties": {
                        "quaternion": {
                            "description": "List of 4 values encoding a quaternion (x, y, z, w).",
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 4,
                            "maxItems": 4
                        },
                        "translation": {
                            "description": "List of 3 values encoding the translation vector (x, y, z)",
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
                    "description": "A transform can be defined with a sequence of Euler angles to encode the rotation of a coordinate system with respect to another and a translation.",
                    "type": "object",
                    "properties": {
                        "euler_angles": {
                            "description": "List of 3 values encoding Euler angle values.",
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 3,
                            "maxItems": 3
                        },
                        "translation": {
                            "description": "List of 3 values encoding the translation vector (x, y, z)",
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 3,
                            "maxItems": 3
                        },
                        "sequence": {
                            "description": "The sequence as a string of 3 characters defining the axis of the Euler angles and their order of application, e.g. \"ZYX\". Default assumption is \"ZYX\".",
                            "type": "string"
                            }
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
                "description": {
                    "description": "Description of the stream.",
                    "type": "string"
                    },
                "stream_properties": {"$ref": "#/definitions/stream_properties"},
                "type": {
                    "description": "A string encoding the type of the stream.",
                    "type": "string",
                    "enum": ["camera", "lidar", "radar", "gps_imu", "other"]
                },
                "uri": {
                    "description": "A string encoding the URI (e.g. a URL) or file name (e.g. a video file name) the stream corresponds to.",
                    "type": "string"
                    },
            },
            'additionalProperties': False
        },
        "stream_properties": {
            "description": "Additional properties of the stream.",
            "type": "object",
            "oneOf": [{
                "intrinsics_pinhole": {
                    "description": "This JSON object defines an instance of the intrinsic parameters of a pinhole camera.",
                    "type": "object",
                    "properties": {
                        "width_px": {"type": "integer"},
                        "height_px": {"type": "integer"},
                        "camera_matrix": {
                            "type": "array",
                            "description": "This is a 3x4 camera matrix which projects  "
                                       "3D homogeneous points (4x1) from a camera coordinate "
                                       "system (ccs) into the image plane (3x1)"                                       
                                       "This is the usual K matrix for camera projection (as in OpenCV), but"
                                       "extended from 3x3 to 3x4, to enable its direct utilisation to project"
                                       "4x1 homogeneous 3D points."
                                       "The matrix is defined to follows the camera model: x-to-right, y-down, z-forward so,"
                                       "x_img = camera_matrix * X_ccs",
                            "minItems": 12,
                            "maxItems": 12,
                            "items": {"type": "number"}                            
                        },
                        "distortion_coeffs": {
                            "type": "array",
                            "description": "This is the array 1xN radial and tangential distortion "
                                       "coefficients. See https://docs.opencv.org/4.2.0/d9/d0c/group__calib3d.html",
                            "minItems": 5,
                            "maxItems": 14,
                            "items": {"type": "number"}
                        }
                    },
                    "additionalProperties": True
                },
                "intrinsics_fisheye": {
                    "description": "This JSON object defines an instance of the intrinsic parameters of a fisheye camera.",
                    "type": "object",
                    "properties": {
                        "width_px": {"type": "integer"},
                        "height_px": {"type": "integer"},                        
                        "center_x_px": {"type": ["number", "null"]},
                        "center_y_px": {"type": ["number", "null"]},
                        "aspect_ratio": {"type": ["number", "null"]},                        
                        "lens_coeffs": {
                            "description": "This is the list of 4 values for the lens coefficients.",
                            "type": "array",
                            "minItems": 4,
                            "maxItems": 4,
                            "items": {"type": "number"}
                        }
                    },
                    "additionalProperties": True
                },
                "intrinsics_custom": {
                    "description": "This is a JSON object completely customizable for other types of camera models.",
                    "type": "object"
                }
            }],
            "sync": {
                "description": "This is the sync information for this stream.",
                "type": "object",
                "oneOf": [{
                    "properties": {
                        "timestamp": {
                            "description": "The timestamp indicates a time instant as a string or numerical value to describe this frame.",
                            "anyOf": [
                                {"type": "string"}, 
                                {"type": "number"}]
                            },
                        "frame_stream": {
                            "description": "This is the internal frame number inside the strem this OpenLABEL frame corresponds to.",
                            "type": "integer"
                            },
                    },
                }, {
                    "properties": {
                        "frame_shift": {
                            "description": "Fixed shift or difference between the OpenLABEL master frame count and this stream's internal frame count.",
                            "type": "integer"
                            }
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
                "name": {
                    "description": "This is a string encoding the name of this object data. It is used as index inside the corresponding object data pointers.",
                    "type": "string"
                    },
                "coordinate_system": {"type": "string", "description": "Name of the coordinate system this object data is expressed with respect to."},
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
                "name": {"type": "string", "description": "This is a string encoding the name of this object data. It is used as index inside the corresponding object data pointers."},
                "coordinate_system": {"type": "string", "description": "Name of the coordinate system this object data is expressed with respect to."},
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
            "description": "A number.",
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "This is a string encoding the name of this object data. It is used as index inside the corresponding object data pointers."},
                "coordinate_system": {"type": "string", "description": "Name of the coordinate system this object data is expressed with respect to."},
                "val": {"type": "number", "description": "The numerical value of the number.",},
                "type": {
                    "description": "This attribute specifies whether the number shall be considered as a value, a minimum or a maximum in its context.",
                    "type": "string", "enum": ["value", "min", "max"]
                    },
                "attributes": {"$ref": "#/definitions/attributes"}
            },
            "required": ["val"],
            "additionalProperties": True
        },
        "text": {
            "description": "A text.",
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "This is a string encoding the name of this object data. It is used as index inside the corresponding object data pointers."},              
                "coordinate_system": {"type": "string", "description": "Name of the coordinate system this object data is expressed with respect to."},
                "val": {"type": "string", "description": "The characters of the text."},
                "type": {"type": "string", "enum": ["value"], "description": "This attribute specifies how the text shall be considered. In this schema only possible option is as a value."},
                "attributes": {"$ref": "#/definitions/attributes"}
            },
            "required": ["val"],
            "additionalProperties": True
        },
        "boolean": {
            "description": "A boolean.",
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "This is a string encoding the name of this object data. It is used as index inside the corresponding object data pointers."},
                "coordinate_system": {"type": "string", "description": "Name of the coordinate system this object data is expressed with respect to."},
                "val": {"type": "boolean", "description": "The boolean value."},
                "type": {"type": "string", "enum": ["value"], "description": "This attribute specifies how the boolean shall be considered. In this schema only possible option is as a value."},
                "attributes": {"$ref": "#/definitions/attributes"}
            },
            "required": ["val"],
            "additionalProperties": True
        },
        "cuboid": {
            "description": "A cuboid or 3D bounding box. It is defined by the position of its center, the rotation in 3D, and its dimensions.",
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "This is a string encoding the name of this object data. It is used as index inside the corresponding object data pointers."},
                "coordinate_system": {"type": "string", "description": "Name of the coordinate system this object data is expressed with respect to."},
                "val": {
                    "oneOf": [
                        {
                            "description": "List of values encoding the position, rotation and dimensions. Two options are supported, using 9 or 10 values. If 9 values are used, "
                                           "the format is (x, y, z, rx, ry, rz, sx, sy, sz), where (x, y, z) encodes the position, (rx, ry, rz) encodes the Euler angles that " 
                                           "encode the rotation, and (sx, sy, sz) are the dimensions of the cuboid in its object coordinate system. If 10 values are used, then "
                                           "the format is (x, y, z, qx, qy, qz, qw, sx, sy, sz) with the only difference of the rotation values which are the 4 values of a quaternion.",
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
            "description": "An image.",
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "This is a string encoding the name of this object data. It is used as index inside the corresponding object data pointers."},
                "coordinate_system": {"type": "string", "description": "Name of the coordinate system this object data is expressed with respect to."},
                "val": {"type": "string", "description": "A string with the encoded bytes of this image."},
                "mime_type": {"type": "string", "description": "This is a string that declares the MIME (Multipurpose internat Mail Extensions) of the image, e.g. \"image/gif\"."},
                "encoding": {"type": "string", "description": "This is a string that declares the encoding type of the bytes for this image, e.g. \"base64\"."},
                "attributes": {"$ref": "#/definitions/attributes"}
            },
            "required": ["name", "val", "mime_type", "encoding"],
            "additionalProperties": True
        },
        "mat": {
            "description": "A matrix.",
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "This is a string encoding the name of this object data. It is used as index inside the corresponding object data pointers."},
                "coordinate_system": {"type": "string", "description": "Name of the coordinate system this object data is expressed with respect to."},
                "val": {
                    "description": "Flattened list of values of the matrix.",
                    "type": "array",
                    "items": {"type": "number"}
                },
                "channels": {"type": "number", "description": "Number of channels of the matrix."},
                "width": {"type": "number", "description": "Width of the matrix (number of columns)."},
                "height": {"type": "number", "description": "Height of the matrix (number of rows)."},
                "data_type": {"type": "string", "description": "This is a string that declares the type of the numerical values of the matrix, e.g. \"float\"."},
                "attributes": {"$ref": "#/definitions/attributes"}
            },
            "required": ["name", "val", "channels", "width", "height", "data_type"],
            "additionalProperties": True
        },
        "binary": {
            "description": "A binary payload.",
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "This is a string encoding the name of this object data. It is used as index inside the corresponding object data pointers."},
                "coordinate_system": {"type": "string", "description": "Name of the coordinate system this object data is expressed with respect to."},
                "val": {"type": "string", "description": "A string with the encoded bytes of this binary payload."},
                "encoding": {"type": "string", "description": "This is a string that declares the encoding type of the bytes for this binary payload, e.g. \"base64\"."},
                "data_type": {"type": "string", "description": "This is a string that declares the type of the values of the binary object."},
                "attributes": {"$ref": "#/definitions/attributes"}
            },
            "required": ["name", "val", "encoding", "data_type"],
            "additionalProperties": True
        },
        "vec": {
            "description": "A vector (list) of numbers or strings.",
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "This is a string encoding the name of this object data. It is used as index inside the corresponding object data pointers."},
                "coordinate_system": {"type": "string", "description": "Name of the coordinate system this object data is expressed with respect to."},
                "val": {
                    "type": "array",
                    "items": {
                        "oneOf": [
                            {"type": "number"},
                            {"type": "string"}
                        ]
                    }
                },
                "type": {"type": "string", "enum": ["values", "range"], "description": "This attribute specifies whether the vector shall be considered as a descriptor of individual values, or as a definition of a range."},
                "attributes": {"$ref": "#/definitions/attributes"}
            },
            "required": ["val"],
            "additionalProperties": True
        },
        "point2d": {
            "description": "A 2D point.",
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "This is a string encoding the name of this object data. It is used as index inside the corresponding object data pointers."},
                "coordinate_system": {"type": "string", "description": "Name of the coordinate system this object data is expressed with respect to."},
                "id": {"type": "integer", "description": "This is an integer identifier of the point in the context of a set of points."},
                "val": {
                    "description": "List of two coordinates to define the point, e.g. (x, y).",
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
            "description": "A 3D point.",
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "This is a string encoding the name of this object data. It is used as index inside the corresponding object data pointers."},
                "coordinate_system": {"type": "string", "description": "Name of the coordinate system this object data is expressed with respect to."},
                "id": {"type": "integer", "description": "This is an integer identifier of the point in the context of a set of points."},
                "val": {
                    "description": "List of three coordinates to define the point, e.g. (x, y, z).",
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
            "description": "A 2D polyline defined as a sequence of 2D points.",
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "This is a string encoding the name of this object data. It is used as index inside the corresponding object data pointers."},
                "coordinate_system": {"type": "string", "description": "Name of the coordinate system this object data is expressed with respect to."},
                "mode": {
                    "type": "string", 
                    "description": "Mode of the polyline list of values: \"MODE_POLY2D_ABSOLUTE\" determines that the poly2d list contains the sequence of (x, y) values of all points of the polyline. "
                                    "\"MODE_POLY2D_RELATIVE\" specifies that only the first point of the sequence is defined with its (x, y) values, while all the rest are defined relative to it. \"MODE_POLY2D_SRF6DCC\" specifies that SRF6DCC chain code method is used. \"MODE_POLY2D_RS6FCC\" specifies that the RS6FCC method is used."
                    },
                "closed": {"type": "boolean", "description": "A boolean that defines whether the polyline is closed or not. In case it is closed, it is assumed that the last point of the sequence is connected with the first one."},
                "val": {
                    "description": "List of numerical values of the polyline, according to its mode.",
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
                    "description": "Hierarchy of the 2D polyline in the context of a set of 2D polylines. See https://docs.opencv.org/4.5.2/d9/d8b/tutorial_py_contours_hierarchy.html",
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
            "description": "A 3D polyline defined as a sequence of 3D points.",
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "This is a string encoding the name of this object data. It is used as index inside the corresponding object data pointers."},
                "coordinate_system": {"type": "string", "description": "Name of the coordinate system this object data is expressed with respect to."},
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
                           "E.g. A certain bounding box can have attributes related to its "
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
            "description": "A mesh encodes a point-line-area structure. "
                           "It is intended to represent flat 3D meshes, such as several connected parking lots, where points, lines and areas composing the mesh "
                           "are interrelated, and can have their own properties.",
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "This is a string encoding the name of this object data. It is used as index inside the corresponding object data pointers."},
                "coordinate_system": {"type": "string", "description": "Name of the coordinate system this object data is expressed with respect to."},
                "point3d": {
                    "description": "This is the JSON object for the 3D points defined for this mesh. Point3d keys are strings containing numerical UIDs.",
                    "type": "object",
                    "patternProperties": {
                        "^[0-9]+$": {"$ref": "#/definitions/point3d"}
                    },
                    "additionalProperties": False
                },
                "line_reference": {
                    "description": "This is the JSON object for the 3D lines defined for this mesh. Line reference keys are strings containing numerical UIDs.",
                    "type": "object",
                    "patternProperties": {
                        "^[0-9]+$": {"$ref": "#/definitions/line_reference"}
                    },
                    "additionalProperties": False
                },
                "area_reference": {
                    "description": "This is the JSON object for the areas defined for this mesh. Area keys are strings containing numerical UIDs.",
                    "type": "object",
                    "patternProperties": {
                        "^[0-9]+$": {"$ref": "#/definitions/area_reference"}
                    },
                    "additionalProperties": False
                }                
            },
            "additionalProperties": True
        },
        "line_reference": {
            "description": "A line reference is a JSON object which defines a 3D line segment by means of defining the indexes of its two extreme points.",
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "This is a string encoding the name of this object data. It is used as index inside the corresponding object data pointers."},
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
            "description": "An area reference is a JSON object which defines the area of a set of 3D line segments by means of defining the indexes of all lines which outline the area. Note that coplanar 3D lines are assumed.",
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "This is a string encoding the name of this object data. It is used as index inside the corresponding object data pointers."},
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