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


def simple_setup_4_cams_pinhole():
    vcd = core.VCD()
    vcd.add_coordinate_system("vehicle-iso8855", cs_type=types.CoordinateSystemType.local_cs)

    # Let's build the cameras
    img_width_px = 960
    img_height_px = 604
    ################################
    # CAM_FRONT
    ################################
    # Intrinsics
    # ------------------------------
    # This matrix converts from scs to ics
    K_3x4 = np.array([[6.038e+002, 0.0, 4.67e+002, 0.0],
                      [0.0, 6.038e+002, 2.94e+002, 0.0],
                      [0.0, 0.0, 1.0, 0.0]])
    d_1x5 = np.array([[-4.0569640920796241e-001, 1.9116055332155032e-001,
                       0., 0.,
                       -4.7033609773998064e-002]])

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
                              intrinsics=types.IntrinsicsPinhole(
                                  width_px=img_width_px,
                                  height_px=img_height_px,
                                  camera_matrix_3x4=list(K_3x4.flatten()),
                                  distortion_coeffs_1xN=list(d_1x5.flatten())
                              )
                              )
    vcd.add_coordinate_system("CAM_FRONT", cs_type=types.CoordinateSystemType.sensor_cs,
                              parent_name="vehicle-iso8855",
                              pose_wrt_parent=types.PoseData(
                                  val=list(P_scs_wrt_lcs.flatten()),
                                  type=types.TransformDataType.matrix_4x4)
                              )

                              #list(P_scs_wrt_lcs.flatten()))

    ################################
    # CAM_REAR
    ################################
    K_3x4 = np.array([[6.038e+002, 0.0, 4.67e+002, 0.0],
                      [0.0, 6.038e+002, 2.94e+002, 0.0],
                      [0.0, 0.0, 1.0, 0.0]])
    d_1x5 = np.array([[-4.0569640920796241e-001, 1.9116055332155032e-001,
                       0., 0.,
                       -4.7033609773998064e-002]])
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
                              intrinsics=types.IntrinsicsPinhole(
                                  width_px=img_width_px,
                                  height_px=img_height_px,
                                  camera_matrix_3x4=list(K_3x4.flatten()),
                                  distortion_coeffs_1xN=list(d_1x5.flatten())
                              )
                              )
    vcd.add_coordinate_system("CAM_REAR", cs_type=types.CoordinateSystemType.sensor_cs,
                              parent_name="vehicle-iso8855",
                              pose_wrt_parent=types.PoseData(
                                  val=list(P_scs_wrt_lcs.flatten()),
                                  type=types.TransformDataType.matrix_4x4)
                              )

    ################################
    # CAM_LEFT
    ################################
    K_3x4 = np.array([[6.038e+002, 0.0, 4.67e+002, 0.0],
                      [0.0, 6.038e+002, 2.94e+002, 0.0],
                      [0.0, 0.0, 1.0, 0.0]])
    d_1x5 = np.array([[-4.0569640920796241e-001, 1.9116055332155032e-001,
                       0., 0.,
                       -4.7033609773998064e-002]])
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
                              intrinsics=types.IntrinsicsPinhole(
                                  width_px=img_width_px,
                                  height_px=img_height_px,
                                  camera_matrix_3x4=list(K_3x4.flatten()),
                                  distortion_coeffs_1xN=list(d_1x5.flatten())
                              )
                              )
    vcd.add_coordinate_system("CAM_LEFT", cs_type=types.CoordinateSystemType.sensor_cs,
                              parent_name="vehicle-iso8855",
                              pose_wrt_parent=types.PoseData(
                                  val=list(P_scs_wrt_lcs.flatten()),
                                  type=types.TransformDataType.matrix_4x4)
                              )

    ################################
    # CAM_RIGHT
    ################################
    K_3x4 = np.array([[6.038e+002, 0.0, 4.67e+002, 0.0],
                      [0.0, 6.038e+002, 2.94e+002, 0.0],
                      [0.0, 0.0, 1.0, 0.0]])
    d_1x5 = np.array([[-4.0569640920796241e-001, 1.9116055332155032e-001,
                       0., 0.,
                       -4.7033609773998064e-002]])
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
                              intrinsics=types.IntrinsicsPinhole(
                                  width_px=img_width_px,
                                  height_px=img_height_px,
                                  camera_matrix_3x4=list(K_3x4.flatten()),
                                  distortion_coeffs_1xN=list(d_1x5.flatten())
                              )
                              )
    vcd.add_coordinate_system("CAM_RIGHT", cs_type=types.CoordinateSystemType.sensor_cs,
                              parent_name="vehicle-iso8855",
                              pose_wrt_parent=types.PoseData(
                                  val=list(P_scs_wrt_lcs.flatten()),
                                  type=types.TransformDataType.matrix_4x4)
                              )

    return vcd


def add_orthographic_camera(vcd):
    # Let's build the cameras
    img_width_px = 1024
    img_height_px = 1024
    
    ################################
    # VIRTUAL CAMERA LOOKING DOWN
    ################################
    # Intrinsics & Extrinsics
    # ------------------------------
    ar = img_width_px/img_height_px
    xmin = -25.0 # meters
    xmax = 25.0
    ymin = -((xmax - xmin) / ar) / 2.0
    ymax = ((xmax - xmin) / ar) / 2.0

    R_scs_wrt_lcs = utils.euler2R([0, np.pi/2.0, 0])  # perfectly looking down
    C_lcs = np.array([[0.0],  # frontal part of the car
                      [0.0],  # centered in the symmetry axis of the car
                      [3.0]])  # at some height over the car (it does not matter, really, this is ortographic projection)

    P_scs_wrt_lcs = utils.create_pose(R_scs_wrt_lcs, C_lcs)
    T_lcs_to_scs = utils.inv(P_scs_wrt_lcs)

    # Extrinsics (2/2): Additional rotation, because usually cameras scs are (x-to-right, y-down, z-to-front)
    # to match better with ics (x-to-right, y-bottom); while the lcs is (x-to-front, y-to-left, z-up)
    T_scs_to_scsics = np.array([[0.0, -1.0, 0.0, 0.0],
                                [0.0, 0.0, -1.0, 0.0],
                                [1.0, 0.0, 0.0, 0.0],
                                [0.0, 0.0, 0.0, 1.0]])
    T_lcs_to_scs = T_scs_to_scsics.dot(T_lcs_to_scs)
    P_scs_wrt_lcs = utils.inv(T_lcs_to_scs)
    
    vcd.add_stream(stream_name="CAM_ORTHO_BEV",
                   uri="",
                   description="Orthographic camera",
                   stream_type=core.StreamType.camera)
    vcd.add_stream_properties(stream_name="CAM_ORTHO_BEV",
                              intrinsics=types.IntrinsicsOrthographic(
                                  width_px=img_width_px,
                                  height_px=img_height_px,
                                  xmin=xmin,
                                  xmax=xmax,
                                  ymin=ymin,
                                  ymax=ymax
                              )
                              )
    vcd.add_coordinate_system("CAM_ORTHO_BEV", cs_type=types.CoordinateSystemType.sensor_cs,
                              parent_name="vehicle-iso8855",
                              pose_wrt_parent=types.PoseData(
                                  val=list(P_scs_wrt_lcs.flatten()),
                                  type=types.TransformDataType.matrix_4x4)
                              )   

    return vcd


def add_some_objects(vcd):
    #########################################
    # Cuboids
    #########################################
    uid1 = vcd.add_object(name="", semantic_type="Car", frame_value=0)
    cuboid1 = types.cuboid(name="box3D",
                              val=(15.0, 0.0, 0.7,
                                   0.0, 0.0, (15.0 * np.pi) / 180.0,
                                   4.2, 1.8, 1.4),
                              coordinate_system="vehicle-iso8855")
    vcd.add_object_data(uid1, cuboid1, frame_value=0)

    uid2 = vcd.add_object(name="", semantic_type="Van", frame_value=0)
    cuboid2 = types.cuboid(name="box3D",
                           val=(-9.0, 4.0, 1.25,
                                0.0, 0.0, (0.0 * np.pi) / 180.0,
                                8.0, 3.1, 2.5),
                           coordinate_system="vehicle-iso8855")
    vcd.add_object_data(uid2, cuboid2, frame_value=0)
    
    #########################################
    # Points3d (Walls)
    #########################################
    xm, ym, zm = utils.generate_grid(x_params=(0, 20, 21), y_params=(-20, 20, 41), z_params=(0, 0, 1))
    points3d_4xN = utils.grid_as_4xN_points3d(xm, ym, zm)
    uid_wall_1 = vcd.add_object(name="ground_x_pos", semantic_type="Ground", frame_value=0)
    mat_wall = types.mat(name="wall",
                          val=points3d_4xN.flatten().tolist(),
                          channels=1,
                          width=points3d_4xN.shape[1],
                          height=points3d_4xN.shape[0],
                         dataType='float',
                         coordinate_system="vehicle-iso8855")
    #mat_wall.add_attribute(types.vec(name="color",
    #                                 val=(255, 0, 0)))
    vcd.add_object_data(uid_wall_1, mat_wall, frame_value=0)

    xm, ym, zm = utils.generate_grid(x_params=(0, -20, 21), y_params=(-20, 20, 41), z_params=(0, 0, 1))
    points3d_4xN = utils.grid_as_4xN_points3d(xm, ym, zm)
    uid_wall_2 = vcd.add_object(name="ground_x_neg", semantic_type="Ground", frame_value=0)
    mat_wall = types.mat(name="wall",
                         val=points3d_4xN.flatten().tolist(),
                         channels=1,
                         width=points3d_4xN.shape[1],
                         height=points3d_4xN.shape[0],
                         dataType='float',
                         coordinate_system="vehicle-iso8855")
    #mat_wall.add_attribute(types.vec(name="color",
    #                                val=(255, 255, 0)))
    vcd.add_object_data(uid_wall_2, mat_wall, frame_value=0)

    xm, ym, zm = utils.generate_grid(x_params=(20, 20, 1), y_params=(-20, 20, 41), z_params=(0, 2, 21))
    points3d_4xN = utils.grid_as_4xN_points3d(xm, ym, zm)
    uid_wall_3 = vcd.add_object(name="wall_front", semantic_type="Wall", frame_value=0)
    mat_wall = types.mat(name="wall",
                         val=points3d_4xN.flatten().tolist(),
                         channels=1,
                         width=points3d_4xN.shape[1],
                         height=points3d_4xN.shape[0],
                         dataType='float',
                         coordinate_system="vehicle-iso8855")
    #mat_wall.add_attribute(types.vec(name="color",
    #                                 val=(0, 255, 0)))
    vcd.add_object_data(uid_wall_3, mat_wall, frame_value=0)

    xm, ym, zm = utils.generate_grid(x_params=(-20, -20, 1), y_params=(-20, 20, 41), z_params=(0, 2, 21))
    points3d_4xN = utils.grid_as_4xN_points3d(xm, ym, zm)
    uid_wall_4 = vcd.add_object(name="wall_rear", semantic_type="Wall", frame_value=0)
    mat_wall = types.mat(name="wall",
                         val=points3d_4xN.flatten().tolist(),
                         channels=1,
                         width=points3d_4xN.shape[1],
                         height=points3d_4xN.shape[0],
                         dataType='float',
                         coordinate_system="vehicle-iso8855")
    #mat_wall.add_attribute(types.vec(name="color",
    #                                 val=(0, 255, 255)))
    vcd.add_object_data(uid_wall_4, mat_wall, frame_value=0)

    xm, ym, zm = utils.generate_grid(x_params=(-20, 20, 41), y_params=(20, 20, 1), z_params=(0, 2, 21))
    points3d_4xN = utils.grid_as_4xN_points3d(xm, ym, zm)
    uid_wall_5 = vcd.add_object(name="wall_right", semantic_type="Wall", frame_value=0)
    mat_wall = types.mat(name="wall",
                         val=points3d_4xN.flatten().tolist(),
                         channels=1,
                         width=points3d_4xN.shape[1],
                         height=points3d_4xN.shape[0],
                         dataType='float',
                         coordinate_system="vehicle-iso8855")
    #mat_wall.add_attribute(types.vec(name="color",
    #                                 val=(255, 0, 255)))
    vcd.add_object_data(uid_wall_5, mat_wall, frame_value=0)

    xm, ym, zm = utils.generate_grid(x_params=(-20, 20, 41), y_params=(-20, -20, 1), z_params=(0, 2, 21))
    points3d_4xN = utils.grid_as_4xN_points3d(xm, ym, zm)
    uid_wall_6 = vcd.add_object(name="wall_left", semantic_type="Wall", frame_value=0)
    mat_wall = types.mat(name="wall",
                         val=points3d_4xN.flatten().tolist(),
                         channels=1,
                         width=points3d_4xN.shape[1],
                         height=points3d_4xN.shape[0],
                         dataType='float',
                         coordinate_system="vehicle-iso8855")
    #mat_wall.add_attribute(types.vec(name="color",
    #                                 val=(255, 255, 0)))
    vcd.add_object_data(uid_wall_6, mat_wall, frame_value=0)

    #########################################
    # Lines3d
    #########################################
    # TODO

    #########################################
    # Ego-vehicle
    #########################################
    vcd.add_object(name="Ego-car", semantic_type="Ego-car", uid=str(-2))

    cuboid_ego = types.cuboid(name="box3D",
                              val=(1.35, 0.0, 0.736,
                                   0.0, 0.0, 0.0,
                                   4.765, 1.82, 1.47),
                              coordinate_system="vehicle-iso8855")
    vcd.add_object_data(str(-2), cuboid_ego)

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

    # Draw the images
    img_width_px = 960
    img_height_px = 604
    img_front = 255*np.ones((img_height_px, img_width_px, 3), np.uint8)
    img_rear = 255*np.ones((img_height_px, img_width_px, 3), np.uint8)
    img_left = 255*np.ones((img_height_px, img_width_px, 3), np.uint8)
    img_right = 255*np.ones((img_height_px, img_width_px, 3), np.uint8)
    imageParams = draw.Image.Params(_colorMap=colorMap, _thickness=2)

    drawer_front.draw(img_front, 0, _params=imageParams)
    drawer_rear.draw(img_rear, 0, _params=imageParams)
    drawer_left.draw(img_left, 0, _params=imageParams)
    drawer_right.draw(img_right, 0, _params=imageParams)

    # Undistort
    cam_front = scene.get_camera("CAM_FRONT", compute_remaps=True)
    cam_rear = scene.get_camera("CAM_REAR", compute_remaps=True)
    cam_left = scene.get_camera("CAM_LEFT", compute_remaps=True)
    cam_right = scene.get_camera("CAM_RIGHT", compute_remaps=True)

    img_front_und = cam_front.undistort_image(img_front)
    img_rear_und = cam_rear.undistort_image(img_rear)
    img_left_und = cam_left.undistort_image(img_left)
    img_right_und = cam_right.undistort_image(img_right)

    # Draw the text
    textImg = frameInfoDrawer.draw(0, cols=400, rows=img_height_px * 2, _params=imageParams)

    mosaic = np.vstack((np.hstack((img_front, img_right)), np.hstack((img_left, img_rear))))
    cv.line(mosaic, (mosaic.shape[1] // 2, 0), (mosaic.shape[1] // 2, mosaic.shape[0]), (0, 0, 0), 3)
    cv.line(mosaic, (0, mosaic.shape[0] // 2), (mosaic.shape[1], mosaic.shape[0] // 2), (0, 0, 0), 3)

    mosaic_und = np.vstack((np.hstack((img_front_und, img_right_und)), np.hstack((img_left_und, img_rear_und))))
    cv.line(mosaic_und, (mosaic_und.shape[1] // 2, 0), (mosaic_und.shape[1] // 2, mosaic_und.shape[0]), (0, 0, 0), 3)
    cv.line(mosaic_und, (0, mosaic_und.shape[0] // 2), (mosaic_und.shape[1], mosaic_und.shape[0] // 2), (0, 0, 0), 3)

    # Draw the top view
    topview_width = 1280
    topview_height = 1280
    ar = topview_width/topview_height
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

    drawerTopViewOrtho = draw.TopViewOrtho(scene, "CAM_ORTHO_BEV")

    topView = drawerTopView.draw(frameNum=0)

    topViewOrtho = drawerTopViewOrtho.draw(frameNum=0, params=imageParams)

    cv.namedWindow("Cameras", cv.WINDOW_NORMAL)
    cv.imshow("Cameras", mosaic)
    cv.namedWindow("Cameras undistorted", cv.WINDOW_NORMAL)
    cv.imshow("Cameras undistorted", mosaic_und)
    cv.namedWindow("VCD info")
    cv.imshow("VCD info", textImg)
    cv.namedWindow("TopView", cv.WINDOW_NORMAL)
    cv.imshow("TopView", topView)
    cv.imshow("TopViewOrtho", topViewOrtho)
    cv.waitKey(0)

    fig1 = setupViewer.plot_setup()
    plt.show()


if __name__ == '__main__':
    print("Running " + os.path.basename(__file__))
    vcd = simple_setup_4_cams_pinhole()    
    vcd = add_some_objects(vcd)
    vcd = add_orthographic_camera(vcd)
    draw_scene(vcd)
