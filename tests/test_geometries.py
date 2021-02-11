"""
VCD (Video Content Description) library v4.3.1

Project website: http://vcd.vicomtech.org

Copyright (C) 2021, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.3.1.
VCD is distributed under MIT License. See LICENSE.

"""

import unittest
import os
import numpy as np
import vcd.core as core
import vcd.schema as schema
import vcd.types as types
import vcd.utils as utils

vcd_version_name = "vcd" + schema.vcd_schema_version.replace(".", "")

overwrite = True


def check_vcd(vcd, vcd_file_name, force_write=False):
    if not os.path.isfile(vcd_file_name) or force_write:
        vcd.save(vcd_file_name)

    vcd_read = core.VCD(vcd_file_name, validation=True)
    return vcd_read.stringify() == vcd.stringify()


class TestBasic(unittest.TestCase):
    def test_intrinsics(self):
        # This tests aims to demonstrate that different intrinsics structures
        # can be used at VCD, including standard intrinsic_pinhole, intrinsic_fisheye,
        # a custom format for user-defined structures

        # Base VCD object
        vcd = core.VCD()

        # Custom instrinsics
        vcd.add_stream(stream_name="CAM_CUSTOM",
                       uri="",
                       description="Camera custom",
                       stream_type=core.StreamType.camera)

        vcd.add_stream_properties(stream_name="CAM_CUSTOM",
                                  intrinsics=types.IntrinsicsCustom(
                                      custom_property1="Some text1",
                                      custom_property2=1200.0,
                                      custom_property3=[100.0, 100.0]
                                  )
                                  )

        # Pinhole intrinsics (additional properties are also valid)
        vcd.add_stream(stream_name="CAM_PINHOLE",
                       uri="",
                       description="Camera pinhole",
                       stream_type=core.StreamType.camera)

        vcd.add_stream_properties(stream_name="CAM_PINHOLE",
                                  intrinsics=types.IntrinsicsPinhole(
                                      width_px=640,
                                      height_px=480,
                                      camera_matrix_3x4=[1000.0, 0.0, 500.0, 0.0,
                                                         0.0, 1000.0, 500.0, 0.0,
                                                         0.0, 0.0, 1.0, 0.0],
                                      distortion_coeffs_1xN=None,
                                      custom_property1=0.99
                                  )
                                  )
        # Pinhole intrinsics (additional properties are valid and none are mandatory)
        vcd.add_stream(stream_name="CAM_FISHEYE",
                       uri="",
                       description="Camera fisheye",
                       stream_type=core.StreamType.camera)

        vcd.add_stream_properties(stream_name="CAM_FISHEYE",
                                  intrinsics=types.IntrinsicsFisheye(
                                      width_px=1280,
                                      height_px=1080,
                                      lens_coeffs_1x4=[333.437012, 0.307729989, 2.4235599, 11.0495005],
                                      center_x=0.0,
                                      center_y=0.0,
                                      fov_deg=None,
                                      radius_x=0.0,
                                      radius_y=0.0,
                                      custom_property1=0.0
                                  )
                                  )

        # Compare with reference
        self.assertTrue(check_vcd(vcd, './etc/' + vcd_version_name + '_test_intrinsics.json', overwrite))

    def test_poses(self):
        # This test aims to show how to create and add extrinsic information of streams
        # In particular, how different pose formats can be used (e.g. matrix, or list of values)

        # Base VCD object
        vcd = core.VCD()

        # Create reference, base or local coordinate system
        vcd.add_coordinate_system(name="base", cs_type=types.CoordinateSystemType.local_cs)

        # Create camera 1 and compose a pose as a 4x4 matrix, using utils from VCD
        vcd.add_stream(stream_name="CAM_1",
                       uri="",
                       description="Camera 1",
                       stream_type=core.StreamType.camera)
        pitch_rad = (10.0 * np.pi) / 180.0
        yaw_rad = (0.0 * np.pi) / 180.0
        roll_rad = (0.0 * np.pi) / 180.0
        R_scs_wrt_lcs = utils.euler2R([yaw_rad, pitch_rad, roll_rad])  # default is ZYX
        C_lcs = np.array([[2.3],  # frontal part of the car
                          [0.0],  # centered in the symmetry axis of the car
                          [1.3]])  # at some height over the ground

        P_scs_wrt_lcs = utils.create_pose(R_scs_wrt_lcs, C_lcs)
        vcd.add_coordinate_system("CAM_1", cs_type=types.CoordinateSystemType.sensor_cs,
                                  parent_name="base",
                                  pose_wrt_parent=list(P_scs_wrt_lcs.flatten()))

        # Create camera 2 and add rotation and translation instead of pose
        vcd.add_stream(stream_name="CAM_2",
                       uri="",
                       description="Camera 2",
                       stream_type=core.StreamType.camera)

        vcd.add_coordinate_system("CAM_2", cs_type=types.CoordinateSystemType.sensor_cs,
                                  parent_name="base",
                                  pose=types.Pose(
                                      reference_name="base",
                                      subject_name="CAM_2",
                                      rotation=[pitch_rad, yaw_rad, roll_rad],
                                      traslation=list(C_lcs.flatten())
                                  )
                                  )
        # Compare with reference
        self.assertTrue(check_vcd(vcd, './etc/' + vcd_version_name + '_test_poses.json', overwrite))

    def test_transforms(self):
        # Transforms are the same as Poses, but applied for a given frame
        # Base VCD object
        vcd = core.VCD()

        # Create reference, base or local coordinate system
        vcd.add_coordinate_system(name="base", cs_type=types.CoordinateSystemType.local_cs)
        vcd.add_coordinate_system(name="world", cs_type=types.CoordinateSystemType.scene_cs)

        # Odometry entries would be like this:
        vcd.add_transform(frame_num=10, transform=types.Transform(
            src_name="base",
            dst_name="world",
            transform_src_to_dst_4x4=[1.0, 0.0, 0.0, 0.1,
                                      0.0, 1.0, 0.0, 0.1,
                                      0.0, 0.0, 1.0, 0.0,
                                      0.0, 0.0, 0.0, 1.0]))

        # Nevertheless, in VCD 4.3.2 it is possible to customize the format of the transform
        vcd.add_transform(frame_num=11, transform=types.Transform(
            src_name="base",
            dst_name="world",
            rotation=[0.0, 0.0, 0.0],
            traslation=[1.0, 1.0, 0.0],
            custom_property1=0.9,
            custom_property2="Some tag"
        ))

        # Compare with reference
        self.assertTrue(check_vcd(vcd, './etc/' + vcd_version_name + '_test_transforms.json', overwrite))


if __name__ == '__main__':  # This changes the command-line entry point to call unittest.main()
    print("Running " + os.path.basename(__file__))
    unittest.main()

