"""
VCD (Video Content Description) library v4.3.1

Project website: http://vcd.vicomtech.org

Copyright (C) 2021, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.3.1.
VCD is distributed under MIT License. See LICENSE.

"""

import vcd.core as core
import vcd.schema as schema

import unittest
import os

#vcd_version_name = "vcd" + schema.vcd_schema_version.replace(".", "")
openlabel_version_name = "openlabel" + schema.openlabel_schema_version.replace(".", "")
vcd_version_name = openlabel_version_name


class TestBasic(unittest.TestCase):

    ###########################################################
    ### From VCD4.2 to OpenLABEL 0.2.0
    ###########################################################
    def test_VCD420_to_OpenLABEL020_dmd(self):
        vcd420_file_name = "./etc/vcd420_1_attm_03-08_ann.json"
        openlabel020 = core.OpenLABEL(vcd420_file_name)

        if not os.path.isfile('./etc/' + vcd_version_name + '_1_attm_03-08_ann.json'):
            openlabel020.save('./etc/' + vcd_version_name + '_1_attm_03-08_ann.json', False)
        openlabel020_read = core.VCD('./etc/' + vcd_version_name + '_1_attm_03-08_ann.json')
        self.assertEqual(openlabel020.stringify(False), openlabel020_read.stringify(False))


if __name__ == '__main__':  # This changes the command-line entry point to call unittest.main()
    print("Running " + os.path.basename(__file__))
    unittest.main()

