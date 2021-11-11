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
from vcd import schema

from draw import vcd_draw_pinhole_4cams
import matplotlib.pyplot as plt


def simple_setup_4_cams_fisheye():
    vcd = core.VCD()
    vcd.add_coordinate_system("vehicle-iso8855", cs_type=types.CoordinateSystemType.local_cs)

    # Let's build the cameras
    img_width_px = 1280
    img_height_px = 966
    cX = img_width_px/2.0 -0.302159995  # center, not deviation
    cY = img_height_px/2.0 -3.44617009  # center, not deviation
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
                                  lens_coeffs_1xN=list(d_1x4.flatten()),
                                  center_x=cX,
                                  center_y=cY,
                                  focal_length_x=1.0,
                                  focal_length_y=1.0,
                                  fisheye_model=types.FisheyeModel.radial_poly
                              )
                              )
    vcd.add_coordinate_system("CAM_FRONT", cs_type=types.CoordinateSystemType.sensor_cs,
                              parent_name="vehicle-iso8855",
                              pose_wrt_parent=types.PoseData(
                                  val=list(P_scs_wrt_lcs.flatten()),
                                  type=types.TransformDataType.matrix_4x4)
                              )


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
                                  lens_coeffs_1xN=list(d_1x4.flatten()),
                                  center_x=cX,
                                  center_y=cY,
                                  aspect_ratio=1.0,
                                  focal_length_x=1.0,
                                  focal_length_y=1.0,
                                  fisheye_model=types.FisheyeModel.radial_poly
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
                                  lens_coeffs_1xN=list(d_1x4.flatten()),
                                  center_x=cX,
                                  center_y=cY,
                                  focal_length_x=1.0,
                                  focal_length_y=1.0,
                                  fisheye_model=types.FisheyeModel.radial_poly
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
                                  lens_coeffs_1xN=list(d_1x4.flatten()),
                                  center_x=cX,
                                  center_y=cY,
                                  focal_length_x=1.0,
                                  focal_length_y=1.0,
                                  fisheye_model=types.FisheyeModel.radial_poly
                              )
                              )
    vcd.add_coordinate_system("CAM_RIGHT", cs_type=types.CoordinateSystemType.sensor_cs,
                              parent_name="vehicle-iso8855",
                              pose_wrt_parent=types.PoseData(
                                  val=list(P_scs_wrt_lcs.flatten()),
                                  type=types.TransformDataType.matrix_4x4)
                              )

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
    img_width_px = 1280
    img_height_px = 966

    img_front = 255 * np.ones((img_height_px, img_width_px, 3), np.uint8) #cv.imread('./png/fisheye_xz1z2/front.jpg')
    img_rear = 255 * np.ones((img_height_px, img_width_px, 3), np.uint8) #cv.imread('./png/fisheye_xz1z2/rear.jpg')
    img_left = 255 * np.ones((img_height_px, img_width_px, 3), np.uint8) #cv.imread('./png/fisheye_xz1z2/left.jpg')
    img_right = 255 * np.ones((img_height_px, img_width_px, 3), np.uint8) #cv.imread('./png/fisheye_xz1z2/right.jpg')

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

    #mosaic_und = np.vstack((np.hstack((img_front_und, img_right_und)), np.hstack((img_left_und, img_rear_und))))
    #cv.line(mosaic_und, (mosaic_und.shape[1] // 2, 0), (mosaic_und.shape[1] // 2, mosaic_und.shape[0]), (0, 0, 0), 3)
    #cv.line(mosaic_und, (0, mosaic_und.shape[0] // 2), (mosaic_und.shape[1], mosaic_und.shape[0] // 2), (0, 0, 0), 3)

    # Draw the top view
    topview_width = 1280
    topview_height = 1280
    ar = topview_width / topview_height
    rangeX = (-15.0, 15.0)
    rangeY = (-((rangeX[1] - rangeX[0]) / ar) / 2, ((rangeX[1] - rangeX[0]) / ar) / 2)
    topviewParams = draw.TopView.Params(colorMap=colorMap,
                                        topViewSize=(topview_width, topview_height),
                                        background_color=255,
                                        rangeX=rangeX,
                                        rangeY=rangeY,
                                        stepX=1.0, stepY=1.0,
                                        draw_grid=False)
    drawerTopView1 = draw.TopView(scene, "vehicle-iso8855", params=topviewParams)
    drawerTopView1.add_images({'CAM_LEFT': img_left, 'CAM_FRONT': img_front, 'CAM_REAR': img_rear, 'CAM_RIGHT': img_right}, frameNum=0)
    topView1 = drawerTopView1.draw(frameNum=0)

    cv.namedWindow("Cameras", cv.WINDOW_NORMAL)
    cv.imshow("Cameras", mosaic)
    #cv.namedWindow("Cameras Undistorted", cv.WINDOW_NORMAL)
    #cv.imshow("Cameras Undistorted", mosaic_und)
    cv.namedWindow("VCD info")
    cv.imshow("VCD info", textImg)
    cv.namedWindow("TopView iso8855")
    cv.imshow("TopView iso8855", topView1)
    cv.waitKey(1)

    fig1 = setupViewer.plot_setup()
    plt.show()


def add_some_objects(vcd):
    #########################################
    # Cuboids
    #########################################
    uid1 = vcd.add_object(name="", semantic_type="Car", frame_value=0)
    cuboid1 = types.cuboid(name="box3D",
                           val=(4.5, 3.5, 0.7,
                                0.0, 0.0, (90.0 * np.pi) / 180.0,
                                4.2, 1.8, 1.4),
                           coordinate_system="vehicle-iso8855")
    vcd.add_object_data(uid1, cuboid1, frame_value=0)

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
    # mat_wall.add_attribute(types.vec(name="color",
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
    # mat_wall.add_attribute(types.vec(name="color",
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
    # mat_wall.add_attribute(types.vec(name="color",
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
    # mat_wall.add_attribute(types.vec(name="color",
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
    # mat_wall.add_attribute(types.vec(name="color",
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
    # mat_wall.add_attribute(types.vec(name="color",
    #                                 val=(255, 255, 0)))
    vcd.add_object_data(uid_wall_6, mat_wall, frame_value=0)

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


if __name__ == '__main__':
    print("Running " + os.path.basename(__file__))

    vcd = simple_setup_4_cams_fisheye()
    vcd = vcd_draw_pinhole_4cams.add_some_objects(vcd)  # so let's add the same objects as in vcd_draw_pinhole_4cams

    draw_scene(vcd)

    openlabel_version_name = "openlabel" + schema.openlabel_schema_version.replace(".", "")
    vcd.save('../tests/etc/' + openlabel_version_name + '_test_scl_camera_fisheye_xz1z2_radial_poly.json')
