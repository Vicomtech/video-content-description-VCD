"""
VCD (Video Content Description) library v4.2.0

Project website: http://vcd.vicomtech.org

Copyright (C) 2020, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.2.0.
VCD is distributed under MIT License. See LICENSE.

"""


import warnings
import numpy as np
from enum import Enum

####################################################
# Frame intervals
####################################################
def intersects(fi_a, fi_b):
    max_start_val = max(fi_a['frame_start'], fi_b['frame_start'])
    min_end_val = min(fi_a['frame_end'], fi_b['frame_end'])
    return max_start_val <= min_end_val


def consecutive(fi_a, fi_b):
    if fi_a['frame_end'] + 1 == fi_b['frame_start'] or fi_b['frame_end'] + 1 == fi_a['frame_start']:
        return True
    else:
        return False


def is_inside(frame_num, frame_interval):
    return frame_interval['frame_start'] <= frame_num <= frame_interval['frame_end']


def get_outer_frame_interval(frame_intervals):
    outer = None
    for fi in frame_intervals:
        if outer is None:
            outer = fi
        else:
            if fi['frame_start'] < outer['frame_start']:
                outer['frame_start'] = fi['frame_start']
            if fi['frame_end'] > outer['frame_end']:
                outer['frame_end'] = fi['frame_end']
    return outer


def as_frame_interval_dict(frame_value):
    if isinstance(frame_value, int):
        return {'frame_start': frame_value, 'frame_end': frame_value}
    elif isinstance(frame_value, tuple):
        return {'frame_start': frame_value[0], 'frame_end': frame_value[1]}
    else:
        warnings.warn("WARNING: trying to convert into frame interval dict a: " + type(frame_value))


def as_frame_intervals_array_dict(frame_value):
    # Allow for multiple type of frame_interval arguments (int, tuple, list(tuple))
    frame_intervals_array_of_dict = []
    if isinstance(frame_value, int):  # The user has given as argument a "frame number"
        frame_intervals_array_of_dict = [{'frame_start': frame_value, 'frame_end': frame_value}]
    elif isinstance(frame_value, tuple):  # The user has given as argument a single "frame interval"
        frame_intervals_array_of_dict = [{'frame_start': frame_value[0], 'frame_end': frame_value[1]}]
    elif frame_value is None:  # The user has provided nothing: this is a static element
        frame_intervals_array_of_dict = []
    else:
        assert isinstance(frame_value, list)  # User provides a list of "frame intervals" tuples
        for frame_interval in frame_value:
            if 'frame_start' in frame_interval:
                # User provided already a dict
                frame_intervals_array_of_dict = frame_value
                break
            else:
                # User provided tuples of numbers
                frame_intervals_array_of_dict.append({'frame_start': frame_interval[0], 'frame_end': frame_interval[1]})

    return frame_intervals_array_of_dict


def as_frame_intervals_array_tuples(frame_intervals_array_of_dict):
    assert isinstance(frame_intervals_array_of_dict, list)
    fi_tuples = []
    for fi_dict in frame_intervals_array_of_dict:
        assert 'frame_start' in fi_dict
        assert 'frame_end' in fi_dict
        fi_tuples.append((fi_dict['frame_start'], fi_dict['frame_end']))
    return fi_tuples

def fuse_frame_interval_dict(frame_interval, frame_intervals):
    # This function inserts frame_interval into frame_intervals fusing intervals
    assert(isinstance(frame_interval, dict))
    assert (isinstance(frame_intervals, list))
    if len(frame_intervals) == 0:
        return [frame_interval]

    frame_intervals_to_return = frame_intervals
    idx_to_fuse = []  # idx of frame_intervals of the list
    for idx, fi in enumerate(frame_intervals):
        if intersects(fi, frame_interval) or consecutive(fi, frame_interval):
            idx_to_fuse.append(idx)
    if len(idx_to_fuse) == 0:
        # New frame interval, separated, just append
        frame_intervals_to_return.append(frame_interval)
    else:
        # New frame interval has caused some fusion
        frame_intervals_to_return = []
        fused_fi = frame_interval
        for idx, fi in enumerate(frame_intervals):
            if idx in idx_to_fuse:
                fused_fi = {
                    'frame_start': min(fused_fi['frame_start'], fi['frame_start']),
                    'frame_end': max(fused_fi['frame_end'], fi['frame_end'])
                }
            else:
                # also add those not affected by fusion
                frame_intervals_to_return.append(fi)
        frame_intervals_to_return.append(fused_fi)

    return frame_intervals_to_return


def fuse_frame_intervals(frame_intervals):
    # This functions receives a list of frame_intervals and returns another one with
    # non-overlapping intervals
    # e.g. input: [(0, 5), (3, 6), (8, 10)]
    #      output:[(0, 6), (8, 10)]
    assert(isinstance(frame_intervals, list))
    num_fis = len(frame_intervals)

    if num_fis == 1:
        return frame_intervals

    # Read first element
    frame_intervals_fused = [frame_intervals[0]]
    i = 1
    while i < num_fis:
        frame_intervals_fused = fuse_frame_interval_dict(frame_intervals[i], frame_intervals_fused)
        i += 1
    return frame_intervals_fused


####################################################
# ROTATION AND ODOMETRY UTILS. See SCL library
####################################################
def create_pose(R, C):
    # Under SCL principles, P = (R C; 0 0 0 1), while T = (R^T -R^TC; 0 0 0 1)
    temp = np.hstack((R, C))
    P = np.vstack((temp, np.array([0, 0, 0, 1])))  # P is 4x4
    return P


def inv(m):
    if m.ndim == 2:  # just an inversion of a square matrix
        return np.linalg.inv(m)
    else:
        assert(m.ndim == 3)  # so batch for N matrices
        m_inv = np.zeros(m.shape, dtype=m.dtype)
        n = m.shape[2]
        for i in range(0, n):
            m_inv[:, :, i] = np.linalg.inv(m[:, :, i])
        return m_inv


def lat_to_scale(lat):
    # Computes mercator scale from latitude
    scale = np.cos(lat*np.pi / 180.0)
    return scale


def latlon_to_mercator(lat, lon, scale):
    # Converts lat/lon coordinates to mercator coordinates using mercator scale
    er = 6378137  # this seems to be the Earth Radius in meters
    mx = scale * lon * np.pi * er / 180.0
    my = scale * er * np.log(np.tan((90+lat) * np.pi / 360))
    return mx, my


class EulerSeq(Enum):
    # https://en.wikipedia.org/wiki/Euler_angles
    ZXZ = 1
    XYX = 2
    YZY = 3
    ZYZ = 4
    XZX = 5
    YXY = 6

    XYZ = 7
    YZX = 8
    ZXY = 9
    XZY = 10
    ZYX = 11  # yaw, pitch, roll (in that order)
    YXZ = 12


def isR(R):
    assert (R.shape == (3, 3))
    Rt = np.transpose(R)
    I_ = np.dot(Rt, R)
    I = np.identity(3, dtype=R.dtype)
    n = np.linalg.norm(I - I_)
    return n < 1e-4


def Rx(angle_rad):
    return np.array([[1, 0, 0],
                    [0, np.cos(angle_rad), -np.sin(angle_rad)],
                    [0, np.sin(angle_rad), np.cos(angle_rad)]
                    ])


def Ry(angle_rad):
    return np.array([[np.cos(angle_rad), 0, np.sin(angle_rad)],
                    [0, 1, 0],
                    [-np.sin(angle_rad), 0, np.cos(angle_rad)]
                    ])


def Rz(angle_rad):
    return np.array([[np.cos(angle_rad), -np.sin(angle_rad), 0],
                    [np.sin(angle_rad), np.cos(angle_rad), 0],
                    [0, 0, 1]
                    ])


def euler2R(a, seq=EulerSeq.ZYX):
    # Proper or improper Euler angles to R
    # Assuming right-hand rotation and radians
    assert(isinstance(a, list))
    assert(len(a) == 3)
    assert(isinstance(seq, EulerSeq))

    # The user introduces 3 angles a=(a[0], a[1], a[2]), and a sequence, e.g. "ZYX"
    # 0, 1 and 2 are identified with XYZ according to the code
    if seq.name[0] == "X":
        R_0 = Rx(a[0])
    elif seq.name[0] == "Y":
        R_0 = Ry(a[0])
    else:
        R_0 = Rz(a[0])

    if seq.name[1] == "X":
        R_1 = Rx(a[1])
    elif seq.name[1] == "Y":
        R_1 = Ry(a[1])
    else:
        R_1 = Rz(a[1])

    if seq.name[2] == "X":
        R_2 = Rx(a[2])
    elif seq.name[2] == "Y":
        R_2 = Ry(a[2])
    else:
        R_2 = Rz(a[2])

    # Using here reverse composition, as this Rotation matrix is built to describe
    # a pose matrix, which encodes the rotation and position of a coordinate system
    # with respect to another.
    # To transform points from origin to destination coordinate systems, the R^T is used
    # which then swaps the order of the sequence to the expected order.
    # NOTE: this formula cannot be applied if the rotation matrix is used to rotate points (active-alibi
    # rotation), instead of rotating coordinate systems (passive-alias rotation)
    R = np.dot(R_0, np.dot(R_1, R_2))

    assert (isR(R))

    return R


def convert_oxts_to_pose(oxts):
    # With a cup of coffee, read:
    # https://support.oxts.com/hc/en-us/articles/115002859149-OxTS-Reference-Frames-and-ISO8855-Reference-Frames#R2

    # This code is a Python version from code in KITTI
    # dev kit (file convertOxtsToPose.m)

    # Converts oxts entries into metric pose,
    # starting at (0,0,0) meters, OXTS coordinates are defined as
    # x = forward, y = right, z = down (see OXTS RT3000 user manual)
    # afterwards, the pose contains the transformation which takes a
    # 3D point in the i'th frame and projecs it into the oxts coordinates
    # of the first frame

    assert(isinstance(oxts, list))

    # Compute scale from first lat value
    lat = oxts[0][0]
    scale = lat_to_scale(lat)

    # Init pose
    poses = []
    Tr_0_inv = None
    transform_wcs_to_geo_4x4 = None

    # For all oxts packets do:
    for oxts_packet in oxts:
        # Translation vector
        lon_utm, lat_utm = latlon_to_mercator(oxts_packet[0], oxts_packet[1], scale)
        alt = oxts_packet[2]

        # Rotation matrix (OXTS RT3000 user manual, page 71/92)
        rx = oxts_packet[3]  # roll
        ry = oxts_packet[4]  # pitch
        rz = oxts_packet[5]  # heading

        rotation_lcs_wrt_geo_3x3 = euler2R([rz, ry, rx])
        location_lcs_wrt_geo_3x1 = np.array([[lon_utm, lat_utm, alt]]).T
        pose_lcs_wrt_geo_4x4 = create_pose(rotation_lcs_wrt_geo_3x3, location_lcs_wrt_geo_3x1)
        transform_geo_to_lcs_4x4 = inv(pose_lcs_wrt_geo_4x4)

        # debug test: check location of lcs expressed in lcs coordinates. Should be zero
        #location_lcs_wrt_geo_4x1 = np.vstack((location_lcs_wrt_geo_3x1, np.array([[1.0]])))
        #location_lcs_wrt_lcs = np.dot(transform_geo_to_lcs_4x4, location_lcs_wrt_geo_4x1)

        if transform_wcs_to_geo_4x4 is None:
            # First entry, let's create wcs as (0,0,0) at the position of lcs
            transform_wcs_to_geo_4x4 = inv(transform_geo_to_lcs_4x4)

        # So this is Identity for the first instant
        transform_wcs_to_lcs_4x4 = np.dot(transform_geo_to_lcs_4x4, transform_wcs_to_geo_4x4)
        pose_lcs_wrt_wcs_4x4 = inv(transform_wcs_to_lcs_4x4)
        poses.append(pose_lcs_wrt_wcs_4x4)


    # Convert to 4x4xN
    n = len(poses)
    poses_4x4xN = np.zeros((4, 4, n), dtype=np.float)

    for count, pose in enumerate(poses):
        poses_4x4xN[:, :, count] = pose

    return poses_4x4xN


def float_2dec(val):
    '''
    This function is useful to print float into JSON with only 2 decimals
    '''
    return float((int(100*val))/100)


def get_key(my_dict, val):
    for key, value in my_dict.items():
        if val == value:
            return key

    return "key doesn't exist"

