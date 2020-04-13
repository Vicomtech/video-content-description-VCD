"""
VCD (Video Content Description) library v4.1.0

Project website: http://vcd.vicomtech.org

Copyright (C) 2020, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.1.0.
VCD is distributed under MIT License. See LICENSE.

"""

import csv
import sys
import os
sys.path.insert(0, "../..")

import glob
import math
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import vcd.core as core
import vcd.types as types
import vcd.serializer as serializer


def float_2dec(val):
    '''
    This function is useful to print float into JSON with only 2 decimals
    '''
    return float((int(100*val))/100)


def convert_KITTI_tracking_to_VCD4():
    object_files_base_path = "../../../../../data/kitti/tracking/training/label_02/"
    calib_files_base_path = "../../../../../data/kitti/tracking/training/calib/"

    for count in range(0, 21):  # We know there are 20 files in KITTI tracking
        object_file_name = object_files_base_path + str(count).zfill(4) + ".txt"
        calib_file_name = calib_files_base_path + str(count).zfill(4) + ".txt"
        vcd = core.VCD()

        # Read Calibration (some info from the documentation)
        img_width_px = 1236
        img_height_px = 366  # these are rectified dimensions
        with open(calib_file_name, newline='') as calib_file:
            calib_reader = csv.reader(calib_file, delimiter=' ')
            calib_matrices = {}
            for row in calib_reader:
                calib_matrices[row[0]] = [float(x) for x in row[1:] if
                                          len(x) > 0]  # filter out some spaces at the end of the row
            # From KITTI readme.txt:
            # To project a point from Velodyne coordinates into the left color image,
            # you can use this formula: x = P2 * R0_rect * Tr_velo_to_cam * y
            # For the right color image: x = P3 * R0_rect * Tr_velo_to_cam * y
            # Note: All matrices are stored row-major, i.e., the first values correspond
            # to the first row. R0_rect contains a 3x3 matrix which you need to extend to
            # a 4x4 matrix by adding a 1 as the bottom-right element and 0's elsewhere.
            # Tr_xxx is a 3x4 matrix (R|t), which you need to extend to a 4x4 matrix
            # in the same way!

            # Virtually, cam_left and cam_right are defined as the same coordinate systems, so their scs are the same
            # But their projection matrices (3x4) include a right-most non-zero column which shifts 3d points when projected
            # into the images, that is why projecting from velodyne to left and right use the same "extrinsics", and just differ
            # in the usage of the "intrinsic" matrices P2 and P3
            # P2 and P3 might be decomposed so P2 = K2*T2 and P3=K3*T3, so T2 and T3 could host extrinsic information
            # while K2 and K3 could host the intrinsic information. This way, the pose of cam_left would be T2*R_rect*Tr_velo
            # However, such decomposition seems to be non-trivial.
            # x = P2 * R0_rect * Tr_velo_to_cam * y
            # x = P3 * R0_rect * Tr_velo_to_cam * y

            # The pose of cameras can't be read from documentation, as these are virtual cameras created via a rectification
            # process, therefore, we need to build them using the velo_to_cam calibration
            # Pose_camLeft_wrt_ccs = RT_camLeft_to_ccs

            left_camera_K3x4 = np.reshape(calib_matrices["P2:"], (3, 4))
            camera_rectification_3x3 = np.reshape(calib_matrices["R_rect"], (3, 3))
            transform_velo_to_camleft_3x4 = np.reshape(calib_matrices["Tr_velo_cam"], (3, 4))  # WRT to LEFT CAMERA ONLY
            camera_rectification_4x4 = np.vstack((np.hstack((camera_rectification_3x3, [[0], [0], [0]])), [0, 0, 0, 1]))

            # LIDAR info http://www.cvlibs.net/datasets/kitti/setup.php
            location_velo_wrt_lcs_3x1 = np.array([[0.76], [0.0], [1.73]])  # according to the documentation
            # Create pose (p=[[R|-RC],[0001]])

            rotation_3x3 = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
            translation_3x1 = -rotation_3x3.dot(location_velo_wrt_lcs_3x1)
            temp = np.hstack((rotation_3x3, translation_3x1))
            pose_velo_wrt_lcs_4x4 = np.vstack((temp, np.array([0, 0, 0, 1])))


            transform_lcs_to_velo_4x4 = pose_velo_wrt_lcs_4x4

            transform_velo_to_camleft_4x4 = np.vstack((transform_velo_to_camleft_3x4, [0, 0, 0, 1]))
            transform_velo_to_camleft_4x4 = np.dot(camera_rectification_4x4,
                                                   transform_velo_to_camleft_4x4)  # such that X_cam = transform_velo_to_cam_4x4 * X_velo
            transform_lcs_to_camleft_4x4 = np.dot(transform_velo_to_camleft_4x4, transform_lcs_to_velo_4x4)
            pose_camleft_wrt_lcs_4x4 = transform_lcs_to_camleft_4x4

            vcd.add_stream(stream_name="CAM_LEFT",
                           uri="",
                           description="Virtual left color camera",
                           stream_type=core.StreamType.camera)
            vcd.add_stream_properties(stream_name="CAM_LEFT",
                                      properties=None,
                                      intrinsics=types.IntrinsicsPinhole(
                                          width_px=img_width_px,
                                          height_px=img_height_px,
                                          camera_matrix_3x4=list(left_camera_K3x4.flatten()),
                                          distortion_coeffs_1xN=None
                                      ),
                                      extrinsics=types.Extrinsics(
                                          pose_scs_wrt_lcs_4x4=list(pose_camleft_wrt_lcs_4x4.flatten())
                                      ))



        # Read objects
        with open(object_file_name, newline='') as object_file:
            object_reader = csv.reader(object_file, delimiter=' ')
            for row in object_reader:
                frameNum = int(row[0])
                trackID = int(row[1]) + 1  # VCD can't handle negative ids

                semantic_class = row[2]
                truncated = float_2dec(float(row[3]))
                occluded = int(row[4])
                alpha = float_2dec(float(row[5]))

                left = float_2dec(float(row[6]))
                top = float_2dec(float(row[7]))
                width = float_2dec(float(row[8]) - left)
                height = float_2dec(float(row[9]) - top)

                dimHeight = float_2dec(float(row[10]))
                dimWidth = float_2dec(float(row[11]))
                dimLength = float_2dec(float(row[12]))

                locX = float_2dec(float(row[13]))
                locY = float_2dec(float(row[14]))
                locZ = float_2dec(float(row[15]))

                rotY = float_2dec(float(row[16]))

                bounding_box = types.bbox(name="", val=(left, top, width, height))
                # Note KITTI uses (h, w, l, x, y, z, ry) for cuboids, in camera coordinates (X-to-right, Y-to-bottom, Z-to-front)
                # while in VCD (x,y,z, rx, ry, rz, sx, sy, sz) is defined as a dextrogire system

                # In addition, cameras are 1.65 m height wrt ground
                # and cameras are 1.03 meters wrt to rear axle
                cam_wrt_rear_axle_z = 1.03
                cam_height = 1.65
                cuboid = types.cuboid(name="",
                                      val=(float_2dec(locZ + cam_wrt_rear_axle_z), float_2dec(-locX),
                                           float_2dec(-locY + cam_height), 0, 0, float_2dec(rotY),
                                           float_2dec(dimWidth), float_2dec(dimLength), float_2dec(dimHeight)))

                if not vcd.has(core.ElementType.object, trackID):
                    vcd.add_object(name="", semantic_type=semantic_class, uid=trackID)

                vcd.add_object_data(trackID, bounding_box, frameNum)
                if semantic_class != "DontCare":
                    vcd.add_object_data(trackID, cuboid, frameNum)
                vcd.add_object_data(trackID, types.num(name="truncated", val=truncated), frameNum)
                vcd.add_object_data(trackID, types.num(name="occluded", val=occluded), frameNum)
                vcd.add_object_data(trackID, types.num(name="alpha", val=alpha), frameNum)


        vcd_json_file_name = "./etc/vcd410_kitti_tracking_" + str(count).zfill(4) + ".json"
        vcd.save(vcd_json_file_name, False)

        #vcd_proto_file_name = "./etc/vcd400_proto_kitti_tracking_" + str(count).zfill(4) + ".txt"
        #serializer.json2proto_bin(vcd_json_file_name, vcd_proto_file_name)

        count += 1


if __name__ == '__main__':  # This changes the command-line entry point to call unittest.main()
    convert_KITTI_tracking_to_VCD4()

