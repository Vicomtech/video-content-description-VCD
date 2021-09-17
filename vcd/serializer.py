"""
VCD (Video Content Description) library v5.0.0

Project website: http://vcd.vicomtech.org

Copyright (C) 2021, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 5.0.0.
VCD is distributed under MIT License. See LICENSE.

"""

import vcd.proto as proto
from google.protobuf.json_format import Parse
from google.protobuf.json_format import MessageToJson

# NOTE: There is a major problem not solved in the conversion JSON -> Proto -> JSON
# In JSON, we can have an empty string "" as the value of a key-value pair.
# Though, this is converted to null in Proto, and for some reason, when
# writing it back to JSON, the entire key-value pair is omitted.

# NOTE: Also, for some reason, booleans in JSON (true/false) are not read by proto
# and the entire entry is ommitted.

# NOTE: The same happens with empty arrays, which in JSON are [], but then going
# through proto and then JSON again are lost

def json2proto_bin(vcd_json_file_in, vcd_proto_file_out):
    vcd_message = proto.VCD()
    with open(vcd_json_file_in, "r") as f:
        Parse(f.read(), vcd_message)

    with open(vcd_proto_file_out, "wb") as f:
        f.write(vcd_message.SerializeToString())


def proto_bin2json(vcd_proto_file_in, vcd_json_file_out):
    vcd_message = proto.VCD()

    with open(vcd_proto_file_in, "rb") as f:
        vcd_message.ParseFromString(f.read())

    with open(vcd_json_file_out, "w") as f:
        f.write(MessageToJson(vcd_message, preserving_proto_field_name=True,
                              indent=4))
