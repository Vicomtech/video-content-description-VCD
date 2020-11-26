"""
VCD (Video Content Description) library v4.3.0

Project website: http://vcd.vicomtech.org

Copyright (C) 2020, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.3.0.
VCD is distributed under MIT License. See LICENSE.

"""

import vcd.core as core

import unittest
import json
import os
import sys
sys.path.insert(0, "..")


class TestBasic(unittest.TestCase):

    ###########################################################
    ### From VCD3.3 to VCD4.3.0
    ###########################################################
    # Converter from VCD 3.3.0 to VCD 4.3.0 (3DOD cuboids)
    def test_VCD330_to_VCD430_3dod(self):
        vcd330_file_name = "./etc/vcd330_sample_3dod.json"
        vcd430 = core.VCD(vcd330_file_name)

        if not os.path.isfile('./etc/vcd430_sample_3dod.json'):
            vcd430.save('./etc/vcd430_sample_3dod.json', False)
        vcd430_read = core.VCD('./etc/vcd430_sample_3dod.json')
        self.assertEqual(vcd430.stringify(False), vcd430_read.stringify(False))

    # Converter from VCD 3.3.0 to VCD 4.3.0 (LS poly3d)
    def test_VCD330_to_VCD430_ls(self):
        vcd330_file_name = "./etc/vcd330_sample_ls.json"
        vcd430 = core.VCD(vcd330_file_name)

        if not os.path.isfile('./etc/vcd430_sample_ls.json'):
            vcd430.save('./etc/vcd430_sample_ls.json', False)
        vcd430_read = core.VCD('./etc/vcd430_sample_ls.json')
        self.assertEqual(vcd430.stringify(False), vcd430_read.stringify(False))

    # Converter from VCD 3.3.0 to VCD 4.3.0 (PD poly2d)
    def test_VCD330_to_VCD430_pd(self):
        vcd330_file_name = "./etc/vcd330_sample_pd.json"
        vcd430 = core.VCD(vcd330_file_name)

        if not os.path.isfile('./etc/vcd430_sample_pd.json'):
            vcd430.save('./etc/vcd430_sample_pd.json', False)
        vcd430_read = core.VCD('./etc/vcd430_sample_pd.json')
        self.assertEqual(vcd430.stringify(False), vcd430_read.stringify(False))

    def test_VCD330_to_VCD430_semantics(self):
        vcd330_file_name = "./etc/vcd330_semantics_fw.json"
        vcd430 = core.VCD(vcd330_file_name)

        if not os.path.isfile('./etc/vcd430_semantics_fw.json'):
            vcd430.save('./etc/vcd430_semantics_fw.json', False)
        vcd430_read = core.VCD('./etc/vcd430_semantics_fw.json')
        self.assertEqual(vcd430.stringify(False), vcd430_read.stringify(False))

    def test_VCD330_to_VCD430_mesh(self):
        vcd330_file_name = "./etc/vcd330_sample_mesh_short.json"
        vcd430 = core.VCD(vcd330_file_name)

        if not os.path.isfile('./etc/vcd430_sample_mesh_short.json'):
            vcd430.save('./etc/vcd430_sample_mesh_short.json', False)
        vcd430_read = core.VCD('./etc/vcd430_sample_mesh_short.json')
        self.assertEqual(vcd430.stringify(False), vcd430_read.stringify(False))

    ###########################################################
    ### From VCD4.2 to VCD4.3.0
    ###########################################################
    def test_VCD420_to_VCD430_dmd(self):
        vcd420_file_name = "./etc/vcd420_1_attm_03-08_ann.json"
        vcd430 = core.VCD(vcd420_file_name)

        if not os.path.isfile('./etc/vcd430_1_attm_03-08_ann.json'):
            vcd430.save('./etc/vcd430_1_attm_03-08_ann.json', False)
        vcd430_read = core.VCD('./etc/vcd430_1_attm_03-08_ann.json')
        self.assertEqual(vcd430.stringify(False), vcd430_read.stringify(False))


if __name__ == '__main__':  # This changes the command-line entry point to call unittest.main()
    print("Running " + os.path.basename(__file__))
    unittest.main()

