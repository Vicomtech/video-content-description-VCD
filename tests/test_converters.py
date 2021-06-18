"""
VCD (Video Content Description) library v4.3.1

Project website: http://vcd.vicomtech.org

Copyright (C) 2021, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.3.1.
VCD is distributed under MIT License. See LICENSE.

"""

import inspect
import unittest
import os

import vcd.core as core

from test_config import check_openlabel
from test_config import openlabel_version_name


class TestBasic(unittest.TestCase):

    ###########################################################
    ### From VCD4.2 to OpenLABEL 0.2.0
    ###########################################################
    def test_VCD420_to_OpenLABEL020_dmd(self):
        vcd420_file_name = "./etc/vcd420_1_attm_03-08_ann.json"
        vcd = core.OpenLABEL(vcd420_file_name)

        # Check equal to reference JSON
        self.assertTrue(check_openlabel(vcd, './etc/' + openlabel_version_name + '_' +
                                        inspect.currentframe().f_code.co_name + '.json'))


if __name__ == '__main__':  # This changes the command-line entry point to call unittest.main()
    print("Running " + os.path.basename(__file__))
    unittest.main()

