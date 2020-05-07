"""
VCD (Video Content Description) library v4.2.0

Project website: http://vcd.vicomtech.org

Copyright (C) 2020, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.2.0.
VCD is distributed under MIT License. See LICENSE.

"""

import unittest
import sys
sys.path.insert(0, "..")
import vcd.serializer as serializer


class TestBasic(unittest.TestCase):
    def test_json_to_proto(self):
        vcd_json_file_name = "./etc/vcd420_sample_3dod.json"
        vcd_proto_file_name = "./etc/vcd420_sample_3dod_proto_from_json.txt"

        serializer.json2proto_bin(vcd_json_file_name, vcd_proto_file_name)

    def test_proto_to_json(self):
        vcd_proto_file_name = "./etc/vcd420_sample_3dod_proto_from_json.txt"
        vcd_json_file_name = "./etc/vcd420_sample_3dod_from_proto.json"

        serializer.proto_bin2json(vcd_proto_file_name, vcd_json_file_name)


if __name__ == '__main__':  # This changes the command-line entry point to call unittest.main()
    print("Running test_serializer.py...")
    unittest.main()