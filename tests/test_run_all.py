"""
VCD (Video Content Description) library v4.3.1

Project website: http://vcd.vicomtech.org

Copyright (C) 2021, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.3.1.
VCD is distributed under MIT License. See LICENSE.

"""


import os

# Clean existing json or txt files at etc
dir_name = "./etc/"
test = os.listdir(dir_name)

os.system("python test_basic.py && "
          "python test_converters.py && "
          #"python test_sanity.py && "
          # "python test_serializer.py &&"
          "python test_mesh.py &&"
          "python test_image.py &&"
          "python test_stream_frame_properties.py &&"
          "python test_action_properties.py &&"
          "python test_semantics.py &&"
          "python test_modify.py &&"
          "python test_geometries.py")

