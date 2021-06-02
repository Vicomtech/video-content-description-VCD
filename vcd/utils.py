"""
VCD (Video Content Description) library v4.3.1

Project website: http://vcd.vicomtech.org

Copyright (C) 2021, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.3.1.
VCD is distributed under MIT License. See LICENSE.

"""

import warnings
import numpy as np
import cv2 as cv
import base64
import math
from bisect import bisect_left
from enum import Enum

####################################################
# Frame intervals
####################################################
def intersection_between_frame_interval_arrays(fisA, fisB):
    assert (isinstance(fisA, list))
    assert (isinstance(fisB, list))
    fis_int = []
    for fiA in fisA:
        assert(isinstance(fiA, tuple))
        for fiB in fisB:
            assert(isinstance(fiB, tuple))
            fi_int = intersection_between_frame_intervals(fiA, fiB)
            if fi_int is not None:
                fis_int.append(fi_int)
    return fis_int


def intersection_between_frame_intervals(fiA, fiB):
    max_start_val = max(fiA[0], fiB[0])
    min_end_val = min(fiA[1], fiB[1])

    if max_start_val <= min_end_val:
        return [max_start_val, min_end_val]
    else:
        return None


def intersects(fi_a, fi_b):
    max_start_val = max(fi_a['frame_start'], fi_b['frame_start'])
    min_end_val = min(fi_a['frame_end'], fi_b['frame_end'])
    return max_start_val <= min_end_val


def consecutive(fi_a, fi_b):
    if fi_a['frame_end'] + 1 == fi_b['frame_start'] or fi_b['frame_end'] + 1 == fi_a['frame_start']:
        return True
    else:
        return False


def is_inside_frame_intervals(frame_num, frame_intervals):
    for fi in frame_intervals:
        if is_inside_frame_interval(frame_num, fi):
            return True
    return False


def is_inside_frame_interval(frame_num, frame_interval):
    return frame_interval[0] <= frame_num <= frame_interval[1]


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


def frame_interval_is_inside(frame_intervals_a, frame_intervals_b):
    assert(isinstance(frame_intervals_a, list))
    assert (isinstance(frame_intervals_b, list))

    all_inside = True
    for fi_a in frame_intervals_a:
        inside = False
        for fi_b in frame_intervals_b:
            if fi_a[0] >= fi_b[0] and fi_a[1] <= fi_b[1]:
                inside = True
                break
        if not inside:
            all_inside = False
            break

    return all_inside


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
    # e.g.input: [{'frame_start': 0, 'frame_end': 5}, {'frame_start': 3, 'frame_end': 6},
    #               {'frame_start': 8, 'frame_end': 10}]
    # output: [{'frame_start': 0, 'frame_end': 6}, {'frame_start': 8, 'frame_end': 10}]

    assert(isinstance(frame_intervals, list))
    num_fis = len(frame_intervals)

    if num_fis == 0:
        return []

    if num_fis == 1:
        return frame_intervals

    # Read first element
    frame_intervals_fused = [frame_intervals[0]]
    i = 1
    while i < num_fis:
        frame_intervals_fused = fuse_frame_interval_dict(frame_intervals[i], frame_intervals_fused)
        i += 1

    frame_intervals_fused_sorted = sort_frame_intervals(frame_intervals_fused)
    return frame_intervals_fused_sorted


def get_frame_start(a):
    return a['frame_start']


def sort_frame_intervals(frame_intervals):
    # This function assumes frame intervals have already been fused, otherwise, there might be problems
    frame_intervals.sort(key=get_frame_start)
    return frame_intervals


def rm_frame_from_frame_intervals(frame_intervals, frame_num):
    fi_dict_new = []
    for fi in frame_intervals:
        if frame_num < fi['frame_start']:
            fi_dict_new.append(fi)
            continue
        if frame_num == fi['frame_start']:
            # Start frame, just remove it
            if fi['frame_end'] > frame_num:
                fi_dict_new.append({'frame_start': frame_num + 1, 'frame_end': fi['frame_end']})
                continue
            else:
                # So, we are removing 4 from [(4, 4)], let's return empty
                continue
        elif frame_num < fi['frame_end']:
            # Inside! Need to split
            for f in range(fi['frame_start'], fi['frame_end'] + 1):
                if f == frame_num:
                    fi_dict_new.append({'frame_start': fi['frame_start'], 'frame_end': frame_num - 1})
                    fi_dict_new.append({'frame_start': frame_num + 1, 'frame_end': fi['frame_end']})
        elif frame_num == fi['frame_end']:
            # End frame just remove it
            # no need to check if fi['frame_start'] > frame_num backwards as we are in the else if
            fi_dict_new.append({'frame_start': fi['frame_start'], 'frame_end': frame_num - 1})
        else:
            fi_dict_new.append(fi)
    return fi_dict_new


####################################################
# ROTATION AND ODOMETRY UTILS
####################################################
def create_pose(R, C):
    # Under SCL principles, P = (R C; 0 0 0 1), while T = (R^T -R^TC; 0 0 0 1)
    if C.shape[0] == 3:
        temp = np.hstack((R, C))
    elif C.shape[0] == 4:
        C = C[0:3, :]
        temp = np.hstack((R, C))
    P = np.vstack((temp, np.array([0, 0, 0, 1])))  # P is 4x4
    return P


def decompose_pose(pose_4x4):
    rotation_3x3 = pose_4x4[0:3, 0:3]
    c_3x1 = pose_4x4[0:3, 3]
    return rotation_3x3, c_3x1


def interpolate_pose(poses_dict, timestamp):
    # Find two adjacent poses between the provided timestamp
    keys = list(poses_dict.keys())

    # Returns the position where to insert x in list a, assuming it is sorted
    # if return 0, x is the smallest value (can't interpolate)
    # if return len(a), x is the largest value (can't interpolate)
    pos = bisect_left(keys, timestamp)

    if pos == 0:
        # The provided timestamp is the smallest value
        return None
    elif pos == len(keys):
        # The provided timestamp is the largest value
        return None
    else:
        pose_prev = poses_dict[keys[pos - 1]]
        pose_next = poses_dict[keys[pos]]
        diff_pose_between = pose_next - pose_prev
        time_between = keys[pos] - keys[pos - 1]
        time_dist = timestamp - keys[pos - 1]
        time_factor = time_dist / time_between
        diff_pose = diff_pose_between.dot(time_factor)
        pose_interpolated = pose_prev + diff_pose
    return pose_interpolated


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


def identity(dim):
    return np.identity(dim, dtype=float)


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


def R2rvec(R):
    assert(isR(R))
    sy = np.sqrt(R[0, 0] * R[0, 0] + R[1, 0] * R[1, 0])
    singular = sy < 1e-6

    if not singular:
        rx = np.arctan2(R[2, 1], R[2, 2])
        ry = np.arctan2(-R[2, 0], sy)
        rz = np.arctan2(R[1, 0], R[0, 0])
    else:
        rx = np.arctan2(-R[1, 2], R[1, 1])
        ry = np.arctan2(-R[2, 0], sy)
        rz = 0

    return np.array([[rx], [ry], [rz]])


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

    # The user introduces 3 angles a=(a[0], a[1], a[2]), and a meaning, e.g. "ZYX"
    # So we can build the Rx, Ry, Rz according to the specified code

    # e.g. a=(0.1, 0.3, 0.2), seq='ZYX', then R0=Rx(0.1), R1=Ry(0.3), R2=Rz(0.2)
    # The application of the rotations in this function is
    # R = R0*R1*R2, which must be read from right-to-left
    # So first R2 is applied, then R1, then R0
    # If the default 'zyx' sequence is selected, the user is providing a=(rz, ry, rx), and it is applied R=RZ*RY*RX

    # e.g. a=(0.1, 0.4, 0.2), seq='xzz')
    # R = Rx(0.1)*Rz(0.4)*Rz(0.2)

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


def get_point3d_of_plane(plane):
    # Provided a plane (a, b, c, d), obtain a point that belongs to the plane
    a, b, c, d = plane
    if a != 0:
        return np.array([[-d / a, 0, 0, 1]]).transpose()
    elif b!= 0:
        return np.array([[0, -d / b, 0, 1]]).transpose()
    elif c != 0:
        return np.array([[0, 0, -d / c, 1]]).transpose()
    else:
        return None


####################################################
# Projections
####################################################
def homography_from_pose(K_3x4, P_4x4, dim_zero=2):
    # dim_zero can be 0, 1 or 2, meaning X, Y or Z
    # For instance, dim_zero=0, means Z=0, so we can null the third column of the Pose
    KP = K_3x4.dot(P_4x4)
    H = np.delete(KP, dim_zero, 1)
    return H


def fromPinholeParamsToCameraMatrix3x4(fx, fy, cx, cy):
    matrix3x4 = [[fx, 0.0, cx, 0.0],
                 [0.0, fy, cy, 0.0],
                 [0.0, 0.0, 1.0, 0.0]]
    return matrix3x4


def fromCameraMatrix3x3toCameraMatrix3x4(camera_matrix_3x3):
    matrix3x4 = np.hstack((camera_matrix_3x3, [[0], [0], [0]]))
    return matrix3x4


def fromCameraMatrix3x4toCameraMatrix3x3(camera_matrix_3x4):
    matrix3x3 = camera_matrix_3x4[:, 0:3]
    return matrix3x3


def round(number_float):
    return int(np.round(number_float))


def norm(ray):
    return math.sqrt(ray[0]*ray[0] + ray[1]*ray[1])


####################################################
# RADIAL DISTORTION
####################################################
def get_distortion_radius(distortion):
    # Next equations work only if p1=p2=p3=0 and k4=k5=k6=0
    # See https://www.wolframalpha.com/input/?i=resolve+1%2B2k_1x%2B3k_2x%5E2%2B4k_3x%5E3%3D0
    if len(distortion) == 8:
        return None

    k1 = distortion[0, 0]
    k2 = distortion[0, 1]
    p1 = distortion[0, 2]
    p2 = distortion[0, 3]
    k3 = distortion[0, 4]
    if p1 == 0 and p2 == 0:
        aux0 = -54*(k2**3) + 216*k1*k2*k3 - 432*(k3**2)
        aux1 = 4*(24*k1*k3-9*(k2**2))**3 + aux0*aux0
        if aux1 < 0:
            return None
        aux2 = aux0 + np.sqrt(aux1)
        aux3 = -k2/(4*k3) + (1/(15.11905*k3)) * (aux2**(1/3))
        aux4 = (24*k1*k3-9*(k2**2))/(9.524406*k3*(aux2**(1/3)))

        r2 = aux3 - aux4

        if r2 < 0:
            return None
        else:
            r = np.sqrt(r2)
            return r
    else:
        return None


####################################################
# Transforms
####################################################
def apply_transform(transform_JxM, data_MxN):
    # e.g. K_3x3, points_3xN
    J = transform_JxM.shape[0]
    N = data_MxN.shape[1]
    assert(transform_JxM.shape[1] == data_MxN.shape[0])
    data_out = transform_JxM.dot(data_MxN)  # output is JxN
    data_out[:, N] /= data_out[J-1, N]
    return data_out


def transform_points3d_4xN(points3d_4xN, T_src_to_dst):
    rows, cols = points3d_4xN.shape
    assert (points3d_4xN.ndim == 2)
    #assert (rows == 4 and cols >= 1)
    if cols < 1:
        return np.array([])

    # Convert first to scs
    points3d_dst_4xN = T_src_to_dst.dot(points3d_4xN)
    return points3d_dst_4xN


def transform_cuboid(cuboid, T_ref_to_dst):
    # All transforms are assumed to be 4x4 matrices, in the form of numpy arrays
    assert(isinstance(cuboid, list))
    if len(cuboid) == 10:
        raise Exception("Quaternion transforms not supported yet.")

    assert(len(cuboid) == 9)
    T_ref_to_dst = np.array(T_ref_to_dst).reshape(4, 4)

    # 1) Obtain pose from cuboid info
    x, y, z, rx, ry, rz, sx, sy, sz = cuboid
    P_obj_wrt_ref = create_pose(R=euler2R([rz, ry, rx], seq=EulerSeq.ZYX), C=np.array([[x, y, z]]).T)  # np.array
    T_obj_to_ref = P_obj_wrt_ref  # SCL principles,   # np.array

    # 2) Concatenate transforms
    T_obj_to_dst = T_ref_to_dst.dot(T_obj_to_ref)    # np.array

    # 3) Obtain new rotation and translation
    P_obj_wrt_dst = T_obj_to_dst    # np.array
    R_obj_wrt_dst, C_obj_wrt_dst = decompose_pose(P_obj_wrt_dst)    # np.array

    rvec = R2rvec(R_obj_wrt_dst)

    cuboid_transformed = [C_obj_wrt_dst[0], C_obj_wrt_dst[1], C_obj_wrt_dst[2],
                          rvec[0][0], rvec[1][0], rvec[2][0],
                          sx, sy, sz]    # list
    return cuboid_transformed


def transform_plane(plane, T_ref_to_dst):
    # plane = (a, b, c, d)
    # such that ax + by + cz + d = 0
    # plane_transformed = transpose(invert(T))* plane
    T = np.array(T_ref_to_dst).reshape(4, 4)
    plane_transformed = inv(T).transpose().dot(np.array(plane).reshape(4, 1))
    return plane_transformed.flatten().tolist()


def generate_cuboid_points_object_4x8(sx, sy, sz):
    points_cuboid_4x8 = np.array([[-sx / 2, -sx / 2, sx / 2, sx / 2, -sx / 2, -sx / 2, sx / 2, sx / 2],
                                  [sy / 2, -sy / 2, -sy / 2, sy / 2, sy / 2, -sy / 2, -sy / 2, sy / 2],
                                  [-sz / 2, -sz / 2, -sz / 2, -sz / 2, sz / 2, sz / 2, sz / 2, sz / 2],
                                  [1, 1, 1, 1, 1, 1, 1, 1]])
    return points_cuboid_4x8


def generate_cuboid_points_ref_4x8(cuboid):
    # Cuboid is (x, y, z, rx, ry, rz, sx, sy, sz)
    # This function converts to 8 4x1 points
    x, y, z, rx, ry, rz, sx, sy, sz = cuboid

    # Create base structure using sizes
    points_cuboid_4x8 = generate_cuboid_points_object_4x8(sx, sy, sz)

    # Create rotation
    R_obj_wrt_ref = euler2R([rz, ry, rx])

    # Create location
    C_ref = np.array([[x, y, z]]).T

    # Create pose from rotation and location
    P_obj_wrt_ref = create_pose(R_obj_wrt_ref, C_ref)
    T_obj_to_ref = P_obj_wrt_ref

    points_cuboid_lcs_4x8 = T_obj_to_ref.dot(points_cuboid_4x8)
    return points_cuboid_lcs_4x8


####################################################
# Other
####################################################
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


def is_inside_image(width, height, x, y):
    return width > x > 0 and height > y > 0


def bounding_rect(points2d_3xN):
    x = points2d_3xN[0, :]
    y = points2d_3xN[1, :]
    x_min = np.min(x)
    x_max = np.max(x)
    y_min = np.min(y)
    y_max = np.max(y)

    return np.int0(np.array([x_min, y_min, x_max - x_min, y_max - y_min]))


def generate_grid(x_params, y_params, z_params):
    xls = np.linspace(x_params[0], x_params[1], x_params[2]),
    yls = np.linspace(y_params[0], y_params[1], y_params[2]),
    zls = np.linspace(z_params[0], z_params[1], z_params[2])
    xm, ym, zm = np.meshgrid(xls, yls, zls)

    return xm, ym, zm


def grid_as_4xN_points3d(xm, ym, zm):
    xm_row = xm.reshape(1, -1)
    ym_row = ym.reshape(1, -1)
    zm_row = zm.reshape(1, -1)
    pad_row = np.zeros(xm_row.shape, np.float)
    pad_row[0, :] = 1.0
    points3d_vcs_4xN = np.concatenate([xm_row, ym_row, zm_row, pad_row])
    return points3d_vcs_4xN


def from_MxN_to_OpenCV_Nx1xM(array_MxN):
    M, N = array_MxN.shape
    array_Nx1xM = np.float32(array_MxN[0:M, np.newaxis, :]).transpose()
    return array_Nx1xM


def from_OpenCV_Nx1xM_to_MxN(array_Nx1xM):
    N = array_Nx1xM.shape[0]
    M = array_Nx1xM.shape[2]
    array_MxN = array_Nx1xM
    array_MxN.shape = (N, M)
    return array_MxN


def filter_outside(points2d_3xN, img_size, idx_valid):
    width, height = img_size
    N = points2d_3xN.shape[1]
    # Remove those outside the limits of the image (after distortion)
    for i in range(0, N):
        if idx_valid[i]:  # ignore those already filtered
            x = points2d_3xN[0, i]
            y = points2d_3xN[1, i]

            if not (0 <= x < width and 0 <= y < height):
                idx_valid[i] = False
                points2d_3xN[:, i] = np.nan
    return points2d_3xN, idx_valid


def rgb_to_hex(rgb):
    return '%02x%02x%02x' % tuple(rgb)


def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i+lv//3], 16) for i in range(0, lv, lv//3))


####################################################
# Images
####################################################
def image_to_base64(img):
    """
    This function converts an OpenCV image, encodes it as PNG, and
    converts the payload into a stringified base64 chain in utf-8
    :param img: OpenCV image
    :return: base64 utf-8 string
    """
    compr_params = [int(cv.IMWRITE_PNG_COMPRESSION), 9]
    result, payload = cv.imencode('.png', img, compr_params)
    payload_b64_str = str(base64.b64encode(payload), 'utf-8')
    return payload_b64_str


def base64_to_image(payload_base64_str, flag=1):
    payload_read = base64.b64decode(payload_base64_str)
    img = cv.imdecode(np.frombuffer(payload_read, dtype=np.uint8), flag)
    return img
