"""
VCD (Video Content Description) library v4.0.0

Project website: http://vcd.vicomtech.org

Copyright (C) 2020, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.0.0.
VCD is distributed under MIT License. See LICENSE.

"""

import csv
import sys
import os
sys.path.insert(0, "../..")

import glob

import vcd.core as core
import vcd.types as types
import vcd.serializer as serializer

def float_2dec(val):
    return float((int(100*val))/100)

def convert_KITTI_object_to_VCD4():
    vcd_json_file_name = "./etc/vcd400_kitti_object.json"
    vcd_proto_file_name = "./etc/vcd400_proto_kitti_object.txt"
    if os.path.isfile(vcd_json_file_name) and os.path.isfile(vcd_proto_file_name):
        return

    vcd = core.VCD()
    list_files = glob.glob("../../../../../data/kitti/object/training/label_2/*.txt")
    frameNum = 0
    for file in list_files:
        with open(file, newline='') as csvfile:
            my_reader = csv.reader(csvfile, delimiter=' ')
            for row in my_reader:
                semantic_class = row[0]
                truncated = float_2dec(float(row[1]))
                occluded = int(row[2])
                alpha = float_2dec(float(row[3]))

                left = float_2dec(float(row[4]))
                top = float_2dec(float(row[5]))
                width = float_2dec(float(row[6]) - left)
                height = float_2dec(float(row[7]) - top)

                dimHeight = float_2dec(float(row[8]))
                dimWidth = float_2dec(float(row[9]))
                dimLength = float_2dec(float(row[10]))

                locX = float_2dec(float(row[11]))
                locY = float_2dec(float(row[12]))
                locZ = float_2dec(float(row[13]))

                rotY = float_2dec(float(row[14]))

                bounding_box = types.bbox(name="", val=(left, top, width, height))
                cuboid = types.cuboid(name="", val=(locX, locY, locZ, dimHeight, dimWidth, dimLength, 0, rotY, 0))

                uid = vcd.add_object(name="", semantic_type=semantic_class)
                vcd.add_object_data(uid, bounding_box, frameNum)
                vcd.add_object_data(uid, cuboid, frameNum)
                vcd.add_object_data(uid, types.num(name="truncated", val=truncated), frameNum)
                vcd.add_object_data(uid, types.num(name="occluded", val=occluded), frameNum)
                vcd.add_object_data(uid, types.num(name="alpha", val=alpha), frameNum)

                frameNum += 1

    vcd.save(vcd_json_file_name, False)
    serializer.json2proto_bin(vcd_json_file_name, vcd_proto_file_name)


def convert_KITTI_tracking_to_VCD4():
    list_files = glob.glob("../../../../../data/kitti/tracking/training/label_02/*.txt")

    count = 0
    for file in list_files:
        vcd = core.VCD()
        with open(file, newline='') as csvfile:
            my_reader = csv.reader(csvfile, delimiter=' ')
            for row in my_reader:
                frameNum = int(row[0])
                trackID = int(row[1]) + 1  # VCD can't handle negative ids

                semantic_class = row[2]
                truncated = float_2dec(float(row[3]))
                occluded = int(row[4])
                alpha = float_2dec(float(row[5]))

                left = float_2dec(float(row[6]))
                top = float_2dec(float(row[7]))
                width = float_2dec(float(row[8]) - left)
                height = float_2dec(float(row[9]) - top)

                dimHeight = float_2dec(float(row[10]))
                dimWidth = float_2dec(float(row[11]))
                dimLength = float_2dec(float(row[12]))

                locX = float_2dec(float(row[13]))
                locY = float_2dec(float(row[14]))
                locZ = float_2dec(float(row[15]))

                rotY = float_2dec(float(row[16]))

                bounding_box = types.bbox(name="", val=(left, top, width, height))
                cuboid = types.cuboid(name="", val=(locX, locY, locZ, dimHeight, dimWidth, dimLength, 0, rotY, 0))

                if not vcd.has(core.ElementType.object, trackID):
                    vcd.add_object(name="", semantic_type=semantic_class, uid=trackID)

                vcd.add_object_data(trackID, bounding_box, frameNum)
                vcd.add_object_data(trackID, cuboid, frameNum)
                vcd.add_object_data(trackID, types.num(name="truncated", val=truncated), frameNum)
                vcd.add_object_data(trackID, types.num(name="occluded", val=occluded), frameNum)
                vcd.add_object_data(trackID, types.num(name="alpha", val=alpha), frameNum)

        vcd_json_file_name = "./etc/vcd400_kitti_tracking_" + str(count).zfill(4) + ".json"
        vcd.save(vcd_json_file_name, False)

        vcd_proto_file_name = "./etc/vcd400_proto_kitti_tracking_" + str(count).zfill(4) + ".txt"
        serializer.json2proto_bin(vcd_json_file_name, vcd_proto_file_name)

        count += 1

if __name__ == '__main__':  # This changes the command-line entry point to call unittest.main()
    convert_KITTI_object_to_VCD4()
    convert_KITTI_tracking_to_VCD4()

