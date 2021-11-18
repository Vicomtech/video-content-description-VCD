"""
VCD (Video Content Description) library v5.0.1

Project website: http://vcd.vicomtech.org

Copyright (C) 2021, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 5.0.1.
VCD is distributed under MIT License. See LICENSE.

"""

import cv2 as cv
import numpy as np

import vcd.core as core
import vcd.types as types

# Create basic rotated bounding box
vcd = core.VCD()
uid1 = vcd.add_object(name="car1", semantic_type="car")
vcd.add_object_data(uid=uid1, object_data=types.rbbox(name="shape1", val=[250, 100, 40, 100, 0.0]))
vcd.add_object_data(uid=uid1, object_data=types.rbbox(name="shape2", val=[250, 100, 40, 100, 0.5]))
vcd.add_object_data(uid=uid1, object_data=types.rbbox(name="shape3", val=[250, 100, 40, 100, 1.56]))

# Draw it
img = np.zeros((500, 500, 3), np.uint8)
rbbox1 = vcd.get_element_data(core.ElementType.object, uid1, 'shape1')['val']
box1 = np.int0(cv.boxPoints(((rbbox1[0], rbbox1[1]), (rbbox1[2], rbbox1[3]), rbbox1[4] * 180.0/np.pi)))
rbbox2 = vcd.get_element_data(core.ElementType.object, uid1, 'shape2')['val']
box2 = np.int0(cv.boxPoints(((rbbox2[0], rbbox2[1]), (rbbox2[2], rbbox2[3]), rbbox2[4] * 180.0/np.pi)))
rbbox3 = vcd.get_element_data(core.ElementType.object, uid1, 'shape3')['val']
box3 = np.int0(cv.boxPoints(((rbbox3[0], rbbox3[1]), (rbbox3[2], rbbox3[3]), rbbox3[4] * 180.0/np.pi)))

cv.drawContours(img, [box1], 0, (0,255,0), 3) 
cv.drawContours(img, [box2], 0, (255,0,0), 3)
cv.drawContours(img, [box3], 0, (0,0,255), 3)

cv.imshow('rbbox', img)
cv.waitKey(0)

