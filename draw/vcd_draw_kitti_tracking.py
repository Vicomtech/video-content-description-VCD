"""
VCD (Video Content Description) library v4.3.0

Project website: http://vcd.vicomtech.org

Copyright (C) 2020, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.3.0.
VCD is distributed under MIT License. See LICENSE.

"""


import copy
import os
import sys
sys.path.insert(0, "..")
import screeninfo
import cv2 as cv
import numpy as np
import math
from vcd import core
from vcd import draw
from vcd import scl


def draw_kitti_tracking(sequence_number=0, record_video=False):
    # Get annotations
    # Run ../converters/kittiConverter/converter.py to generate the json files
    #vcd_file_name = "../tests/etc/vcd430_kitti_tracking_" + str(sequence_number).zfill(4) + ".json"
    vcd_file_name = "../converters/kittiConverter/etc/vcd430_kitti_tracking_" + str(sequence_number).zfill(4) + ".json"
    vcd = core.VCD(vcd_file_name)
    scene = scl.Scene(vcd)  # scl.Scene has functions to project images, transforms, etc.

    drawerCamera = draw.Image(scene, "CAM_LEFT")
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
                 'Tram': (127, 0, 127), 'Misc': (127, 127, 127), 'DontCare': (0, 255, 255),
                'Cyclist': (0, 127, 255),
                'Ego-car': (127, 127, 127)}
    imageParams = draw.Image.Params(_colorMap=colorMap,
                                    _draw_trajectory=False,
                                    _ignore_classes={"DontCare"},
                                    _draw_types={"bbox", "cuboid"})
    ar = video_width/(video_height*2)

    # Next values define which region of the selected coordinate_system is to be monitored by the TopView
    rangeX = (-5.0, 55.0)
    rangeY = (-((rangeX[1] - rangeX[0])/ar)/2, ((rangeX[1] - rangeX[0])/ar)/2)
    topviewParams1 = draw.TopView.Params(colorMap=colorMap,
                                        topViewSize=(video_width, video_height*2),
                                        background_color=255,
                                        rangeX=rangeX,
                                        rangeY=rangeY,
                                        stepX=1.0, stepY=1.0,
                                        ignore_classes={"DontCare"})
    drawerTopView1 = draw.TopView(scene, "vehicle-iso8855", params=topviewParams1)
    rangeX = (0.0, 80.0)
    rangeY = (-5, 25) #(-((rangeX[1] - rangeX[0]) / ar) / 2, ((rangeX[1] - rangeX[0]) / ar) / 2)
    topviewParams2 = draw.TopView.Params(colorMap=colorMap,
                                         topViewSize=(video_width, video_height * 2),
                                         background_color=255,
                                         rangeX=rangeX,
                                         rangeY=rangeY,
                                         stepX=5.0, stepY=5.0,
                                         ignore_classes={"DontCare"},
                                         draw_only_current_image=False)
    drawerTopView2 = draw.TopView(scene, "odom", params=topviewParams2)

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

        # Top View
        drawerTopView1.add_images({'CAM_LEFT': img}, f)
        topView1 = drawerTopView1.draw(frameNum=f)
        drawerTopView2.add_images({'CAM_LEFT': img}, f)
        topView2 = drawerTopView2.draw(frameNum=f)

        # Camera
        img_out = copy.deepcopy(img)
        drawerCamera.draw(img_out, f, _params=imageParams)

        # VCD text viewer
        textImg = frameInfoDrawer.draw(f, cols=400, rows=video_height*5, _params=imageParams)

        # Stack
        stack1 = np.vstack((img_out, topView1))
        stack1 = np.vstack((stack1, topView2))
        mosaic = np.hstack((stack1, textImg))
        cv.imshow('KITTI Tracking', mosaic)
        cv.waitKey(1)

        if record_video:
            video_writer.write(mosaic)

        # Update frame num
        f += 1

    video_cap.release()
    if record_video:
        video_writer.release()
    cv.destroyAllWindows()


if __name__ == "__main__":
    print("Running " + os.path.basename(__file__))

    draw_kitti_tracking(sequence_number=0, record_video=False)


