"""
VCD (Video Content Description) library v4.3.1

Project website: http://vcd.vicomtech.org

Copyright (C) 2021, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.3.1.
VCD is distributed under MIT License. See LICENSE.

"""


import os
import sys
sys.path.insert(0, "..")
import screeninfo
import cv2 as cv
import numpy as np
import math
from vcd import core
from vcd import draw

# TODO

def draw_nuscenes(scene_token):
    # Get annotations
    vcd_file_name = "../converters/nuScenesConverter/vcd_files/vcd_nuscenes_" + scene_token + ".json"
    vcd = core.VCD(vcd_file_name)

    vcd_new = convertnuScenesFromQuaternionToCuboid(vcd)

    drawerTopView = draw.TopView(vcd_new)

    # Read frame information
    fis = vcd.get_frame_intervals()
    frame_start = fis[0]['frame_start']
    frame_end = fis[-1]['frame_end']

    # Prepare color map
    topviewParams = draw.TopView.Params(_imgSize=(2000, 1000),
                                        _rangeX=(1400, 1800),
                                        _rangeY=(1200, 1400))

    # Prepare window
    screen = screeninfo.get_monitors()[0]
    cv.namedWindow('nuScenes ' + scene_token, cv.WINDOW_NORMAL)
    cv.moveWindow('nuScenes ' + scene_token, screen.x + screen.width // 8, screen.y + screen.height // 8)
    cv.resizeWindow('nuScenes ' + scene_token, (int(3 * screen.width / 4), int(3 * screen.height / 4)))

    for frame_num in range(frame_start, frame_end+1):
        topView = drawerTopView.draw(frame_num, _params=topviewParams)
        cv.imshow('nuScenes ' + scene_token, topView)
        cv.waitKey(0)

def quaternion_to_euler(w, x, y, z):
    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + y * y)
    roll = math.atan2(t0, t1)
    t2 = +2.0 * (w * y - z * x)
    t2 = +1.0 if t2 > +1.0 else t2
    t2 = -1.0 if t2 < -1.0 else t2
    pitch = math.asin(t2)
    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (y * y + z * z)
    yaw = math.atan2(t3, t4)
    return roll, pitch, yaw

def convertnuScenesFromQuaternionToCuboid(vcd):
    assert(isinstance(vcd, core.VCD))
    vcd_new = vcd
    fis = vcd_new.get_frame_intervals()
    for fi in fis:
        for frame_num in range(fi['frame_start'], fi['frame_end'] + 1):
            frame = vcd_new.data['vcd']['frames'][frame_num]

            # Read object data
            for object_uid, object in frame['objects'].items():
                od = object['object_data']
                pos3d = [0, 0, 0]
                size3d = [0, 0, 0]
                quaternion = [0, 0, 0, 0]

                for od_k, od_v in od.items():
                    if od_k == "point3d":
                        if od_v[0]['name'] == "translation":
                            pos3d = od_v[0]['val']
                    elif od_k == "vec":
                        for vec in od_v:
                            if vec['name'] == "size":
                                size3d = vec['val']
                            elif vec['name'] == "rotation":
                                quaternion = vec['val']

                rx, ry, rz = quaternion_to_euler(quaternion[0],
                                                 quaternion[1],
                                                 quaternion[2],
                                                 quaternion[3])

                cuboid = [pos3d[0], pos3d[1], pos3d[2], rx, ry, rz, size3d[0], size3d[1], size3d[2]]
                del od['point3d']
                del od['vec']

                od['cuboid'] = [{"name": "cuboid3d", "val": cuboid}]

    return vcd_new

if __name__ == "__main__":
    print("Running " + os.path.basename(__file__))
    draw_nuscenes(scene_token="0ac05652a4c44374998be876ba5cd6fd")

