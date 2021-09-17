"""
VCD (Video Content Description) library v5.0.0

Project website: http://vcd.vicomtech.org

Copyright (C) 2021, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 5.0.0.
VCD is distributed under MIT License. See LICENSE.

"""

import inspect
import unittest

import cv2 as cv
import numpy as np

import base64
import vcd.core as core

import vcd.types as types
import vcd.poly2d as poly

from test_config import check_openlabel
from test_config import openlabel_version_name

show_images = False

#############################################################################
# See more examples of semantic segmentation in converters/mapillaryConverter
#############################################################################

def draw_basic_image(classes_colors):
    img = np.zeros((640, 480, 3), np.uint8)

    cv.rectangle(img, (50, 50, 150, 150), classes_colors['class1'], -1)
    cv.circle(img, (110, 110), 50, classes_colors['class2'], -1)
    cv.rectangle(img, (60, 60, 10, 10), (0,0,0), -1)
    cv.line(img, (500, 20), (33, 450), classes_colors['class3'], 10)

    return img


class TestBasic(unittest.TestCase):
    def test_polygon2D(self):
        vcd = core.OpenLABEL()

        uid_obj1 = vcd.add_object('someName1', '#Some')

        # Add a polygon with SRF6DCC encoding (list of strings)
        poly1 = types.poly2d('poly1', (5, 5, 10, 5, 11, 6, 11, 8, 9, 10, 5, 10, 3, 8, 3, 6, 4, 5),
                     types.Poly2DType.MODE_POLY2D_SRF6DCC, False)
        self.assertEqual(poly1.data['name'], "poly1")
        self.assertEqual(poly1.data['mode'], "MODE_POLY2D_SRF6DCC")
        self.assertEqual(poly1.data['closed'], False)
        vcd.add_object_data(uid_obj1, poly1)

        # Add a polygon with absolute coordinates (list of numbers)
        poly2 = types.poly2d('poly2', (5, 5, 10, 5, 11, 6, 11, 8, 9, 10, 5, 10, 3, 8, 3, 6, 4, 5),
                     types.Poly2DType.MODE_POLY2D_ABSOLUTE, False)
        vcd.add_object_data(uid_obj1, poly2)

        # Check equal to reference JSON
        self.assertTrue(check_openlabel(vcd, './etc/' + openlabel_version_name + '_' +
                                        inspect.currentframe().f_code.co_name + '.json'))

    def test_create_image_png(self):
        # 1.- Create a VCD instance
        vcd = core.OpenLABEL()

        # 2.- Create image
        colors = [(125, 32, 64), (98, 12, 65), (12, 200, 190)]
        classes = ["class1", "class2", "class3"]
        classes_colors = dict(zip(classes, colors))
        img = draw_basic_image(classes_colors)
        # cv.imshow('src_image', img)
        # cv.waitKey(1)

        # 3.- Encode
        compr_params = [int(cv.IMWRITE_PNG_COMPRESSION), 9]
        result, payload = cv.imencode('.png', img, compr_params)

        self.assertEqual(result, True)

        # 4.- Convert to base64
        payload_b64_bytes = base64.b64encode(payload)  # starts with b' (NOT SERIALIZABLE!)
        payload_b64_str = str(base64.b64encode(payload), 'utf-8')  # starts with s'

        # 5.- Insert into VCD
        vcd_image = types.image('labels', payload_b64_str, 'image/png', 'base64')
        uid = vcd.add_object('', '')
        vcd.add_object_data(uid, vcd_image)

        # 6.- Get and decode
        od = vcd.get_object_data(uid, 'labels')
        mime_type = od['mime_type']
        encoding = od['encoding']
        payload_b64_read = od['val']
        payload_read = base64.b64decode(payload_b64_read)
        self.assertEqual(mime_type, 'image/png')
        self.assertEqual(encoding, 'base64')
        img_dec = cv.imdecode(np.frombuffer(payload_read, dtype=np.uint8), 1)

        # Check equals
        diff_val = np.sum(cv.absdiff(img, img_dec))

        self.assertEqual(diff_val, 0)

        # Check equal to reference JSON
        self.assertTrue(check_openlabel(vcd, './etc/' + openlabel_version_name + '_' +
                                        inspect.currentframe().f_code.co_name + '.json'))

        #cv.imshow('decoded_image', img_dec)
        #cv.waitKey(0)

    def test_contours(self):
        # 1.- Create a VCD instance
        vcd = core.OpenLABEL()

        # 1.- Create (color) image
        colors = [(125, 32, 64), (98, 12, 65), (12, 200, 190)]
        classes = ["class1", "class2", "class3"]
        classes_colors = dict(zip(classes, colors))

        img = draw_basic_image(classes_colors)
        #cv.imshow('src_image', img)
        #cv.waitKey(1)

        # 2.- Split into channels
        for class_name, color in classes_colors.items():
            seg = cv.inRange(img, color, color)

            # Get contours for this channel
            # Contours is a list of ndarray with shape (num_points, 1, 2)
            # Hierarchy is a ndarray with shape (1, num_contours, 4)
            contours, hierarchy = cv.findContours(seg, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
            #print(hierarchy)

            uid = vcd.add_object('', class_name)
            for idx, contour in enumerate(contours):
                flatten_contour = contour.flatten()
                points = flatten_contour.tolist()
                hierarchy_list = hierarchy[0][idx].tolist()
                vcd.add_object_data(uid,
                                    types.poly2d('contour' + str(idx),  # WARNING: In VCD 4.3.0, names MUST be unique
                                                 points,
                                                 types.Poly2DType.MODE_POLY2D_SRF6DCC,
                                                 closed=True,
                                                 hierarchy=hierarchy_list)
                                    )

        # Check equal to reference JSON
        self.assertTrue(check_openlabel(vcd, './etc/' + openlabel_version_name + '_' +
                                        inspect.currentframe().f_code.co_name + '.json'))

        # 3.- Reconstruct the image from the VCD poly2d and hierarchies (using OpenCV)
        contours_dict = {}  # A dictionary of contours. Each key is one class type, each value, a contours array
        hierarchy_dict = {}

        for object_key, object_val in vcd.get_objects().items():
            # Assuming this is static (no frame info)
            contours_dict.setdefault(object_val['type'], [])
            hierarchy_dict.setdefault(object_val['type'], [])
            if 'object_data' in object_val:
                if 'poly2d' in object_val['object_data']:
                    for idx_pol, poly2d in enumerate(object_val['object_data']['poly2d']):
                        val = poly2d['val']  # (x, y, rest, chain)
                        mode = poly2d['mode']
                        #closed = poly2d['closed']  # Not used in OpenCV
                        hierarchy = poly2d['hierarchy']

                        if mode == types.Poly2DType.MODE_POLY2D_SRF6DCC.name:
                            vec = poly.getVecFromEncodedSRF6(int(val[0]), int(val[1]), int(val[2]), val[3])
                            #print(vec)
                        else:
                            vec = val

                        # Then, create contours, format as OpenCV expects
                        num_coords = len(vec)
                        num_points = int(num_coords / 2)

                        contour = np.asarray(vec).reshape((num_points, 1, 2))
                        contours_dict[object_val['type']].append(contour)
                        hierarchy_dict[object_val['type']].append(hierarchy)

        img_out = np.zeros((640, 480, 3), np.uint8)
        for class_name, contours in contours_dict.items():
            hierarchy_list = hierarchy_dict[class_name]
            num_contours = len(contours)
            hierarchy_array = np.asarray(hierarchy_list).reshape(num_contours, 1, 4)

            color = classes_colors[class_name]

            cv.drawContours(img_out, contours, -1, color, hierarchy=hierarchy_array, thickness=-1)
            #cv.imshow('out_image', img_out)
            #cv.waitKey(0)

        # 4.- Check equals
        diff_val = np.sum(cv.absdiff(img, img_out))
        self.assertEqual(diff_val, 0)


if __name__ == '__main__':  # This changes the command-line entry point to call unittest.main()
    print("Running test_image.py...")
    unittest.main()

