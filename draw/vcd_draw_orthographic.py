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


def setup_1_camera_orthographic():
    vcd = core.VCD()
    vcd.add_coordinate_system("vehicle-iso8855", cs_type=types.CoordinateSystemType.local_cs)

    # Let's build the cameras
    img_width_px = 1280
    img_height_px = 966
    
    ################################
    # CAM_FRONT
    ################################
    # Intrinsics & Extrinsics
    # ------------------------------
    ar = img_width_px/img_height_px
    xmin = -30.0 # meters
    xmax = 30.0
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
    
    vcd.add_stream(stream_name="CAM_FRONT_ORTHO",
                   uri="",
                   description="Orthographic camera",
                   stream_type=core.StreamType.camera)
    vcd.add_stream_properties(stream_name="CAM_FRONT_ORTHO",
                              intrinsics=types.IntrinsicsOrthographic(
                                  width_px=img_width_px,
                                  height_px=img_height_px,
                                  xmin=xmin,
                                  xmax=xmax,
                                  ymin=ymin,
                                  ymax=ymax
                              )
                              )
    vcd.add_coordinate_system("CAM_FRONT_ORTHO", cs_type=types.CoordinateSystemType.sensor_cs,
                              parent_name="vehicle-iso8855",
                              pose_wrt_parent=types.PoseData(
                                  val=list(P_scs_wrt_lcs.flatten()),
                                  type=types.TransformDataType.matrix_4x4)
                              )   

    return vcd


def draw_scene(vcd):
    # Prepare objects
    scene = scl.Scene(vcd)  # scl.Scene has functions to project images, transforms, etc.

    # Define viewers
    drawer_front_ortho = draw.Image(scene, "CAM_FRONT_ORTHO")
    setupViewer = draw.SetupViewer(scene, "vehicle-iso8855")

    # Draw the images
    img_width_px = 1280
    img_height_px = 966
    img_front_ortho = 255 * np.ones((img_height_px, img_width_px, 3), np.uint8)     
    imageParams = draw.Image.Params(_colorMap=utils.colorMap_1)
    drawer_front_ortho.draw(img_front_ortho, 0, _params=imageParams)
    
    # Draw the top view
    topview_width = 1280
    topview_height = 1280
    ar = topview_width/topview_height
    rangeX = (-30.0, 30.0)
    rangeY = (-((rangeX[1] - rangeX[0]) / ar) / 2, ((rangeX[1] - rangeX[0]) / ar) / 2)
    topviewParams = draw.TopView.Params(colorMap=utils.colorMap_1,
                                         topViewSize=(topview_width, topview_height),
                                         background_color=255,
                                         rangeX=rangeX,
                                         rangeY=rangeY,
                                         stepX=1.0, stepY=1.0,
                                        draw_grid=False)
    drawerTopView = draw.TopView(scene, "vehicle-iso8855", params=topviewParams)
    topView = drawerTopView.draw(frameNum=0)
    
    cv.namedWindow("CAM_FRONT_ORTHO", cv.WINDOW_NORMAL)
    cv.imshow("CAM_FRONT_ORTHO", img_front_ortho)    
    cv.namedWindow("TopView", cv.WINDOW_NORMAL)
    cv.imshow("TopView", topView)    
    cv.waitKey(1)

    fig1 = setupViewer.plot_setup()
    plt.show()

if __name__ == '__main__':
    print("Running " + os.path.basename(__file__))

    vcd = setup_1_camera_orthographic()
    vcd = vcd_draw_pinhole_4cams.add_some_objects(vcd)  # so let's add the same objects as in vcd_draw_pinhole_4cams

    draw_scene(vcd)

    openlabel_version_name = "openlabel" + schema.openlabel_schema_version.replace(".", "")
    #vcd.save('../tests/etc/' + openlabel_version_name + '_test_scl_camera_orthographic.json')
