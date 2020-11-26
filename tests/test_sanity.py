"""
VCD (Video Content Description) library v4.3.0

Project website: http://vcd.vicomtech.org

Copyright (C) 2020, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.3.0.
VCD is distributed under MIT License. See LICENSE.

"""


import unittest
import vcd.core as core
import vcd.sanity as sanity


class TestBasic(unittest.TestCase):
    def test_sanity_frame_intervals(self):
        vcd_file_name = "./etc/vcd430_sample_3dod.json"
        vcd = core.VCD(vcd_file_name, validation=True)
        valid = sanity.check_frame_intervals(vcd)
        self.assertEqual(valid, True)

    def test_sanity_frames_elements(self):
        vcd_file_name = "./etc/vcd430_sample_3dod.json"
        vcd = core.VCD(vcd_file_name, validation=True)
        valid = sanity.check_frames_elements(vcd)
        self.assertEqual(valid, True)


if __name__ == '__main__':  # This changes the command-line entry point to call unittest.main()
    print("Running test_sanity.py...")
    unittest.main()