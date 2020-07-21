"""
VCD (Video Content Description) library v4.3.0

Project website: http://vcd.vicomtech.org

Copyright (C) 2020, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.3.0.
VCD is distributed under MIT License. See LICENSE.

"""


import unittest
import json
import os
import sys
sys.path.insert(0, "..")
import converters.vcdConverter.converter as converter


class TestBasic(unittest.TestCase):

    ###########################################################
    ### From VCD3.3 to VCD4
    ###########################################################
    # Converter from VCD 3.3.0 to VCD 4.3.0 (3DOD cuboids)
    def test_VCD330_to_VCD430_3dod(self):
        vcd330_file_name = "./etc/in/vcd330_sample_3dod.json"
        myConverter = converter.ConverterVCD330toVCD430(vcd330_file_name)
        vcd = myConverter.get()

        if not os.path.isfile('./etc/vcd430_sample_3dod.json'):
            vcd.save('./etc/vcd430_sample_3dod.json', False)

    # Converter from VCD 3.3.0 to VCD 4.3.0 (LS poly3d)
    def test_VCD330_to_VCD430_ls(self):
        vcd330_file_name = "./etc/in/vcd330_sample_ls.json"
        myConverter = converter.ConverterVCD330toVCD430(vcd330_file_name)
        vcd = myConverter.get()

        if not os.path.isfile('./etc/vcd430_sample_ls.json'):
            vcd.save('./etc/vcd430_sample_ls.json', False)

    # Converter from VCD 3.3.0 to VCD 4.3.0 (PD poly2d)
    def test_VCD330_to_VCD430_pd(self):
        vcd330_file_name = "./etc/in/vcd330_sample_pd.json"
        myConverter = converter.ConverterVCD330toVCD430(vcd330_file_name)
        vcd = myConverter.get()

        if not os.path.isfile('./etc/vcd430_sample_pd.json'):
            vcd.save('./etc/vcd430_sample_pd.json', False)

    def test_VCD330_to_VCD430_semantics(self):
        vcd330_file_name = "./etc/in/vcd330_semantics_fw.json"
        myConverter = converter.ConverterVCD330toVCD430(vcd330_file_name)
        vcd = myConverter.get()

        if not os.path.isfile('./etc/vcd430_semantics_fw.json'):
            vcd.save('./etc/vcd430_semantics_fw.json', False)

    def test_VCD330_to_VCD430_mesh(self):
        vcd330_file_name = "./etc/in/vcd330_sample_mesh_short.json"
        myConverter = converter.ConverterVCD330toVCD430(vcd330_file_name)
        vcd = myConverter.get()

        if not os.path.isfile('./etc/vcd430_sample_mesh_short.json'):
            vcd.save('./etc/vcd430_sample_mesh_short.json', False)


    ###########################################################
    ### From VCD4 to VCD3.3
    ###########################################################
    # Converter from VCD 4.3.0 to VCD 3.3.0 (DMD)
    def test_VCD430_to_VCD330_dmd(self):
        vcd430_file_name = "./etc/in/vcd430_1_attm_03-08_ann.json"
        myConverter = converter.ConverterVCD430toVCD330(vcd430_file_name)
        vcd = myConverter.get()

        if not os.path.isfile('./etc/vcd330_1_attm_03-08_ann.json'):
            file = open('./etc/vcd330_1_attm03-08.json', 'w')
            file.write(json.dumps(vcd))
            file.close()

    # Converter from VCD 4.3.0 to VCD 3.3.0
    def test_VCD430_to_VCD330_3dod(self):
        vcd430_file_name = "./etc/vcd430_sample_3dod.json"
        myConverter = converter.ConverterVCD430toVCD330(vcd430_file_name)
        vcd = myConverter.get()

        if not os.path.isfile('./etc/vcd330_from_vcd430_sample_3dod.json'):
            file = open('./etc/vcd330_from_vcd430_sample_3dod.json', 'w')
            file.write(json.dumps(vcd))
            file.close()

    # Converter from VCD 4.3.0 to VCD 3.3.0
    def test_VCD430_to_VCD330_ls(self):
        vcd430_file_name = "./etc/vcd430_sample_ls.json"
        myConverter = converter.ConverterVCD430toVCD330(vcd430_file_name)
        vcd = myConverter.get()

        if not os.path.isfile('./etc/vcd330_from_vcd430_sample_ls.json'):
            file = open('./etc/vcd330_from_vcd430_sample_ls.json', 'w')
            file.write(json.dumps(vcd))
            file.close()

    # Converter from VCD 4.3.0 to VCD 3.3.0 (PD poly2d)
    def test_VCD430_to_VCD330_pd(self):
        vcd430_file_name = "./etc/vcd430_sample_pd.json"
        myConverter = converter.ConverterVCD430toVCD330(vcd430_file_name)
        vcd = myConverter.get()

        if not os.path.isfile('./etc/vcd330_from_vcd430_sample_pd.json'):
            file = open('./etc/vcd330_from_vcd430_sample_pd.json', 'w')
            file.write(json.dumps(vcd, indent=4, sort_keys=True))
            file.close()

    # Converter from VCD 4.3.0 to VCD 3.3.0
    def test_VCD430_to_VCD330_semantics(self):
        vcd430_file_name = "./etc/vcd430_semantics_fw.json"
        myConverter = converter.ConverterVCD430toVCD330(vcd430_file_name)
        vcd = myConverter.get()

        if not os.path.isfile('./etc/vcd330_from_vcd430_semantics_fw.json'):
            file = open('./etc/vcd330_from_vcd430_semantics_fw.json', 'w')
            file.write(json.dumps(vcd, indent=4, sort_keys=True))
            file.close()

    def test_VCD430_to_VCD330_mesh(self):
        vcd430_file_name = "./etc/vcd430_sample_mesh_short.json"
        myConverter = converter.ConverterVCD430toVCD330(vcd430_file_name)
        vcd = myConverter.get()

        if not os.path.isfile('./etc/vcd330_from_vcd430_sample_mesh_short.json'):
            file = open('./etc/vcd330_from_vcd430_sample_mesh_short.json', 'w')
            file.write(json.dumps(vcd, indent=4, sort_keys=True))
            file.close()


if __name__ == '__main__':  # This changes the command-line entry point to call unittest.main()
    print("Running " + os.path.basename(__file__))
    unittest.main()

