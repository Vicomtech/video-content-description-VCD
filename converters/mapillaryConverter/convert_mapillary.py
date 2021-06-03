import cv2 as cv
import json
import numpy as np
import time

from PIL import Image
import os
import sys
sys.path.insert(0, "../..")
import vcd.poly2d as poly
import vcd.core as core
import vcd.types as types
import vcd.utils as utils

import converter

use_profiler = False
show_images = False
quick_test = True
root_name = 'openlabel'

with open('config.json') as f:
    mapillary_config = json.load(f)

labels = mapillary_config['labels']
path = 'labels'


def convert_labels_to_poly(img_name, vcd_poly_mode):
    print('VCD Poly2d mode ' + vcd_poly_mode.name)
    start = time.time()
    vcd_class = converter.mapillary_classes_to_vcd(img_name=img_name,
                                                   mapillary_config=mapillary_config,
                                                   vcd_poly_mode=vcd_poly_mode,
                                                   vcd_root_name=root_name)
    end = time.time()
    print('\tConverted class labels to VCD in {:.2f} ms'.format((end - start) * 1000))

    start = time.time()
    vcd_class.save('vcd_files/' + root_name + img_name[0:len(img_name) - 4] + '_class_' + vcd_poly_mode.name + '.json')
    end = time.time()

    print('\tSaved to VCD JSON file in {:.2f} ms'.format((end - start) * 1000))

    start = time.time()
    img_class_out = converter.vcd_mapillary_classes_to_png(vcd=vcd_class,
                                                           mapillary_config=mapillary_config)
    end = time.time()
    print('\tClass reconstructed from VCD in {:.2f} ms'.format((end - start) * 1000))

    # Prepare mosaic & compute differences
    img_label = cv.imread('labels/' + img_name)
    difference_class = cv.subtract(img_label, img_class_out)
    # Check equals
    difference_class_sum = np.sum(difference_class)
    print("\tClass differences: " + str(difference_class_sum))

    if show_images:
        stack = np.hstack((img_label, img_class_out, difference_class))
        cv.namedWindow(img_name + vcd_poly_mode.name, cv.WINDOW_NORMAL)
        cv.resizeWindow(img_name + vcd_poly_mode.name, img_label.shape[0], img_label.shape[1])
        cv.imshow(img_name + vcd_poly_mode.name, stack)
        cv.waitKey(0)


def convert_instances_to_poly(img_name, vcd_poly_mode):
    print('VCD Poly2d mode ' + vcd_poly_mode.name)
    start = time.time()
    vcd_ins = converter.mapillary_instances_to_vcd(img_name=img_name,
                                                   mapillary_config=mapillary_config,
                                                   vcd_poly_mode=vcd_poly_mode,
                                                   vcd_root_name=root_name)
    end = time.time()
    print('\tConverted instances to VCD in {:.2f} ms'.format((end - start) * 1000))

    start = time.time()
    vcd_ins.save('vcd_files/' + root_name + img_name[0:len(img_name) - 4] + '_instances_' + vcd_poly_mode.name + '.json')
    end = time.time()

    print('\tSaved to VCD JSON file in {:.2f} ms'.format((end - start) * 1000))

    start = time.time()
    img_instances_out = converter.vcd_mapillary_instances_to_png(vcd=vcd_ins,
                                                           mapillary_config=mapillary_config)
    end = time.time()
    print('\tInstances reconstructed from VCD in {:.2f} ms'.format((end - start) * 1000))

    # Prepare mosaic & compute differences
    img_instances = cv.imread('instances/' + img_name, cv.IMREAD_ANYDEPTH)

    # Check equals
    difference_instances = cv.subtract(img_instances, img_instances_out)
    difference_instances_sum = np.sum(difference_instances)
    print("\tInstances differences: " + str(difference_instances_sum))

    height = img_instances.shape[0]
    width = img_instances.shape[1]
    temp = np.zeros((height, width), np.uint8)

    if show_images:
        stack = np.hstack((img_instances, img_instances_out, difference_instances))
        cv.namedWindow(img_name + '_instances', cv.WINDOW_NORMAL)
        cv.resizeWindow(img_name + '_instances', img_instances.shape[0], img_instances.shape[1])
        cv.imshow(img_name + '_instances', stack)
        cv.waitKey(0)


def convert_labels_to_base64(img_name):
    img_label = cv.imread('labels/' + img_name)
    payload_b64_str = utils.image_to_base64(img_label)

    if root_name == 'vcd':
        vcd = core.VCD()
    elif root_name == 'openlabel':
        vcd = core.OpenLABEL()

    # Create VCD
    height = img_label.shape[0]
    width = img_label.shape[1]
    vcd.add_metadata_properties(properties={'labels': 'class'})
    vcd.add_stream(stream_name="Camera", uri=img_name, description="Mapillary image",
                   stream_type=core.StreamType.camera)
    vcd.add_stream_properties(stream_name="Camera", properties={'height': height, 'width': width})
    vcd_image = types.image('labels', payload_b64_str, 'image/png', 'base64')
    uid = vcd.add_object('', '')
    vcd.add_object_data(uid, vcd_image)

    vcd.save('vcd_files/' + root_name + img_name[0:len(img_name) - 4] + '_class_b64.json')

    # Decode
    od = vcd.get_object_data(uid, 'labels')
    payload_b64_read = od['val']
    img_class_out = utils.base64_to_image(payload_b64_read)

    # Check equals
    difference_class = cv.subtract(img_label, img_class_out)
    difference_class_sum = np.sum(difference_class)
    print("\tClass differences: " + str(difference_class_sum))

    if show_images:
        stack = np.hstack((img_label, img_class_out, difference_class))
        cv.namedWindow(img_name + '_b64', cv.WINDOW_NORMAL)
        cv.resizeWindow(img_name + '_b64', img_label.shape[0], img_label.shape[1])
        cv.imshow(img_name + '_b64', stack)
        cv.waitKey(0)


def convert_instances_to_base64(img_name):
    img_instances = cv.imread('instances/' + img_name, cv.IMREAD_ANYDEPTH)
    payload_b64_str = utils.image_to_base64(img_instances)

    if root_name == 'vcd':
        vcd = core.VCD()
    elif root_name == 'openlabel':
        vcd = core.OpenLABEL()

    # Create VCD
    height = img_instances.shape[0]
    width = img_instances.shape[1]
    vcd.add_metadata_properties(properties={'labels': 'class'})
    vcd.add_stream(stream_name="Camera", uri=img_name, description="Mapillary image",
                   stream_type=core.StreamType.camera)
    vcd.add_stream_properties(stream_name="Camera", properties={'height': height, 'width': width})
    vcd_image = types.image('instances', payload_b64_str, 'image/png', 'base64')
    uid = vcd.add_object('', '')
    vcd.add_object_data(uid, vcd_image)

    vcd.save('vcd_files/' + root_name + img_name[0:len(img_name) - 4] + '_instances_b64.json')

    # Decode
    od = vcd.get_object_data(uid, 'instances')
    payload_b64_read = od['val']
    img_instances_out = utils.base64_to_image(payload_b64_read, cv.IMREAD_ANYDEPTH)

    # Save image
    compr_params = [int(cv.IMWRITE_PNG_COMPRESSION), 9]
    cv.imwrite(filename='vcd_files/' + root_name + img_name[0:len(img_name) - 4] + '_instances_reconstructed_from_b64.png',
               img=img_instances_out,
               params=compr_params)

    # Check equals
    difference_instances = cv.subtract(img_instances, img_instances_out)
    difference_instances_sum = np.sum(difference_instances)
    print("\tInstances differences: " + str(difference_instances_sum))

    if show_images:
        stack = np.hstack((img_instances, img_instances_out, difference_instances))
        cv.namedWindow(img_name + '_b64', cv.WINDOW_NORMAL)
        cv.resizeWindow(img_name + '_b64', img_instances.shape[0], img_instances.shape[1])
        cv.imshow(img_name + '_b64', stack)
        cv.waitKey(0)


for img_name in os.listdir(path):
    # Class LABELS
    print(img_name)

    # Convert class images
    convert_labels_to_base64(img_name=img_name)
    convert_labels_to_poly(img_name=img_name, vcd_poly_mode=types.Poly2DType.MODE_POLY2D_SRF6DCC)
    convert_labels_to_poly(img_name=img_name, vcd_poly_mode=types.Poly2DType.MODE_POLY2D_ABSOLUTE)

    # Convert instance images
    convert_instances_to_base64(img_name=img_name)
    convert_instances_to_poly(img_name=img_name, vcd_poly_mode=types.Poly2DType.MODE_POLY2D_SRF6DCC)
    convert_instances_to_poly(img_name=img_name, vcd_poly_mode=types.Poly2DType.MODE_POLY2D_ABSOLUTE)




    '''
    img_instance = cv.imread('instances/' + img_name, cv.IMREAD_GRAYSCALE)
    imgPIL_instance = Image.open('instances/' + img_name)
    imgPIL_instance = np.array(imgPIL_instance, dtype=np.uint16)
    instance_ids_array = np.array(imgPIL_instance % 256, dtype=np.uint8)
    img_label = cv.imread('labels/' + img_name)

    x = cv.cvtColor(instance_ids_array, cv.COLOR_GRAY2BGR)
    #x[np.where((x == [0, 0, 0]).all(axis=2))] = [0, 255, 0]
    img_instance = cv.cvtColor(img_instance, cv.COLOR_GRAY2BGR)
    difference_instance = cv.subtract(img_instance_out, x)
    difference_class = cv.subtract(img_label, img_class_out)

    if show_images:
        stack = np.hstack((img_instance, img_instance_out, difference_instance))
        stack2 = np.hstack((img_label, img_class_out, difference_class))
        vstack = np.vstack((stack, stack2))
        cv.namedWindow(img_name, cv.WINDOW_NORMAL)
        cv.resizeWindow(img_name, img_instance.shape[0], img_instance.shape[1])
        cv.imshow(img_name, vstack)
        cv.waitKey(0)

    # Check equals
    difference_instance_sum = np.sum(difference_instance)
    difference_class_sum = np.sum(difference_class)
    print("\tInstance differences: " + str(difference_instance_sum))
    print("\tClass differences: " + str(difference_class_sum))
    '''
    if quick_test:
        break
