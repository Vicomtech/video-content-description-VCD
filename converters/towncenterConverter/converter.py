"""
VCD (Video Content Description) library v4.0.0

Project website: http://vcd.vicomtech.org

Copyright (C) 2020, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.0.0.
VCD is distributed under MIT License. See LICENSE.

"""

import csv
import os
import sys
sys.path.insert(0, "../..")

import vcd.core as core
import vcd.types as types
import vcd.serializer as serializer


def convert_town_center_to_VCD4():
    if not os.path.isfile('./etc/TownCentreXVID_groundTruth.top'):
        import urllib.request
        url = 'https://www.robots.ox.ac.uk/ActiveVision/Research/Projects/2009bbenfold_headpose/Datasets/TownCentre-groundtruth.top'
        urllib.request.urlretrieve(url, './etc/TownCentreXVID_groundTruth.top')

    orig_file_name = "./etc/TownCentreXVID_groundTruth.top"
    vcd = core.VCD()
    with open(orig_file_name, newline='') as csvfile:
        my_reader = csv.reader(csvfile, delimiter=',')
        for row in my_reader:
            personNumber = int(row[0])
            frameNumber = int(row[1])
            headValid = int(row[2])
            bodyValid = int(row[3])

            headLeft = float(row[4])
            headTop = float(row[5])
            headRight = float(row[6])
            headBottom = float(row[7])

            headWidth = float((int(1000*headRight) - int(1000*headLeft))/1000)
            headHeight = float((int(1000*headBottom) - int(1000*headTop))/1000)

            bodyLeft = float(row[8])
            bodyTop = float(row[9])
            bodyRight = float(row[10])
            bodyBottom = float(row[11])

            bodyWidth = float((int(1000*bodyRight) - int(1000*bodyLeft))/1000)
            bodyHeight = float((int(1000*bodyBottom) - int(1000*bodyTop))/1000)

            body = types.bbox(name="body",
                              val=(bodyLeft, bodyTop, bodyWidth, bodyHeight))
            head = types.bbox("head", (headLeft, headTop, headWidth, headHeight))
            if not vcd.has(core.ElementType.object, personNumber):
                vcd.add_object(name="", semantic_type="Pedestrian",
                               uid=personNumber)
                if bodyValid:
                    vcd.add_object_data(personNumber, body, frameNumber)
                if headValid:
                    vcd.add_object_data(personNumber, head, frameNumber)
            else:
                if bodyValid:
                    vcd.add_object_data(personNumber, body, frameNumber)
                if headValid:
                    vcd.add_object_data(personNumber, head, frameNumber)

    vcd_json_file_name = "./etc/vcd400_towncenter.json"
    vcd.save(vcd_json_file_name, False)

    vcd_proto_file_name = "./etc/vcd400_proto_towncenter.txt"
    serializer.json2proto_bin(vcd_json_file_name, vcd_proto_file_name)


if __name__ == '__main__':  # This changes the command-line entry point to call unittest.main()
    convert_town_center_to_VCD4()

