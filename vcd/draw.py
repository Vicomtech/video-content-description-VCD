"""
VCD (Video Content Description) library v4.1.0

Project website: http://vcd.vicomtech.org

Copyright (C) 2020, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.1.0.
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
    class Params:
        '''
        Assuming cuboids are drawn top view, so Z coordinate is ignored
        RZ is the rotation in Z-axis, it assumes/enforces SY>SX, thus keeping
        RZ between pi/2 and -pi/2

        Z, RX, RY, and SZ are ignored

        For Vehicle cases, we adopt ISO8855: origin at rear axle at ground, x-to-front, y-to-left
        '''

        def __init__(self, _imgSize=None, _rangeX=None, _rangeY=None, _colorMap=None):
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
            self.stepY = 1.0

            self.gridLinesThickness = 1
            self.backgroundColor = 255
            self.gridTextColor = (0, 0, 0)

            if _colorMap is None:
                self.colorMap = dict()
            else:
                assert (isinstance(_colorMap, dict))
                self.colorMap = _colorMap

    def __init__(self, vcd):
        assert(isinstance(vcd, core.VCD))
        self.vcd = vcd
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
        cv.putText(self.topView, "Frame: " + str(frameNum),
                   (_params.imgSize[0] - 100, _params.imgSize[1] - 20),
                   cv.FONT_HERSHEY_PLAIN, 1.0, (0,0,0), 1, cv.LINE_AA)

        return self.topView

    def drawEgoCar(self, _topView, size, wheelbase):
        cuboid = [wheelbase/2, 0, 0, 0, 0, 0, size[0], size[1], size[2]]
        self.drawCuboidTopView(_topView, cuboid, "", (0, 0, 0), 3)
        self.drawCuboidTopView(_topView, cuboid, "", (127, 127, 127), 2)

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

        locX = _cuboid[0]
        locY = _cuboid[1]
        rotZ_rad = _cuboid[5]
        #if rotZ_rad > np.pi/2 or rotZ_rad < -np.pi/2:
            # Can't paint this cuboid (this condition enforces sy>sx)
        #    return
        rotZ_deg = rotZ_rad * 180 / np.pi
        sizeX = _cuboid[6]
        sizeY = _cuboid[7]

        center = (locX, locY)
        size = (sizeX, sizeY)

        center_pix = self.point2Pixel(center)
        size_pix = self.size2Pixel(size)

        rrect = (center_pix, size_pix, rotZ_deg)
        box = cv.boxPoints(rrect)
        box = np.int0(box)

        cv.drawContours(_img, [box], 0, _color, _thick)

    def drawObjectsAtFrame(self, _img, _vcd, uid, _frameNum, _drawTrajectory, _params):
        assert(isinstance(_vcd, core.VCD))

        # Explore objects at VCD
        vcd_frame = _vcd.get_frame(_frameNum)
        if 'objects' in vcd_frame:
            for object_id, object in vcd_frame['objects'].items():
                if uid is not None:
                    if object_id != uid:
                        continue
                # Get object static info
                name = _vcd.get_object(object_id)['name']
                object_class = _vcd.get_object(object_id)['type']

                # Colors
                if self.params.colorMap.get(object_class) is None:
                    # Let's create a new entry for this class
                    self.params.colorMap[object_class] = (randint(0, 255), randint(0, 255), randint(0, 255))

                # Get current value at this frame
                hasCuboid = False
                if "object_data" in object:
                    for object_data_key in object['object_data'].keys():
                        for object_data_item in object['object_data'][object_data_key]:
                            if object_data_key == "cuboid":
                                hasCuboid = True
                                cuboid = object_data_item['val']
                                self.drawCuboidTopView(_img,
                                                       cuboid,
                                                       object_class,
                                                       self.params.colorMap[object_class],
                                                       2,
                                                       object_id)

                if _drawTrajectory and hasCuboid:
                    fis = _vcd.get_frame_intervals_of_element(core.ElementType.object, object_id)
                    for fi in fis:
                        prev_center = dict()
                        for f in range(fi['frame_start'], _frameNum + 1):
                            vcd_other_frame = _vcd.get_frame(f)
                            if 'objects' in vcd_other_frame:
                                for object_id_this, object in vcd_other_frame['objects'].items():
                                    if object_id_this is not object_id:
                                        continue

                                    # Get value at this frame
                                    if "object_data" in object:
                                        for object_data_key in object['object_data'].keys():
                                            for object_data_item in object['object_data'][object_data_key]:
                                                if object_data_key == "cuboid":
                                                    cuboid = object_data_item['val']
                                                    name = object_data_item['name']

                                                    center = (cuboid[0], cuboid[1])
                                                    center_pix = self.point2Pixel(center)

                                                    # this is a dict to allow multiple trajectories
                                                    # (e.g. several cuboids per object)
                                                    if prev_center.get(name) is not None:
                                                        cv.line(_img, prev_center[name], center_pix, (0,0,0),
                                                                1, cv.LINE_AA)

                                                    cv.circle(_img, center_pix, 2,
                                                                  self.params.colorMap[object_class], -1)

                                                    prev_center[name] = center_pix

    def size2Pixel(self, _size):
        return (int(round(_size[0] * abs(self.params.scaleX))),
                int(round(_size[1] * abs(self.params.scaleY))))

    def point2Pixel(self, _point):
        pixel = (int(round(_point[0]*self.params.scaleX + self.params.offsetX)),
                 int(round(_point[1]*self.params.scaleY + self.params.offsetY)))
        return pixel

class Image:
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
        self.params = Image.Params()

    def draw_bbox(self, _img, _bbox, _object_class, _color):
        pt1 = (int(round(_bbox[0])), int(round(_bbox[1])))
        pt2 = (int(round(_bbox[0] + _bbox[2])), int(round(_bbox[1] + _bbox[3])))

        pta = (pt1[0], pt1[1] - 15)
        ptb = (pt2[0], pt1[1])

        cv.rectangle(_img, pta, ptb, _color, 2)
        cv.rectangle(_img, pta, ptb, _color, -1)
        cv.putText(_img, _object_class, (pta[0], pta[1] + 10), cv.FONT_HERSHEY_PLAIN, 0.6, (0,0,0), 1, cv.LINE_AA)
        cv.rectangle(_img, pt1, pt2, _color, 2)

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

                # Colors
                if self.params.colorMap.get(object_class) is None:
                    # Let's create a new entry for this class
                    self.params.colorMap[object_class] = (randint(0, 255), randint(0, 255), randint(0, 255))

                # Get current value at this frame
                if "object_data" in object:
                    for object_data_key in object['object_data'].keys():
                        for object_data_item in object['object_data'][object_data_key]:
                            if object_data_key == "bbox":
                                bbox = object_data_item['val']
                                self.draw_bbox(_img, bbox, object_class, self.params.colorMap[object_class])


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
