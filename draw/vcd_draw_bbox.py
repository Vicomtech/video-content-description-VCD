"""
VCD (Video Content Description) library v4.3.1

Project website: http://vcd.vicomtech.org

Copyright (C) 2021, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.3.1.
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

def draw_bboxes(vcd_file_name, image_file_name, save_image):
    # Get annotations
    vcd = core.VCD(vcd_file_name)
    scene = scl.Scene(vcd)

    drawerCamera = draw.Image(scene)
    #textDrawer = draw.TextDrawer()
    frameInfoDrawer = draw.FrameInfoDrawer(vcd)

    # Get the size of the screen
    screen = screeninfo.get_monitors()[0]

    # Get image
    img = cv.imread(image_file_name)
    height, width = img.shape[:2]

    cv.namedWindow('Bounding boxes', cv.WINDOW_NORMAL)
    cv.moveWindow('Bounding boxes', screen.x + screen.width // 8, screen.y + screen.height // 8)
    cv.resizeWindow('Bounding boxes', (int(3 * screen.width / 4), int(3 * screen.height / 4)))

    # Prepare color map
    colorMap = {'Car': (0, 230, 118), 'Bus': (143, 131, 0), 'Semaphore': (0, 171, 255), 'ZebraCross': (91, 24, 194)}
    imageParams = draw.Image.Params(_colorMap=colorMap)

    # Camera
    drawerCamera.draw(_img=img, _frameNum=None, _params=imageParams)

    # VCD text viewer
    #textImg = textDrawer.draw(vcd.stringify_frame(f, pretty=False), cols=400, rows=video_height)
    textImg = frameInfoDrawer.draw(_frameNum=None, cols=400, rows=height, _params=imageParams)

    if save_image:
        cv.imwrite("./png/bboxes.png", img)

    # Stack
    outImg = np.hstack((img, textImg))
    cv.imshow('Bounding boxes', outImg)

    cv.waitKey(0)
    cv.destroyAllWindows()


if __name__ == "__main__":
    vcd_file_name = "../tests/etc/" + openlabel_version_name + "_test_bbox_simple.json"
    image_file_name = "./etc/sample_bbox.png"
    draw_bboxes(vcd_file_name=vcd_file_name, image_file_name=image_file_name, save_image=False)

    vcd_file_name = "../tests/etc/" + openlabel_version_name + "_test_bbox_simple_attributes.json"
    image_file_name = "./etc/sample_bbox.png"
    draw_bboxes(vcd_file_name=vcd_file_name, image_file_name=image_file_name, save_image=False)


