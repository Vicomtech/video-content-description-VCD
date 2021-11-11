"""
VCD (Video Content Description) library v5.0.1

Project website: http://vcd.vicomtech.org

Copyright (C) 2021, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 5.0.1.
VCD is distributed under MIT License. See LICENSE.

"""

import os
import cv2 as cv
import numpy as np
from vcd import core
from vcd import types
from vcd import utils
from vcd import draw
from vcd import scl

import matplotlib.pyplot as plt

#vcd.save('./etc/' + openlabel_version_name + '_test_scl_camera_projection.json')

def read_camera_pinhole():
    fs = cv.FileStorage("./etc/pinhole_camera.yml", cv.FILE_STORAGE_READ)
    image_width = fs.getNode("image_width").real()
    image_height = fs.getNode("image_height").real()
    camera_matrix = fs.getNode("camera_matrix").mat()
    distortion_coefficients = fs.getNode("distortion_coefficients").mat()

    vcd = core.OpenLABEL()
    vcd.add_coordinate_system(name="camera_pinhole", cs_type=types.CoordinateSystemType.sensor_cs)
    vcd.add_stream(stream_name='camera_pinhole', uri='', description='USB camera with radial distortion', stream_type=core.StreamType.camera)
    vcd.add_stream_properties(stream_name="camera_pinhole", intrinsics=types.IntrinsicsPinhole(
        width_px=int(image_width),
        height_px=int(image_height),
        camera_matrix_3x4=utils.fromCameraMatrix3x3toCameraMatrix3x4(camera_matrix).flatten().tolist(),
        distortion_coeffs_1xN=distortion_coefficients.flatten().tolist()
    ))
    return vcd


def draw_scene(vcd):
    # Prepare objects
    scene = scl.Scene(vcd)  # scl.Scene has functions to project images, transforms, etc.
    drawer_front = draw.Image(scene, "camera_pinhole")

    # Draw the images
    img_front = cv.imread('./png/pinhole/pinhole_camera_0.png')
    drawer_front.draw(img_front)

    # Undistort
    cam_front = scene.get_camera("camera_pinhole", compute_remaps=True)
    img_front_und = cam_front.undistort_image(img_front)
    
    cv.namedWindow("camera_pinhole", cv.WINDOW_NORMAL)
    cv.imshow("camera_pinhole", img_front)
    cv.namedWindow("camera_pinhole undistorted", cv.WINDOW_NORMAL)
    cv.imshow("camera_pinhole undistorted", img_front_und)    
    cv.waitKey(0)


if __name__ == '__main__':
    print("Running " + os.path.basename(__file__))
    vcd = read_camera_pinhole()
    draw_scene(vcd)
