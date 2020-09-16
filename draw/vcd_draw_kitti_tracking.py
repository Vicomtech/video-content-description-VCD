"""
VCD (Video Content Description) library v4.3.0

Project website: http://vcd.vicomtech.org

Copyright (C) 2020, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.3.0.
VCD is distributed under MIT License. See LICENSE.

"""


import os
import sys
sys.path.insert(0, "..")
import screeninfo
import cv2 as cv
import numpy as np
import math
from vcd import core
from vcd import draw


def draw_kitti_tracking(sequence_number=0, record_video=False):
    # Get annotations
    # Run ../converters/kittiConverter/converter.py to generate the json files
    #vcd_file_name = "../tests/etc/vcd430_kitti_tracking_" + str(sequence_number).zfill(4) + ".json"
    vcd_file_name = "../converters/kittiConverter/etc/vcd430_kitti_tracking_" + str(sequence_number).zfill(4) + ".json"
    vcd = core.VCD(vcd_file_name)
    drawerTopView1 = draw.TopView(vcd, "vehicle-iso8855")
    drawerTopView2 = draw.TopView(vcd, "odom")
    drawerCamera = draw.Image(vcd)
    frameInfoDrawer = draw.FrameInfoDrawer(vcd)

    # Get the size of the screen
    screen = screeninfo.get_monitors()[0]

    # Get video
    video_file_name = "../../../../data/kitti/tracking/video/" + str(sequence_number).zfill(4) + ".mp4"
    video_cap = cv.VideoCapture(video_file_name)
    video_width = int(video_cap.get(cv.CAP_PROP_FRAME_WIDTH))
    video_height = int(video_cap.get(cv.CAP_PROP_FRAME_HEIGHT))

    cv.namedWindow('KITTI Tracking', cv.WINDOW_NORMAL)
    cv.moveWindow('KITTI Tracking', screen.x + screen.width // 8, screen.y + screen.height // 8)
    cv.resizeWindow('KITTI Tracking', (int(3 * screen.width / 4), int(3 * screen.height / 4)))

    # Prepare color map
    colorMap = {'Car': (0, 0, 255), 'Van': (255, 0, 0), 'Truck': (127, 127, 0),
                 'Pedestrian': (0, 255, 0), 'Person_sitting': (0, 127, 127),
                 'Tram': (127, 0, 127), 'Misc': (127, 127, 127), 'DontCare': (255, 255, 255),
                'Cyclist': (0, 127, 255),
                'Ego-car': (127, 127, 127)}
    imageParams = draw.Image.Params(_colorMap=colorMap,
                                    _draw_trajectory=False,
                                    _ignore_classes={"DontCare"})
    ar = video_width/(video_height*2)

    # Next values define which region of the selected coordinate_system is to be monitored by the TopView
    rangeX = (-5.0, 55.0)
    rangeY = (-((rangeX[1] - rangeX[0])/ar)/2, ((rangeX[1] - rangeX[0])/ar)/2)
    topviewParams1 = draw.TopView.Params(_colorMap=colorMap,
                                        _imgSize=(video_width, video_height*2),
                                        _background_color=255,
                                        _rangeX=rangeX,
                                        _rangeY=rangeY,
                                        _stepX=1.0, _stepY=1.0,
                                        _ignore_classes={"DontCare"})
    rangeX = (-5.0, 140.0)
    rangeY = (-((rangeX[1] - rangeX[0]) / ar) / 2, ((rangeX[1] - rangeX[0]) / ar) / 2)
    topviewParams2 = draw.TopView.Params(_colorMap=colorMap,
                                         _imgSize=(video_width, video_height * 2),
                                         _background_color=255,
                                         _rangeX=rangeX,
                                         _rangeY=rangeY,
                                         _stepX=5.0, _stepY=5.0,
                                         _ignore_classes={"DontCare"})

    # Video record
    if record_video:
        video_writer = cv.VideoWriter("kitti_tracking_vcd_" + str(sequence_number).zfill(4) + '.mp4',
                                      cv.VideoWriter_fourcc(*'mp4v'), 30.0, (video_width + 400, video_height*5))

    # Loop over video
    f = 0
    while(True):
        # Capture frame
        ret, img = video_cap.read()
        if ret is not True:
            cv.waitKey(0)
            break

        # Camera
        drawerCamera.draw(img, f, _params=imageParams)

        # Top View
        topView1 = drawerTopView1.draw(f, _params=topviewParams1)
        topView2 = drawerTopView2.draw(f, _params=topviewParams2)

        # VCD text viewer
        textImg = frameInfoDrawer.draw(f, cols=400, rows=video_height*5, _params=imageParams)

        # Stack
        stack1 = np.vstack((img, topView1))
        stack1 = np.vstack((stack1, topView2))
        outImg = np.hstack((stack1, textImg))
        cv.imshow('KITTI Tracking', outImg)
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
    print("Running " + os.path.basename(__file__))

    draw_kitti_tracking(sequence_number=0, record_video=False)


