"""
VCD (Video Content Description) library v4.0.0

Project website: http://vcd.vicomtech.org

Copyright (C) 2020, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.0.0.
VCD is distributed under MIT License. See LICENSE.

"""



import sys
sys.path.insert(0, "..")
from proto.build.vcd_proto_v4_pb2 import VCD
from google.protobuf.json_format import Parse
from google.protobuf.json_format import MessageToJson


def json2proto_bin(vcd_json_file_in, vcd_proto_file_out):
    vcd_message = VCD()
    with open(vcd_json_file_in, "r") as f:
        Parse(f.read(), vcd_message)

    with open(vcd_proto_file_out, "wb") as f:
        f.write(vcd_message.SerializeToString())


def proto_bin2json(vcd_proto_file_in, vcd_json_file_out):
    vcd_message = VCD()

    with open(vcd_proto_file_in, "rb") as f:
        vcd_message.ParseFromString(f.read())

    with open(vcd_json_file_out, "w") as f:
        f.write(MessageToJson(vcd_message, preserving_proto_field_name=True,
                              indent=4))
