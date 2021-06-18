"""
VCD (Video Content Description) library v4.3.1

Project website: http://vcd.vicomtech.org

Copyright (C) 2021, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.3.1.
VCD is distributed under MIT License. See LICENSE.

"""

import subprocess

# Clean existing json or txt files at etc
dir_name = "./etc/"

subprocess.check_call(["python.exe", "test_basic.py"])
subprocess.check_call(["python.exe", "test_converters.py"])
subprocess.check_call(["python.exe", "test_mesh.py"])
subprocess.check_call(["python.exe", "test_image.py"])
subprocess.check_call(["python.exe", "test_stream_frame_properties.py"])
subprocess.check_call(["python.exe", "test_action_properties.py"])
subprocess.check_call(["python.exe", "test_semantics.py"])
subprocess.check_call(["python.exe", "test_modify.py"])
subprocess.check_call(["python.exe", "test_geometries.py"])
subprocess.check_call(["python.exe", "test_openlabel_labeling.py"])
subprocess.check_call(["python.exe", "test_openlabel_tagging.py"])
subprocess.check_call(["python.exe", "test_uuid.py"])
subprocess.check_call(["python.exe", "test_bbox.py"])

