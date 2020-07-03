"""
VCD (Video Content Description) library v4.2.1

Project website: http://vcd.vicomtech.org

Copyright (C) 2020, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.2.1.
VCD is distributed under MIT License. See LICENSE.

"""

import csv
import sys
import os
sys.path.insert(0, "../..")

import glob
import math
import numpy as np

import vcd.core as core
import vcd.types as types
import vcd.utils as utils


class KITTI_Tracking_reader():
    def __init__(self, kitti_tracking_base_path):
        self.kitti_tracking_calib_path = os.path.join(kitti_tracking_base_path, "training/calib")
        self.kitti_tracking_oxts_path = os.path.join(kitti_tracking_base_path, "training/oxts")
        self.kitti_tracking_objects_path = os.path.join(kitti_tracking_base_path, "training/label_02")
        self.kitti_tracking_video_path = os.path.join(kitti_tracking_base_path, "video")

        self.vcds = {}

        # Parse all sequences
        for i in range(0, 21):
            print("Parsing sequence " + str(i))
            self.vcds[i] = self.parse_sequence(i)
        print("All parsing done!")

    def parse_sequence(self, seq_number):
        vcd = core.VCD()

        #########################################
        # OPEN files
        #########################################
        calib_file_name = os.path.join(self.kitti_tracking_calib_path, str(seq_number).zfill(4) + ".txt")
        oxts_file_name = os.path.join(self.kitti_tracking_oxts_path, str(seq_number).zfill(4) + ".txt")
        object_file_name = os.path.join(self.kitti_tracking_objects_path, str(seq_number).zfill(4) + '.txt')

        calib_file = open(calib_file_name, newline='')
        oxts_file = open(oxts_file_name, newline='')
        object_file = open(object_file_name, newline='')
        calib_reader = csv.reader(calib_file, delimiter=' ')
        oxts_reader = csv.reader(oxts_file, delimiter=' ')
        object_reader = csv.reader(object_file, delimiter=' ')

        #########################################
        # READ calibration matrices
        #########################################
        img_width_px = 1236
        img_height_px = 366  # these are rectified dimensions
        calib_matrices = {}
        for row in calib_reader:
            calib_matrices[row[0]] = [float(x) for x in row[1:] if len(x) > 0]  # filter out some spaces at the end of the row

        left_camera_K3x4 = np.reshape(calib_matrices["P2:"], (3, 4))
        right_camera_K3x4 = np.reshape(calib_matrices["P3:"], (3, 4))
        camera_rectification_3x3 = np.reshape(calib_matrices["R_rect"], (3, 3))
        transform_velo_to_camleft_3x4 = np.reshape(calib_matrices["Tr_velo_cam"], (3, 4))  # WRT to LEFT CAMERA ONLY

        #########################################
        # LIDAR info
        #########################################
        # http://www.cvlibs.net/datasets/kitti/setup.php
        location_velo_wrt_lcs_3x1 = np.array([[0.76], [0.0], [1.73]])  # according to the documentation
        # Create pose (p=[[R|C],[0001]])
        pose_velo_wrt_lcs_4x4 = utils.create_pose(np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]),
                                                  location_velo_wrt_lcs_3x1)
        transform_lcs_to_velo_4x4 = utils.inv(pose_velo_wrt_lcs_4x4)

        vcd.add_stream(stream_name="VELO_TOP",
                         uri="",
                         description="Velodyne roof",
                         stream_type=core.StreamType.lidar)
        vcd.add_stream_properties(stream_name="VELO_TOP",
                                    extrinsics=types.Extrinsics(
                                        pose_scs_wrt_lcs_4x4=list(pose_velo_wrt_lcs_4x4.flatten())
                                    ))


        #########################################
        # GPS/IMU info
        #########################################
        # Let's build also the pose of the imu
        location_imu_wrt_lcs_4x4 = np.array([[-0.05], [0.32], [0.93]])  # according to documentation
        pose_imu_wrt_lcs_4x4 = utils.create_pose(np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]),
                                                 location_imu_wrt_lcs_4x4)

        vcd.add_stream(stream_name="IMU",
                         uri="",
                         description="GPS/IMU",
                         stream_type=core.StreamType.other)
        vcd.add_stream_properties(stream_name="IMU",
                                    extrinsics=types.Extrinsics(
                                        pose_scs_wrt_lcs_4x4=list(pose_imu_wrt_lcs_4x4.flatten())
                                    ))


        #########################################
        # CAMERAS
        #########################################
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
        camera_rectification_4x4 = np.vstack((np.hstack((camera_rectification_3x3, [[0], [0], [0]])), [0, 0, 0, 1]))
        transform_velo_to_camleft_4x4 = np.vstack((transform_velo_to_camleft_3x4, [0, 0, 0, 1]))
        transform_velo_to_camleft_4x4 = np.dot(camera_rectification_4x4, transform_velo_to_camleft_4x4)  # such that X_cam = transform_velo_to_cam_4x4 * X_velo

        # The pose of cameras can't be read from documentation, as these are virtual cameras created via a rectification
        # process, therefore, we need to build them using the velo_to_cam calibration
        # Pose_camLeft_wrt_ccs = RT_camLeft_to_ccs
        transform_lcs_to_camleft_4x4 = np.dot(transform_velo_to_camleft_4x4, transform_lcs_to_velo_4x4)
        pose_camleft_wrt_lcs_4x4 = utils.inv(transform_lcs_to_camleft_4x4)
        pose_camright_wrt_lcs_4x4 = pose_camleft_wrt_lcs_4x4

        # Create cams and fill scene
        vcd.add_stream(stream_name="CAM_LEFT",
                            uri="",
                            description="Virtual Left color camera",
                            stream_type=core.StreamType.camera)
        vcd.add_stream_properties(stream_name="CAM_LEFT",
                                       intrinsics=types.IntrinsicsPinhole(
                                           width_px=img_width_px,
                                           height_px=img_height_px,
                                           camera_matrix_3x4=list(left_camera_K3x4.flatten()),
                                           distortion_coeffs_1xN=None
                                       ),
                                       extrinsics=types.Extrinsics(
                                           pose_scs_wrt_lcs_4x4=list(pose_camleft_wrt_lcs_4x4.flatten())
                                       )
                                       )


        vcd.add_stream(stream_name="CAM_RIGHT",
                         uri="",
                         description="Virtual Right color camera",
                         stream_type=core.StreamType.camera)
        vcd.add_stream_properties(stream_name="CAM_RIGHT",
                                    intrinsics=types.IntrinsicsPinhole(
                                        width_px=img_width_px,
                                        height_px=img_height_px,
                                        camera_matrix_3x4=list(right_camera_K3x4.flatten()),
                                        distortion_coeffs_1xN=None
                                    ),
                                    extrinsics=types.Extrinsics(
                                        pose_scs_wrt_lcs_4x4=list(pose_camright_wrt_lcs_4x4.flatten())
                                    )
                                    )


        #########################################
        # ODOMETRY
        #########################################
        oxts = []
        for row in oxts_reader:
            row = row[0:len(row) - 1]
            floats = [float(i) for i in row]
            oxts.append(floats)
            '''lat_deg = row[0]  # deg
            lon_deg = row[1]
            alt_deg = row[2]
            roll_rad = row[3]  # 0 = level, positive = left side up (-pi..pi)
            pitch_rad = row[4]  # 0 = level, positive = front down (-pi/2..pi/2)
            yaw_rad = row[5]  # 0 = east,  positive = counter clockwise (-pi..pi)
            vn = row[6] # velocity towards north(m / s)
            ve = row[7] # velocity towards east(m / s)
            vf = row[8]  # forward velocity, i.e.parallel to earth - surface(m / s)
            vl = row[9] # leftward velocity, i.e.parallel to earth - surface(m / s)
            vu = row[10] # upward velocity, i.e.perpendicular to earth - surface(m / s)
            ax = row[11] # acceleration in x, i.e. in direction of vehicle front(m / s ^ 2)
            ay = row[12] # acceleration in y, i.e. in direction of vehicle left(m / s ^ 2)
            az = row[13] # acceleration in z, i.e. in direction of vehicle top(m / s ^ 2)
            af = row[14] # forward acceleration(m / s ^ 2)
            al = row[15] # leftward acceleration(m / s ^ 2)
            au = row[16] # upward acceleration(m / s ^ 2)
            wx = row[17] # angular rate around x(rad / s)
            wy = row[18] # angular rate around y(rad / s)
            wz = row[19] # angular rate around z(rad / s)
            wf = row[20] # angular rate around forward axis(rad / s)
            wl = row[21] # angular rate around leftward axis(rad / s)
            wu = row[22] # angular rate around upward axis(rad / s)
            posacc = row[23] # velocity accuracy(north / east in m)
            velacc = row[24] # velocity accuracy(north / east in m / s)
            navstat = row[25] # navigation status
            numsats = row[26] # number of satellites tracked by primary GPS receiver
            posmode = row[27] # position mode of primary GPS receiver
            velmode = row[28] # velocity mode of primary GPS receiver
            orimode = row[29] # orientation mode of primary GPS receiver
            '''

        # Convert odometry (GPS) to poses
        odometry_4x4xN = utils.convert_oxts_to_pose(oxts)
        # An odometry entry is a 4x4 pose matrix of the lcs wrt wcs
        # poses_4x4xN_lcs_wrt_wcs = odometry_4x4xN
        frames_1xN = np.arange(0, odometry_4x4xN.shape[2], 1).reshape((1, odometry_4x4xN.shape[2]))
        r, c = frames_1xN.shape
        for i in range(0, c):
            vcd.add_odometry(int(frames_1xN[0, i]),
                                  types.Odometry(
                                      pose_lcs_wrt_wcs_4x4=list(odometry_4x4xN[:, :, i].flatten())
                                  )
                                  )

        #########################################
        # LABELS
        #########################################
        for row in object_reader:
            frameNum = int(row[0])
            trackID = int(row[1]) + 1  # VCD can't handle negative ids

            semantic_class = row[2]
            truncated = utils.float_2dec(float(row[3]))
            occluded = int(row[4])
            alpha = utils.float_2dec(float(row[5]))

            left = utils.float_2dec(float(row[6]))
            top = utils.float_2dec(float(row[7]))
            width = utils.float_2dec(float(row[8]) - left)
            height = utils.float_2dec(float(row[9]) - top)

            bounding_box = types.bbox(name="",
                                      val=(left, top, width, height),
                                      stream='CAM_LEFT')

            dimHeight = utils.float_2dec(float(row[10]))
            dimWidth = utils.float_2dec(float(row[11]))
            dimLength = utils.float_2dec(float(row[12]))

            locX = utils.float_2dec(float(row[13]))
            locY = utils.float_2dec(float(row[14]))
            locZ = utils.float_2dec(float(row[15]))

            rotY = utils.float_2dec(float(row[16]))

            # Note KITTI uses (h, w, l, x, y, z, ry) for cuboids, in camera coordinates (X-to-right, Y-to-bottom, Z-to-front)
            # while in VCD (x,y,z, rx, ry, rz, sx, sy, sz) is defined as a dextrogire system
            # To express the cuboid in LCS (Local-Coordinate-System), we can add the pose of the camera
            # Cameras are 1.65 m height wrt ground
            # Cameras are 1.03 meters wrt to rear axle
            cam_wrt_rear_axle_z = 1.03
            cam_height = 1.65
            cuboid = types.cuboid(name="",
                                  val=(utils.float_2dec(locZ + cam_wrt_rear_axle_z), utils.float_2dec(-locX),
                                       utils.float_2dec(-locY + cam_height), 0, 0, utils.float_2dec(rotY),
                                       utils.float_2dec(dimWidth), utils.float_2dec(dimLength), utils.float_2dec(dimHeight)))
            # Note that if no "stream" parameter is given to this cuboid, LCS is assumed

            if not vcd.has(core.ElementType.object, trackID):
                vcd.add_object(name="", semantic_type=semantic_class, uid=trackID)

            vcd.add_object_data(trackID, bounding_box, frameNum)
            if semantic_class != "DontCare":
                vcd.add_object_data(trackID, cuboid, frameNum)
            vcd.add_object_data(trackID, types.num(name="truncated", val=truncated), frameNum)
            vcd.add_object_data(trackID, types.num(name="occluded", val=occluded), frameNum)
            vcd.add_object_data(trackID, types.num(name="alpha", val=alpha), frameNum)

        # Return
        return vcd


def convert_KITTI_tracking_to_VCD4():
    # Base paths
    kitti_tracking_base_path = "../../../../../data/kitti/tracking"
    kitti_tracking_output_vcd_path = "./etc"

    # Create scenes
    kitti_parser = KITTI_Tracking_reader(kitti_tracking_base_path)

    # Draw/store scenes in VCD
    for count, key in enumerate(kitti_parser.vcds):
        # Store
        vcd_file_name = os.path.join(kitti_tracking_output_vcd_path,
                                     "vcd_421_kitti_tracking_" + str(count).zfill(4) + ".json")
        print('Storing VCD file...' + vcd_file_name)
        kitti_parser.vcds[key].save(file_name=vcd_file_name)


if __name__ == '__main__':
    print("Running " + os.path.basename(__file__))
    convert_KITTI_tracking_to_VCD4()

