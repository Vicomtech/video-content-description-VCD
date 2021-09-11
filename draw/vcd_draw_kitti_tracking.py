"""
VCD (Video Content Description) library v4.3.1

Project website: http://vcd.vicomtech.org

Copyright (C) 2021, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.3.1.
VCD is distributed under MIT License. See LICENSE.

"""


import copy
import os
import sys
sys.path.insert(0, "..")
#import screeninfo
import cv2 as cv
import numpy as np
import math
from vcd import core
from vcd import draw
from vcd import scl
from vcd import schema

openlabel_version_name = "openlabel" + schema.openlabel_schema_version.replace(".", "")
vcd_version_name = openlabel_version_name

def draw_kitti_tracking(sequence_number, record_video, draw_images):
    # Get annotations
    # Run ../converters/kittiConverter/converter.py to generate the json files
    #vcd_file_name = "../tests/etc/vcd430_kitti_tracking_" + str(sequence_number).zfill(4) + ".json"
    vcd_file_name = "../converters/kittiConverter/etc/" + vcd_version_name + "_kitti_tracking_" + str(sequence_number).zfill(4) + ".json"
    vcd = core.VCD(vcd_file_name)
    scene = scl.Scene(vcd)  # scl.Scene has functions to project images, transforms, etc.

    drawerCameraLeft = draw.Image(scene, "CAM_LEFT")
    drawerCameraRight = draw.Image(scene, "CAM_RIGHT")
    
    frameInfoDrawer = draw.FrameInfoDrawer(vcd)

    # Get the size of the screen
    #screen = screeninfo.get_monitors()[0]    

    # Get video
    video_file_name_left = "../../../../data/kitti/tracking/video/left/" + str(sequence_number).zfill(4) + ".mp4"
    video_file_name_right = "../../../../data/kitti/tracking/video/right/" + str(sequence_number).zfill(4) + ".mp4"
    video_cap_left = cv.VideoCapture(video_file_name_left)
    video_cap_right = cv.VideoCapture(video_file_name_right)
    video_width = int(video_cap_left.get(cv.CAP_PROP_FRAME_WIDTH))
    video_height = int(video_cap_left.get(cv.CAP_PROP_FRAME_HEIGHT))

    cv.namedWindow('KITTI Tracking', cv.WINDOW_NORMAL)
    screen_width = 1920
    screen_height = 1080
    cv.moveWindow('KITTI Tracking', screen_width // 8, screen_height // 8)
    cv.resizeWindow('KITTI Tracking', (int(3 * screen_width / 4), int(3 * screen_height / 4)))
    #cv.moveWindow('KITTI Tracking', screen.x + screen.width // 8, screen.y + screen.height // 8)
    #cv.resizeWindow('KITTI Tracking', (int(3 * screen.width / 4), int(3 * screen.height / 4)))

    # Prepare color map
    colorMap = {'Car': (0, 0, 255), 'Van': (255, 0, 0), 'Truck': (127, 127, 0),
                 'Pedestrian': (0, 255, 0), 'Person_sitting': (0, 127, 127),
                 'Tram': (127, 0, 127), 'Misc': (127, 127, 127), 'DontCare': (0, 255, 255),
                'Cyclist': (0, 127, 255),
                'Egocar': (127, 127, 127)}
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
    if sequence_number == 0:
        rangeX = (0.0, 80.0)
        rangeY = (-25, 25)
    elif sequence_number == 3:
        rangeX = (0.0, 250.0)
        rangeY = (-25, 25)
    elif sequence_number == 5:
        rangeX = (0.0, 500.0)
        rangeY = (-5, 50)

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
                                      cv.VideoWriter_fourcc(*'mp4v'), 30.0, (video_width + 400, video_height*6))

    # Loop over video
    f = 0
    while(True):
        # Capture frame
        ret_left, img_left = video_cap_left.read()
        ret_right, img_right = video_cap_right.read()
        if (ret_left or ret_right) is not True:
            cv.waitKey(0)
            break

        # Top View
        if draw_images:
            drawerTopView1.add_images({'CAM_LEFT': img_left}, f)
        topView1 = drawerTopView1.draw(frameNum=f)
        if draw_images:
            drawerTopView2.add_images({'CAM_LEFT': img_left}, f)
        topView2 = drawerTopView2.draw(frameNum=f)

        # Camera
        img_out_left = copy.deepcopy(img_left)
        img_out_right = copy.deepcopy(img_right)
        drawerCameraLeft.draw(img_out_left, f, _params=imageParams)
        drawerCameraRight.draw(img_out_right, f, _params=imageParams)

        # VCD text viewer
        textImg = frameInfoDrawer.draw(f, cols=400, rows=video_height*6, _params=imageParams)

        # Stack
        stack1 = np.vstack((img_out_left, img_out_right))
        stack1 = np.vstack((stack1, topView1))
        stack1 = np.vstack((stack1, topView2))
        mosaic = np.hstack((stack1, textImg))
        cv.imshow('KITTI Tracking', mosaic)
        cv.waitKey(0)

        if record_video:
            video_writer.write(mosaic)

        # Update frame num
        f += 1

    video_cap_left.release()
    video_cap_right.release()
    if record_video:
        video_writer.release()
    cv.destroyAllWindows()


if __name__ == "__main__":
    print("Running " + os.path.basename(__file__))

    draw_kitti_tracking(sequence_number=0, record_video=False, draw_images=True)


