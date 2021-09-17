"""
VCD (Video Content Description) library v5.0.0

Project website: http://vcd.vicomtech.org

Copyright (C) 2021, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 5.0.0.
VCD is distributed under MIT License. See LICENSE.

"""

# NOTE: This test is left out of v4.3.1
# TODO: Update proto to v4.3.1

import unittest
import vcd.core as core
import vcd.schema as schema
import vcd.serializer as serializer

vcd_version_name = "vcd" + schema.vcd_schema_version.replace(".", "")

class TestBasic(unittest.TestCase):

    def test_json_proto(self):
        vcd_json_file_name = './etc/' + vcd_version_name + '_test_create_search_simple_nopretty.json'
        vcd_proto_file_name = './etc/' + vcd_version_name + '_test_create_search_simple_nopretty_proto_from_json.txt'
        vcd_json_file_name_rebuilt = './etc/' + vcd_version_name + '_test_create_search_simple_nopretty_from_proto.json'

        serializer.json2proto_bin(vcd_json_file_name, vcd_proto_file_name)
        serializer.proto_bin2json(vcd_proto_file_name, vcd_json_file_name_rebuilt)

        vcd_src = core.VCD(vcd_json_file_name)
        vcd_dst = core.VCD(vcd_json_file_name_rebuilt)

        self.assertEqual(vcd_src.stringify(False), vcd_dst.stringify(False))


if __name__ == '__main__':  # This changes the command-line entry point to call unittest.main()
    print("Running test_serializer.py...")
    unittest.main()
