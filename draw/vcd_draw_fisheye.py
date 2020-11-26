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
from vcd import types
from vcd import utils
from vcd import draw
from vcd import scl

from draw import vcd_draw_pinhole

import matplotlib.pyplot as plt


def simple_setup_4_cams_fisheye():
    vcd = core.VCD()
    vcd.add_coordinate_system("vehicle-iso8855", cs_type=types.CoordinateSystemType.local_cs)

    # Let's build the cameras
    img_width_px = 1280
    img_height_px = 966
    cX = -0.302159995
    cY = -3.44617009
    ################################
    # CAM_FRONT
    ################################
    # Intrinsics
    # ------------------------------
    # This matrix converts from scs to ics
    d_1x4 = np.array([333.437012, 0.307729989, 2.4235599, 11.0495005])

    # Extrinsics
    # ------------------------------
    # Extrinsics (1/2): Rotation using yaw(Z), pitch(Y), roll(X). This is rotation of SCS wrt LCS
    pitch_rad = (10.0 * np.pi) / 180.0
    yaw_rad = (0.0 * np.pi) / 180.0
    roll_rad = (0.0 * np.pi) / 180.0
    R_scs_wrt_lcs = utils.euler2R([yaw_rad, pitch_rad, roll_rad])  # default is ZYX
    C_lcs = np.array([[2.3],  # frontal part of the car
                      [0.0],  # centered in the symmetry axis of the car
                      [1.3]])  # at some height over the ground

    P_scs_wrt_lcs = utils.create_pose(R_scs_wrt_lcs, C_lcs)

    # As explained in core.py, a pose matrix of scs wrt lcs can be also seen as the inverse transformation from lcs to scs
    T_lcs_to_scs = utils.inv(P_scs_wrt_lcs)

    # Extrinsics (2/2): Additional rotation, because usually cameras scs are (x-to-right, y-down, z-to-front)
    # to match better with ics (x-to-right, y-bottom); while the lcs is (x-to-front, y-to-left, z-up)
    T_scs_to_scsics = np.array([[0.0, -1.0, 0.0, 0.0],
                                [0.0, 0.0, -1.0, 0.0],
                                [1.0, 0.0, 0.0, 0.0],
                                [0.0, 0.0, 0.0, 1.0]])

    # Now we can compose the final transform
    T_lcs_to_scs = T_scs_to_scsics.dot(T_lcs_to_scs)
    P_scs_wrt_lcs = utils.inv(T_lcs_to_scs)

    vcd.add_stream(stream_name="CAM_FRONT",
                   uri="",
                   description="Virtual camera",
                   stream_type=core.StreamType.camera)
    vcd.add_stream_properties(stream_name="CAM_FRONT",
                              intrinsics=types.IntrinsicsFisheye(
                                  width_px=img_width_px,
                                  height_px=img_height_px,
                                  lens_coeffs_1x4=list(d_1x4.flatten()),
                                  center_x=cX,
                                  center_y=cY,
                                  fov_deg=0.0,
                                  radius_x=0.0,
                                  radius_y=0.0
                              )
                              )
    vcd.add_coordinate_system("CAM_FRONT", cs_type=types.CoordinateSystemType.sensor_cs,
                              parent_name="vehicle-iso8855",
                              pose_wrt_parent=list(P_scs_wrt_lcs.flatten()))

    ################################
    # CAM_REAR
    ################################
    # This matrix converts from scs to ics
    d_1x4 = np.array([333.437012, 0.307729989, 2.4235599, 11.0495005])
    pitch_rad = (2.0 * np.pi) / 180.0
    yaw_rad = (180.0 * np.pi) / 180.0
    roll_rad = (0.0 * np.pi) / 180.0
    R_scs_wrt_lcs = utils.euler2R([yaw_rad, pitch_rad, roll_rad])  # default is ZYX
    C_lcs = np.array([[-0.725],  # rear part of the car
                      [0.0],  # centered in the symmetry axis of the car
                      [0.4]])  # at some height over the ground
    P_scs_wrt_lcs = utils.create_pose(R_scs_wrt_lcs, C_lcs)
    T_lcs_to_scs = utils.inv(P_scs_wrt_lcs)
    T_scs_to_scsics = np.array([[0.0, -1.0, 0.0, 0.0],
                                [0.0, 0.0, -1.0, 0.0],
                                [1.0, 0.0, 0.0, 0.0],
                                [0.0, 0.0, 0.0, 1.0]])
    T_lcs_to_scs = T_scs_to_scsics.dot(T_lcs_to_scs)
    P_scs_wrt_lcs = utils.inv(T_lcs_to_scs)

    vcd.add_stream(stream_name="CAM_REAR",
                   uri="",
                   description="Virtual camera",
                   stream_type=core.StreamType.camera)
    vcd.add_stream_properties(stream_name="CAM_REAR",
                              intrinsics=types.IntrinsicsFisheye(
                                  width_px=img_width_px,
                                  height_px=img_height_px,
                                  lens_coeffs_1x4=list(d_1x4.flatten()),
                                  center_x=cX,
                                  center_y=cY,
                                  fov_deg=0.0,
                                  radius_x=0.0,
                                  radius_y=0.0
                              )
                              )
    vcd.add_coordinate_system("CAM_REAR", cs_type=types.CoordinateSystemType.sensor_cs,
                              parent_name="vehicle-iso8855",
                              pose_wrt_parent=list(P_scs_wrt_lcs.flatten()))

    ################################
    # CAM_LEFT
    ################################
    # This matrix converts from scs to ics
    d_1x4 = np.array([333.437012, 0.307729989, 2.4235599, 11.0495005])
    pitch_rad = (2.0 * np.pi) / 180.0
    yaw_rad = (90.0 * np.pi) / 180.0
    roll_rad = (0.0 * np.pi) / 180.0
    R_scs_wrt_lcs = utils.euler2R([yaw_rad, pitch_rad, roll_rad])  # default is ZYX
    C_lcs = np.array([[1.2],
                      [0.6],  # at the left
                      [1.45]])  # at the roof
    P_scs_wrt_lcs = utils.create_pose(R_scs_wrt_lcs, C_lcs)
    T_lcs_to_scs = utils.inv(P_scs_wrt_lcs)
    T_scs_to_scsics = np.array([[0.0, -1.0, 0.0, 0.0],
                                [0.0, 0.0, -1.0, 0.0],
                                [1.0, 0.0, 0.0, 0.0],
                                [0.0, 0.0, 0.0, 1.0]])
    T_lcs_to_scs = T_scs_to_scsics.dot(T_lcs_to_scs)
    P_scs_wrt_lcs = utils.inv(T_lcs_to_scs)

    vcd.add_stream(stream_name="CAM_LEFT",
                   uri="",
                   description="Virtual camera",
                   stream_type=core.StreamType.camera)
    vcd.add_stream_properties(stream_name="CAM_LEFT",
                              intrinsics=types.IntrinsicsFisheye(
                                  width_px=img_width_px,
                                  height_px=img_height_px,
                                  lens_coeffs_1x4=list(d_1x4.flatten()),
                                  center_x=cX,
                                  center_y=cY,
                                  fov_deg=0.0,
                                  radius_x=0.0,
                                  radius_y=0.0
                              )
                              )
    vcd.add_coordinate_system("CAM_LEFT", cs_type=types.CoordinateSystemType.sensor_cs,
                              parent_name="vehicle-iso8855",
                              pose_wrt_parent=list(P_scs_wrt_lcs.flatten()))

    ################################
    # CAM_RIGHT
    ################################
    # This matrix converts from scs to ics
    d_1x4 = np.array([333.437012, 0.307729989, 2.4235599, 11.0495005])
    pitch_rad = (2.0 * np.pi) / 180.0
    yaw_rad = (-90.0 * np.pi) / 180.0
    roll_rad = (0.0 * np.pi) / 180.0
    R_scs_wrt_lcs = utils.euler2R([yaw_rad, pitch_rad, roll_rad])  # default is ZYX
    C_lcs = np.array([[1.2],
                      [-0.6],  # at the left
                      [1.45]])  # at the roof
    P_scs_wrt_lcs = utils.create_pose(R_scs_wrt_lcs, C_lcs)
    T_lcs_to_scs = utils.inv(P_scs_wrt_lcs)
    T_scs_to_scsics = np.array([[0.0, -1.0, 0.0, 0.0],
                                [0.0, 0.0, -1.0, 0.0],
                                [1.0, 0.0, 0.0, 0.0],
                                [0.0, 0.0, 0.0, 1.0]])
    T_lcs_to_scs = T_scs_to_scsics.dot(T_lcs_to_scs)
    P_scs_wrt_lcs = utils.inv(T_lcs_to_scs)

    vcd.add_stream(stream_name="CAM_RIGHT",
                   uri="",
                   description="Virtual camera",
                   stream_type=core.StreamType.camera)
    vcd.add_stream_properties(stream_name="CAM_RIGHT",
                              intrinsics=types.IntrinsicsFisheye(
                                  width_px=img_width_px,
                                  height_px=img_height_px,
                                  lens_coeffs_1x4=list(d_1x4.flatten()),
                                  center_x=cX,
                                  center_y=cY,
                                  fov_deg=0.0,
                                  radius_x=0.0,
                                  radius_y=0.0
                              )
                              )
    vcd.add_coordinate_system("CAM_RIGHT", cs_type=types.CoordinateSystemType.sensor_cs,
                              parent_name="vehicle-iso8855",
                              pose_wrt_parent=list(P_scs_wrt_lcs.flatten()))

    return vcd


def draw_scene(vcd):
    # Prepare objects
    scene = scl.Scene(vcd)  # scl.Scene has functions to project images, transforms, etc.
    drawer_front = draw.Image(scene, "CAM_FRONT")
    drawer_rear = draw.Image(scene, "CAM_REAR")
    drawer_left = draw.Image(scene, "CAM_LEFT")
    drawer_right = draw.Image(scene, "CAM_RIGHT")

    frameInfoDrawer = draw.FrameInfoDrawer(vcd)
    setupViewer = draw.SetupViewer(scene, "vehicle-iso8855")

    # Class colormap
    colorMap = {'Car': (0, 0, 255), 'Van': (255, 0, 0), 'Truck': (127, 127, 0),
                'Pedestrian': (0, 255, 0), 'Person_sitting': (0, 127, 127),
                'Tram': (127, 0, 127), 'Misc': (127, 127, 127), 'DontCare': (255, 255, 255),
                'Cyclist': (0, 127, 255),
                'Ego-car': (0, 0, 0),
                'Wall': (0, 0, 255),
                'Ground': (0, 255, 0)}

    # Get the size of the screen
    screen = screeninfo.get_monitors()[0]

    # Draw the images
    img_width_px = 1280
    img_height_px = 966
    img_front = 255 * np.ones((img_height_px, img_width_px, 3), np.uint8)
    img_rear = 255 * np.ones((img_height_px, img_width_px, 3), np.uint8)
    img_left = 255 * np.ones((img_height_px, img_width_px, 3), np.uint8)
    img_right = 255 * np.ones((img_height_px, img_width_px, 3), np.uint8)
    imageParams = draw.Image.Params(_colorMap=colorMap)

    drawer_front.draw(img_front, 0, _params=imageParams)
    drawer_rear.draw(img_rear, 0, _params=imageParams)
    drawer_left.draw(img_left, 0, _params=imageParams)
    drawer_right.draw(img_right, 0, _params=imageParams)

    # Draw the text
    textImg = frameInfoDrawer.draw(0, cols=400, rows=img_height_px * 2, _params=imageParams)

    mosaic = np.vstack((np.hstack((img_front, img_right)), np.hstack((img_left, img_rear))))
    cv.line(mosaic, (mosaic.shape[1] // 2, 0), (mosaic.shape[1] // 2, mosaic.shape[0]), (0, 0, 0), 3)
    cv.line(mosaic, (0, mosaic.shape[0] // 2), (mosaic.shape[1], mosaic.shape[0] // 2), (0, 0, 0), 3)
    '''
    mosaic_und = np.vstack((np.hstack((img_front_und, img_right_und)), np.hstack((img_left_und, img_rear_und))))
    cv.line(mosaic_und, (mosaic_und.shape[1] // 2, 0), (mosaic_und.shape[1] // 2, mosaic_und.shape[0]), (0, 0, 0), 3)
    cv.line(mosaic_und, (0, mosaic_und.shape[0] // 2), (mosaic_und.shape[1], mosaic_und.shape[0] // 2), (0, 0, 0), 3)
'''
    # Draw the top view
    topview_width = 1280
    topview_height = 1280
    ar = topview_width / topview_height
    rangeX = (-30.0, 30.0)
    rangeY = (-((rangeX[1] - rangeX[0]) / ar) / 2, ((rangeX[1] - rangeX[0]) / ar) / 2)
    topviewParams = draw.TopView.Params(colorMap=colorMap,
                                        topViewSize=(topview_width, topview_height),
                                        background_color=255,
                                        rangeX=rangeX,
                                        rangeY=rangeY,
                                        stepX=1.0, stepY=1.0,
                                        draw_grid=False)
    drawerTopView = draw.TopView(scene, "vehicle-iso8855", params=topviewParams)

    topView = drawerTopView.draw(frameNum=0)

    cv.namedWindow("Cameras", cv.WINDOW_NORMAL)
    cv.imshow("Cameras", mosaic)
    '''
    cv.namedWindow("Cameras undistorted", cv.WINDOW_NORMAL)
    cv.imshow("Cameras undistorted", mosaic_und)
    '''
    cv.namedWindow("VCD info")
    cv.imshow("VCD info", textImg)
    cv.namedWindow("TopView")
    cv.imshow("TopView", topView)
    cv.waitKey(1)

    fig1 = setupViewer.plot_setup()
    plt.show()


if __name__ == '__main__':
    print("Running " + os.path.basename(__file__))
    vcd = simple_setup_4_cams_fisheye()
    vcd = vcd_draw_pinhole.add_some_objects(vcd)  # so let's add the same objects as in vcd_draw_pinhole
    draw_scene(vcd)
