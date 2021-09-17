"""
VCD (Video Content Description) library v5.0.0

Project website: http://vcd.vicomtech.org

Copyright (C) 2021, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 5.0.0.
VCD is distributed under MIT License. See LICENSE.

"""


import sys
sys.path.insert(0, "..")
import screeninfo
import cv2 as cv
import numpy as np

import vcd.core as core
import vcd.draw as draw
import vcd.scl as scl
import vcd.schema as schema

openlabel_version_name = "openlabel" + schema.openlabel_schema_version.replace(".", "")
vcd_version_name = openlabel_version_name

def draw_towncentre(record_video=False):
    # Get annotations
    # Run ../converters/towncenterConverter/converter.py to generate the json files
    vcd_file_name = "../converters/towncenterConverter/etc/" + vcd_version_name + "_towncenter.json"
    vcd = core.VCD(vcd_file_name)
    scene = scl.Scene(vcd)

    drawerCamera = draw.Image(scene)
    #textDrawer = draw.TextDrawer()
    frameInfoDrawer = draw.FrameInfoDrawer(vcd)

    # Get the size of the screen
    screen = screeninfo.get_monitors()[0]

    # Get video
    video_file_name = "../../../../data/TownCentre/TownCentreXVID.avi"
    video_cap = cv.VideoCapture(video_file_name)
    video_width = int(video_cap.get(cv.CAP_PROP_FRAME_WIDTH))
    video_height = int(video_cap.get(cv.CAP_PROP_FRAME_HEIGHT))

    cv.namedWindow('TownCentre', cv.WINDOW_NORMAL)
    cv.moveWindow('TownCentre', screen.x + screen.width // 8, screen.y + screen.height // 8)
    cv.resizeWindow('TownCentre', (int(3 * screen.width / 4), int(3 * screen.height / 4)))

    # Prepare color map
    colorMap = {'Car': (0, 0, 255), 'Van': (255, 0, 0), 'Truck': (127, 127, 0),
                 'Pedestrian': (0, 255, 0), 'Person_sitting': (0, 127, 127),
                 'Tram': (127, 0, 127), 'Misc': (127, 127, 127), 'DontCare': (255, 255, 255)}
    imageParams = draw.Image.Params(_colorMap=colorMap,
                                    _draw_trajectory=True)
    ar = video_width/(video_height*2)

    # Video record
    if record_video:
        video_writer = cv.VideoWriter("towncentre_vcd.mp4",
                                      cv.VideoWriter_fourcc(*'mp4v'), 30.0, (video_width + 400, video_height*3))

    # Loop over video
    f = 0
    while True:
        # Capture frame
        ret, img = video_cap.read()
        if ret is not True:
            break

        # Camera
        drawerCamera.draw(img, f, _params=imageParams)

        # VCD text viewer
        #textImg = textDrawer.draw(vcd.stringify_frame(f, pretty=False), cols=400, rows=video_height)
        textImg = frameInfoDrawer.draw(f, cols=400, rows=video_height, _params=imageParams)


        # Stack
        outImg = np.hstack((img, textImg))
        cv.imshow('TownCentre', outImg)
        cv.waitKey(1)

        if record_video:
            video_writer.write(outImg)

        # Update frame num
        f += 1

    video_cap.release()
    if record_video:
        video_writer.release()
    cv.destroyAllWindows()


if __name__ == "__main__":
    draw_towncentre(record_video=False)


