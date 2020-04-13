"""
VCD (Video Content Description) library v4.1.0

Project website: http://vcd.vicomtech.org

Copyright (C) 2020, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.1.0.
VCD is distributed under MIT License. See LICENSE.

"""


import os

# Clean existing json or txt files at etc
dir_name = "./etc/"
test = os.listdir(dir_name)

for item in test:
    if item.endswith(".json") or item.endswith(".txt"):
        os.remove(os.path.join(dir_name, item))


os.system("python test_basic.py && "
          "python test_converters.py && "
          "python test_sanity.py && "
          "python test_serializer.py &&"
          "python test_mesh.py &&"
          "python test_image.py &&"
          "python test_stream_frame_properties.py")

# Clean existing json or txt files at etc
dir_name = "./etc/"
test = os.listdir(dir_name)

for item in test:
    if item.endswith(".json") or item.endswith(".txt"):
        os.remove(os.path.join(dir_name, item))