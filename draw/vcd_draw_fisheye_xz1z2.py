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


def simple_setup_4_cams_fisheye_2():
    vcd = core.VCD()
    vcd.add_coordinate_system("vehicle-iso8855", cs_type=types.CoordinateSystemType.local_cs)
    T = np.array([[-1.0, 0.0, 0.0, 0.0],
                  [0.0, -1.0, 0.0, 0.0],
                  [0.0, 0.0, 1.0, 0.0],
                  [0.0, 0.0, 0.0, 1.0]]) # This is a custom local ego-vehicle system, with x-back, z-down, y-left


    # We use it here because the provided rotations (x1z1z2) are expressed wrt this custom system
    # In VCD we adopt ISO8855, which defines x-front, z-up, y-left, therefore T encodes the pose of the custom wrt iso,
    # or equivalently, the transform needed to convert points from custom to iso
    vcd.add_coordinate_system("custom-ego-vehicle",
                              cs_type=types.CoordinateSystemType.local_cs,
                              parent_name="vehicle-iso8855",
                              pose_wrt_parent=T.flatten().tolist())

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
    #X-Z1-Z2 provided wrt z-down x-back y-left
    # to be applied z1xz2
    x1 = ((72) * np.pi) / 180.0
    z1 = ((90.70) * np.pi) / 180.0
    z2 = (-0.12 * np.pi) / 180.0
    R_scs_wrt_lcs = utils.euler2R([z1, x1, z2], seq=utils.EulerSeq.ZXZ)  # default is ZYX

    C_lcs = np.array([[3.9],  # frontal part of the car
                      [0.04],  # centered in the symmetry axis of the car
                      [0.6]])  # at some height over the ground

    P_scs_wrt_lcs = utils.create_pose(R_scs_wrt_lcs, C_lcs)

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
                              parent_name="custom-ego-vehicle",
                              pose_wrt_parent=list(P_scs_wrt_lcs.flatten()))

    ################################
    # CAM_REAR
    ################################
    # This matrix converts from scs to ics
    d_1x4 = np.array([333.437012, 0.307729989, 2.4235599, 11.0495005])
    # Extrinsics
    # ------------------------------
    x1 = ((41) * np.pi) / 180.0
    z1 = ((-90.05) * np.pi) / 180.0
    z2 = (-1.07 * np.pi) / 180.0
    R_scs_wrt_lcs = utils.euler2R([z1, x1, z2], seq=utils.EulerSeq.ZXZ)  # default is ZYX
    C_lcs = np.array([[-1.125],  # frontal part of the car
                      [-0.05],  # centered in the symmetry axis of the car
                      [0.8]])  # at some height over the ground
    P_scs_wrt_lcs = utils.create_pose(R_scs_wrt_lcs, C_lcs)

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
                              parent_name="custom-ego-vehicle",
                              pose_wrt_parent=list(P_scs_wrt_lcs.flatten()))

    ################################
    # CAM_LEFT
    ################################
    # This matrix converts from scs to ics
    d_1x4 = np.array([333.437012, 0.307729989, 2.4235599, 11.0495005])
    # Extrinsics
    # ------------------------------
    # Extrinsics (1/2): Rotation using yaw(Z), pitch(Y), roll(X). This is rotation of SCS wrt LCS
    x1 = ((14) * np.pi) / 180.0
    z1 = ((-164) * np.pi) / 180.0
    z2 = (13.29 * np.pi) / 180.0
    R_scs_wrt_lcs = utils.euler2R([z1, x1, z2], seq=utils.EulerSeq.ZXZ)  # default is ZYX
    C_lcs = np.array([[2.2],  # frontal part of the car
                      [0.9],  # centered in the symmetry axis of the car
                      [0.9]])  # at some height over the ground
    P_scs_wrt_lcs = utils.create_pose(R_scs_wrt_lcs, C_lcs)

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
                              parent_name="custom-ego-vehicle",
                              pose_wrt_parent=list(P_scs_wrt_lcs.flatten()))

    ################################
    # CAM_RIGHT
    ################################
    # This matrix converts from scs to ics
    d_1x4 = np.array([333.437012, 0.307729989, 2.4235599, 11.0495005])
    # Extrinsics
    # ------------------------------
    # Extrinsics (1/2): Rotation using yaw(Z), pitch(Y), roll(X). This is rotation of SCS wrt LCS
    x1 = ((14) * np.pi) / 180.0
    z1 = ((-22.05) * np.pi) / 180.0
    z2 = (-6.6 * np.pi) / 180.0
    R_scs_wrt_lcs = utils.euler2R([z1, x1, z2], seq=utils.EulerSeq.ZXZ)  # default is ZYX
    C_lcs = np.array([[2.2],  # frontal part of the car
                      [-0.9],  # centered in the symmetry axis of the car
                      [0.9]])  # at some height over the ground

    P_scs_wrt_lcs = utils.create_pose(R_scs_wrt_lcs, C_lcs)

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
                              parent_name="custom-ego-vehicle",
                              pose_wrt_parent=list(P_scs_wrt_lcs.flatten()))

    return vcd

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
    #X-Z1-Z2 provided wrt z-down x-back y-left
    # to be applied z1xz2
    x1 = ((72-180) * np.pi) / 180.0
    z1 = ((90.70 - 180) * np.pi) / 180.0
    z2 = -(-0.12 * np.pi) / 180.0
    R_scs_wrt_lcs = utils.euler2R([z1, x1, z2], seq=utils.EulerSeq.ZXZ)  # default is ZYX

    C_lcs = np.array([[3.9],  # frontal part of the car
                      [0.04],  # centered in the symmetry axis of the car
                      [0.6]])  # at some height over the ground

    P_scs_wrt_lcs = utils.create_pose(R_scs_wrt_lcs, C_lcs)

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
    # Extrinsics
    # ------------------------------
    x1 = ((41-180) * np.pi) / 180.0
    z1 = ((-90.05 - 180) * np.pi) / 180.0
    z2 = -(-1.07 * np.pi) / 180.0
    R_scs_wrt_lcs = utils.euler2R([z1, x1, z2], seq=utils.EulerSeq.ZXZ)  # default is ZYX
    C_lcs = np.array([[-1.125],  # frontal part of the car
                      [-0.05],  # centered in the symmetry axis of the car
                      [0.8]])  # at some height over the ground
    P_scs_wrt_lcs = utils.create_pose(R_scs_wrt_lcs, C_lcs)

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
    # Extrinsics
    # ------------------------------
    # Extrinsics (1/2): Rotation using yaw(Z), pitch(Y), roll(X). This is rotation of SCS wrt LCS
    x1 = ((14-180) * np.pi) / 180.0
    z1 = ((-164-180) * np.pi) / 180.0
    z2 = -(13.29 * np.pi) / 180.0
    R_scs_wrt_lcs = utils.euler2R([z1, x1, z2], seq=utils.EulerSeq.ZXZ)  # default is ZYX
    C_lcs = np.array([[2.2],  # frontal part of the car
                      [0.9],  # centered in the symmetry axis of the car
                      [0.9]])  # at some height over the ground
    P_scs_wrt_lcs = utils.create_pose(R_scs_wrt_lcs, C_lcs)

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
    # Extrinsics
    # ------------------------------
    # Extrinsics (1/2): Rotation using yaw(Z), pitch(Y), roll(X). This is rotation of SCS wrt LCS
    x1 = ((14-180) * np.pi) / 180.0
    z1 = ((-22.05 - 180) * np.pi) / 180.0
    z2 = -(-6.6 * np.pi) / 180.0
    R_scs_wrt_lcs = utils.euler2R([z1, x1, z2], seq=utils.EulerSeq.ZXZ)  # default is ZYX
    C_lcs = np.array([[2.2],  # frontal part of the car
                      [-0.9],  # centered in the symmetry axis of the car
                      [0.9]])  # at some height over the ground

    P_scs_wrt_lcs = utils.create_pose(R_scs_wrt_lcs, C_lcs)

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

    drawerTopView1 = draw.TopView(scene, "vehicle-iso8855")
    #drawerTopView2 = draw.TopView(scene, "custom-ego-vehicle")

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

    img_front = cv.imread('./png/front.jpg')
    img_rear = cv.imread('./png/rear.jpg')
    img_left = cv.imread('./png/left.jpg')
    img_right = cv.imread('./png/right.jpg')

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
    topviewParams = draw.TopView.Params(_colorMap=colorMap,
                                        _imgSize=(topview_width, topview_height),
                                        _background_color=255,
                                        _rangeX=rangeX,
                                        _rangeY=rangeY,
                                        _stepX=1.0, _stepY=1.0,
                                        _draw_grid=False)

    topView1 = drawerTopView1.draw(imgs=None, frameNum=0, _params=topviewParams)
    #topView2 = drawerTopView2.draw(0, _params=topviewParams)

    cv.namedWindow("Cameras", cv.WINDOW_NORMAL)
    cv.imshow("Cameras", mosaic)
    cv.namedWindow("VCD info")
    cv.imshow("VCD info", textImg)
    cv.namedWindow("TopView iso8855")
    cv.imshow("TopView iso8855", topView1)
    #cv.namedWindow("TopView custom")
    #cv.imshow("TopView custom", topView2)
    cv.waitKey(1)

    fig1 = setupViewer.plot_setup()
    plt.show()


if __name__ == '__main__':
    print("Running " + os.path.basename(__file__))
    vcd = simple_setup_4_cams_fisheye()
    #vcd = simple_setup_4_cams_fisheye_2()
    vcd = vcd_draw_pinhole.add_some_objects(vcd)  # so let's add the same objects as in vcd_draw_pinhole
    draw_scene(vcd)
