"""
VCD (Video Content Description) library v5.0.1

Project website: http://vcd.vicomtech.org

Copyright (C) 2021, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 5.0.1.
VCD is distributed under MIT License. See LICENSE.

"""

import copy
from random import randint
import vcd.core as core
import vcd.utils as utils
import vcd.scl as scl
import numpy as np
import cv2 as cv
import warnings

import matplotlib.pyplot as plt


class SetupViewer:
    '''
    This class offers Matplotlib routines to display the coordinate systems of the Scene.
    '''
    def __init__(self, scene, coordinate_system):
        assert (isinstance(scene, scl.Scene))
        self.scene = scene
        self.fig = plt.figure(figsize=(8, 8))
        self.ax = self.fig.add_subplot(projection='3d')
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

    def plot_cuboid(self, cuboid_cs, cuboid_vals, color):
        t, static = self.scene.get_transform(cuboid_cs, self.coordinate_system)
        cuboid_vals_transformed = utils.transform_cuboid(cuboid_vals, t)

        p = utils.generate_cuboid_points_ref_4x8(cuboid_vals_transformed)

        pairs = (
        [0, 1], [1, 2], [2, 3], [3, 0], [0, 4], [1, 5], [2, 6], [3, 7], [4, 5], [5, 6], [6, 7], [7, 4])
        for pair in pairs:
            self.ax.plot([p[0, pair[0]], p[0, pair[1]]],
                            [p[1, pair[0]], p[1, pair[1]]],
                            [p[2, pair[0]], p[2, pair[1]]], c=color)

    def plot_setup(self, axes=None):
        for cs_name, cs in self.scene.vcd.get_root()['coordinate_systems'].items():
            T, static = self.scene.get_transform(cs_name, self.coordinate_system)
            L=2.0
            if cs['type'] == 'sensor_cs':
                L=0.5
            self.__plot_cs(T, cs_name, L)

        if 'objects' in self.scene.vcd.get_root():
            for object_id, object in self.scene.vcd.get_root()['objects'].items():
                if object['name'] == "Ego-car":
                    cuboid = object['object_data']['cuboid'][0]
                    cuboid_cs = cuboid['coordinate_system']
                    cuboid_vals = cuboid['val']
                    self.plot_cuboid(cuboid_cs, cuboid_vals, 'k')                    
                
                else:
                    if 'object_data' in object:
                        if 'cuboid' in object['object_data']:
                            for cuboid in object['object_data']['cuboid']:
                                self.plot_cuboid(cuboid['coordinate_system'], cuboid['val'], 'k')

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
    '''
    This class draws a top view of the scene, assuming Z=0 is the ground plane (i.e. the topview sees the XY plane)
    Range and scale can be used to select a certain part of the XY plane
    '''
    class Params:
        '''
        Assuming cuboids are drawn top view, so Z coordinate is ignored
        RZ is the rotation in Z-axis, it assumes/enforces SY>SX, thus keeping
        RZ between pi/2 and -pi/2

        Z, RX, RY, and SZ are ignored

        For Vehicle cases, we adopt ISO8855: origin at rear axle at ground, x-to-front, y-to-left
        '''

        def __init__(self, stepX=None, stepY=None, background_color=None, topViewSize=None, rangeX=None, rangeY=None,
                     colorMap=None, ignore_classes=None,
                     draw_grid=None,
                     draw_only_current_image=None):
            self.topViewSize = (1920, 1080)  # width, height
            if topViewSize is not None:
                assert (isinstance(topViewSize, tuple))
                self.topViewSize = topViewSize

            self.ar = self.topViewSize[0] / self.topViewSize[1]

            self.rangeX = (-80.0, 80.0)
            if rangeX is not None:
                assert (isinstance(rangeX, tuple))
                self.rangeX = rangeX

            self.rangeY = (self.rangeX[0] / self.ar, self.rangeX[1] / self.ar)
            if rangeY is not None:
                assert (isinstance(rangeX, tuple))
                self.rangeY = rangeY

            self.scaleX = self.topViewSize[0] / (self.rangeX[1] - self.rangeX[0])
            self.scaleY = -self.topViewSize[1] / (self.rangeY[1] - self.rangeY[0])

            self.offsetX = round(-self.rangeX[0] * self.scaleX)
            self.offsetY = round(-self.rangeY[1] * self.scaleY)

            self.S = np.array([[self.scaleX, 0, self.offsetX],
                               [0, self.scaleY, self.offsetY],
                               [0, 0, 1]])

            self.stepX = 1.0
            if stepX is not None:
                self.stepX = stepX
            self.stepY = 1.0
            if stepY is not None:
                self.stepY = stepY

            self.gridLinesThickness = 1
            self.backgroundColor = 255
            if background_color is not None:
                self.backgroundColor = background_color

            self.gridTextColor = (0, 0, 0)

            if colorMap is None:
                self.colorMap = dict()
            else:
                assert (isinstance(colorMap, dict))
                self.colorMap = colorMap

            if ignore_classes is None:
                self.ignore_classes = dict()
            else:
                self.ignore_classes = ignore_classes

            if draw_grid is None:
                self.draw_grid = True
            else:
                self.draw_grid = draw_grid

            if draw_only_current_image is None:
                self.draw_only_current_image = True
            else:
                self.draw_only_current_image = draw_only_current_image

    def __init__(self, scene, coordinate_system, params=None):
        # scene contains the VCD and helper functions for transforms and projections
        assert(isinstance(scene, scl.Scene))
        self.scene = scene
        # This value specifies which coordinate system is fixed in the
        # center of the TopView, e.g. "odom" or "vehicle-iso8855"
        assert(scene.vcd.has_coordinate_system(coordinate_system))
        self.coordinate_system = coordinate_system
        if params is not None:
            self.params = params
        else:
            self.params = TopView.Params()

        # Start topView base with a background color
        self.topView = np.zeros((self.params.topViewSize[1], self.params.topViewSize[0], 3), np.uint8)  # Needs to be here
        self.topView.fill(self.params.backgroundColor) 
        self.images = {}

    def add_images(self, imgs, frameNum):
        """
        This function adds images to the TopView representation. By specifying the frame num and the camera name,
        several images can be loaded in one single call. Images should be provided
        as dictionary: {"CAM_FRONT": img_front, "CAM_REAR": img_rear}

        The function pre-computes all the necessary variables to create the TopView, such as the homography from
        image plane to world plane, or the camera region of interest, which is stored in scene.cameras dictionary
        :param imgs: dictionary of images
        :param frameNum: frame number
        :return: nothing
        """
        # Base images
        if imgs is not None:
            assert (isinstance(imgs, dict))
            # should be {"CAM_FRONT": img_front, "CAM_REAR": img_rear}

            # This option creates 1 remap for the entire topview, and not 1 per camera
            # The key idea is to weight the contribution of each camera depending on the distance betw point and cam
            # Instead of storing the result in self.images[cam_name] and then paint them in drawBEV, we can store
            # in self.images[frameNum] directly
            h = self.params.topViewSize[1]
            w = self.params.topViewSize[0]
            num_cams = len(imgs)
            cams = {}
            need_to_recompute_weights_acc = False
            need_to_recompute_maps = {}
            need_to_recompute_weights = {}
            for cam_name, img in imgs.items():
                assert self.scene.vcd.has_coordinate_system(cam_name)
                cam = self.scene.get_camera(cam_name, frameNum, compute_remaps=False)  # this call creates an entry inside scene
                cams[cam_name] = cam
                self.images.setdefault(cam_name, {})
                self.images[cam_name]['img'] = img
                t_ref_to_cam_4x4, static = self.scene.get_transform(self.coordinate_system, cam_name, frameNum)

                # Compute distances to this camera and add to weight map
                need_to_recompute_maps[cam_name] = False
                need_to_recompute_weights[cam_name] = False

                if (num_cams > 1 and not static) or (
                        num_cams > 1 and static and 'weights' not in self.images[cam_name]):
                    need_to_recompute_weights[cam_name] = True
                    need_to_recompute_weights_acc = True

                if (not static) or (static and 'mapX' not in self.images[cam_name]):
                    need_to_recompute_maps[cam_name] = True


                if need_to_recompute_maps[cam_name]:
                    print(cam_name + ' top view remap computation...')
                    self.images[cam_name]['mapX'] = np.zeros((h, w), dtype=np.float32)
                    self.images[cam_name]['mapY'] = np.zeros((h, w), dtype=np.float32)

                if need_to_recompute_weights[cam_name]:
                    print(cam_name + ' top view weights computation...')
                    self.images[cam_name].setdefault('weights', np.zeros((h, w, 3), dtype=np.float32))

            # Loop over top view domain
            for i in range(0, h):
                # Read all pixels pos of this row
                points2d_z0_3xN = np.array([np.linspace(0, w - 1, num=w),
                                            i * np.ones(w),
                                            np.ones(w)])
                # from pixels to points 3d
                temp = utils.inv(self.params.S).dot(points2d_z0_3xN)
                # hom. coords.
                points3d_z0_4xN = np.vstack((temp[0, :], temp[1, :], np.zeros(w), temp[2, :]))

                # Loop over cameras
                for idx, (cam_name, cam) in enumerate(cams.items()):
                    # Convert into camera coordinate system for all M cameras
                    t_ref_to_cam_4x4, static = self.scene.get_transform(self.coordinate_system, cam_name, frameNum)
                    points3d_cam_4xN = t_ref_to_cam_4x4.dot(points3d_z0_4xN)

                    if need_to_recompute_weights[cam_name]:
                            self.images[cam_name]['weights'][i, :, 0] = 1.0/np.linalg.norm(points3d_cam_4xN, axis=0)
                            self.images[cam_name]['weights'][i, :, 1] = self.images[cam_name]['weights'][i, :, 0]
                            self.images[cam_name]['weights'][i, :, 2] = self.images[cam_name]['weights'][i, :, 0]

                    if need_to_recompute_maps[cam_name]:
                        # Project into image
                        points2d_dist_3xN, idx_valid = cam.project_points3d(points3d_cam_4xN, remove_outside=True)

                        # Assign into map
                        self.images[cam_name]['mapX'][i, :] = points2d_dist_3xN[0, :]
                        self.images[cam_name]['mapY'][i, :] = points2d_dist_3xN[1, :]

            # Compute accumulated weights if more than 1 camera
            if need_to_recompute_weights_acc:
                self.images['weights_acc'] = np.zeros((h, w, 3), dtype=np.float32)
                for idx, (cam_name, cam) in enumerate(cams.items()):
                    self.images['weights_acc'] = cv.add(self.images[cam_name]['weights'], self.images['weights_acc'])

    def draw(self, frameNum=None, uid=None, _drawTrajectory=True):
        """
        This is the main drawing function for the TopView drawer. If explres the provided params to select different
        options.
        :param frameNum: frame number
        :param uid: unique identifier of object to be drawn (if None, all are drawn)
        :param _drawTrajectory: boolean to draw the trajectory of objects
        :param _params: additional parameters
        :return: the TopView image
        """
        # Base top view is used from previous iteration
        if self.params.draw_only_current_image:
            self.topView = np.zeros((self.params.topViewSize[1], self.params.topViewSize[0], 3),
                                    np.uint8)  # Needs to be here
            self.topView.fill(self.params.backgroundColor)

            # Draw BEW
        self.draw_BEVs(frameNum)

        # Base grids
        self.draw_topview_base()

        # Draw objects
        topViewWithObjects = copy.deepcopy(self.topView)
        self.draw_objects_at_frame(topViewWithObjects, uid, frameNum, _drawTrajectory)

        # Draw frame info
        self.draw_info(topViewWithObjects, frameNum)

        return topViewWithObjects

    def draw_info(self, topView, frameNum=None):
        h = topView.shape[0]
        w = topView.shape[1]
        w_margin = 250
        h_margin = 140
        h_step = 20
        font_size = 0.8
        cv.putText(topView, "Img. Size(px): " + str(w) + " x " + str(h),
                   (w - w_margin, h - h_margin),
                   cv.FONT_HERSHEY_PLAIN, font_size, (0, 0, 0), 1, cv.LINE_AA)
        if frameNum is None:
            frameNum = -1
        cv.putText(topView, "Frame: " + str(frameNum),
                   (w - w_margin, h - h_margin + h_step),
                   cv.FONT_HERSHEY_PLAIN, font_size, (0, 0, 0), 1, cv.LINE_AA)
        cv.putText(topView, "CS: " + str(self.coordinate_system),
                   (w - w_margin, h - h_margin + 2*h_step),
                   cv.FONT_HERSHEY_PLAIN, font_size, (0, 0, 0), 1, cv.LINE_AA)

        cv.putText(topView, "RangeX (m): (" + str(self.params.rangeX[0]) + ", " + str(self.params.rangeX[1]) + ")",
                   (w - w_margin, h - h_margin + 3*h_step),
                   cv.FONT_HERSHEY_PLAIN, font_size, (0, 0, 0), 1, cv.LINE_AA)
        cv.putText(topView, "RangeY (m): (" + str(self.params.rangeY[0]) + ", " + str(self.params.rangeY[1]) + ")",
                   (w - w_margin, h - h_margin + 4*h_step),
                   cv.FONT_HERSHEY_PLAIN, font_size, (0, 0, 0), 1, cv.LINE_AA)

        cv.putText(topView, "OffsetX (px): (" + str(self.params.offsetX) + ", " + str(self.params.offsetX) + ")",
                   (w - w_margin, h - h_margin + 5*h_step),
                   cv.FONT_HERSHEY_PLAIN, font_size, (0, 0, 0), 1, cv.LINE_AA)
        cv.putText(topView, "OffsetY (px): (" + str(self.params.offsetY) + ", " + str(self.params.offsetY) + ")",
                   (w - w_margin, h - h_margin + 6*h_step),
                   cv.FONT_HERSHEY_PLAIN, font_size, (0, 0, 0), 1, cv.LINE_AA)

    def draw_topview_base(self):
        #self.topView.fill(self.params.backgroundColor)

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
        assert(len(_cuboid) == 9 or len(_cuboid) == 10)  # (X, Y, Z, RX, RY, RZ, SX, SY, SZ)
        
        points_4x8 = utils.generate_cuboid_points_ref_4x8(_cuboid)
        # Project into topview
        points_4x8[2, :] = 0

        pairs = ([0, 1], [1, 2], [2, 3], [3, 0], [0, 4], [1, 5], [2, 6], [3, 7], [4, 5], [5, 6], [6, 7], [7, 4])
        for pair in pairs:
            p_a = (points_4x8[0, pair[0]], points_4x8[1, pair[0]])
            p_b = (points_4x8[0, pair[1]], points_4x8[1, pair[1]])
            cv.line(_img, self.point2Pixel(p_a), self.point2Pixel(p_b), _color, _thick )

    def draw_mesh_topview(self, img, mesh, points3d_4xN):
        mesh_name = mesh['name']
        mesh_point_dict = mesh['point3d']
        mesh_line_refs = mesh['line_reference']
        mesh_area_refs = mesh['area_reference']

        # Convert points into pixels
        points2d = []
        rows, cols = points3d_4xN.shape
        for i in range(0, cols):
            pt = self.point2Pixel((points3d_4xN[0, i], points3d_4xN[1, i]))  # thus ignoring z component
            points2d.append(pt)

        # Draw areas first
        for area_id, area in mesh_area_refs.items():
            line_refs = area['val']
            points_area = []
            # Loop over lines and create a list of points
            for line_ref in line_refs:
                line = mesh_line_refs[str(line_ref)]

                point_refs = line['val']
                point_a_ref = point_refs[0]
                point_b_ref = point_refs[1]
                point_a = points2d[list(mesh_point_dict).index(str(point_a_ref))]
                point_b = points2d[list(mesh_point_dict).index(str(point_b_ref))]

                points_area.append(point_a)
                points_area.append(point_b)

            cv.fillConvexPoly(img, np.array(points_area), (0, 255, 0))

        # Draw lines
        for line_id, line in mesh_line_refs.items():
            point_refs = line['val']
            point_a_ref = point_refs[0]
            point_b_ref = point_refs[1]

            point_a = points2d[list(mesh_point_dict).index(str(point_a_ref))]
            point_b = points2d[list(mesh_point_dict).index(str(point_b_ref))]

            cv.line(img, point_a, point_b, (255, 0, 0), 2)

        # Draw points
        for pt in points2d:
            cv.circle(img, pt, 5, (0, 0, 0), -1)
            cv.circle(img, pt, 3, (0, 0, 255), -1)

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

                        if _drawTrajectory and _frameNum is not None:
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
                                        transform_src_dst, static = self.scene.get_transform(src_cs,
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
                    ########################################
                    # point3d - Single point in 3D
                    ########################################
                    elif object_data_key == "point3d":
                        color = self.params.colorMap[object_class]
                        point_name = object_data_item['name']

                        if 'coordinate_system' in object_data_item:
                            cs_data = object_data_item['coordinate_system']
                        else:
                            warnings.warn("WARNING: The point3d of this VCD don't have a coordinate_system.")
                            # For simplicity, let's assume they are already expressed in the target cs
                            cs_data = self.coordinate_system

                        x = object_data_item['val'][0]
                        y = object_data_item['val'][1]
                        z = object_data_item['val'][2]
                        points3d_4xN = np.array([x, y, z, 1]).reshape(4, 1)
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

                        if _drawTrajectory and _frameNum is not None:
                            fis_object = self.scene.vcd.get_object_data_frame_intervals(uid, point_name)
                            if fis_object.empty():
                                # So this object is static, let's project its geometry into the current transform
                                fis = self.scene.vcd.get_frame_intervals().get_dict()
                            else:
                                fis = fis_object.get_dict()

                            for fi in fis:
                                prev_center = dict()
                                for f in range(fi['frame_start'], _frameNum + 1):
                                    object_data_item = self.scene.vcd.get_object_data(uid, point_name, f)

                                    x = object_data_item['val'][0]
                                    y = object_data_item['val'][1]
                                    z = object_data_item['val'][2]
                                    points3d_4xN = np.array([x, y, z, 1]).reshape(4, 1)
                                    points3d_4xN_transformed = points3d_4xN
                                    
                                    if cs_data != self.coordinate_system:
                                        src_cs = cs_data
                                        dst_cs = self.coordinate_system
                                        transform_src_dst, static = self.scene.get_transform(src_cs,
                                                                                dst_cs, f)
                                        if transform_src_dst is not None:
                                            points3d_4xN_transformed = self.scene.transform_points3d_4xN(points3d_4xN,
                                                                                        points_cs,
                                                                                        self.coordinate_system)

                                    name = object_data_item['name']

                                    center = (points3d_4xN_transformed[0,0], points3d_4xN_transformed[1,0])
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
                    # mesh - Point-line-area structure
                    ########################################
                    elif object_data_key == "mesh":

                        if 'coordinate_system' in object_data_item:
                            cs_data = object_data_item['coordinate_system']
                        else:
                            warnings.warn("WARNING: The mesh of this VCD don't have a coordinate_system.")
                            # For simplicity, let's assume they are already expressed in the target cs
                            cs_data = self.coordinate_system

                        # Let's convert mesh points into 4xN array
                        points = object_data_item['point3d']
                        points3d_4xN = np.ones((4, len(points)))
                        for point_count, (point_id, point) in enumerate(points.items()):
                            points3d_4xN[0, point_count] = point['val'][0]
                            points3d_4xN[1, point_count] = point['val'][1]
                            points3d_4xN[2, point_count] = point['val'][2]

                        points3d_4xN_transformed = self.scene.transform_points3d_4xN(points3d_4xN,
                                                                                     cs_data,
                                                                                     self.coordinate_system)

                        # Let's send the data and the possible transform info to the drawing function
                        self.draw_mesh_topview(img=_img, mesh=object_data_item, points3d_4xN=points3d_4xN_transformed)

                        # Convert from data coordinate system (e.g. "CAM_LEFT")
                        #  into reference coordinate system (e.g. "VEHICLE-ISO8855")
                        #if cs_data != self.coordinate_system:
                        #    cuboid_vals_transformed = self.scene.transform_cuboid(cuboid_vals,
                        #                                                          cs_data, self.coordinate_system,
                        #                                                          _frameNum)
                        # Draw
                        #self.draw_cuboid_topview(_img,
                        #                         cuboid_vals_transformed,
                        #                         object_class,
                        #                         self.params.colorMap[object_class],
                        #                         2,
                        #                         uid)

    def draw_objects_at_frame(self, topView, uid, _frameNum, _drawTrajectory):
        img = topView

        # Select static or dynamic objects depending on the provided input _frameNum
        objects = {}
        if _frameNum is not None:
            vcd_frame = self.scene.vcd.get_frame(_frameNum)
            if 'objects' in vcd_frame:
                objects = vcd_frame['objects']
        else:
            if self.scene.vcd.has_objects():
                objects = self.scene.vcd.get_objects()

        # Explore objects at this VCD frame
        for object_id, object_ in objects.items():
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
                static_object = self.scene.vcd.get_root()['objects'][object_id]
                self.draw_object_data(static_object, object_class,
                                           img, object_id, _frameNum, _drawTrajectory)
            else:
                # Let's use the dynamic info of this object
                self.draw_object_data(object_, object_class,
                                           img, object_id, _frameNum, _drawTrajectory)



    def draw_BEV(self, cam_name):
        img = self.images[cam_name]['img']
        h = self.params.topViewSize[1]
        w = self.params.topViewSize[0]

        mapX = self.images[cam_name]['mapX']
        mapY = self.images[cam_name]['mapY']
        bev = cv.remap(img, mapX, mapY, interpolation=cv.INTER_LINEAR,
                        borderMode=cv.BORDER_CONSTANT)

        bev32 = np.float32(bev)
        if 'weights' in self.images[cam_name]:
            cv.multiply(self.images[cam_name]['weights'], bev32, bev32)

        #cv.imshow('bev' + cam_name, bev)
        #cv.waitKey(1)

        #bev832 = np.uint8(bev32)
        #cv.imshow('bev8' + cam_name, bev832)
        #cv.waitKey(1)

        return bev32

    def draw_BEVs(self, _frameNum=None):
        """
        This function draws BEVs into the topview
        :param _frameNum:
        :return:
        """
        num_cams = len(self.images)
        if num_cams == 0:
            return

        h = self.params.topViewSize[1]
        w = self.params.topViewSize[0]
        # Prepare image with drawing for this call
        acc32 = np.zeros((h, w, 3), dtype=np.float32)  # black background

        for cam_name in self.images:
            if self.scene.get_camera(cam_name, _frameNum) is not None:
                temp32 = self.draw_BEV(cam_name=cam_name)
                #mask = np.zeros((h, w), dtype=np.uint8)
                #mask[temp32 > 0] = 255
                #mask = (temp32 > 0)
                if num_cams > 1:
                    acc32 = cv.add(temp32, acc32)
        if num_cams > 1:
            acc32 /= self.images['weights_acc']
        else:
            acc32 = temp32
        acc8 = np.uint8(acc32)
        #cv.imshow('acc', acc8)
        #cv.waitKey(1)

        # Copy into topView only new pixels
        nonzero = (acc8>0)
        self.topView[nonzero] = acc8[nonzero]


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
        def __init__(self, _draw_trajectory=False, _colorMap=None, _ignore_classes=None, _draw_types=None, _barrel=None, _thickness=None):
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

            if _barrel is not None:
                self.draw_barrel = _barrel
            else:
                self.draw_barrel = False

            if _thickness is not None:
                self.thickness = _thickness
            else:
                self.thickness = 1

    def __init__(self, scene, camera_coordinate_system=None):
        assert (isinstance(scene, scl.Scene))
        self.scene = scene
        if camera_coordinate_system is not None:
            assert (scene.vcd.has_coordinate_system(camera_coordinate_system))
        self.camera_coordinate_system = camera_coordinate_system
        self.camera = self.scene.get_camera(self.camera_coordinate_system, compute_remaps=False)
        self.params = Image.Params()

    def draw_points3d(self, _img, points3d_4xN, _color):
        # this function may return LESS than N points IF 3D points are BEHIND the camera
        points2d_3xN, idx_valid = self.camera.project_points3d(points3d_4xN, remove_outside=True)
        if points2d_3xN is None:
            return
        rows, cols = points2d_3xN.shape
        img_rows, img_cols, img_channels = _img.shape
        for i in range(0, cols):
            if idx_valid[i]:
                if np.isnan(points2d_3xN[0, i]) or np.isnan(points2d_3xN[1, i]):
                    continue
                center = (utils.round(points2d_3xN[0, i]), utils.round(points2d_3xN[1, i]))                            
                if not utils.is_inside_image(img_cols, img_rows, center[0], center[1]):
                    continue
                cv.circle(_img, (int(center[0]), int(center[1])), 2, _color, -1)

    def draw_cuboid(self, _img, _cuboid_vals, _class, _color, _thickness=1):
        assert (isinstance(_cuboid_vals, list))
        assert (len(_cuboid_vals) == 9)  # (X, Y, Z, RX, RY, RZ, SX, SY, SZ)
        # TODO cuboids with quaternions

        # Generate object coordinates
        points3d_4x8 = utils.generate_cuboid_points_ref_4x8(_cuboid_vals)

        points2d_4x8, idx_valid = self.camera.project_points3d(points3d_4x8, remove_outside=True)  # this function may return LESS than 8 points IF 3D points are BEHIND the camera
        if points2d_4x8 is None:
            return
        img_rows, img_cols, img_channels = _img.shape

        pairs = ([0, 1], [1, 2], [2, 3], [3, 0], [0, 4], [1, 5], [2, 6], [3, 7], [4, 5], [5, 6], [6, 7], [7, 4])
        for count, pair in enumerate(pairs):
            if idx_valid[pair[0]] and idx_valid[pair[1]]:
                #if pair[0] >= num_points_projected or pair[1] >= num_points_projected:
                #    continue
                p_a = (utils.round(points2d_4x8[0, pair[0]]), utils.round(points2d_4x8[1, pair[0]]))
                p_b = (utils.round(points2d_4x8[0, pair[1]]), utils.round(points2d_4x8[1, pair[1]]))

                if not utils.is_inside_image(img_cols, img_rows, p_a[0], p_b[1]) or not utils.is_inside_image(img_cols, img_rows, p_b[0], p_b[1]):
                    continue

                cv.line(_img, p_a, p_b, _color, _thickness)        

    def draw_bbox(self, _img, _bbox, _object_class, _color, add_border=False):
        pt1 = (int(round(_bbox[0] - _bbox[2]/2)), int(round(_bbox[1] - _bbox[3]/2)))
        pt2 = (int(round(_bbox[0] + _bbox[2]/2)), int(round(_bbox[1] + _bbox[3]/2)))

        pta = (pt1[0], pt1[1] - 15)
        ptb = (pt2[0], pt1[1])
        img_rows, img_cols, img_channels = _img.shape
        if add_border:
            cv.rectangle(_img, pta, ptb, _color, 2)
            cv.rectangle(_img, pta, ptb, _color, -1)
        cv.putText(_img, _object_class, (pta[0], pta[1] + 10), cv.FONT_HERSHEY_PLAIN, 0.6, (0,0,0), 1, cv.LINE_AA)

        if utils.is_inside_image(img_cols, img_rows, pt1[0], pt1[1]) and utils.is_inside_image(img_cols, img_rows, pt2[0], pt2[1]):
            cv.rectangle(_img, pt1, pt2, _color, 2)

    def draw_line(self, _img, _pt1, _pt2, _color, _thickness=1):
        cv.line(_img, _pt1, _pt2, _color, _thickness)

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

    '''
    def draw_barrel_distortion_grid(self, img, color, only_outer=True, extended=False):
        # Define grid in undistorted space and then apply distortPoint
        height, width = img.shape[:2]

        # Debug, see where the points fall if undistorted
        num_steps = 50
        xStart = 0
        xEnd = width
        yStart = 0
        yEnd = height

        if extended:
            factor = 1
            xStart = int(-factor * width)
            xEnd = int(width + factor * width)
            yStart = int(-factor * height)
            yEnd = int(height + factor * height)

        stepX = (xEnd - xStart) / num_steps
        stepY = (yEnd - yStart) / num_steps

        # Lines in X
        for y in np.linspace(yStart, yEnd, num_steps + 1):
            for x in np.linspace(xStart, xEnd, num_steps + 1):
                if only_outer:
                    if y > 0 and y < height:
                        continue

                pA = (x, y, 1)  # (i * stepX, j * stepY)
                pB = (x + stepX, y, 1)  # ((i+1) * stepX, j * stepY)
                if not extended:
                    if x + stepX > width:
                        continue
                pDA = self.camera.distort_points2d(np.array(pA).reshape(3, 1))
                pDB = self.camera.distort_points2d(np.array(pB).reshape(3, 1))

                # cv2.circle(imgDist, pointDistA, 3, bgr, -1)
                if 0 <= pDA[0, 0] < width and 0 <= pDA[1, 0] < height and \
                        0 <= pDB[0, 0] < width and 0 <= pDB[1, 0] < height:
                    color_to_use = color
                    if y == 0 or y == height:
                        color_to_use = (255, 0, 0)
                    cv.line(img, (utils.round(pDA[0, 0]), utils.round(pDA[1, 0])),
                            (utils.round(pDB[0, 0]), utils.round(pDB[1, 0])), color_to_use, 2)

        # Lines in Y
        for y in np.linspace(yStart, yEnd, num_steps + 1):
            for x in np.linspace(xStart, xEnd, num_steps + 1):
                if only_outer:
                    if x > 0 and x < width:
                        continue
                pA = (x, y, 1)  # (i * stepX, j * stepY)
                pB = (x, y + stepY, 1)  # (i * stepX, (j + 1) * stepY)
                if not extended:
                    if y + stepY > height:
                        continue
                pDA = self.camera.distort_points2d(np.array(pA).reshape(3, 1))
                pDB = self.camera.distort_points2d(np.array(pB).reshape(3, 1))

                # cv2.circle(imgDist, pointDistA, 3, bgr, -1)
                if 0 <= pDA[0, 0] < width and 0 <= pDA[1, 0] < height and \
                        0 <= pDB[0, 0] < width and 0 <= pDB[1, 0] < height:
                    color_to_use = color
                    if x == 0 or x == width:
                        color_to_use = (255, 0, 0)
                    cv.line(img, (utils.round(pDA[0, 0]), utils.round(pDA[1, 0])),
                            (utils.round(pDB[0, 0]), utils.round(pDB[1, 0])), color_to_use, 2)

        # r_limit
        if self.camera.r_limit is not None:
            # r_limit is a radius limit in calibrated coordinates
            # It might be possible to draw it by sampling points of a circle r in the undistorted domain
            # and apply distortPoints to them
            num_points = 100
            points2d_und_3xN = np.ones((3, num_points), dtype=np.float)
            count = 0
            for angle in np.linspace(0, 2 * np.pi, num_points, endpoint=False):
                x = np.sin(angle) * self.camera.r_limit
                y = np.cos(angle) * self.camera.r_limit
                points2d_und_3xN[0, count] = x
                points2d_und_3xN[1, count] = y
                count += 1
            points2d_und_3xN = self.camera.K_3x3.dot(points2d_und_3xN)
            points2d_dist_3xN = self.camera.distort_points2d(points2d_und_3xN)
            point2d_prev = None
            for point2d in points2d_dist_3xN.transpose():
                x = utils.round(point2d[0])
                y = utils.round(point2d[1])
                if point2d_prev is not None:
                    cv.line(img, point2d_prev, (x, y), (0, 255, 255), 3)
                point2d_prev = (x, y)
    '''

    def draw_cs(self, _img, cs_name, length=1.0, thickness=1):
        '''
        This function draws a coordinate system, as 3 lines of 1 meter length (Red, Green, Blue) corresponding to
        the X-axis, Y-axis, and Z-axis of the coordinate system
        '''
        if not self.scene.vcd.has_coordinate_system(cs_name):
            warnings.warn("WARNING: Trying to draw coordinate system" + cs_name + " not existing in VCD.")

        x_axis_as_points3d_4x2 = np.array([[0.0, length], [0.0, 0.0], [0.0, 0.0], [1.0, 1.0]])
        y_axis_as_points3d_4x2 = np.array([[0.0, 0.0], [0.0, length], [0.0, 0.0], [1.0, 1.0]])
        z_axis_as_points3d_4x2 = np.array([[0.0, 0.0], [0.0, 0.0], [0.0, length], [1.0, 1.0]])        
        
        x_axis, _ = self.scene.project_points3d_4xN(x_axis_as_points3d_4x2, cs_name, cs_cam=self.camera_coordinate_system)
        y_axis, _ = self.scene.project_points3d_4xN(y_axis_as_points3d_4x2, cs_name, cs_cam=self.camera_coordinate_system)
        z_axis, _ = self.scene.project_points3d_4xN(z_axis_as_points3d_4x2, cs_name, cs_cam=self.camera_coordinate_system)
        
        self.draw_line(_img, (int(x_axis[0,0]), int(x_axis[1,0])), (int(x_axis[0,1]), int(x_axis[1,1])), (0, 0, 255), thickness)
        self.draw_line(_img, (int(y_axis[0,0]), int(y_axis[1,0])), (int(y_axis[0,1]), int(y_axis[1,1])), (0, 255, 0), thickness)
        self.draw_line(_img, (int(z_axis[0,0]), int(z_axis[1,0])), (int(z_axis[0,1]), int(z_axis[1,1])), (255, 0, 0), thickness)

        cv.putText(_img, "X", (int(x_axis[0,1]), int(x_axis[1,1])), cv.FONT_HERSHEY_DUPLEX, 0.8, (0, 0, 255), thickness, cv.LINE_AA)
        cv.putText(_img, "Y", (int(y_axis[0,1]), int(y_axis[1,1])), cv.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 0), thickness, cv.LINE_AA)
        cv.putText(_img, "Z", (int(z_axis[0,1]), int(z_axis[1,1])), cv.FONT_HERSHEY_DUPLEX, 0.8, (255, 0, 0), thickness, cv.LINE_AA)


    def draw(self, _img, _frameNum=None, _params=None):
        if _params is not None:
            assert(isinstance(_params, Image.Params))
            self.params = _params

        # Explore objects at VCD
        objects = None
        if _frameNum is not None:
            vcd_frame = self.scene.vcd.get_frame(_frameNum)
            if 'objects' in vcd_frame:
                objects = vcd_frame['objects']
        else:
            if self.scene.vcd.has_objects():
                objects = self.scene.vcd.get_objects()

        if not objects:
            return

        for object_id, object in objects.items():
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
            if 'object_data' in object:
                object_data = object['object_data'] 
            else:
                # Check if the object has an object_data in root
                object_ = self.scene.vcd.get_object(object_id)
                if 'object_data' in object_:
                    object_data = object_['object_data']

            # Loop over object data            
            for object_data_key in object_data.keys():
                for object_data_item in object_data[object_data_key]:
                    ############################################
                    # bbox
                    ############################################
                    if object_data_key == "bbox":
                        bbox = object_data_item['val']
                        bbox_name = object_data_item['name']
                        if 'coordinate_system' in object_data_item:  # Check if this bbox corresponds to this camera
                            if object_data_item['coordinate_system'] != self.camera_coordinate_system:
                                continue
                            
                        if len(object_data[object_data_key]) == 1:
                            # Only one bbox, let's write the class name
                            text = object_id + " " + object_class
                        else:
                            # If several bounding boxes, let's write the bounding box name
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
                        self.draw_cuboid(_img, cuboid_vals_transformed, "", self.params.colorMap[object_class], self.params.thickness)
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

        # Draw barrel
        # if self.params.draw_barrel:
        #    self.draw_barrel_distortion_grid(_img, (0, 255, 0), False, False)


class TopViewOrtho(Image):
    def __init__(self, scene, camera_coordinate_system=None, stepX=1.0, stepY=1.0):
        super().__init__(scene, camera_coordinate_system=camera_coordinate_system)
            
        # Initialize image      
        self.images = {}

        # Grid config
        self.stepX = stepX  # meters
        self.stepY = stepY
        self.gridTextColor = (0, 0, 0)

    ##################################
    # Public functions
    ##################################
    def draw(self, frameNum=None, params=None, cs_names_to_draw=None):
        # Create image        
        img = self.__reset_topView()

        # Draw BEW
        self.__draw_BEVs(img, frameNum)

        # Draw base grid
        self.__draw_topview_base(img)

        # Draw coordinate systems
        if cs_names_to_draw is not None:
            for cs_name in cs_names_to_draw:
                self.draw_cs(img, cs_name, 2, 2)

        # Draw objects
        super().draw(img, frameNum, params)

        # Draw frame info
        self.__draw_info(img, frameNum)

        return img

    ##################################
    # Internal functions
    ##################################
    def __reset_topView(self):
        img = np.zeros((self.camera.width, self.camera.height, 3), np.uint8) 
        img.fill(255)
        return img 

    def __draw_topview_base(self, _img):
        # Grid x (1/2)
        for x in np.arange(self.camera.xmin, self.camera.xmax + self.stepX, self.stepX):
            x_0 = round(x)
            y_0 = self.camera.ymin
            y_1 = self.camera.ymax
            #points3d_4x2 = np.array([[x_0, y_0, 0.0, 1.0], [x_0, y_1, 0.0, 1.0]])
            points3d_4x2 = np.array([[x_0, x_0], [y_0, y_1], [0.0, 0.0], [1.0, 1.0]])
            points2d_3x2, _ = self.camera.project_points3d(points3d_4xN=points3d_4x2)
            self.draw_line(_img, (int(points2d_3x2[0,0]), int(points2d_3x2[1,0])), (int(points2d_3x2[0,1]), int(points2d_3x2[1,1])), (127, 127, 127))
        # Grid y (1/2)
        for y in np.arange(self.camera.ymin, self.camera.ymax + self.stepY, self.stepY):
            y_0 = round(y)
            x_0 = self.camera.xmin
            x_1 = self.camera.xmax
            #points3d_4x2 = np.array([[x_0, y_0, 0.0, 1.0], [x_1, y_0, 0.0, 1.0]])
            points3d_4x2 = np.array([[x_0, x_1], [y_0, y_0], [0.0, 0.0], [1.0, 1.0]])
            points2d_3x2, _ = self.camera.project_points3d(points3d_4xN=points3d_4x2)
            self.draw_line(_img, (int(points2d_3x2[0,0]), int(points2d_3x2[1,0])), (int(points2d_3x2[0,1]), int(points2d_3x2[1,1])), (127, 127, 127))
        # Grid x (2/2)
        for x in np.arange(self.camera.xmin, self.camera.xmax + self.stepX, self.stepX):
            x_0 = round(x)
            y_0 = self.camera.ymin            
            points3d_4x1 = np.array([[x_0], [y_0], [0.0], [1.0]])
            points2d_3x1, _ = self.camera.project_points3d(points3d_4xN=points3d_4x1)
            cv.putText(_img, str(round(x_0)) + " m", (int(points2d_3x1[0,0]) + 5, 15), cv.FONT_HERSHEY_PLAIN,
                           0.6, self.gridTextColor, 1, cv.LINE_AA)  
        # Grid y (2/2)
        for y in np.arange(self.camera.ymin, self.camera.ymax + self.stepY, self.stepY):
            y_0 = round(y)
            x_0 = self.camera.xmin            
            points3d_4x1 = np.array([[x_0], [y_0], [0.0], [1.0]])
            points2d_3x1, _ = self.camera.project_points3d(points3d_4xN=points3d_4x1)
            cv.putText(_img, str(round(y_0)) + " m", (5, int(points2d_3x1[1,0]) - 5), cv.FONT_HERSHEY_PLAIN,
                           0.6, self.gridTextColor, 1, cv.LINE_AA)                   

        # World origin
        #cv.circle(self.topView, self.point2Pixel((0.0, 0.0)), 4, (255, 255, 255), -1)
        #cv.line(self.topView, self.point2Pixel((0.0, 0.0)), self.point2Pixel((5.0, 0.0)), (0, 0, 255), 2)
        #cv.line(self.topView, self.point2Pixel((0.0, 0.0)), self.point2Pixel((0.0, 5.0)), (0, 255, 0), 2)
        #cv.putText(self.topView, "X", self.point2Pixel((5.0, -0.5)), cv.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 255), 1, cv.LINE_AA)
        #cv.putText(self.topView, "Y", self.point2Pixel((-1.0, 5.0)), cv.FONT_HERSHEY_PLAIN, 1.0, (0, 255, 0), 1, cv.LINE_AA)

    def __draw_BEV(self, cam_name):
        img = self.images[cam_name]['img']

        mapX = self.images[cam_name]['mapX']
        mapY = self.images[cam_name]['mapY']
        bev = cv.remap(img, mapX, mapY, interpolation=cv.INTER_LINEAR,
                        borderMode=cv.BORDER_CONSTANT)

        bev32 = np.float32(bev)
        if 'weights' in self.images[cam_name]:
            cv.multiply(self.images[cam_name]['weights'], bev32, bev32)

        #cv.imshow('bev' + cam_name, bev)
        #cv.waitKey(1)

        #bev832 = np.uint8(bev32)
        #cv.imshow('bev8' + cam_name, bev832)
        #cv.waitKey(1)

        return bev32

    def __draw_BEVs(self, _img, _frameNum=None):
        """
        This function draws BEVs into the topview
        :param _frameNum:
        :return:
        """
        num_cams = len(self.images)
        if num_cams == 0:
            return

        h = self.camera.height
        w = self.camera.width
        # Prepare image with drawing for this call
        acc32 = np.zeros((h, w, 3), dtype=np.float32)  # black background

        for cam_name in self.images:
            if self.scene.get_camera(cam_name, _frameNum) is not None:
                temp32 = self.__draw_BEV(cam_name=cam_name)
                #mask = np.zeros((h, w), dtype=np.uint8)
                #mask[temp32 > 0] = 255
                #mask = (temp32 > 0)
                if num_cams > 1:
                    acc32 = cv.add(temp32, acc32)
        if num_cams > 1:
            acc32 /= self.images['weights_acc']
        else:
            acc32 = temp32
        acc8 = np.uint8(acc32)
        #cv.imshow('acc', acc8)
        #cv.waitKey(1)

        # Copy into topView only new pixels
        nonzero = (acc8>0)
        _img[nonzero] = acc8[nonzero]

    def __draw_info(self, topView, frameNum=None):
        h = topView.shape[0]
        w = topView.shape[1]
        w_margin = 250
        h_margin = 140
        h_step = 20
        font_size = 0.8
        cv.putText(topView, "Img. Size(px): " + str(w) + " x " + str(h),
                   (w - w_margin, h - h_margin),
                   cv.FONT_HERSHEY_PLAIN, font_size, (0, 0, 0), 1, cv.LINE_AA)
        if frameNum is None:
            frameNum = -1
        cv.putText(topView, "Frame: " + str(frameNum),
                   (w - w_margin, h - h_margin + h_step),
                   cv.FONT_HERSHEY_PLAIN, font_size, (0, 0, 0), 1, cv.LINE_AA)
        cv.putText(topView, "CS: " + str(self.camera_coordinate_system),
                   (w - w_margin, h - h_margin + 2*h_step),
                   cv.FONT_HERSHEY_PLAIN, font_size, (0, 0, 0), 1, cv.LINE_AA)

        cv.putText(topView, "RangeX (m): (" + str(self.camera.xmin) + ", " + str(self.camera.xmax) + ")",
                   (w - w_margin, h - h_margin + 3*h_step),
                   cv.FONT_HERSHEY_PLAIN, font_size, (0, 0, 0), 1, cv.LINE_AA)
        cv.putText(topView, "RangeY (m): (" + str(self.camera.ymin) + ", " + str(self.camera.ymax) + ")",
                   (w - w_margin, h - h_margin + 4*h_step),
                   cv.FONT_HERSHEY_PLAIN, font_size, (0, 0, 0), 1, cv.LINE_AA)

        #cv.putText(topView, "OffsetX (px): (" + str(self.params.offsetX) + ", " + str(self.params.offsetX) + ")",
        #           (w - w_margin, h - h_margin + 5*h_step),
        #           cv.FONT_HERSHEY_PLAIN, font_size, (0, 0, 0), 1, cv.LINE_AA)
        #cv.putText(topView, "OffsetY (px): (" + str(self.params.offsetY) + ", " + str(self.params.offsetY) + ")",
        #           (w - w_margin, h - h_margin + 6*h_step),
        #           cv.FONT_HERSHEY_PLAIN, font_size, (0, 0, 0), 1, cv.LINE_AA)

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
        if _frameNum is not None:
            last_frame = self.vcd.get_frame_intervals().get()[-1][1]
            text = "Frame: " + str(_frameNum) + " / " + str(last_frame)
        else:
            text = "Static image"

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

        # Explore objects at VCD
        if _frameNum is not None:
            vcd_frame = self.vcd.get_frame(_frameNum)
            if 'objects' in vcd_frame:
                objects = vcd_frame['objects']
        else:
            if self.vcd.has_objects():
                objects = self.vcd.get_objects()

        if len(objects) > 0:
            num_objects = len(objects.keys())
            text = "Objects: " + str(num_objects)
            cv.putText(img, text,
                       (margin, margin),
                       cv.FONT_HERSHEY_DUPLEX, 0.8, (0, 0, 0), 1, cv.LINE_AA)
            cv.line(img, (0, margin + 10), (cols, margin + 10), (0, 0, 0), 1)
            count +=1
            for object_id, object in objects.items():
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
