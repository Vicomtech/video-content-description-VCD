"""
VCD (Video Content Description) library v4.0.0

Project website: http://vcd.vicomtech.org

Copyright (C) 2020, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.0.0.
VCD is distributed under MIT License. See LICENSE.

"""


import json
import sys
sys.path.insert(0, "..")
from jsonschema import validate

# Load schema and file
with open("test_create_search_mid.json", "r") as json_file, open("vcd_schema_json-v4.0.0.json", "r") as json_schema_file:
    vcd_json_dict = json.load(json_file)
    vcd_json_schema_dict = json.load(json_schema_file)
    validate(instance=vcd_json_dict, schema=vcd_json_schema_dict)
    print("Valid schema and file")