"""
VCD (Video Content Description) library v4.1.0

Project website: http://vcd.vicomtech.org

Copyright (C) 2020, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.1.0.
VCD is distributed under MIT License. See LICENSE.

"""

from datetime import date, datetime
import unittest
import os
import sys
sys.path.insert(0, "..")
import vcd.core as core
import vcd.types as types


class TestBasic(unittest.TestCase):
    # Create several streams
    def test_create_streams_simple(self):
        # This example shows how to introduce Stream (Intrinsics, Extrinsics), Sync and Odometry information
        # Fully detailed examples will be introduced for specific datasets such as KITTI tracking and nuScenes

        vcd = core.VCD()
        vcd.add_stream(stream_name='Camera1',
                       uri='./somePath/someVideo1.mp4',
                       description='Description 1',
                       stream_type=core.StreamType.camera)
        vcd.add_stream(stream_name='Camera2',
                       uri='./somePath/someVideo2.mp4',
                       description='Description 2',
                       stream_type=core.StreamType.camera)
        # See schema.py for more details on Coordinate Systems
        vcd.add_stream_properties(stream_name="Camera1",
                                  intrinsics=types.IntrinsicsPinhole(
                                      width_px=640,
                                      height_px=480,
                                      camera_matrix_3x4=[1000.0, 0.0, 500.0, 0.0,
                                                         0.0, 1000.0, 500.0, 0.0,
                                                         0.0, 0.0, 1.0, 0.0],
                                      distortion_coeffs_1xN=None
                                  ),
                                  extrinsics=types.Extrinsics(
                                      pose_scs_wrt_lcs_4x4=[1.0, 0.0, 0.0, 0.0,
                                                            0.0, 1.0, 0.0, 0.0,
                                                            0.0, 0.0, 1.0, 0.0,
                                                            0.0, 0.0, 0.0, 1.0]
                                  )
                                  )
        # Sync info can be added as a shift between the master vcd frame count and each of the sensors
        # e.g. Camera2 may have started 3 frames after Camera1, therefore, to label Elements for Camera2, we can use
        # frame_shift=3 for Camera2
        vcd.add_stream_properties(stream_name="Camera2",
                                  intrinsics=types.IntrinsicsPinhole(
                                      width_px=640,
                                      height_px=480,
                                      camera_matrix_3x4=[1000.0, 0.0, 500.0, 0.0,
                                                         0.0, 1000.0, 500.0, 0.0,
                                                         0.0, 0.0, 1.0, 0.0],
                                      distortion_coeffs_1xN=None
                                  ),
                                  extrinsics=types.Extrinsics(
                                      pose_scs_wrt_lcs_4x4=[1.0, 0.0, 0.0, 0.0,
                                                            0.0, 1.0, 0.0, 0.0,
                                                            0.0, 0.0, 1.0, 0.0,
                                                            0.0, 0.0, 0.0, 1.0]
                                  ),
                                  stream_sync=types.StreamSync(
                                      frame_shift=3
                                  )
                                  )

        # Let's suppose we want to add a master timestamp coming from a GPS or LIDAR sensor
        # Let's create here some dummy timestamps
        t_start = datetime(year=2020, month=4, day=11, hour=12, minute=0, second=1)
        t_end = datetime(year=2020, month=4, day=11, hour=12, minute=0, second=31)
        t_diff = t_end - t_start
        steps = 10
        t_step = t_diff / steps
        t_data = [t_start + i*t_step for i in range(0, steps)]

        for frame_num, t in enumerate(t_data):
            vcd.add_frame_properties(frame_num=frame_num, timestamp=str(t))

        # Additionally, we may want to introduce timestamping, intrinsics and extrinsics specific for each Sensor
        # and for each frame, for increased detail
        for frame_num, t in enumerate(t_data):
            vcd.add_stream_properties(stream_name="Camera1",
                                      stream_sync=types.StreamSync(
                                        frame_vcd=frame_num,
                                        frame_stream=frame_num + 1,  # Camera1's frames are shifted wrt to master count
                                        timestamp_ISO8601=str(t)
                                      ), intrinsics=types.IntrinsicsPinhole(
                                          width_px=640,
                                          height_px=480,
                                          camera_matrix_3x4=[1001.0, 0.0, 500.0, 0.0,
                                                             0.0, 1001.0, 500.0, 0.0,
                                                             0.0, 0.0, 1.0, 0.0],
                                          distortion_coeffs_1xN=None
                                      ), extrinsics=types.Extrinsics(
                                          pose_scs_wrt_lcs_4x4=[1.0, 0.0, 0.0, 0.1,
                                                                0.0, 1.0, 0.0, 0.1,
                                                                0.0, 0.0, 1.0, 0.0,
                                                                0.0, 0.0, 0.0, 1.0]
                                      )
                                      )

        # Odometry information is also included as frame_properties
        # Odometry must be provided as pose_lcs_wrt_wcs (i.e. Local Coordinate System wrt World Coordinate System)
        # in the form of pose 4x4 matrices.
        # As additional properties you can include raw GPS/IMU for instance
        vcd.add_odometry(frame_num=6, odometry=types.Odometry(
            pose_lcs_wrt_wcs_4x4=[1.0, 0.0, 0.0, 20.0,
                                  0.0, 1.0, 0.0, 20.0,
                                  0.0, 0.0, 1.0, 0.0,
                                  0.0, 0.0, 0.0, 1.0],
            raw_gps_data=[49.011212804408, 8.4228850417969, 112.83492279053, 0.022447,1e-05,
                                                   -1.2219096732051, -3.3256321640686, 1.1384311814592, 3.5147680214713,
                                                   0.037625160413037, -0.03878884255623, -0.29437452763793,
                                                   0.037166856911681, 9.9957015129717, -0.30581030960531,
                                                   -0.19635662515203, 9.9942128010936, -0.017332142869546,
                                                   0.024792163815438, 0.14511808479348, -0.017498934149631,
                                                   0.021393359392165, 0.14563031426063, 0.49229361157748,
                                                   0.068883960397178, 4, 10, 4, 4, 0],
            status="interpolated",  # we can add any thing (it is permitted by VCD schema)
        ))

        if not os.path.isfile('./etc/test_stream_frame_properties.json'):
            vcd.save('./etc/test_stream_frame_properties.json', True)

        vcd_read = core.VCD('./etc/test_stream_frame_properties.json', validation=True)
        self.assertEqual(vcd_read.stringify(), vcd.stringify())


if __name__ == '__main__':  # This changes the command-line entry point to call unittest.main()
    print("Running " + os.path.basename(__file__))

    unittest.main()