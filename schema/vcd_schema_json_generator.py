"""
VCD (Video Content Description) library v5.0.0

Project website: http://vcd.vicomtech.org

Copyright (C) 2021, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 5.0.0.
VCD is distributed under MIT License. See LICENSE.

"""


import os
import json
import sys
sys.path.insert(0, "..")

import vcd.schema as schema

######################################
# Save schema
######################################
name = "vcd_schema_json-v" + schema.vcd_schema_version + ".json"
with open(name, "w") as write_file:
    print(json.dumps(schema.vcd_schema, indent=4, sort_keys=True))
    json.dump(schema.vcd_schema, write_file, indent=4, sort_keys=True)
