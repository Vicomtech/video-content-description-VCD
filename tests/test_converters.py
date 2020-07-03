"""
VCD (Video Content Description) library v4.2.1

Project website: http://vcd.vicomtech.org

Copyright (C) 2020, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.2.1.
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
    ### From VCD3.3 to VCD4.1
    ###########################################################
    # Converter from VCD 3.3.0 to VCD 4.2.1 (3DOD cuboids)
    def test_VCD330_to_VCD421_3dod(self):
        vcd330_file_name = "./etc/in/vcd330_sample_3dod.json"
        myConverter = converter.ConverterVCD330toVCD421(vcd330_file_name)
        vcd = myConverter.get()

        if not os.path.isfile('./etc/vcd421_sample_3dod.json'):
            vcd.save('./etc/vcd421_sample_3dod.json', False)

    # Converter from VCD 3.3.0 to VCD 4.2.1 (LS poly3d)
    def test_VCD330_to_VCD421_ls(self):
        vcd330_file_name = "./etc/in/vcd330_sample_ls.json"
        myConverter = converter.ConverterVCD330toVCD421(vcd330_file_name)
        vcd = myConverter.get()

        if not os.path.isfile('./etc/vcd421_sample_ls.json'):
            vcd.save('./etc/vcd421_sample_ls.json', False)

    # Converter from VCD 3.3.0 to VCD 4.2.1 (PD poly2d)
    def test_VCD330_to_VCD421_pd(self):
        vcd330_file_name = "./etc/in/vcd330_sample_pd.json"
        myConverter = converter.ConverterVCD330toVCD421(vcd330_file_name)
        vcd = myConverter.get()

        if not os.path.isfile('./etc/vcd421_sample_pd.json'):
            vcd.save('./etc/vcd421_sample_pd.json', False)

    def test_VCD330_to_VCD421_KITTI_tracking(self):
        vcd330_file_name = "./etc/in/vcd330_kitti_tracking_0_fw.json"
        myConverter = converter.ConverterVCD330toVCD421(vcd330_file_name)
        vcd = myConverter.get()

        if not os.path.isfile('./etc/vcd421_kitti_tracking_0_from_vcd330fw.json'):
            vcd.save('./etc/vcd421_kitti_tracking_0_from_vcd330fw.json', False)

    def test_VCD330_to_VCD421_semantics(self):
        vcd330_file_name = "./etc/in/vcd330_semantics_fw.json"
        myConverter = converter.ConverterVCD330toVCD421(vcd330_file_name)
        vcd = myConverter.get()

        if not os.path.isfile('./etc/vcd421_semantics_fw.json'):
            vcd.save('./etc/vcd421_semantics_fw.json', False)

    def test_VCD330_to_VCD421_mesh(self):
        vcd330_file_name = "./etc/in/vcd330_sample_mesh_short.json"
        myConverter = converter.ConverterVCD330toVCD421(vcd330_file_name)
        vcd = myConverter.get()

        if not os.path.isfile('./etc/vcd421_sample_mesh_short.json'):
            vcd.save('./etc/vcd421_sample_mesh_short.json', False)


    ###########################################################
    ### From VCD4 to VCD3.3
    ###########################################################
    # Converter from VCD 3.3.0 to VCD 4.2.1 (DMD)
    def test_VCD421_to_VCD330_dmd(self):
        vcd421_file_name = "./etc/in/vcd421_1_attm03-08.json"
        myConverter = converter.ConverterVCD421toVCD330(vcd421_file_name)
        vcd = myConverter.get()

        if not os.path.isfile('./etc/vcd330_1_attm03-08.json'):
            file = open('./etc/vcd330_1_attm03-08.json', 'w')
            file.write(json.dumps(vcd))
            file.close()

    # Converter from VCD 3.3.0 to VCD 4.2.1
    def test_VCD421_to_VCD330_3dod(self):
        vcd421_file_name = "./etc/vcd421_sample_3dod.json"
        myConverter = converter.ConverterVCD421toVCD330(vcd421_file_name)
        vcd = myConverter.get()

        if not os.path.isfile('./etc/vcd330_from_vcd421_sample_3dod.json'):
            file = open('./etc/vcd330_from_vcd421_sample_3dod.json', 'w')
            file.write(json.dumps(vcd))
            file.close()

    # Converter from VCD 3.3.0 to VCD 4.2.1
    def test_VCD421_to_VCD330_ls(self):
        vcd421_file_name = "./etc/vcd421_sample_ls.json"
        myConverter = converter.ConverterVCD421toVCD330(vcd421_file_name)
        vcd = myConverter.get()

        if not os.path.isfile('./etc/vcd330_from_vcd421_sample_ls.json'):
            file = open('./etc/vcd330_from_vcd421_sample_ls.json', 'w')
            file.write(json.dumps(vcd))
            file.close()

    # Converter from VCD 3.3.0 to VCD 4.2.1 (PD poly2d)
    def test_VCD421_to_VCD330_pd(self):
        vcd421_file_name = "./etc/vcd421_sample_pd.json"
        myConverter = converter.ConverterVCD421toVCD330(vcd421_file_name)
        vcd = myConverter.get()

        if not os.path.isfile('./etc/vcd330_from_vcd421_sample_pd.json'):
            file = open('./etc/vcd330_from_vcd421_sample_pd.json', 'w')
            file.write(json.dumps(vcd, indent=4, sort_keys=True))
            file.close()

    # Converter from VCD 3.3.0 to VCD 4.2.1
    def test_VCD421_to_VCD330_semantics(self):
        vcd421_file_name = "./etc/vcd421_semantics_fw.json"
        myConverter = converter.ConverterVCD421toVCD330(vcd421_file_name)
        vcd = myConverter.get()

        if not os.path.isfile('./etc/vcd330_from_vcd421_semantics_fw.json'):
            file = open('./etc/vcd330_from_vcd421_semantics_fw.json', 'w')
            file.write(json.dumps(vcd, indent=4, sort_keys=True))
            file.close()

    def test_VCD421_to_VCD330_mesh(self):
        vcd421_file_name = "./etc/vcd421_sample_mesh_short.json"
        myConverter = converter.ConverterVCD421toVCD330(vcd421_file_name)
        vcd = myConverter.get()

        if not os.path.isfile('./etc/vcd330_from_vcd421_sample_mesh_short.json'):
            file = open('./etc/vcd330_from_vcd421_sample_mesh_short.json', 'w')
            file.write(json.dumps(vcd, indent=4, sort_keys=True))
            file.close()


if __name__ == '__main__':  # This changes the command-line entry point to call unittest.main()
    print("Running " + os.path.basename(__file__))
    unittest.main()

