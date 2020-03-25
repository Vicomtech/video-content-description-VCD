"""
VCD (Video Content Description) library v4.0.0

Project website: http://vcd.vicomtech.org

Copyright (C) 2020, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.0.0.
VCD is distributed under MIT License. See LICENSE.

"""


import sys
sys.path.insert(0, "..")
import screeninfo
import cv2 as cv
from vcd import core
from vcd import draw

def draw_kitti_tracking(num):
    #vcd = core.VCD("./json/vcd400_kitti_tracking_0000.json")
    # Get annotations
    vcd_file_name = "../converters/kittiConverter/etc/vcd400_kitti_tracking_" + str(num).zfill(4) + ".json"
    vcd = core.VCD(vcd_file_name)
    drawerTopView = draw.TopView(vcd)
    drawerCamera = draw.Image(vcd)
    textDrawer = draw.TextDrawer()

    # Get the size of the screen
    screen = screeninfo.get_monitors()[0]

    # Get video
    video_file_name = "../../../../data/kitti/tracking/" + str(num).zfill(4) + ".avi"
    video_cap = cv.VideoCapture(video_file_name)

    # Prepare Top View image
    cv.namedWindow('Top view', cv.WINDOW_NORMAL)
    cv.moveWindow('Top view', screen.x + screen.width//8, screen.y + screen.height // 8)
    cv.resizeWindow('Top view', (int(3 * screen.width / 4), int(3 * screen.height / 4)))

    #cv.namedWindow('Camera', cv.WINDOW_NORMAL)
    #cv.moveWindow('Camera', screen.x + screen.width // 8, screen.y + screen.height // 8)
    #cv.resizeWindow('Camera', (int(3 * screen.width / 4), int(3 * screen.height / 4)))

    # Prepare color map
    colorMap = {'Car': (0, 0, 255), 'Van': (255, 0, 0), 'Truck': (127, 127, 0),
                 'Pedestrian': (0, 255, 0), 'Person_sitting': (0, 127, 127),
                 'Tram': (127, 0, 127), 'Misc': (127, 127, 127), 'DontCare': (255, 255, 255)}
    imageParams = draw.Image.Params(_colorMap=colorMap)
    topviewParams = draw.TopView.Params(_colorMap=colorMap)

    # Loop over video
    f = 0
    while(True):
        # Capture frame
        ret, img = video_cap.read()
        if ret != True:
            break

        rows, cols, depth = img.shape

        # Camera
        drawerCamera.draw(img, f, _params=imageParams)
        cv.imshow('Camera', img)

        # Top View
        topView = drawerTopView.draw(f, _params=topviewParams)
        cv.imshow('Top view', topView)

        # VCD text viewer
        textImg = textDrawer.draw(vcd.stringify_frame(f, pretty=False))
        cv.imshow('VCD Frame', textImg)
        cv.waitKey(0)

        # Update frame num
        f += 1

    cv.destroyAllWindows()


if __name__ == "__main__":
    draw_kitti_tracking(2)

