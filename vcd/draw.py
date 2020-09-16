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
import vcd.types as types
import vcd.utils as utils
import numpy as np
import cv2 as cv
import warnings


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

        def __init__(self, _stepX=None, _stepY=None, _background_color=None,_imgSize=None, _rangeX=None, _rangeY=None, _colorMap=None, _ignore_classes=None):
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

    def __init__(self, vcd, coordinate_system):
        assert(isinstance(vcd, core.VCD))
        self.vcd = vcd
        # This value specifies which coordinate system is fixed in the
        # center of the TopView, e.g. "odom" or "vehicle-iso8855"
        assert(vcd.has_coordinate_system(coordinate_system))
        self.coordinate_system = coordinate_system
        self.params = TopView.Params()

    def draw(self, frameNum, uid=None, _drawTrajectory=True, _params=None):
        self.topView = None
        if _params is not None:
            assert(isinstance(_params, TopView.Params))
            self.params = _params

        # Base
        self.topView = np.zeros((_params.imgSize[1], _params.imgSize[0], 3), np.uint8)  # Needs to be here
        self.drawTopViewBase(self.topView, self.params)

        # Draw objects
        self.drawObjectsAtFrame(self.topView, self.vcd, uid, frameNum, _drawTrajectory, _params)

        # Draw frame info
        cv.putText(self.topView, "Img. Size(px): " + str(self.params.imgSize[0]) + " x " + str(self.params.imgSize[1]),
                   (_params.imgSize[0] - 250, _params.imgSize[1] - 140),
                   cv.FONT_HERSHEY_PLAIN, 1.0, (0,0,0), 1, cv.LINE_AA)
        cv.putText(self.topView, "Frame: " + str(frameNum),
                   (_params.imgSize[0] - 250, _params.imgSize[1] - 120),
                   cv.FONT_HERSHEY_PLAIN, 1.0, (0,0,0), 1, cv.LINE_AA)
        cv.putText(self.topView, "CS: " + str(self.coordinate_system),
                   (_params.imgSize[0] - 250, _params.imgSize[1] - 100),
                   cv.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 0), 1, cv.LINE_AA)

        cv.putText(self.topView, "RangeX (m): (" + str(self.params.rangeX[0]) + ", " + str(self.params.rangeX[1]) + ")",
                   (_params.imgSize[0] - 250, _params.imgSize[1] - 80),
                   cv.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 0), 1, cv.LINE_AA)
        cv.putText(self.topView, "RangeY (m): (" + str(self.params.rangeX[0]) + ", " + str(self.params.rangeX[1]) + ")",
                                                       (_params.imgSize[0] - 250, _params.imgSize[1] - 60),
                                                       cv.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 0), 1, cv.LINE_AA)

        cv.putText(self.topView, "OffsetX(m): (" + str(self.params.offsetX) + ", " + str(self.params.offsetX) + ")",
                                                       (_params.imgSize[0] - 250, _params.imgSize[1] - 40),
                                                       cv.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 0), 1, cv.LINE_AA)
        cv.putText(self.topView, "OffsetY (m): (" + str(self.params.offsetY) + ", " + str(self.params.offsetY) + ")",
                                                       (_params.imgSize[0] - 250, _params.imgSize[1] - 20),
                                                       cv.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 0), 1, cv.LINE_AA)

        return self.topView


    def drawTopViewBase(self, _topView, _params):

        _topView.fill(_params.backgroundColor)

        # Grid x (1/2)
        for x in np.arange(_params.rangeX[0], _params.rangeX[1] + _params.stepX, _params.stepX):
            x_round = round(x)
            ptImg1 = self.point2Pixel((x_round, _params.rangeY[0]))
            ptImg2 = self.point2Pixel((x_round, _params.rangeY[1]))
            cv.line(_topView, ptImg1, ptImg2, (127, 127, 127), _params.gridLinesThickness)

        # Grid y (1/2)
        for y in np.arange(_params.rangeY[0], _params.rangeY[1] + _params.stepY, _params.stepY):
            y_round = round(y)
            ptImg1 = self.point2Pixel((_params.rangeX[0], y_round))
            ptImg2 = self.point2Pixel((_params.rangeX[1], y_round))
            cv.line(_topView, ptImg1, ptImg2, (127, 127, 127), _params.gridLinesThickness)

        # Grid x (2/2)
        for x in np.arange(_params.rangeX[0], _params.rangeX[1] + _params.stepX, _params.stepX):
            x_round = round(x)
            ptImg1 = self.point2Pixel((x_round, _params.rangeY[0]))
            cv.putText(_topView, str(round(x)) + " m", (ptImg1[0] + 5, 15), cv.FONT_HERSHEY_PLAIN,
                       0.6, _params.gridTextColor, 1, cv.LINE_AA)
        # Grid y (2/2)
        for y in np.arange(_params.rangeY[0], _params.rangeY[1] + _params.stepY, _params.stepY):
            y_round = round(y)
            ptImg1 = self.point2Pixel((_params.rangeX[0], y_round))
            cv.putText(_topView, str(round(y)) + " m", (5, ptImg1[1] - 5),
                       cv.FONT_HERSHEY_PLAIN,
                       0.6, _params.gridTextColor, 1, cv.LINE_AA)

        # World origin
        cv.circle(_topView, self.point2Pixel((0.0, 0.0)), 4, (255, 255, 255), -1)
        cv.line(_topView, self.point2Pixel((0.0, 0.0)), self.point2Pixel((5.0, 0.0)), (0, 0, 255), 2)
        cv.line(_topView, self.point2Pixel((0.0, 0.0)), self.point2Pixel((0.0, 5.0)), (0, 255, 0), 2)

        cv.putText(_topView, "X", self.point2Pixel((5.0, -0.5)), cv.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 255), 1, cv.LINE_AA)
        cv.putText(_topView, "Y", self.point2Pixel((-1.0, 5.0)), cv.FONT_HERSHEY_PLAIN, 1.0, (0, 255, 0), 1, cv.LINE_AA)

    def drawCuboidTopView(self, _img, _cuboid, _class, _color, _thick, _ID=""):
        assert(isinstance(_cuboid, list))
        assert(len(_cuboid) == 9)  # (X, Y, Z, RX, RY, RZ, SX, SY, SZ)
        # TODO cuboids with quaternions

        points_4x8 = utils.generate_cuboid_points_ref_4x8(_cuboid)
        points_4x8[2, :] = 0

        pairs = ([0, 1], [1, 2], [2, 3], [3, 0], [0, 4], [1, 5], [2, 6], [3, 7], [4, 5], [5, 6], [6, 7], [7, 4])
        for pair in pairs:
            p_a = (points_4x8[0, pair[0]], points_4x8[1, pair[0]])
            p_b = (points_4x8[0, pair[1]], points_4x8[1, pair[1]])
            cv.line(_img, self.point2Pixel(p_a), self.point2Pixel(p_b), _color, _thick )

    def __draw_transform_cuboid(self, vcd_other_frame, _vcd, f, uid, cs_data, prev_center, _img, object_class, _params):
        if 'objects' in vcd_other_frame:
            for object_id_this, object in vcd_other_frame['objects'].items():
                if object_id_this is not uid:
                    continue

                if "object_data" in object:
                    for object_data_key in object['object_data'].keys():
                        for object_data_item in object['object_data'][object_data_key]:
                            if object_data_key == "cuboid":
                                cuboid_vals = object_data_item['val']

                                cuboid_vals_transformed = cuboid_vals
                                if cs_data != self.coordinate_system:
                                    src_cs = cs_data
                                    dst_cs = self.coordinate_system
                                    transform_src_dst = utils.get_transform(_vcd, src_cs,
                                                                            dst_cs, f)

                                    if transform_src_dst is not None:
                                        cuboid_vals_transformed = utils.transform_cuboid(
                                            cuboid_vals, transform_src_dst)

                                name = object_data_item['name']

                                center = (cuboid_vals_transformed[0], cuboid_vals_transformed[1])
                                # if object_id == "1":
                                #    print(transform_src_dst[3])
                                #    print(cuboid_vals_transformed)
                                #    print("Traj(" + str(f) + ")", center)
                                center_pix = self.point2Pixel(center)

                                # this is a dict to allow multiple trajectories
                                # (e.g. several cuboids per object)
                                if prev_center.get(name) is not None:
                                    cv.line(_img, prev_center[name], center_pix, (0, 0, 0),
                                            1, cv.LINE_AA)

                                cv.circle(_img, center_pix, 2,
                                          _params.colorMap[object_class], -1)

                                prev_center[name] = center_pix

    def __draw_object_cuboids(self, object_, object_class, _img, _vcd, uid, _frameNum, _drawTrajectory, _params):
        # Get current value at this frame
        hasCuboid = False
        if "object_data" in object_:
            for object_data_key in object_['object_data'].keys():
                for object_data_item in object_['object_data'][object_data_key]:
                    if object_data_key == "cuboid":
                        hasCuboid = True
                        cuboid_vals = object_data_item['val']
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
                            src_cs = cs_data
                            dst_cs = self.coordinate_system
                            transform_src_dst = utils.get_transform(_vcd, src_cs, dst_cs, _frameNum)

                            if transform_src_dst is not None:
                                cuboid_vals_transformed = utils.transform_cuboid(cuboid_vals, transform_src_dst)

                        # Draw
                        self.drawCuboidTopView(_img,
                                               cuboid_vals_transformed,
                                               object_class,
                                               self.params.colorMap[object_class],
                                               2,
                                               uid)
                        center = (cuboid_vals_transformed[0], cuboid_vals_transformed[1])
                        # if object_id == "1":
                        #    print("Obj(" + str(_frameNum) + ")", center)

        if _drawTrajectory and hasCuboid:
            fis_object = _vcd.get_element_frame_intervals(core.ElementType.object, uid)
            if fis_object.empty():
                # So, this object has no frame information, it is static, so let's read its static value
                # and project it using the transforms at each frame
                fis = _vcd.get_frame_intervals().get_dict()
                for fi in fis:
                    prev_center = dict()
                    for f in range(fi['frame_start'], _frameNum + 1):
                        vcd_other_frame = _vcd.data['vcd']
                        self.__draw_transform_cuboid(vcd_other_frame, _vcd, f, uid,
                                                     cs_data, prev_center,
                                                     _img, object_class, _params)

            else:
                # So, this object has frame information, let's read each cuboid and transform it
                fis = fis_object.get_dict()

                for fi in fis:
                    prev_center = dict()
                    for f in range(fi['frame_start'], _frameNum + 1):
                        vcd_other_frame = _vcd.get_frame(f)
                        self.__draw_transform_cuboid(vcd_other_frame, _vcd, f, uid,
                                                     cs_data, prev_center,
                                                     _img, object_class, _params)

    def drawObjectsAtFrame(self, _img, _vcd, uid, _frameNum, _drawTrajectory, _params):
        assert(isinstance(_vcd, core.VCD))

        # Explore objects at VCD
        vcd_frame = _vcd.get_frame(_frameNum)
        if 'objects' in vcd_frame:
            for object_id, object_ in vcd_frame['objects'].items():
                if uid is not None:
                    if object_id != uid:
                        continue

                # Get object static info
                object_class = _vcd.get_object(object_id)['type']

                # Ignore classes
                if object_class in _params.ignore_classes:
                    continue

                # Colors
                if _params.colorMap.get(object_class) is None:
                    # Let's create a new entry for this class
                    _params.colorMap[object_class] = (randint(0, 255), randint(0, 255), randint(0, 255))

                if len(object_) == 0:
                    # So this is a pointer to a static object
                    static_object = _vcd.data['vcd']['objects'][object_id]
                    self.__draw_object_cuboids(static_object, object_class,
                                               _img, _vcd, object_id, _frameNum, _drawTrajectory, _params)
                else:
                    # Let's use the dynamic info of this object
                    self.__draw_object_cuboids(object_, object_class,
                                               _img, _vcd, object_id, _frameNum, _drawTrajectory, _params)

    def size2Pixel(self, _size):
        return (int(round(_size[0] * abs(self.params.scaleX))),
                int(round(_size[1] * abs(self.params.scaleY))))

    def point2Pixel(self, _point):
        pixel = (int(round(_point[0]*self.params.scaleX + self.params.offsetX)),
                 int(round(_point[1]*self.params.scaleY + self.params.offsetY)))
        return pixel


class Image:
    class Params:
        def __init__(self, _draw_trajectory=False, _colorMap=None, _ignore_classes=None):
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

    def __init__(self, vcd):
        assert (isinstance(vcd, core.VCD))
        self.vcd = vcd
        self.params = Image.Params()

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
        object_class = self.vcd.get_object(_object_id)['type']
        fis = (self.vcd.get_element_frame_intervals(core.ElementType.object, _object_id)).get_dict()

        for fi in fis:
            prev_center = dict()
            for f in range(fi['frame_start'], _frameNum + 1):
                vcd_other_frame = self.vcd.get_frame(f)
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
        vcd_frame = self.vcd.get_frame(_frameNum)
        if 'objects' in vcd_frame:
            for object_id, object in vcd_frame['objects'].items():
                # Get object static info
                name = self.vcd.get_object(object_id)['name']
                object_class = self.vcd.get_object(object_id)['type']
                if object_class in _params.ignore_classes:
                    continue

                # Colors
                if _params.colorMap.get(object_class) is None:
                    # Let's create a new entry for this class
                    _params.colorMap[object_class] = (randint(0, 255), randint(0, 255), randint(0, 255))

                # Get current value at this frame
                if "object_data" in object:
                    for object_data_key in object['object_data'].keys():
                        for object_data_item in object['object_data'][object_data_key]:
                            if object_data_key == "bbox":
                                bbox = object_data_item['val']
                                bbox_name = object_data_item['name']
                                #text = "(" + object_id + "," + name +")-(" + object_class + ")-(" + bbox_name +")"
                                text = object_id + " " + bbox_name
                                self.draw_bbox(_img, bbox, text, _params.colorMap[object_class], True)
                                if _params.draw_trajectory:
                                    self.draw_trajectory(_img,object_id, _frameNum, _params)


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
                   cv.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1, cv.LINE_AA)
        rows, cols, channels = _img.shape
        cv.line(_img, (0, margin + 10), (cols, margin + 10), (255, 255, 255), 1)

    def draw(self, _frameNum, cols=600, rows=1200, _params=None):
        img = np.zeros((rows, cols, 3), np.uint8)
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
                       cv.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1, cv.LINE_AA)
            cv.line(img, (0, margin + 10), (cols, margin + 10), (255, 255, 255), 1)
            count +=1
            for object_id, object in vcd_frame['objects'].items():
                # Get object static info
                name = self.vcd.get_object(object_id)['name']
                object_class = self.vcd.get_object(object_id)['type']
                fis = self.vcd.get_element_frame_intervals(core.ElementType.object, object_id)

                # Colors
                if _params.colorMap.get(object_class) is None:
                    # Let's create a new entry for this class
                    _params.colorMap[object_class] = (randint(0, 255), randint(0, 255), randint(0, 255))

                #text = object_id + " " + object_class + " \"" + name + "\" " + fis.to_str()
                text = object_id + " " + object_class + " " + fis.to_str()
                cv.putText(img, text,
                           (margin, margin + count * jump),
                           cv.FONT_HERSHEY_DUPLEX, 0.6, _params.colorMap[object_class], 1, cv.LINE_AA)
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
