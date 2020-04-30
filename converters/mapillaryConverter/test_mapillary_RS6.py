import cv2 as cv
import json
import numpy as np
from PIL import Image
import os
import sys
sys.path.insert(0, "../..")
import vcd.poly2d as poly
import vcd.core as core
import vcd.types as types
import vcd.utils as utils
import time

with open('config.json') as f:
    data = json.load(f)

labels = data['labels']
path = 'labels'

for img_name in os.listdir(path):
    vcd = core.VCD()
    img_label = cv.imread('labels/' + img_name)
    img_instance = cv.imread('instances/' + img_name, cv.IMREAD_GRAYSCALE)
    img_instance2 = cv.imread('instances/' + img_name, cv.IMREAD_ANYDEPTH)

    imgPIL_instance = Image.open('instances/' + img_name)
    imgPIL_instance = np.array(imgPIL_instance, dtype=np.uint16)

    label_path = 'labels/' + img_name
    instance_path = 'instances/' + img_name

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
    img_class_out = np.zeros((img_instance.shape[0], img_instance.shape[1], 3), np.uint8)

    instance_bgr = cv.cvtColor(instance_ids_array, cv.COLOR_GRAY2BGR)
    final = np.zeros(img_label.shape, np.uint8)
    cont = 0

    cv.namedWindow('image', cv.WINDOW_NORMAL)
    cv.resizeWindow('image', img_instance.shape[0], img_instance.shape[1])

    # Get contours of each instance and retrieve it's class to write in vcd as instance -> True
    for i in range(1, np.max(instance_ids_array)+1):
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
                    uid = vcd.add_object("Instance " + str(i), instance_class)
                    vcd.add_object_data(uid, types.boolean('isInstance', True))

                c = c.flatten()
                hierarchy_list = hierarchy[0][cnt_id].tolist()
                # Write poly, hierarchy and instance
                polygon = types.poly2d('contour', c.tolist(), types.Poly2DType.MODE_POLY2D_RS6FCC, closed=True,
                                       hierarchy=hierarchy_list)
                vcd.add_object_data(uid, polygon)
                cnt_id += 1

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
                polygon = types.poly2d('contour', c.tolist(), types.Poly2DType.MODE_POLY2D_RS6FCC, closed=True,
                                       hierarchy=hierarchy_list)
                vcd.add_object_data(uid, polygon)
                cnt_id += 1
            cont += 1


    vcd.save('vcd_files/' + img_name[0:len(img_name)-4] + '.json', True)  # Change to True to use json prettifier


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
                        elif mode == types.Poly2DType.MODE_POLY2D_RS6FCC.name:
                            vec = poly.getVecFromEncodedRS6(int(val[0]), int(val[1]),int(val[2]), int(val[3]), int(val[4]), val[5])
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
        cv.drawContours(img_class_out, contours, -1, color[::-1], hierarchy=np.asarray([hierarchy_list]), thickness=-1)
        #cv.drawContours(img_class_out, contours, -1, color[::-1], thickness=-1)


    # Retrieve instance img from VCD
    cont = 255
    for class_name, contours in contours_dict_instance.items():
        hierarchy_list = hierarchy_dict_instance[class_name]
        num_contours = len(contours)
        hierarchy_array = np.asarray(hierarchy_list).reshape(num_contours, 1, 4)
        color = classes_colors[class_name]
        for c in contours:
            cv.drawContours(img_instance_out, [c], -1, (cont, cont, cont), thickness=-1)
        cont -= 1

    x = cv.cvtColor(instance_ids_array, cv.COLOR_GRAY2BGR)
    x[np.where((x == [0, 0, 0]).all(axis=2))] = [0, 255, 0]
    img_instance = cv.cvtColor(img_instance, cv.COLOR_GRAY2BGR)
    difference_instance = cv.subtract(img_instance_out, x)
    difference_class = cv.subtract(img_label, img_class_out)
    stack = np.hstack((img_instance, img_instance_out, difference_instance))
    stack2 = np.hstack((img_label, img_class_out, difference_class))
    vstack = np.vstack((stack, stack2))
    print(not np.any(difference_class.flatten()))
    cv.imshow('image', vstack)
    cv.waitKey(0)
