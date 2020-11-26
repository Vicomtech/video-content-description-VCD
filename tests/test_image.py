"""
VCD (Video Content Description) library v4.3.0

Project website: http://vcd.vicomtech.org

Copyright (C) 2020, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.3.0.
VCD is distributed under MIT License. See LICENSE.

"""


import unittest
import os
import cv2 as cv
import numpy as np
from PIL import Image
import json
import base64
import sys
sys.path.insert(0, "..")
import vcd.core as core
import vcd.types as types
import vcd.poly2d as poly
import vcd.utils as utils

def draw_basic_image(classes_colors):
    img = np.zeros((640, 480, 3), np.uint8)

    cv.rectangle(img, (50, 50, 150, 150), classes_colors['class1'], -1)
    cv.circle(img, (110, 110), 50, classes_colors['class2'], -1)
    cv.rectangle(img, (60, 60, 10, 10), (0,0,0), -1)
    cv.line(img, (500, 20), (33, 450), classes_colors['class3'], 10)

    return img

class TestBasic(unittest.TestCase):

    def test_polygon2D(self):
        vcd = core.VCD()

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

        if not os.path.isfile('./etc/vcd430_test_polygon2D.json'):
            vcd.save('./etc/vcd430_test_polygon2D.json', True)

        vcd_read = core.VCD('./etc/vcd430_test_polygon2D.json', validation=True)
        vcd_read_stringified = vcd_read.stringify()
        vcd_stringified = vcd.stringify()
        # print(vcd_stringified)
        self.assertEqual(vcd_read_stringified, vcd_stringified)

    def test_create_image_png(self):
        # 1.- Create a VCD instance
        vcd = core.VCD()

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

        if not os.path.isfile('./etc/vcd430_test_image.json'):
            vcd.save('./etc/vcd430_test_image.json', True)

        #cv.imshow('decoded_image', img_dec)
        #cv.waitKey(0)

    def test_contours(self):
        # 1.- Create a VCD instance
        vcd = core.VCD()

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

        if not os.path.isfile('./etc/vcd430_test_contours.json'):
            vcd.save('./etc/vcd430_test_contours.json', True)

        # 3.- Reconstruct the image from the VCD poly2d and hierarchies (using OpenCV)
        contours_dict = {}  # A dictionary of contours. Each key is one class type, each value, a contours array
        hierarchy_dict = {}

        for object_key, object_val in vcd.data['vcd']['objects'].items():
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

    def mapillary_image_analysis(self, img_name, labels):
        #print(img_name)
        vcd = core.VCD()
        img_label = cv.imread('../converters/mapillaryConverter/labels/' + img_name)
        img_instance = cv.imread('../converters/mapillaryConverter/instances/' + img_name, cv.IMREAD_GRAYSCALE)

        imgPIL_instance = Image.open('../converters/mapillaryConverter/instances/' + img_name)
        imgPIL_instance = np.array(imgPIL_instance, dtype=np.uint16)

        label_path = '../converters/mapillaryConverter/labels/' + img_name
        instance_path = '../converters/mapillaryConverter/instances/' + img_name

        instance_image = Image.open(instance_path)

        # convert labeled data to numpy arrays for better handling
        instance_array = np.array(instance_image, dtype=np.uint16)

        classes_colors = {}
        for x in labels:
            classes_colors[x['name']] = x['color']

        # prepare arrays for instance and class retrieval
        instance_ids_array = np.array(imgPIL_instance % 256, dtype=np.uint8)
        instance_label_array = np.array(imgPIL_instance / 256, dtype=np.uint8)
        img_instance_out = np.zeros((img_instance.shape[0], img_instance.shape[1], 3), np.uint8)
        img_instance_out[np.where((img_instance_out == [0, 0, 0]).all(axis=2))] = [0, 255, 0]
        img_class_out = np.zeros((img_instance.shape[0], img_instance.shape[1], 3), np.uint8)

        instance_bgr = cv.cvtColor(instance_ids_array, cv.COLOR_GRAY2BGR)
        final = np.zeros(img_label.shape, np.uint8)
        cont = 0

        #cv.namedWindow('image', cv.WINDOW_NORMAL)
        #cv.resizeWindow('image', img_instance.shape[0], img_instance.shape[1])

        # Get contours of each instance and retrieve it's class to write in vcd as instance -> True
        for i in range(1, np.max(instance_ids_array) + 1):
            seg = cv.inRange(instance_bgr, (i, i, i), (i, i, i))
            if cv.countNonZero(seg) != 0:
                contours, hierarchy = cv.findContours(seg, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
                cnt_id = 0
                # Reverse point_color from bgr to rgb to get class
                # Write class in vcd
                for c in contours:
                    extLeft = tuple(c[c[:, :, 0].argmin()][0])
                    color = img_label[extLeft[1]][extLeft[0]]
                    color = tuple([int(x) for x in color])
                    color = list(color)
                    instance_class = utils.get_key(classes_colors, color[::-1])

                    if cnt_id == 0:
                        uid = vcd.add_object("object " + str(cont), instance_class)
                        vcd.add_object_data(uid, types.boolean('isInstance', True))

                    c = c.flatten()
                    hierarchy_list = hierarchy[0][cnt_id].tolist()
                    # Write poly, hierarchy and instance
                    polygon = types.poly2d('contour' + str(cnt_id), c.tolist(), types.Poly2DType.MODE_POLY2D_SRF6DCC, closed=True,
                                           hierarchy=hierarchy_list)
                    vcd.add_object_data(uid, polygon)
                    cnt_id += 1
                    cont += 1

        # Get contours of each CLASS and write it in VCD as instance -> False
        for class_val in labels:
            # check all posible classes of mapillary
            seg = cv.inRange(img_label, tuple(class_val['color'][::-1]), tuple(class_val['color'][::-1]))
            if cv.countNonZero(seg) != 0:
                contours, hierarchy = cv.findContours(seg, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
                cv.drawContours(final, contours, -1, tuple(class_val['color'][::-1]), thickness=-1)

                cnt_id = 0
                instance_class = utils.get_key(classes_colors, class_val['color'])
                uid = vcd.add_object("object " + str(cont), instance_class)
                vcd.add_object_data(uid, types.boolean('isInstance', False))
                for c in contours:
                    c = c.flatten()
                    hierarchy_list = hierarchy[0][cnt_id].tolist()
                    polygon = types.poly2d('contour' + str(cnt_id), c.tolist(), types.Poly2DType.MODE_POLY2D_SRF6DCC, closed=True,
                                           hierarchy=hierarchy_list)
                    vcd.add_object_data(uid, polygon)
                    cont += 1
                    cnt_id += 1

        #vcd.save('../converters/mapillaryConverter/vcd_files/' + img_name[0:len(img_name) - 4] + '.json', True)
        vcd.save('../converters/mapillaryConverter/vcd_files/' + img_name[0:len(img_name) - 4] + '.json', False, False)

        # 3.- Reconstruct the image from the VCD poly2d and hierarchies (using OpenCV)
        contours_dict_instance = {}  # A dictionary of contours. Each key is one class type, each value, a contours array
        hierarchy_dict_instance = {}

        contours_dict_class = {}  # A dictionary of contours. Each key is one class type, each value, a contours array
        hierarchy_dict_class = {}

        for object_key, object_val in vcd.data['vcd']['objects'].items():
            # Assuming this is static (no frame info)
            contours_dict_instance.setdefault(object_val['type'], [])
            contours_dict_class.setdefault(object_val['type'], [])
            hierarchy_dict_instance.setdefault(object_val['type'], [])
            hierarchy_dict_class.setdefault(object_val['type'], [])
            if 'object_data' in object_val:
                if 'boolean' in object_val['object_data']:
                    if 'poly2d' in object_val['object_data']:
                        for idx_pol, poly2d in enumerate(object_val['object_data']['poly2d']):
                            val = poly2d['val']  # (x, y, rest, chain)
                            mode = poly2d['mode']
                            # closed = poly2d['closed']  # Not used in OpenCV
                            hierarchy = poly2d['hierarchy']
                            instance = object_val['object_data']['boolean'][0]['val']
                            if mode == types.Poly2DType.MODE_POLY2D_SRF6DCC.name:
                                vec = poly.getVecFromEncodedSRF6(int(val[0]), int(val[1]), int(val[2]), val[3])
                            else:
                                vec = val

                            # Then, create contours, format as OpenCV expects
                            num_coords = len(vec)
                            num_points = int(num_coords / 2)

                            contour = np.asarray(vec).reshape((num_points, 1, 2))
                            if instance:
                                contours_dict_instance[object_val['type']].append(contour)
                                hierarchy_dict_instance[object_val['type']].append(hierarchy)
                            else:
                                contours_dict_class[object_val['type']].append(contour)
                                hierarchy_dict_class[object_val['type']].append(hierarchy)

        # Retrieve class img from VCD
        for class_name, contours in contours_dict_class.items():
            hierarchy_list = hierarchy_dict_class[class_name]
            num_contours = len(contours)
            hierarchy_array = np.asarray(hierarchy_list).reshape(num_contours, 1, 4)
            color = classes_colors[class_name]
            cv.drawContours(img_class_out, contours, -1, color[::-1], hierarchy=np.asarray([hierarchy_list]),
                            thickness=-1)

        # Retrieve instance img from VCD
        for class_name, contours in contours_dict_instance.items():
            hierarchy_list = hierarchy_dict_instance[class_name]
            num_contours = len(contours)
            hierarchy_array = np.asarray(hierarchy_list).reshape(num_contours, 1, 4)
            color = classes_colors[class_name]

            for c in contours:
                cv.drawContours(img_instance_out, [c], -1, (0, 0, 0), thickness=-1)
                # cv.drawContours(img_instance_out, [c], -1, color[::-1], thickness=-1)
                # cv.drawContours(img_instance_out, [c], -1, (0, 255, 0), thickness=3)

        x = cv.cvtColor(instance_ids_array, cv.COLOR_GRAY2BGR)
        x[np.where((x == [0, 0, 0]).all(axis=2))] = [0, 255, 0]
        img_instance = cv.cvtColor(img_instance, cv.COLOR_GRAY2BGR)
        difference_instance = cv.subtract(img_instance_out, x)
        difference_class = cv.subtract(img_label, img_class_out)
        stack = np.hstack((img_instance, img_instance_out, difference_instance))
        stack2 = np.hstack((img_label, img_class_out, difference_class))
        vstack = np.vstack((stack, stack2))

        # 4.- Check equals
        difference_instance_sum = np.sum(difference_instance)
        difference_class_sum = np.sum(difference_class)
        self.assertEqual(difference_instance_sum, 0)
        self.assertEqual(difference_class_sum, 0)

        #cv.imshow('image', vstack)
        #cv.waitKey(0)

    def test_mapillary(self):
        # Dump content from test_mapillary_SRF6.py at /mapillaryConverter
        with open('../converters/mapillaryConverter/config.json') as f:
            data = json.load(f)

        labels = data['labels']
        path = '../converters/mapillaryConverter/labels'

        quick_test = True
        for img_name in os.listdir(path):
            self.mapillary_image_analysis(img_name, labels)
            if quick_test:
                break


if __name__ == '__main__':  # This changes the command-line entry point to call unittest.main()
    print("Running test_image.py...")
    unittest.main()

