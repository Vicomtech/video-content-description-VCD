"""
VCD (Video Content Description) library v4.3.1

Project website: http://vcd.vicomtech.org

Copyright (C) 2021, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.3.1.
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
import vcd.scl as scl
import vcd.schema as schema
import vcd.types as types
import vcd.utils as utils


class KITTI_Tracking_reader():
    def __init__(self, kitti_tracking_base_path, num=None):
        self.kitti_tracking_calib_path = os.path.join(kitti_tracking_base_path, "training/calib")
        self.kitti_tracking_oxts_path = os.path.join(kitti_tracking_base_path, "training/oxts")
        self.kitti_tracking_objects_path = os.path.join(kitti_tracking_base_path, "training/label_02")
        self.kitti_tracking_video_path = os.path.join(kitti_tracking_base_path, "video")

        self.vcds = {}

        # Parse all sequences
        if num is None:
            for i in range(0, 21):
                print("Parsing sequence " + str(i))
                #self.vcds[i] = self.parse_sequence(i)
                self.vcds[i] = self.parse_sequence_direct(i)
            print("All parsing done!")
        else:
            print("Parsing sequence " + str(num))
            # self.vcds[i] = self.parse_sequence(i)
            self.vcds[num] = self.parse_sequence_direct(num)

    @staticmethod
    def read_odometry_from_oxts(oxts_reader):
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
        return odometry_4x4xN

    def parse_sequence_direct(self, seq_number):
        # This is a variant approach for creating a VCD 4.3.0 file reading the KITTI calibration files,
        # trying to avoid additional computation at this level, and exploiting the ability of VCD 4.3.0 to
        # express arbitrary transforms across coordinate systems

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
        # CREATE base coordinate system
        #########################################
        # The main coordinate system for the scene "odom" represents a static cs (which coincides with first local cs).
        vcd.add_coordinate_system("odom", cs_type=types.CoordinateSystemType.scene_cs)

        #########################################
        # CREATE vehicle coordinate system
        #########################################
        # Local coordinate system, moving with the vehicle. Following iso8855 (x-front, y-left, z-up)
        vcd.add_coordinate_system("vehicle-iso8855", cs_type=types.CoordinateSystemType.local_cs, parent_name="odom")
        # Sensor coordinate systems are added

        # Add transforms for each time instant
        odometry_4x4xN = self.read_odometry_from_oxts(oxts_reader)

        # An odometry entry is a 4x4 pose matrix of the lcs wrt wcs (ergo a transform lcs_to_wcs)
        # poses_4x4xN_lcs_wrt_wcs = odometry_4x4xN
        frames_1xN = np.arange(0, odometry_4x4xN.shape[2], 1).reshape((1, odometry_4x4xN.shape[2]))
        r, c = frames_1xN.shape
        for i in range(0, c):
            vcd.add_transform(int(frames_1xN[0, i]), transform=types.Transform(
                src_name="vehicle-iso8855",
                dst_name="odom",
                transform_src_to_dst=types.TransformData(
                    val=list(odometry_4x4xN[:, :, i].flatten()),
                    type=types.TransformDataType.matrix_4x4))
            )

        #########################################
        # CREATE SENSORS coordinate system: LASER
        #########################################
        # http://www.cvlibs.net/datasets/kitti/setup.php
        location_velo_wrt_vehicle_3x1 = np.array([[0.76], [0.0], [1.73]])  # according to the documentation
        pose_velo_wrt_vehicle_4x4 = utils.create_pose(utils.identity(3), location_velo_wrt_vehicle_3x1)
        vcd.add_stream(stream_name="VELO_TOP",
                       uri="",
                       description="Velodyne roof",
                       stream_type=core.StreamType.lidar)
        vcd.add_coordinate_system("VELO_TOP", cs_type=types.CoordinateSystemType.sensor_cs,
                                  parent_name="vehicle-iso8855",
                                  pose_wrt_parent=types.PoseData(
                                      val=list(pose_velo_wrt_vehicle_4x4.flatten()),
                                      type=types.TransformDataType.matrix_4x4)
                                  )
        #########################################
        # CREATE SENSORS coordinate system: GPS/IMU
        #########################################
        # Let's build also the pose of the imu
        location_imu_wrt_vehicle_4x4 = np.array([[-0.05], [0.32], [0.93]])  # according to documentation
        pose_imu_wrt_vehicle_4x4 = utils.create_pose(utils.identity(3), location_imu_wrt_vehicle_4x4)
        vcd.add_stream(stream_name="IMU",
                       uri="",
                       description="GPS/IMU",
                       stream_type=core.StreamType.other)
        vcd.add_coordinate_system("IMU", cs_type=types.CoordinateSystemType.sensor_cs,
                                  parent_name="vehicle-iso8855",
                                  pose_wrt_parent=types.PoseData(
                                      val=list(pose_imu_wrt_vehicle_4x4.flatten()),
                                      type=types.TransformDataType.matrix_4x4)
                                  )

        #########################################
        # CREATE SENSORS coordinate system: CAM
        #########################################
        img_width_px = 1242
        img_height_px = 375  # these are rectified dimensions
        calib_matrices = {}
        for row in calib_reader:
            calib_matrices[row[0]] = [float(x) for x in row[1:] if
                                      len(x) > 0]  # filter out some spaces at the end of the row
        # From KITTI readme.txt:
        # To project a point from Velodyne coordinates into the left color image,
        # you can use this formula: x = P2 * R0_rect * Tr_velo_to_cam * y
        # For the right color image: x = P3 * R0_rect * Tr_velo_to_cam * y
        left_camera_K3x4 = np.reshape(calib_matrices["P2:"], (3, 4))
        right_camera_K3x4 = np.reshape(calib_matrices["P3:"], (3, 4))
        camera_rectification_3x3 = np.reshape(calib_matrices["R_rect"], (3, 3))

        transform_velo_to_camleft_3x4 = np.reshape(calib_matrices["Tr_velo_cam"], (3, 4))  # WRT to LEFT CAMERA ONLY
        camera_rectification_4x4 = np.vstack((np.hstack((camera_rectification_3x3, [[0], [0], [0]])), [0, 0, 0, 1]))
        transform_velo_to_camleft_4x4 = np.vstack((transform_velo_to_camleft_3x4, [0, 0, 0, 1]))
        transform_velo_to_camleft_4x4 = np.dot(camera_rectification_4x4,
                                               transform_velo_to_camleft_4x4)  # such that X_cam = transform_velo_to_cam_4x4 * X_velo
        pose_camleft_wrt_velo_4x4 = utils.inv(transform_velo_to_camleft_4x4)

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
                                  )
                                  )
        vcd.add_coordinate_system("CAM_LEFT", cs_type=types.CoordinateSystemType.sensor_cs,
                                  parent_name="VELO_TOP",
                                  pose_wrt_parent=types.PoseData(
                                      val=list(pose_camleft_wrt_velo_4x4.flatten()),
                                      type=types.TransformDataType.matrix_4x4)
                                  )

        # Virtually, cam_left and cam_right are defined as the same coordinate systems, so their scs are the same
        # But their projection matrices (3x4) include a right-most non-zero column which shifts 3d points when projected
        # into the images, that is why projecting from velodyne to left and right use the same "extrinsics", and just differ
        # in the usage of the "intrinsic" matrices P2 and P3
        # P2 and P3 might be decomposed so P2 = K2*T2 and P3=K3*T3, so T2 and T3 could host extrinsic information
        # while K2 and K3 could host the intrinsic information. This way, the pose of cam_left would be T2*R_rect*Tr_velo
        # However, such decomposition seems to be non-trivial.
        # x = P2 * R0_rect * Tr_velo_to_cam * y
        # x = P3 * R0_rect * Tr_velo_to_cam * y
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
                                  )
                                  )
        vcd.add_coordinate_system("CAM_RIGHT", cs_type=types.CoordinateSystemType.sensor_cs,
                                  parent_name="VELO_TOP",
                                  pose_wrt_parent=types.PoseData(
                                      val=list(pose_camleft_wrt_velo_4x4.flatten()),
                                      type=types.TransformDataType.matrix_4x4)
                                  )

        #########################################
        # Prepare SCL scripts to manage transforms
        #########################################
        scene = scl.Scene(vcd)

        #########################################
        # LABELS
        #########################################
        for row in object_reader:
            frameNum = int(row[0])
            #trackID = int(row[1]) + 1  # VCD can't handle negative ids
            trackID = int(row[1])
            #if trackID == 0:
            #    continue  # Let's ignore DontCare labels

            semantic_class = row[2]
            truncated = utils.float_2dec(float(row[3]))
            occluded = int(row[4])

            alpha = utils.float_2dec(float(row[5]))  # this is the observation angle (see cs_overview.pdf)

            left = utils.float_2dec(float(row[6]))
            top = utils.float_2dec(float(row[7]))
            width = utils.float_2dec(float(row[8]) - left)
            height = utils.float_2dec(float(row[9]) - top)

            if trackID == -1:  # This is DontCare, there are multiple boxes
                count = vcd.get_element_data_count_per_type(core.ElementType.object, trackID, types.ObjectDataType.bbox, frameNum)
                name_box = "box2D" + str(count)
            else:
                name_box = "box2D"
            bounding_box_left = types.bbox(name=name_box + "_left",
                                      val=(left + width/2, top + height/2, width, height),
                                      coordinate_system='CAM_LEFT')
            # see cs_overview.pdf
            dimH = utils.float_2dec(float(row[10]))
            dimW = utils.float_2dec(float(row[11]))
            dimL = utils.float_2dec(float(row[12]))

            locX = utils.float_2dec(float(row[13]))
            locY = utils.float_2dec(float(row[14]))
            locZ = utils.float_2dec(float(row[15]))

            rotY = utils.float_2dec(float(row[16]))

            # Note KITTI uses (h, w, l, x,  y,  z,  ry) for cuboids, in camera coordinates (X-to-right, Y-to-bottom, Z-to-front)
            # while in VCD    (x, y, z, rx, ry, rz, sx, sy, sz) is defined as a dextrogire system, centroid-based
            # NOTE: changing locY by locY + dimH/2 as VCD uses centroid and KITTI uses bottom face
            # NOTE: All in Camera coordinate system
            # NOTE: x = length, y = height, z = width because of convention in readme.txt
            # The reference point for the 3D bounding box for each object is centered on the
            # bottom face of the box. The corners of bounding box are computed as follows with
            # respect to the reference point and in the object coordinate system:
            # x_corners = [l/2, l/2, -l/2, -l/2,  l/2,  l/2, -l/2, -l/2]^T
            # y_corners = [0,   0,    0,    0,   -h,   -h,   -h,   -h  ]^T
            # z_corners = [w/2, -w/2, -w/2, w/2, w/2, -w/2, -w/2, w/2  ]^T
            # with l=length, h=height, and w=width.
            cuboid_vals = [utils.float_2dec(locX), utils.float_2dec(locY - dimH/2), utils.float_2dec(locZ),
                                       0, utils.float_2dec(rotY), 0,
                                       utils.float_2dec(dimL), utils.float_2dec(dimH), utils.float_2dec(dimW)]
            cuboid = types.cuboid(name="box3D",
                                  val=cuboid_vals,
                                  coordinate_system="CAM_LEFT")

            if not vcd.has(core.ElementType.object, str(trackID)):
                # First time
                if trackID >= 0:
                    vcd.add_object(name=semantic_class + str(trackID), semantic_type=semantic_class, uid=str(trackID), frame_value=frameNum)
                else:  # so this is for DontCare object
                    vcd.add_object(name=semantic_class, semantic_type=semantic_class, uid=str(trackID),
                                   frame_value=frameNum)

            vcd.add_object_data(str(trackID), bounding_box_left, frameNum)
            vcd.add_object_data(str(trackID), cuboid, frameNum)
            vcd.add_object_data(trackID, types.num(name="truncated", val=truncated), frameNum)
            vcd.add_object_data(trackID, types.num(name="occluded", val=occluded), frameNum)
            vcd.add_object_data(trackID, types.num(name="alpha", val=alpha), frameNum)

            
            # Adding CAM_RIGHT data: KITTI GT does not include these boxes explictly, but we can obtain them projecting from the 3D box
            # NOTE 1: cuboids are expressed with respect to the CAM_LEFT coordinate system
            # NOTE 2: (see above) CAM_LEFT and CAM_RIGHT are the same coordinate systems, they just differ in the intrinsics, therefore, no need to convert the 3D boxes
            # NOTE 3: Can't project DontCare objects as the 3D cuboids are absurd
            #cuboid_vals_right = scene.transform_cuboid(cuboid_vals, "CAM_LEFT", "CAM_RIGHT", frameNum)
            if trackID != -1:  # Don'tCare objects 
                points3d_4x8 = utils.generate_cuboid_points_ref_4x8(cuboid_vals)
                cam_right = scene.get_camera("CAM_RIGHT")
                points2d_4x8, idx_valid = cam_right.project_points3d(points3d_4x8)
                points2d_4x8_valid = points2d_4x8[:, idx_valid]
                bbox_right_vals = utils.bounding_rect(points2d_4x8_valid)

                bounding_box_right = types.bbox(name=name_box + '_right',
                                        val=bbox_right_vals,
                                        coordinate_system='CAM_RIGHT')

                vcd.add_object_data(str(trackID), bounding_box_right, frameNum)            
            

        #########################################
        # Ego-vehicle
        #########################################
        vcd.add_object(name="Egocar", semantic_type="Egocar", uid=str(-2))

        cuboid_ego = types.cuboid(name="box3D",
                                  val=(1.35, 0.0, 0.736,
                                       0.0, 0.0, 0.0,
                                       4.765, 1.82, 1.47),
                                  coordinate_system="vehicle-iso8855")
        vcd.add_object_data(str(-2), cuboid_ego)

        # Return
        return vcd


def convert_KITTI_tracking_to_VCD4():
    # Base paths
    kitti_tracking_base_path = "../../../../../data/kitti/tracking"
    kitti_tracking_output_vcd_path = "./etc"

    num = None  # use None for all

    # Create scenes
    kitti_parser = KITTI_Tracking_reader(kitti_tracking_base_path, num)

    # Draw/store scenes in VCD
    for count, key in enumerate(kitti_parser.vcds):
        # Store
        openlabel_version_name = "openlabel" + schema.openlabel_schema_version.replace(".", "")
        vcd_base_name = openlabel_version_name
        vcd_file_name = os.path.join(kitti_tracking_output_vcd_path,
                                     vcd_base_name + "_kitti_tracking_" + str(count).zfill(4) + ".json")
        print('Storing VCD file...' + vcd_file_name)
        kitti_parser.vcds[key].save(file_name=vcd_file_name)

        if count == 3:  # Save a copy of trace #003 to tests for further VCD tests
            vcd_file_name = os.path.join("../../tests/etc", vcd_base_name + "_kitti_tracking_" + str(count).zfill(4) + ".json")
            kitti_parser.vcds[key].save(file_name=vcd_file_name)


if __name__ == '__main__':
    print("Running " + os.path.basename(__file__))
    convert_KITTI_tracking_to_VCD4()

