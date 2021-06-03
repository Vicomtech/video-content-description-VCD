import cv2 as cv
import json
import numpy as np
from PIL import Image
import os
import sys
sys.path.insert(0, "../..")
import random as rng

import vcd.poly2d as poly
import vcd.core as core
import vcd.types as types
import vcd.utils as utils

verbose = False


def mapillary_classes_to_vcd(img_name, mapillary_config, vcd_poly_mode, vcd_root_name):
    '''
    This function converts an image of labels (classes) of the Mapillary Vistas dataset into a VCD file
    :param img_name: name and extension of image
    :param mapillary_config: configuration file with class names and colors
    :param vcd_poly_mode: VCD 4.3.1 poly2d mode
    :param vcd_root_name: 'vcd' or 'openlabel'
    :return: VCD object
    '''
    # 0) Create VCD object
    if vcd_root_name == 'vcd':
        vcd = core.VCD()
    elif vcd_root_name == 'openlabel':
        vcd = core.OpenLABEL()

    # 1) Get class colors (using hexadecimal to enable reverse dictionary)
    classes_colors = {}
    color_classes = {}
    for x in mapillary_config['labels']:
        classes_colors[x['name']] = utils.rgb_to_hex(tuple(x['color']))
        color_classes[utils.rgb_to_hex(tuple(x['color']))] = x['name']

    # 2) Prepare arrays for instance and class retrieval
    # Mapillary instance PNG image contains class and instance value
    #  class value can be retrieved dividing by 256, the rest is the instance id
    #  though, a class PNG is also available which covers the entire image (countable and non-countable objects)
    img_label = cv.imread('labels/' + img_name)

    height = img_label.shape[0]
    width = img_label.shape[1]
    vcd.add_metadata_properties(properties={'labels': 'class'})
    vcd.add_stream(stream_name="Camera", uri=img_name, description="Mapillary image", stream_type=core.StreamType.camera)
    vcd.add_stream_properties(stream_name="Camera", properties={'height': height, 'width': width})

    # 3) Get contours of each class and write in VCD
    cont = 0
    for class_val in mapillary_config['labels']:
        # check all posible classes of mapillary
        color_rgb = class_val['color']
        color_bgr = color_rgb[::-1]
        seg = cv.inRange(img_label, tuple(color_bgr), tuple(color_bgr))
        if cv.countNonZero(seg) != 0:
            contours, hierarchy = cv.findContours(seg, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
            # cv.drawContours(final, contours, -1, tuple(class_val['color'][::-1]), thickness=-1)

            cnt_id = 0
            color_hex = utils.rgb_to_hex(tuple(color_rgb))
            class_ = color_classes[color_hex]
            #class_ = utils.get_key(classes_colors, class_val['color'])
            uid = vcd.add_object(name="class" + str(cont), semantic_type=class_)
            # vcd.add_object_data(uid, types.boolean('isInstance', False))
            #vcd.add_object_data(uid=uid, object_data=types.text('dict', 'class'))

            for c in contours:
                c = c.flatten().tolist()
                hierarchy_list = hierarchy[0][cnt_id].tolist()
                polygon = types.poly2d(name='contour' + str(cnt_id),
                                       val=c,
                                       mode=vcd_poly_mode,
                                       closed=True,
                                       hierarchy=hierarchy_list)
                vcd.add_object_data(uid=uid, object_data=polygon)
                cnt_id += 1
            cont += 1

    return vcd


def mapillary_instances_to_vcd(img_name, mapillary_config, vcd_poly_mode, vcd_root_name):
    # 0) Create VCD object
    if vcd_root_name == 'vcd':
        vcd = core.VCD()
    elif vcd_root_name == 'openlabel':
        vcd = core.OpenLABEL()

    # 1) Get class colors dictionary (using hexadecimal to enable reverse dictionary)
    classes_colors = {}
    color_classes = {}
    for x in mapillary_config['labels']:
        classes_colors[x['name']] = utils.rgb_to_hex(tuple(x['color']))
        color_classes[utils.rgb_to_hex(tuple(x['color']))] = x['name']

    # 2) Prepare arrays for instance and class retrieval
    # Mapillary instance PNG image contains class and instance value
    #  class value can be retrieved dividing by 256, the rest is the instance id
    #  though, a class PNG is also available which covers the entire image (countable and non-countable objects)
    img_instances = cv.imread('instances/' + img_name, cv.IMREAD_ANYDEPTH)
    #img_instances = np.array(Image.open('instances/' + img_name), dtype=np.uint16)
    img_ids_array = np.array(img_instances % 256, dtype=np.uint8)  # instance id
    img_class_array = np.array(img_instances / 256, dtype=np.uint8)  # instance class
    img_ids_array_bgr = cv.cvtColor(img_ids_array, cv.COLOR_GRAY2BGR)  # color_rgb bgr so we can segment
    img_class_array_bgr = cv.cvtColor(img_class_array, cv.COLOR_GRAY2BGR)

    height = img_instances.shape[0]
    width = img_instances.shape[1]
    vcd.add_metadata_properties(properties={'labels': 'instances'})
    vcd.add_stream(stream_name="Camera", uri=img_name, description="Mapillary image",
                   stream_type=core.StreamType.camera)
    vcd.add_stream_properties(stream_name="Camera", properties={'height': height, 'width': width})

    # We shouldn't segment by class, because contours may merge instances of same class
    # We shouldn't segment by instance, because contours may merge instances of different classes
    # In addition, cv.findContours works on binarized images, and 8bits to get full hiearchies
    # As a consequence, we first need to separate content per class, convert to 8 bits and then separate per instance
    # before applying findcontours (note that a single a instance may have several contours defining it, e.g. holes)

    # Can we go class by class, and create a 8-bit range version of the instances image
    # And then create as many images as id values so findcontours won't merge any two instances that correspond to different classes
    for class_index, label in enumerate(mapillary_config['labels']):
        class_name = label['name']
        is_instance = mapillary_config['labels'][class_index]['instances']

        # Range of values should be [class_idx*256, class_idx*256 + 255] for this class
        range_min = class_index*256
        range_max = (class_index+1)*256
        temp = np.zeros((height, width), np.uint8)
        idx = np.where(np.logical_and(img_instances >= range_min, img_instances < range_max))

        if len(idx[0]) == 0:  # that would mean no pixel belong to this class
            continue
        if verbose:
            print(class_name)

        # So now temp contains an 8-bit version of instances id of this class only
        # Let's re-encode the instance values so they don't go from 0 upwards, but from 255 downwards (the reason is
        # that the background of the image is 0, and then pixels with instance id 0 would pass undetected)
        temp[idx] = 255 - (img_instances[idx] % 256)

        # Now we can see which instance id values we have (warning: reencoded from 255 downards)
        min_val = np.min(temp[idx])
        max_val = np.max(temp[idx])

        # Iterate from minium to maximum...
        for val in range(min_val, max_val + 1):
            # Mask only those for this id value
            idx_val = np.where(temp == val)
            seg = np.zeros((height, width), np.uint8)
            seg[idx_val] = temp[idx_val]

            # Let's retrieve the contours for this particular instance and class
            contours, hierarchy = cv.findContours(seg, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

            # Prepare id val and uid for vcd
            id = 255 - val  # retrieve id value
            uid = int(class_index * 256 + id)  # so it is unique and equal to the value of the pixels in the PNG16b

            '''if class_index == 45:
                cv.destroyAllWindows()
                cv.namedWindow('seg_' + str(class_index) + "_" + str(255 - val), cv.WINDOW_NORMAL)
                cv.imshow('seg_' + str(class_index) + "_" + str(255 - val), seg)

                rec = np.zeros((seg.shape[0], seg.shape[1], 3), np.uint8)
                for i in range(len(contours)):
                    color = (rng.randint(0, 256), rng.randint(0, 256), rng.randint(0, 256))
                    cv.drawContours(rec, contours, i, color, 2, cv.LINE_8, hierarchy, 0)

                #cv.drawContours(temp2, contours, -1, (0, 255, 0), hierarchy=hierarchy, thickness=-1)
                cv.namedWindow('rec_' + str(class_index) + "_" + str(255 - val), cv.WINDOW_NORMAL)
                cv.imshow('rec_' + str(class_index) + "_" + str(255 - val), seg)
                cv.waitKey(0)
                '''

            for c in contours:
                if is_instance:
                    if not vcd.has(core.ElementType.object, uid):
                        vcd.add_object(name="instance" + str(uid), semantic_type=class_name, uid=uid)
                        if verbose:
                            print("\tAdded object instance: " + str(uid))

                    cnt_id = 0
                    if 'object_data' in vcd.get_root()['objects'][str(uid)]:
                        cnt_id = len(vcd.get_root()['objects'][str(uid)]['object_data']['poly2d'])

                    c = c.flatten()
                    hierarchy_list = hierarchy[0][cnt_id].tolist()
                    polygon = types.poly2d(name='contour' + str(cnt_id),
                                           val=c.tolist(),
                                           mode=vcd_poly_mode,
                                           closed=True,
                                           hierarchy=hierarchy_list)
                    vcd.add_object_data(uid=uid, object_data=polygon)
                else:
                    cnt_id = 0
                    uid = int(class_index * 256)
                    if vcd.has(core.ElementType.object, uid):  # this may happen with instances of value 0
                        continue

                    vcd.add_object(name="class" + str(class_index), semantic_type=class_name, uid=uid)
                    if verbose:
                        print("\tAdded object class: " + str(uid))

                    for c in contours:
                        c = c.flatten().tolist()
                        hierarchy_list = hierarchy[0][cnt_id].tolist()
                        polygon = types.poly2d(name='contour' + str(cnt_id),
                                               val=c,
                                               mode=vcd_poly_mode,
                                               closed=True,
                                               hierarchy=hierarchy_list)
                        vcd.add_object_data(uid=uid, object_data=polygon)
                        cnt_id += 1
            if cnt_id > 0 and verbose:
                print("\tAdded {cnt_id} contours".format(cnt_id=cnt_id))

    return vcd


def vcd_mapillary_classes_to_png(vcd, mapillary_config):
    '''
    This function reads a VCD file containing Mapillary Vistas labels (classes), as generated by function
    mapillary_classes_to_vcd(), and creates a PNG image, equal to the original Mapillary Vistas label PNG
    :param vcd: VCD object
    :param mapillary_config: configuration file
    :return: PNG image as a numpy array
    '''
    assert(vcd.get_metadata()['labels'] == 'class')

    # 1) Prepare structures
    contours_dict_class = {}  # A dictionary of contours. Each key is one class type, each value, a contours array
    hierarchy_dict_class = {}

    # 2) Get class colors
    classes_colors = {}
    color_classes = {}
    for x in mapillary_config['labels']:
        classes_colors[x['name']] = utils.rgb_to_hex(tuple(x['color']))
        color_classes[utils.rgb_to_hex(tuple(x['color']))] = x['name']

    # 3) Reconstruct hierarchies
    for object_key, object_val in vcd.get_objects().items():
        # Assuming this is static (no frame info)
        contours_dict_class.setdefault(object_val['type'], [])
        hierarchy_dict_class.setdefault(object_val['type'], [])
        if 'object_data' in object_val:
            if 'poly2d' in object_val['object_data']:
                for idx_pol, poly2d in enumerate(object_val['object_data']['poly2d']):
                    val = poly2d['val']
                    mode = poly2d['mode']
                    # closed = poly2d['closed']  # Not used in OpenCV
                    hierarchy = poly2d['hierarchy']
                    if mode == types.Poly2DType.MODE_POLY2D_SRF6DCC.name:
                        vec = poly.getVecFromEncodedSRF6(int(val[0]), int(val[1]), int(val[2]), val[3])
                    elif mode == types.Poly2DType.MODE_POLY2D_RS6FCC.name:
                        vec = poly.getVecFromEncodedRS6(int(val[0]), int(val[1]), int(val[2]), int(val[3]),
                                                        int(val[4]), val[5])
                    else:
                        vec = val

                    # Then, create contours, format as OpenCV expects
                    num_coords = len(vec)
                    num_points = int(num_coords / 2)

                    contour = np.asarray(vec).reshape((num_points, 1, 2))

                    contours_dict_class[object_val['type']].append(contour)
                    hierarchy_dict_class[object_val['type']].append(hierarchy)

    # 4) Retrieve class img from VCD
    height = vcd.get_stream(stream_name="Camera")['stream_properties']['height']
    width = vcd.get_stream(stream_name="Camera")['stream_properties']['width']
    img_class_out = np.zeros((height, width, 3), np.uint8)
    for class_name, contours in contours_dict_class.items():
        hierarchy_list = hierarchy_dict_class[class_name]
        color_hex = classes_colors[class_name]
        color_rgb = utils.hex_to_rgb(color_hex)
        cv.drawContours(img_class_out, contours, -1, color_rgb[::-1], hierarchy=np.asarray([hierarchy_list]),
                        thickness=-1)

    return img_class_out


def vcd_mapillary_instances_to_png(vcd, mapillary_config):
    assert (vcd.get_metadata()['labels'] == 'instances')

    # 2) Get class colors
    classes_idxs = {}
    classes_colors = {}
    color_classes = {}
    for count, x in enumerate(mapillary_config['labels']):
        classes_idxs[x['name']] = count
        classes_colors[x['name']] = utils.rgb_to_hex(tuple(x['color']))
        color_classes[utils.rgb_to_hex(tuple(x['color']))] = x['name']

    # 3) Reconstruct hierarchies and build images
    height = vcd.get_stream(stream_name="Camera")['stream_properties']['height']
    width = vcd.get_stream(stream_name="Camera")['stream_properties']['width']
    temp1_class_idx = np.zeros((height, width), np.uint8)
    temp2_inst_id = np.zeros((height, width), np.uint8)

    #cv.namedWindow('classes', cv.WINDOW_NORMAL)
    #cv.namedWindow('instances', cv.WINDOW_NORMAL)
    for object_key, object_val in vcd.get_objects().items():
        # Assuming this is static (no frame info)
        instance_id = int(object_key) % 256
        class_name = object_val['type']
        class_idx = classes_idxs[class_name]
        contours = []
        hierarchies = []

        if 'object_data' in object_val:
            if 'poly2d' in object_val['object_data']:
                for idx_pol, poly2d in enumerate(object_val['object_data']['poly2d']):
                    val = poly2d['val']
                    mode = poly2d['mode']
                    # closed = poly2d['closed']  # Not used in OpenCV
                    hierarchy = poly2d['hierarchy']
                    if mode == types.Poly2DType.MODE_POLY2D_SRF6DCC.name:
                        vec = poly.getVecFromEncodedSRF6(int(val[0]), int(val[1]), int(val[2]), val[3])
                    elif mode == types.Poly2DType.MODE_POLY2D_RS6FCC.name:
                        vec = poly.getVecFromEncodedRS6(int(val[0]), int(val[1]), int(val[2]), int(val[3]),
                                                        int(val[4]), val[5])
                    else:
                        vec = val

                    # Then, create contours, format as OpenCV expects
                    num_coords = len(vec)
                    num_points = int(num_coords / 2)

                    contour = np.asarray(vec).reshape((num_points, 1, 2))

                    contours.append(contour)
                    hierarchies.append(hierarchy)

        # Draw the contour, using the color of the class, multiply by 256 and add instance id
        if not mapillary_config['labels'][class_idx]['instances']:
            # This is a class contour (non-countable thing)
            cv.drawContours(temp1_class_idx, contours, -1, class_idx, hierarchy=np.asarray([hierarchies]),
                            thickness=-1)
        else:
            # So this is an instance contour
            cv.drawContours(temp1_class_idx, contours, -1, class_idx, hierarchy=np.asarray([hierarchies]),
                            thickness=-1)
            cv.drawContours(temp2_inst_id, contours, -1, instance_id, hierarchy=np.asarray([hierarchies]), thickness=-1)


        #print('object_uid: ' + object_key + ' object_name: ' + object_val['name'] + ' object_class: ' + class_name)
        #cv.imshow('classes', temp1_class_idx)
        #cv.imshow('instances', temp2_inst_id)
        #cv.waitKey(0)

    img_instance_out = np.array(temp1_class_idx * 256 + temp2_inst_id, dtype=np.uint16)

    return img_instance_out

