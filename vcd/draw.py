"""
VCD (Video Content Description) library v4.3.0

Project website: http://vcd.vicomtech.org

Copyright (C) 2020, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.3.0.
VCD is distributed under MIT License. See LICENSE.

"""



import sys
sys.path.insert(0, ".")
from random import seed
from random import randint
import vcd.core as core
import vcd.utils as utils
import vcd.scl as scl
import numpy as np
import cv2 as cv
import warnings

import matplotlib.pyplot as plt


def draw_barrel_distortion_grid(img, cam, color, only_outer=True, extended=False):
    # Define grid in undistorted space and then apply distortPoint
    height, width = img.shape[:2]

    # Debug, see where the points fall if undistorted
    num_steps = 50
    xStart = 0
    xEnd = width
    yStart = 0
    yEnd = height

    if extended:
        xStart = int(-2 * width)
        xEnd = int(width + 2 * width)
        yStart = int(-2 * height)
        yEnd = int(height + 2 * height)

    stepX = (xEnd - xStart) / num_steps
    stepY = (yEnd - yStart) / num_steps

    # Lines in X
    for y in np.linspace(yStart, yEnd, num_steps+1):
        for x in np.linspace(xStart, xEnd, num_steps+1):
            if only_outer:
                if y > 0 and y < height:
                    continue

            pA = (x, y)  # (i * stepX, j * stepY)
            pB = (x + stepX, y)  # ((i+1) * stepX, j * stepY)
            if x + stepX > width:
                continue
            pDA = cam.distort_points2d_scs(np.array([[pA[0]], [pA[1]]]))
            pDB = cam.distort_points2d_scs(np.array([[pB[0]], [pB[1]]]))

            # cv2.circle(imgDist, pointDistA, 3, bgr, -1)
            if 0 <= pDA[0, 0] < width and 0 <= pDA[1, 0] < height and \
                    0 <= pDB[0, 0] < width and 0 <= pDB[1, 0] < height:
                color_to_use = color
                if y == 0 or y == height:
                    color_to_use = (255, 0, 0)
                cv.line(img, (utils.round(pDA[0, 0]), utils.round(pDA[1, 0])),
                        (utils.round(pDB[0, 0]), utils.round(pDB[1, 0])), color_to_use, 2)

    # Lines in Y
    for y in np.linspace(yStart, yEnd, num_steps+1):
        for x in np.linspace(xStart, xEnd, num_steps+1):
            if only_outer:
                if x > 0 and x < width:
                    continue
            pA = (x, y)  # (i * stepX, j * stepY)
            pB = (x, y + stepY)  # (i * stepX, (j + 1) * stepY)
            if y + stepY > height:
                continue
            pDA = cam.distort_points2d_scs(np.array([[pA[0]], [pA[1]]]))
            pDB = cam.distort_points2d_scs(np.array([[pB[0]], [pB[1]]]))

            # cv2.circle(imgDist, pointDistA, 3, bgr, -1)
            if 0 <= pDA[0, 0] < width and 0 <= pDA[1, 0] < height and \
                    0 <= pDB[0, 0] < width and 0 <= pDB[1, 0] < height:
                color_to_use = color
                if x == 0 or x == width:
                    color_to_use = (255, 0, 0)
                cv.line(img, (utils.round(pDA[0, 0]), utils.round(pDA[1, 0])),
                            (utils.round(pDB[0, 0]), utils.round(pDB[1, 0])), color_to_use, 2)


def draw_barrel_distortion_limits(img, cam, num_steps=1):
    height, width = img.shape[:2]

    # Create extended image
    margin = width//2
    imExt = np.zeros((height + 2 * margin, width + 2 * margin, 3), np.uint8)
    imExt[margin:margin + height, margin:margin + width] = img
    cv.namedWindow("extended", cv.WINDOW_NORMAL)

    # Debug, see where the points fall if undistorted
    xStart = 0
    xEnd = width
    yStart = 0
    yEnd = height
    stepX = (xEnd - xStart) / num_steps
    stepY = (yEnd - yStart) / num_steps

    # Lines in X
    for y in np.linspace(yStart, yEnd, num_steps+1):
        for x in np.linspace(xStart, xEnd, num_steps+1):
            pA = (x, y)  # (i * stepX, j * stepY)
            pB = (x + stepX, y)  # ((i+1) * stepX, j * stepY)
            if x + stepX > width:
                continue

            pUA = cam.undistort_points2d_scs(np.array([[pA[0]], [pA[1]]]))
            pUB = cam.undistort_points2d_scs(np.array([[pB[0]], [pB[1]]]))

            cv.line(imExt, (utils.round(pUA[0, 0] + margin), utils.round(pUA[1, 0] + margin)),
                     (utils.round(pUB[0, 0] + margin), utils.round(pUB[1, 0] + margin)), (0,255,0), 2)

    # Lines in X
    for y in np.linspace(yStart, yEnd, num_steps + 1):
        for x in np.linspace(xStart, xEnd, num_steps + 1):
            pA = (x, y)  # (i * stepX, j * stepY)
            pB = (x, y + stepY)  # (i * stepX, (j + 1) * stepY)
            pUA = cam.undistort_points2d_scs(np.array([[pA[0]], [pA[1]]]))
            pUB = cam.undistort_points2d_scs(np.array([[pB[0]], [pB[1]]]))

            if y + stepY > height:
                continue

            cv.line(imExt, (utils.round(pUA[0, 0] + margin), utils.round(pUA[1, 0] + margin)),
                    (utils.round(pUB[0, 0] + margin), utils.round(pUB[1, 0] + margin)), (0, 255, 0), 2)

    cv.imshow("extended", imExt)
    cv.waitKey(0)


class SetupViewer:
    def __init__(self, scene, coordinate_system):
        assert (isinstance(scene, scl.Scene))
        self.scene = scene
        self.fig = plt.figure(figsize=(8, 8))
        self.ax = self.fig.gca(projection='3d')
        self.coordinate_system = coordinate_system
        assert(self.scene.vcd.has_coordinate_system(coordinate_system))

    def __plot_cs(self, pose_wrt_ref, name, L=1):
        # Explore the coordinate systems defined for this scene
        axis = np.array([[0, L, 0, 0, 0, 0],
                [0, 0, 0, L, 0, 0],
                [0, 0, 0, 0, 0, L],
                [1, 1, 1, 1, 1, 1]])  # matrix with several 4x1 points
        pose_wrt_ref = np.array(pose_wrt_ref).reshape(4, 4)
        axis_ref = pose_wrt_ref.dot(axis)
        origin = axis_ref[:, 0]
        x_axis_end = axis_ref[:, 1]
        y_axis_end = axis_ref[:, 3]
        z_axis_end = axis_ref[:, 5]
        self.ax.plot([origin[0], x_axis_end[0]], [origin[1], x_axis_end[1]], [origin[2], x_axis_end[2]], 'r-')
        self.ax.plot([origin[0], y_axis_end[0]], [origin[1], y_axis_end[1]], [origin[2], y_axis_end[2]], 'g-')
        self.ax.plot([origin[0], z_axis_end[0]], [origin[1], z_axis_end[1]], [origin[2], z_axis_end[2]], 'b-')

        self.ax.text(origin[0], origin[1], origin[2], r'{}'.format(name))
        self.ax.text(x_axis_end[0], x_axis_end[1], x_axis_end[2], 'X')
        self.ax.text(y_axis_end[0], y_axis_end[1], y_axis_end[2], 'Y')
        self.ax.text(z_axis_end[0], z_axis_end[1], z_axis_end[2], 'Z')

    def plot_setup(self, axes=None):
        for cs_name, cs in self.scene.vcd.data['vcd']['coordinate_systems'].items():
            T = self.scene.get_transform(cs_name, self.coordinate_system)
            L=2.0
            if cs['type'] == 'sensor_cs':
                L=0.5
            self.__plot_cs(T, cs_name, L)

        if 'objects' in self.scene.vcd.data['vcd']:
            for object_id, object in self.scene.vcd.data['vcd']['objects'].items():
                if object['name'] == "Ego-car":
                    cuboid = object['object_data']['cuboid'][0]
                    cuboid_cs = object['object_data']['cuboid'][0]['coordinate_system']
                    cuboid_vals = object['object_data']['cuboid'][0]['val']

                    t = self.scene.get_transform(cuboid_cs, self.coordinate_system)
                    cuboid_vals_transformed = utils.transform_cuboid(cuboid_vals, t)

                    p = utils.generate_cuboid_points_ref_4x8(cuboid_vals_transformed)

                    pairs = (
                    [0, 1], [1, 2], [2, 3], [3, 0], [0, 4], [1, 5], [2, 6], [3, 7], [4, 5], [5, 6], [6, 7], [7, 4])
                    for pair in pairs:
                        self.ax.plot([p[0, pair[0]], p[0, pair[1]]],
                                     [p[1, pair[0]], p[1, pair[1]]],
                                     [p[2, pair[0]], p[2, pair[1]]], c='k')

        if axes is None:
            self.ax.set_xlim(-1.25, 4.25)
            self.ax.set_ylim(-2.75, 2.75)
            self.ax.set_zlim(0, 5.5)
        else:
            self.ax.set_xlim(axes[0][0], axes[0][1])
            self.ax.set_ylim(axes[1][0], axes[1][1])
            self.ax.set_zlim(axes[2][0], axes[2][1])

        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')

        return self.fig

class TopView:
    # This class draws a top view of the scene, assuming Z=0 is the ground plane (i.e. the topview sees the XY plane)
    # Range and scale can be used to select a certain part of the XY plane
    class Params:
        '''
        Assuming cuboids are drawn top view, so Z coordinate is ignored
        RZ is the rotation in Z-axis, it assumes/enforces SY>SX, thus keeping
        RZ between pi/2 and -pi/2

        Z, RX, RY, and SZ are ignored

        For Vehicle cases, we adopt ISO8855: origin at rear axle at ground, x-to-front, y-to-left
        '''

        def __init__(self, _stepX=None, _stepY=None, _background_color=None,_imgSize=None, _rangeX=None, _rangeY=None,
                     _colorMap=None, _ignore_classes=None,
                     _draw_grid=None):
            self.imgSize = (1920, 1080)  # width, height
            if _imgSize is not None:
                assert (isinstance(_imgSize, tuple))
                self.imgSize = _imgSize

            self.ar = self.imgSize[0] / self.imgSize[1]

            self.rangeX = (-80.0, 80.0)
            if _rangeX is not None:
                assert (isinstance(_rangeX, tuple))
                self.rangeX = _rangeX

            self.rangeY = (self.rangeX[0] / self.ar, self.rangeX[1] / self.ar)
            if _rangeY is not None:
                assert (isinstance(_rangeX, tuple))
                self.rangeY = _rangeY

            self.scaleX = self.imgSize[0] / (self.rangeX[1] - self.rangeX[0])
            self.scaleY = -self.imgSize[1] / (self.rangeY[1] - self.rangeY[0])

            self.offsetX = round(-self.rangeX[0] * self.scaleX)
            self.offsetY = round(-self.rangeY[1] * self.scaleY)

            self.stepX = 1.0
            if _stepX is not None:
                self.stepX = _stepX
            self.stepY = 1.0
            if _stepY is not None:
                self.stepY = _stepY

            self.gridLinesThickness = 1
            self.backgroundColor = 255
            if _background_color is not None:
                self.backgroundColor = _background_color

            self.gridTextColor = (0, 0, 0)

            if _colorMap is None:
                self.colorMap = dict()
            else:
                assert (isinstance(_colorMap, dict))
                self.colorMap = _colorMap

            if _ignore_classes is None:
                self.ignore_classes = dict()
            else:
                self.ignore_classes = _ignore_classes

            if _draw_grid is None:
                self.draw_grid = True
            else:
                self.draw_grid = _draw_grid

    def __init__(self, scene, coordinate_system):
        # scene contains the VCD and helper functions for transforms and projections
        assert(isinstance(scene, scl.Scene))
        self.scene = scene
        # This value specifies which coordinate system is fixed in the
        # center of the TopView, e.g. "odom" or "vehicle-iso8855"
        assert(scene.vcd.has_coordinate_system(coordinate_system))
        self.coordinate_system = coordinate_system
        self.params = TopView.Params()

    def draw(self, frameNum, uid=None, _drawTrajectory=True, _params=None):
        self.topView = None
        if _params is not None:
            assert(isinstance(_params, TopView.Params))
            self.params = _params

        # Base
        self.topView = np.zeros((self.params.imgSize[1], self.params.imgSize[0], 3), np.uint8)  # Needs to be here
        self.draw_topview_base()

        # Draw objects
        self.draw_objects_at_frame(uid, frameNum, _drawTrajectory)

        # Draw frame info
        self.draw_info(frameNum)

        return self.topView

    def draw_info(self, frameNum):
        cv.putText(self.topView, "Img. Size(px): " + str(self.params.imgSize[0]) + " x " + str(self.params.imgSize[1]),
                   (self.params.imgSize[0] - 250, self.params.imgSize[1] - 140),
                   cv.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 0), 1, cv.LINE_AA)
        cv.putText(self.topView, "Frame: " + str(frameNum),
                   (self.params.imgSize[0] - 250, self.params.imgSize[1] - 120),
                   cv.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 0), 1, cv.LINE_AA)
        cv.putText(self.topView, "CS: " + str(self.coordinate_system),
                   (self.params.imgSize[0] - 250, self.params.imgSize[1] - 100),
                   cv.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 0), 1, cv.LINE_AA)

        cv.putText(self.topView, "RangeX (m): (" + str(self.params.rangeX[0]) + ", " + str(self.params.rangeX[1]) + ")",
                   (self.params.imgSize[0] - 250, self.params.imgSize[1] - 80),
                   cv.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 0), 1, cv.LINE_AA)
        cv.putText(self.topView, "RangeY (m): (" + str(self.params.rangeX[0]) + ", " + str(self.params.rangeX[1]) + ")",
                   (self.params.imgSize[0] - 250, self.params.imgSize[1] - 60),
                   cv.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 0), 1, cv.LINE_AA)

        cv.putText(self.topView, "OffsetX (px): (" + str(self.params.offsetX) + ", " + str(self.params.offsetX) + ")",
                   (self.params.imgSize[0] - 250, self.params.imgSize[1] - 40),
                   cv.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 0), 1, cv.LINE_AA)
        cv.putText(self.topView, "OffsetY (px): (" + str(self.params.offsetY) + ", " + str(self.params.offsetY) + ")",
                   (self.params.imgSize[0] - 250, self.params.imgSize[1] - 20),
                   cv.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 0), 1, cv.LINE_AA)

    def draw_topview_base(self):
        self.topView.fill(self.params.backgroundColor)

        if self.params.draw_grid:
            # Grid x (1/2)
            for x in np.arange(self.params.rangeX[0], self.params.rangeX[1] + self.params.stepX, self.params.stepX):
                x_round = round(x)
                ptImg1 = self.point2Pixel((x_round, self.params.rangeY[0]))
                ptImg2 = self.point2Pixel((x_round, self.params.rangeY[1]))
                cv.line(self.topView, ptImg1, ptImg2, (127, 127, 127), self.params.gridLinesThickness)

            # Grid y (1/2)
            for y in np.arange(self.params.rangeY[0], self.params.rangeY[1] + self.params.stepY, self.params.stepY):
                y_round = round(y)
                ptImg1 = self.point2Pixel((self.params.rangeX[0], y_round))
                ptImg2 = self.point2Pixel((self.params.rangeX[1], y_round))
                cv.line(self.topView, ptImg1, ptImg2, (127, 127, 127), self.params.gridLinesThickness)

            # Grid x (2/2)
            for x in np.arange(self.params.rangeX[0], self.params.rangeX[1] + self.params.stepX, self.params.stepX):
                x_round = round(x)
                ptImg1 = self.point2Pixel((x_round, self.params.rangeY[0]))
                cv.putText(self.topView, str(round(x)) + " m", (ptImg1[0] + 5, 15), cv.FONT_HERSHEY_PLAIN,
                           0.6, self.params.gridTextColor, 1, cv.LINE_AA)
            # Grid y (2/2)
            for y in np.arange(self.params.rangeY[0], self.params.rangeY[1] + self.params.stepY, self.params.stepY):
                y_round = round(y)
                ptImg1 = self.point2Pixel((self.params.rangeX[0], y_round))
                cv.putText(self.topView, str(round(y)) + " m", (5, ptImg1[1] - 5),
                           cv.FONT_HERSHEY_PLAIN,
                           0.6, self.params.gridTextColor, 1, cv.LINE_AA)

        # World origin
        cv.circle(self.topView, self.point2Pixel((0.0, 0.0)), 4, (255, 255, 255), -1)
        cv.line(self.topView, self.point2Pixel((0.0, 0.0)), self.point2Pixel((5.0, 0.0)), (0, 0, 255), 2)
        cv.line(self.topView, self.point2Pixel((0.0, 0.0)), self.point2Pixel((0.0, 5.0)), (0, 255, 0), 2)

        cv.putText(self.topView, "X", self.point2Pixel((5.0, -0.5)), cv.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 255), 1, cv.LINE_AA)
        cv.putText(self.topView, "Y", self.point2Pixel((-1.0, 5.0)), cv.FONT_HERSHEY_PLAIN, 1.0, (0, 255, 0), 1, cv.LINE_AA)

    def draw_points3d(self, _img, points3d_4xN, _color):
        rows, cols = points3d_4xN.shape
        for i in range(0, cols):
            pt = self.point2Pixel((points3d_4xN[0, i], points3d_4xN[1, i]))  # thus ignoring z component
            cv.circle(_img, pt, 2, _color, -1)

    def draw_cuboid_topview(self, _img, _cuboid, _class, _color, _thick, _ID=""):
        assert(isinstance(_cuboid, list))
        assert(len(_cuboid) == 9)  # (X, Y, Z, RX, RY, RZ, SX, SY, SZ)
        # TODO cuboids with quaternions

        points_4x8 = utils.generate_cuboid_points_ref_4x8(_cuboid)
        # Project into topview
        points_4x8[2, :] = 0

        pairs = ([0, 1], [1, 2], [2, 3], [3, 0], [0, 4], [1, 5], [2, 6], [3, 7], [4, 5], [5, 6], [6, 7], [7, 4])
        for pair in pairs:
            p_a = (points_4x8[0, pair[0]], points_4x8[1, pair[0]])
            p_b = (points_4x8[0, pair[1]], points_4x8[1, pair[1]])
            cv.line(_img, self.point2Pixel(p_a), self.point2Pixel(p_b), _color, _thick )

    def draw_object_data(self, object_, object_class, _img, uid, _frameNum, _drawTrajectory):
        # Reads cuboids
        hasCuboid = False
        if "object_data" in object_:
            for object_data_key in object_['object_data'].keys():
                for object_data_item in object_['object_data'][object_data_key]:
                    ########################################
                    # CUBOIDS
                    ########################################
                    if object_data_key == "cuboid":
                        hasCuboid = True
                        cuboid_vals = object_data_item['val']
                        cuboid_name = object_data_item['name']
                        if 'coordinate_system' in object_data_item:
                            cs_data = object_data_item['coordinate_system']
                        else:
                            warnings.warn("WARNING: The cuboids of this VCD don't have a coordinate_system.")
                            # For simplicity, let's assume they are already expressed in the target cs
                            cs_data = self.coordinate_system

                        # Convert from data coordinate system (e.g. "CAM_LEFT")
                        #  into reference coordinate system (e.g. "VEHICLE-ISO8855")
                        cuboid_vals_transformed = cuboid_vals
                        if cs_data != self.coordinate_system:
                            cuboid_vals_transformed = self.scene.transform_cuboid(cuboid_vals,
                                                                                  cs_data, self.coordinate_system,
                                                                                  _frameNum)
                        # Draw
                        self.draw_cuboid_topview(_img,
                                               cuboid_vals_transformed,
                                               object_class,
                                               self.params.colorMap[object_class],
                                               2,
                                               uid)

                        if _drawTrajectory:
                            fis_object = self.scene.vcd.get_object_data_frame_intervals(uid, cuboid_name)
                            if fis_object.empty():
                                # So this object is static, let's project its cuboid into the current transform
                                fis = self.scene.vcd.get_frame_intervals().get_dict()
                            else:
                                fis = fis_object.get_dict()

                            for fi in fis:
                                prev_center = dict()
                                for f in range(fi['frame_start'], _frameNum + 1):
                                    object_data_item = self.scene.vcd.get_object_data(uid, cuboid_name, f)

                                    cuboid_vals = object_data_item['val']
                                    cuboid_vals_transformed = cuboid_vals
                                    if cs_data != self.coordinate_system:
                                        src_cs = cs_data
                                        dst_cs = self.coordinate_system
                                        transform_src_dst = self.scene.get_transform(src_cs,
                                                                                dst_cs, f)
                                        if transform_src_dst is not None:
                                            cuboid_vals_transformed = utils.transform_cuboid(
                                                cuboid_vals, transform_src_dst)

                                    name = object_data_item['name']

                                    center = (cuboid_vals_transformed[0], cuboid_vals_transformed[1])
                                    center_pix = self.point2Pixel(center)

                                    # this is a dict to allow multiple trajectories
                                    # (e.g. several cuboids per object)
                                    if prev_center.get(name) is not None:
                                        cv.line(_img, prev_center[name], center_pix, (0, 0, 0),
                                                1, cv.LINE_AA)

                                    cv.circle(_img, center_pix, 2,
                                              self.params.colorMap[object_class], -1)

                                    prev_center[name] = center_pix
                    ########################################
                    # mat - points3d_4xN
                    ########################################
                    elif object_data_key == "mat":
                        width = object_data_item['width']
                        height = object_data_item['height']

                        if height == 4:
                            # These are points 4xN
                            color = self.params.colorMap[object_class]
                            points3d_4xN = np.array(object_data_item['val']).reshape(height, width)
                            points_cs = object_data_item['coordinate_system']

                            # First convert from the src coordinate system into the camera coordinate system
                            points3d_4xN_transformed = self.scene.transform_points3d_4xN(points3d_4xN,
                                                                                         points_cs,
                                                                                         self.coordinate_system)

                            if 'attributes' in object_data_item:
                                for attr_type, attr_list in object_data_item['attributes'].items():
                                    if attr_type == 'vec':
                                        for attr in attr_list:
                                            if attr['name'] == 'color':
                                                color = attr['val']

                            self.draw_points3d(_img, points3d_4xN_transformed, color)


    def draw_objects_at_frame(self, uid, _frameNum, _drawTrajectory):
        img = self.topView

        # Explore objects at this VCD frame
        vcd_frame = self.scene.vcd.get_frame(_frameNum)
        if 'objects' in vcd_frame:
            for object_id, object_ in vcd_frame['objects'].items():
                if uid is not None:
                    if object_id != uid:
                        continue

                # Get object static info
                object_class = self.scene.vcd.get_object(object_id)['type']

                # Ignore classes
                if object_class in self.params.ignore_classes:
                    continue

                # Colors
                if self.params.colorMap.get(object_class) is None:
                    # Let's create a new entry for this class
                    self.params.colorMap[object_class] = (randint(0, 255), randint(0, 255), randint(0, 255))

                # Check if the object has specific info at this frame, or if we need to consult the static object info
                if len(object_) == 0:
                    # So this is a pointer to a static object
                    static_object = self.scene.vcd.data['vcd']['objects'][object_id]
                    self.draw_object_data(static_object, object_class,
                                               img, object_id, _frameNum, _drawTrajectory)
                else:
                    # Let's use the dynamic info of this object
                    self.draw_object_data(object_, object_class,
                                               img, object_id, _frameNum, _drawTrajectory)

    def size2Pixel(self, _size):
        return (int(round(_size[0] * abs(self.params.scaleX))),
                int(round(_size[1] * abs(self.params.scaleY))))

    def point2Pixel(self, _point):
        pixel = (int(round(_point[0]*self.params.scaleX + self.params.offsetX)),
                 int(round(_point[1]*self.params.scaleY + self.params.offsetY)))
        return pixel


class Image:
    '''
    This class draws 2D elements in the Image.
    Devised to draw bboxes, it can also project 3D entities (e.g. cuboids) using the calibration parameters
    '''
    class Params:
        def __init__(self, _draw_trajectory=False, _colorMap=None, _ignore_classes=None, _draw_types=None):
            if _colorMap is None:
                self.colorMap = dict()
            else:
                assert (isinstance(_colorMap, dict))
                self.colorMap = _colorMap
            self.draw_trajectory = _draw_trajectory
            if _ignore_classes is None:
                self.ignore_classes = dict()
            else:
                self.ignore_classes = _ignore_classes

            if _draw_types is not None:
                self.draw_types = _draw_types
            else:
                self.draw_types = {"bbox"}

    def __init__(self, scene, camera_coordinate_system=None):
        assert (isinstance(scene, scl.Scene))
        self.scene = scene
        if camera_coordinate_system is not None:
            assert (scene.vcd.has_coordinate_system(camera_coordinate_system))
        self.camera_coordinate_system = camera_coordinate_system
        self.params = Image.Params()

    def draw_points3d(self, _img, points3d_4xN, _color):
        cam = self.scene.get_camera(self.camera_coordinate_system)
        # this function may return LESS than N points IF 3D points are BEHIND the camera
        points2d_4xN = cam.project_points3d(points3d_4xN)
        if points2d_4xN is None:
            return
        rows, cols = points2d_4xN.shape
        for i in range(0, cols):
            cv.circle(_img, (utils.round(points2d_4xN[0, i]), utils.round(points2d_4xN[1, i])), 2, _color, -1)

    def draw_cuboid(self, _img, _cuboid_vals, _class, _color):
        assert (isinstance(_cuboid_vals, list))
        assert (len(_cuboid_vals) == 9)  # (X, Y, Z, RX, RY, RZ, SX, SY, SZ)
        # TODO cuboids with quaternions

        # Generate object coordinates
        points3d_4x8 = utils.generate_cuboid_points_ref_4x8(_cuboid_vals)

        cam = self.scene.get_camera(self.camera_coordinate_system)
        points2d_4x8 = cam.project_points3d(points3d_4x8)  # this function may return LESS than 8 points IF 3D points are BEHIND the camera
        if points2d_4x8 is None:
            return

        num_points_projected = points2d_4x8.shape[1]

        pairs = ([0, 1], [1, 2], [2, 3], [3, 0], [0, 4], [1, 5], [2, 6], [3, 7], [4, 5], [5, 6], [6, 7], [7, 4])
        for count, pair in enumerate(pairs):
            if pair[0] >= num_points_projected or pair[1] >= num_points_projected:
                continue
            p_a = (utils.round(points2d_4x8[0, pair[0]]), utils.round(points2d_4x8[1, pair[0]]))
            p_b = (utils.round(points2d_4x8[0, pair[1]]), utils.round(points2d_4x8[1, pair[1]]))
            cv.line(_img, p_a, p_b, _color, 1)
        pass

    def draw_bbox(self, _img, _bbox, _object_class, _color, add_border=False):
        pt1 = (int(round(_bbox[0] - _bbox[2]/2)), int(round(_bbox[1] - _bbox[3]/2)))
        pt2 = (int(round(_bbox[0] + _bbox[2]/2)), int(round(_bbox[1] + _bbox[3]/2)))

        pta = (pt1[0], pt1[1] - 15)
        ptb = (pt2[0], pt1[1])

        if add_border:
            cv.rectangle(_img, pta, ptb, _color, 2)
            cv.rectangle(_img, pta, ptb, _color, -1)
        cv.putText(_img, _object_class, (pta[0], pta[1] + 10), cv.FONT_HERSHEY_PLAIN, 0.6, (0,0,0), 1, cv.LINE_AA)
        cv.rectangle(_img, pt1, pt2, _color, 2)

    def draw_trajectory(self, _img, _object_id, _frameNum, _params):
        object_class = self.scene.vcd.get_object(_object_id)['type']
        fis = (self.scene.vcd.get_element_frame_intervals(core.ElementType.object, _object_id)).get_dict()

        for fi in fis:
            prev_center = dict()
            for f in range(fi['frame_start'], _frameNum + 1):
                vcd_other_frame = self.scene.vcd.get_frame(f)
                if 'objects' in vcd_other_frame:
                    for object_id_this, object in vcd_other_frame['objects'].items():
                        if object_id_this is not _object_id:
                            continue

                        # Get value at this frame
                        if "object_data" in object:
                            for object_data_key in object['object_data'].keys():
                                for object_data_item in object['object_data'][object_data_key]:
                                    if object_data_key == "bbox":
                                        bbox = object_data_item['val']
                                        name = object_data_item['name']

                                        center = (int(round(bbox[0])), int(round(bbox[1])))

                                        # this is a dict to allow multiple trajectories
                                        # (e.g. several bbox per object)
                                        if prev_center.get(name) is not None:
                                            cv.line(_img, prev_center[name], center, (0, 0, 0),
                                                    1, cv.LINE_AA)

                                        #cv.circle(_img, center, 2,
                                        #          _params.colorMap[object_class], -1)

                                        prev_center[name] = center


    def draw(self, _img, _frameNum, _params=None):
        if _params is not None:
            assert(isinstance(_params, Image.Params))
            self.params = _params

        # Explore objects at VCD
        vcd_frame = self.scene.vcd.get_frame(_frameNum)
        if 'objects' in vcd_frame:
            for object_id, object in vcd_frame['objects'].items():
                # Get object static info
                name = self.scene.vcd.get_object(object_id)['name']
                object_class = self.scene.vcd.get_object(object_id)['type']
                if object_class in self.params.ignore_classes:
                    continue

                # Colors
                if self.params.colorMap.get(object_class) is None:
                    # Let's create a new entry for this class
                    self.params.colorMap[object_class] = (randint(0, 255), randint(0, 255), randint(0, 255))

                # Get current value at this frame
                if "object_data" in object:
                    for object_data_key in object['object_data'].keys():
                        for object_data_item in object['object_data'][object_data_key]:
                            ############################################
                            # bbox
                            ############################################
                            if object_data_key == "bbox":
                                bbox = object_data_item['val']
                                bbox_name = object_data_item['name']
                                #text = "(" + object_id + "," + name +")-(" + object_class + ")-(" + bbox_name +")"
                                text = object_id + " " + bbox_name
                                self.draw_bbox(_img, bbox, text, self.params.colorMap[object_class], True)
                                if self.params.draw_trajectory:
                                    self.draw_trajectory(_img, object_id, _frameNum, _params)
                            ############################################
                            # cuboid
                            ############################################
                            elif object_data_key == "cuboid":
                                # Read coordinate system of this cuboid, and transform into camera coordinate system
                                cuboid_cs = object_data_item['coordinate_system']
                                cuboid_vals = object_data_item['val']
                                cuboid_vals_transformed = self.scene.transform_cuboid(cuboid_vals,
                                                                                      cuboid_cs,
                                                                                      self.camera_coordinate_system)
                                self.draw_cuboid(_img, cuboid_vals_transformed, "", self.params.colorMap[object_class])
                            ############################################
                            # mat as points3d_4xN
                            ############################################
                            elif object_data_key == "mat":
                                width = object_data_item['width']
                                height = object_data_item['height']

                                if height == 4:
                                    # These are points 4xN
                                    color = self.params.colorMap[object_class]
                                    points3d_4xN = np.array(object_data_item['val']).reshape(height, width)
                                    points_cs = object_data_item['coordinate_system']

                                    # First convert from the src coordinate system into the camera coordinate system
                                    points3d_4xN_transformed = self.scene.transform_points3d_4xN(points3d_4xN,
                                                                      points_cs, self.camera_coordinate_system)

                                    if 'attributes' in object_data_item:
                                        for attr_type, attr_list in object_data_item['attributes'].items():
                                            if attr_type == 'vec':
                                                for attr in attr_list:
                                                    if attr['name'] == 'color':
                                                        color = attr['val']

                                    self.draw_points3d(_img, points3d_4xN_transformed, color)

        # Draw info
        if self.camera_coordinate_system is not None:
            text = self.camera_coordinate_system
            margin = 20
            cv.putText(_img, text,
                       (margin, margin),
                       cv.FONT_HERSHEY_DUPLEX, 0.8, (0, 0, 0), 2, cv.LINE_AA)
            cv.putText(_img, text,
                       (margin, margin),
                       cv.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1, cv.LINE_AA)


class FrameInfoDrawer:
    # This class draws Element information in a window
    class Params:
        def __init__(self, _colorMap=None):
            if _colorMap is None:
                self.colorMap = dict()
            else:
                assert (isinstance(_colorMap, dict))
                self.colorMap = _colorMap

    def __init__(self, vcd):
        assert (isinstance(vcd, core.VCD))
        self.vcd = vcd
        self.params = FrameInfoDrawer.Params()

    def draw_base(self, _img, _frameNum):
        text = "Frame: " + str(_frameNum)
        margin = 20
        cv.putText(_img, text,
                   (margin, margin),
                   cv.FONT_HERSHEY_DUPLEX, 0.8, (0, 0, 0), 1, cv.LINE_AA)
        rows, cols, channels = _img.shape
        cv.line(_img, (0, margin + 10), (cols, margin + 10), (0, 0, 0), 1)

    def draw(self, _frameNum, cols=600, rows=1200, _params=None):
        img = 255*np.ones((rows, cols, 3), np.uint8)
        if _params is not None:
            assert(isinstance(_params, Image.Params))
            self.params = _params

        self.draw_base(img, _frameNum)
        rows, cols, channels = img.shape

        # Explore objects at VCD
        count = 0
        margin = 50
        jump = 30
        vcd_frame = self.vcd.get_frame(_frameNum)

        if 'objects' in vcd_frame:
            num_objects = len(vcd_frame['objects'].keys())
            text = "Objects: " + str(num_objects)
            cv.putText(img, text,
                       (margin, margin),
                       cv.FONT_HERSHEY_DUPLEX, 0.8, (0, 0, 0), 1, cv.LINE_AA)
            cv.line(img, (0, margin + 10), (cols, margin + 10), (0, 0, 0), 1)
            count +=1
            for object_id, object in vcd_frame['objects'].items():
                # Get object static info
                name = self.vcd.get_object(object_id)['name']
                object_class = self.vcd.get_object(object_id)['type']
                fis = self.vcd.get_element_frame_intervals(core.ElementType.object, object_id)

                # Colors
                if self.params.colorMap.get(object_class) is None:
                    # Let's create a new entry for this class
                    self.params.colorMap[object_class] = (randint(0, 255), randint(0, 255), randint(0, 255))

                #text = object_id + " " + object_class + " \"" + name + "\" " + fis.to_str()
                text = object_id + " " + object_class + " " + fis.to_str()
                cv.putText(img, text,
                           (margin, margin + count * jump),
                           cv.FONT_HERSHEY_DUPLEX, 0.6, self.params.colorMap[object_class], 1, cv.LINE_AA)
                count += 1

        return img


class TextDrawer:
    def __init__(self):
        pass

    def draw(self, _str, cols=600, rows=1200):
        img = np.zeros((rows, cols, 3), np.uint8)
        count = 0

        # Split into pieces
        chars_per_line = cols//8  # fits well with 0.4 fontsize
        text_rows = [_str[i:i + chars_per_line] for i in range(0, len(_str), chars_per_line)]

        margin = 20
        jump = 20
        for text_row in text_rows:
            cv.putText(img, text_row,
                       (margin, margin + count*jump),
                       cv.FONT_HERSHEY_DUPLEX, 0.4, (255, 255, 255), 1, cv.LINE_AA)
            count += 1

        return img
