"""
VCD (Video Content Description) library v4.3.1

Project website: http://vcd.vicomtech.org

Copyright (C) 2021, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.3.1.
VCD is distributed under MIT License. See LICENSE.

"""

import unittest
import os
import inspect
import numpy as np
import vcd.core as core
import vcd.schema as schema
import vcd.types as types
import vcd.utils as utils

#vcd_version_name = "vcd" + schema.vcd_schema_version.replace(".", "")
openlabel_version_name = "openlabel" + schema.openlabel_schema_version.replace(".", "")

overwrite = False


def check_openlabel(openlabel, openlabel_file_name, force_write=False):
    if not os.path.isfile(openlabel_file_name) or force_write:
        openlabel.save(openlabel_file_name)

    openlabel_read = core.OpenLABEL(openlabel_file_name, validation=True)
    return openlabel_read.stringify() == openlabel.stringify()


class TestBasic(unittest.TestCase):
    def test_create_openlabel(self):
        openlabel = core.OpenLABEL()
        openlabel.add_object(name="object1", semantic_type="car")
        openlabel.add_object(name="object2", semantic_type="pedestrian")

        # Compare with reference
        self.assertTrue(check_openlabel(openlabel, './etc/' + openlabel_version_name + '_' + inspect.currentframe().f_code.co_name + '.json', overwrite))

    def test_read_vcd431_file(self):
        openlabel = core.OpenLABEL(file_name='./etc/vcd431_test_contours.json')

        self.assertTrue(check_openlabel(openlabel,
                                        './etc/' + openlabel_version_name + '_' + inspect.currentframe().f_code.co_name + '.json',
                                        overwrite))



if __name__ == '__main__':  # This changes the command-line entry point to call unittest.main()
    print("Running " + os.path.basename(__file__))
    unittest.main()
