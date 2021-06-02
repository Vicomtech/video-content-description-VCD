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
    pass

'''
def convert_mapillary_into_vcd(img_label_path, img_instance_path, mapillary_config, vcd_poly_mode, vcd_root_name):
    # 0) Create VCD object
    if vcd_root_name == 'vcd':
        vcd = core.VCD()
    elif vcd_root_name == 'openlabel':
        vcd = core.OpenLABEL()

    # 1) Get class colors (using hexadecimal to enable reverse dictionary)
    classes_colors = {}
    color_classes = {}
    for x in mapillary_config['labels']:
        classes_colors[x['name']] = rgb_to_hex(tuple(x['color']))
        color_classes[rgb_to_hex(tuple(x['color']))] = x['name']

    # 2) Prepare arrays for instance and class retrieval
    # Mapillary instance PNG image contains class and instance value
    #  class value can be retrieved dividing by 256, the rest is the instance id
    #  though, a class PNG is also available which covers the entire image (countable and non-countable objects)
    img_label = cv.imread(img_label_path)
    imgPIL_instance = np.array(Image.open(img_instance_path), dtype=np.uint16)
    instance_ids_array = np.array(imgPIL_instance % 256, dtype=np.uint8) # instance id
    instance_class_array = np.array(imgPIL_instance / 256, dtype=np.uint8) # instance class
    instance_bgr = cv.cvtColor(instance_ids_array, cv.COLOR_GRAY2BGR)  # bgr so we can segment with opencv

    height = img_label.shape[0]
    width = img_label.shape[1]
    vcd.add_stream(stream_name="Camera", uri="", description="Mapillary image", stream_type=core.StreamType.camera)
    vcd.add_stream_properties(stream_name="Camera", properties={'height': height, 'width': width})

    # 3) Get contours of each instance and retrieve its class
    cont = 0
    for i in range(1, np.max(instance_ids_array) + 1):
        seg = cv.inRange(instance_bgr, (i, i, i), (i, i, i))
        if cv.countNonZero(seg) != 0:
            contours, hierarchy = cv.findContours(seg, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
            cnt_id = 0
            # Reverse point_color from bgr to rgb to get class
            # Write class in vcd
            for c in contours:
                # Pick class value from contour
                extLeft = tuple(c[c[:, :, 0].argmin()][0])
                color = img_label[extLeft[1]][extLeft[0]]
                color = tuple([int(x) for x in color])
                color = list(color)
                instance_class = utils.get_key(classes_colors, color[::-1])

                if cnt_id == 0:  # first time, let's create the VCD object for this polygon
                    uid = vcd.add_object("instance" + str(cont), instance_class)
                    #vcd.add_object_data(uid, types.boolean('isInstance', True))
                    vcd.add_object_data(uid, types.text('dict', 'instance', coordinate_system=None, properties={"id": cont}))

                c = c.flatten()
                hierarchy_list = hierarchy[0][cnt_id].tolist()
                # Write poly, hierarchy and instance
                polygon = types.poly2d('contour' + str(cnt_id), c.tolist(), vcd_poly_mode,
                                       closed=True,
                                       hierarchy=hierarchy_list)
                vcd.add_object_data(uid, polygon)
                cnt_id += 1
            cont += 1

    # 4) Get contours of each class and write in VCD
    cont = 0
    for class_val in mapillary_config['labels']:
        # check all posible classes of mapillary
        seg = cv.inRange(img_label, tuple(class_val['color'][::-1]), tuple(class_val['color'][::-1]))
        if cv.countNonZero(seg) != 0:
            contours, hierarchy = cv.findContours(seg, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
            #cv.drawContours(final, contours, -1, tuple(class_val['color'][::-1]), thickness=-1)

            cnt_id = 0
            class_ = utils.get_key(classes_colors, class_val['color'])
            uid = vcd.add_object("class" + str(cont), class_)
            #vcd.add_object_data(uid, types.boolean('isInstance', False))
            vcd.add_object_data(uid, types.text('dict', 'class'))

            for c in contours:
                c = c.flatten()
                hierarchy_list = hierarchy[0][cnt_id].tolist()
                polygon = types.poly2d('contour' + str(cnt_id), c.tolist(), vcd_poly_mode,
                                       closed=True,
                                       hierarchy=hierarchy_list)
                vcd.add_object_data(uid, polygon)
                cnt_id += 1
            cont += 1

    return vcd

'''

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
    pass

