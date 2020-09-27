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

import matplotlib.pyplot as plt


def simple_setup_4_cams_pinhole():
    vcd = core.VCD()
    vcd.add_coordinate_system("vehicle-iso8855", cs_type=types.CoordinateSystemType.local_cs)

    # Let's build the cameras
    img_width_px = 1920
    img_height_px = 1208
    ################################
    # CAM_FRONT
    ################################
    # Intrinsics
    # ------------------------------
    # This matrix converts from scs to ics
    K_3x4 = np.array([[12.028e+002, 0.0, 9.60e+002, 0.0],
                      [0.0, 12.153e+002, 6.04e+002, 0.0],
                      [0.0, 0.0, 1.0, 0.0]])
    d_1x5 = np.array([[-4.0569640920796241e-001, 1.9116055332155032e-001,
                       0., 0.,
                       -4.7033609773998064e-002]])


    # Extrinsics
    # ------------------------------
    # Extrinsics (1/2): Rotation using yaw(Z), pitch(Y), roll(X). This is rotation of SCS wrt LCS
    pitch_rad = (1.0 * np.pi) / 180.0
    yaw_rad = (0.0 * np.pi) / 180.0
    roll_rad = (0.0 * np.pi) / 180.0
    R_scs_wrt_lcs = utils.euler2R([yaw_rad, pitch_rad, roll_rad])  # default is ZYX
    C_lcs = np.array([[2.01494884490967],  # frontal part of the car
                      [-0.0447371117770672],  # centered in the symmetry axis of the car
                      [1.297135674953461]])  # at some height over the ground

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
                              pose_wrt_parent=list(P_scs_wrt_lcs.flatten()))

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
    # Points3d (Ground)
    #########################################
    step_x = 1.0
    step_y = 1.0
    x_min = 0
    x_max = 50
    y_min = -20
    y_max = 20
    num_points_x = int((x_max - x_min)/step_x)
    num_points_y = int((y_max - y_min)/step_y)
    xm, ym, zm = utils.generate_grid(x_params=(x_min, x_max, num_points_x + 1), y_params=(y_min, y_max, num_points_y+1), z_params=(0, 0, 1))
    points3d_4xN = utils.grid_as_4xN_points3d(xm, ym, zm)
    uid_ground_1 = vcd.add_object(name="ground_x_pos", semantic_type="Ground", frame_value=0)
    mat_ground = types.mat(name="points_rep",
                         val=points3d_4xN.flatten().tolist(),
                         channels=1,
                         width=points3d_4xN.shape[1],
                         height=points3d_4xN.shape[0],
                         dataType='float',
                         coordinate_system="vehicle-iso8855")
    # mat_wall.add_attribute(types.vec(name="color",
    #                                 val=(255, 0, 0)))
    vcd.add_object_data(uid_ground_1, mat_ground, frame_value=0)
    '''

    #########################################
    # Points3d (Walls)
    #########################################
    xm, ym, zm = utils.generate_grid(x_params=(0, 20, 21), y_params=(-20, 20, 41), z_params=(0, 0, 1))
    points3d_4xN = utils.grid_as_4xN_points3d(xm, ym, zm)
    uid_wall_1 = vcd.add_object(name="ground_x_pos", semantic_type="Ground", frame_value=0)
    mat_wall = types.mat(name="points",
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
    mat_wall = types.mat(name="points",
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
    mat_wall = types.mat(name="points",
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
    mat_wall = types.mat(name="points",
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
    mat_wall = types.mat(name="points",
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
    mat_wall = types.mat(name="points",
                         val=points3d_4xN.flatten().tolist(),
                         channels=1,
                         width=points3d_4xN.shape[1],
                         height=points3d_4xN.shape[0],
                         dataType='float',
                         coordinate_system="vehicle-iso8855")
    #mat_wall.add_attribute(types.vec(name="color",
    #                                 val=(255, 255, 0)))
    vcd.add_object_data(uid_wall_6, mat_wall, frame_value=0)
    '''

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


def create_reprojections(vcd):
    scene = scl.Scene(vcd)
    # Read the "ground" objects and reproject from image to world
    # Assuming data for frame 0
    for object_id, object in vcd.data['vcd']['objects'].items():
        name = object['name']
        if 'ground' in name:
            vcd_frame = vcd.get_frame(0)
            object_data = vcd_frame['objects'][object_id]['object_data']['mat'][0]
            #ground_x_neg = vcd_frame['objects'][object_id]['object_data']['mat'][1]
            width = object_data['width']
            height = object_data['height']
            points_cs = object_data['coordinate_system']


            '''
             # DEBUG: distord-undistort cycle: works!
            cam = scene.get_camera('CAM_FRONT', 0)
            original_undistorted = np.array([1537, 846, 1]).reshape(3, 1)
            distorted = cam.distort_points2d(original_undistorted)
            undistorted = cam.undistort_points2d(distorted)

            original_distorted = np.array([1481, 823, 1]).reshape(3, 1)
            undistorted = cam.undistort_points2d(original_distorted)
            distorted = cam.distort_points2d(undistorted)
            '''

            # Read 3d points
            points3d_4xN = np.array(object_data['val']).reshape(height, width)
            N = points3d_4xN.shape[1]

            # Project into image
            points2d_3xN, idx_valid_proj = scene.project_points3d_4xN(points3d_4xN, points_cs, 'CAM_FRONT')

            # Re-project into plane
            points2d_3xN_filt = points2d_3xN[:, idx_valid_proj]
            points3d_4xN_rep, idx_valid_rep = scene.reproject_points2d_3xN(points2d_3xN_filt, (0, 0, 1, 0), 'CAM_FRONT', 'vehicle-iso8855')


            # Create output object
            mat_ground_reprojected = types.mat(name="points",
                                 val=points3d_4xN_rep.flatten().tolist(),
                                 channels=1,
                                 width=points3d_4xN_rep.shape[1],
                                 height=points3d_4xN_rep.shape[0],
                                 dataType='float',
                                 coordinate_system="vehicle-iso8855")
            mat_ground_reprojected.add_attribute(types.vec(name="color",
                                            val=(0, 0, 255)))
            vcd.add_object_data(object_id, mat_ground_reprojected, frame_value=0)

            # Filter out those not valid during projection and reprojection from original set of 3D points...
            if len(idx_valid_rep) > 0:
                temp1 = points3d_4xN[:, idx_valid_proj]
                temp2 = temp1[:, idx_valid_rep]

                # ... so we can compare with the valid reprojected 3D points
                temp3 = points3d_4xN_rep[:, idx_valid_rep]
                temp4 = temp3 - temp2
                error = np.linalg.norm(temp4)

                print("Reprojection error:", error, " - Num. points: ", temp2.shape[1])


def draw_scene(vcd):
    # Prepare objects
    scene = scl.Scene(vcd)  # scl.Scene has functions to project images, transforms, etc.
    drawer_front = draw.Image(scene, "CAM_FRONT")

    frameInfoDrawer = draw.FrameInfoDrawer(vcd)

    drawerTopView = draw.TopView(scene, "vehicle-iso8855")

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
    img_width_px = 1920
    img_height_px = 1208
    img_front = 255*np.ones((img_height_px, img_width_px, 3), np.uint8)
    imageParams = draw.Image.Params(_colorMap=colorMap, _barrel=True)
    drawer_front.draw(img_front, 0, _params=imageParams)

    # Undistort
    cam_front = scene.get_camera("CAM_FRONT")
    img_front_und = cam_front.undistort_image(img_front)

    # Draw the text
    textImg = frameInfoDrawer.draw(0, cols=400, rows=img_height_px * 2, _params=imageParams)

    # Draw the top view
    topview_width = 1280
    topview_height = 1280
    ar = topview_width/topview_height
    rangeX = (-30.0, 30.0)
    rangeY = (-((rangeX[1] - rangeX[0]) / ar) / 2, ((rangeX[1] - rangeX[0]) / ar) / 2)
    topviewParams = draw.TopView.Params(_colorMap=colorMap,
                                         _imgSize=(topview_width, topview_height),
                                         _background_color=255,
                                         _rangeX=rangeX,
                                         _rangeY=rangeY,
                                         _stepX=1.0, _stepY=1.0,
                                        _draw_grid=False)

    topView = drawerTopView.draw(imgs=None, frameNum=0, _params=topviewParams)

    cv.namedWindow("front", cv.WINDOW_NORMAL)
    cv.imshow("front", img_front)
    cv.namedWindow("front_und", cv.WINDOW_NORMAL)
    cv.imshow("front_und", img_front_und)
    cv.namedWindow("VCD info")
    cv.imshow("VCD info", textImg)
    cv.namedWindow("TopView", cv.WINDOW_NORMAL)
    cv.imshow("TopView", topView)
    cv.waitKey(0)

    fig1 = setupViewer.plot_setup()
    plt.show()


if __name__ == '__main__':
    print("Running " + os.path.basename(__file__))
    vcd = simple_setup_4_cams_pinhole()
    vcd = add_some_objects(vcd)
    create_reprojections(vcd)
    draw_scene(vcd)
