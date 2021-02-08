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

vcd_version_name = "vcd" + schema.vcd_schema_version.replace(".", "")


class TestBasic(unittest.TestCase):

    ###########################################################
    ### From VCD3.3 to VCD4.3.1
    ###########################################################
    # Converter from VCD 3.3.0 to VCD 4.3.1 (3DOD cuboids)
    def test_VCD330_to_VCD431_3dod(self):
        vcd330_file_name = "./etc/vcd330_sample_3dod.json"
        vcd431 = core.VCD(vcd330_file_name)

        if not os.path.isfile('./etc/' + vcd_version_name + '_sample_3dod.json'):
            vcd431.save('./etc/' + vcd_version_name + '_sample_3dod.json', False)
        vcd431_read = core.VCD('./etc/' + vcd_version_name + '_sample_3dod.json')
        self.assertEqual(vcd431.stringify(False), vcd431_read.stringify(False))

    # Converter from VCD 3.3.0 to VCD 4.3.1 (LS poly3d)
    def test_VCD330_to_VCD431_ls(self):
        vcd330_file_name = "./etc/vcd330_sample_ls.json"
        vcd431 = core.VCD(vcd330_file_name)

        if not os.path.isfile('./etc/' + vcd_version_name + '_sample_ls.json'):
            vcd431.save('./etc/' + vcd_version_name + '_sample_ls.json', False)
        vcd431_read = core.VCD('./etc/' + vcd_version_name + '_sample_ls.json')
        self.assertEqual(vcd431.stringify(False), vcd431_read.stringify(False))

    # Converter from VCD 3.3.0 to VCD 4.3.1 (PD poly2d)
    def test_VCD330_to_VCD431_pd(self):
        vcd330_file_name = "./etc/vcd330_sample_pd.json"
        vcd431 = core.VCD(vcd330_file_name)

        if not os.path.isfile('./etc/' + vcd_version_name + '_sample_pd.json'):
            vcd431.save('./etc/' + vcd_version_name + '_sample_pd.json', False)
        vcd431_read = core.VCD('./etc/' + vcd_version_name + '_sample_pd.json')
        self.assertEqual(vcd431.stringify(False), vcd431_read.stringify(False))

    def test_VCD330_to_VCD431_semantics(self):
        vcd330_file_name = "./etc/vcd330_semantics_fw.json"
        vcd431 = core.VCD(vcd330_file_name)

        if not os.path.isfile('./etc/' + vcd_version_name + '_semantics_fw.json'):
            vcd431.save('./etc/' + vcd_version_name + '_semantics_fw.json', False)
        vcd431_read = core.VCD('./etc/' + vcd_version_name + '_semantics_fw.json')
        self.assertEqual(vcd431.stringify(False), vcd431_read.stringify(False))

    def test_VCD330_to_VCD431_mesh(self):
        vcd330_file_name = "./etc/vcd330_sample_mesh_short.json"
        vcd431 = core.VCD(vcd330_file_name)

        if not os.path.isfile('./etc/' + vcd_version_name + '_sample_mesh_short.json'):
            vcd431.save('./etc/' + vcd_version_name + '_sample_mesh_short.json', False)
        vcd431_read = core.VCD('./etc/' + vcd_version_name + '_sample_mesh_short.json')
        self.assertEqual(vcd431.stringify(False), vcd431_read.stringify(False))

    ###########################################################
    ### From VCD4.2 to VCD4.3.1
    ###########################################################
    def test_VCD420_to_VCD431_dmd(self):
        vcd420_file_name = "./etc/vcd420_1_attm_03-08_ann.json"
        vcd431 = core.VCD(vcd420_file_name)

        if not os.path.isfile('./etc/' + vcd_version_name + '_1_attm_03-08_ann.json'):
            vcd431.save('./etc/' + vcd_version_name + '_1_attm_03-08_ann.json', False)
        vcd431_read = core.VCD('./etc/' + vcd_version_name + '_1_attm_03-08_ann.json')
        self.assertEqual(vcd431.stringify(False), vcd431_read.stringify(False))


if __name__ == '__main__':  # This changes the command-line entry point to call unittest.main()
    print("Running " + os.path.basename(__file__))
    unittest.main()

