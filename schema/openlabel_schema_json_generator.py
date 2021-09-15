"""
VCD (Video Content Description) library v4.3.1

Project website: http://vcd.vicomtech.org

Copyright (C) 2021, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.3.1.
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
name = "openlabel_json_schema-v" + schema.openlabel_schema_version + ".json"
with open(name, "w") as write_file:
    print(json.dumps(schema.openlabel_schema, indent=4, sort_keys=True))
    json.dump(schema.openlabel_schema, write_file, indent=4, sort_keys=True)
