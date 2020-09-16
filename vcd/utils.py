"""
VCD (Video Content Description) library v4.3.0

Project website: http://vcd.vicomtech.org

Copyright (C) 2020, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.3.0.
VCD is distributed under MIT License. See LICENSE.

"""


import warnings
import numpy as np
from enum import Enum
from collections import deque, namedtuple

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
# ROTATION AND ODOMETRY UTILS. See SCL library
####################################################
def create_pose(R, C):
    # Under SCL principles, P = (R C; 0 0 0 1), while T = (R^T -R^TC; 0 0 0 1)
    temp = np.hstack((R, C))
    P = np.vstack((temp, np.array([0, 0, 0, 1])))  # P is 4x4
    return P


def decompose_pose(pose_4x4):
    rotation_3x3 = pose_4x4[0:3, 0:3]
    c_3x1 = pose_4x4[0:3, 3]
    return rotation_3x3, c_3x1


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


####################################################
# Transforms
####################################################
# From https://dev.to/mxl/dijkstras-algorithm-in-python-algorithms-for-beginners-dkc
# we'll use infinity as a default distance to nodes.
inf = float('inf')
Edge = namedtuple('Edge', 'start, end, cost')


def make_edge(start, end, cost=1):
    return Edge(start, end, cost)


class Graph:
    def __init__(self, edges):
        # let's check that the data is right
        wrong_edges = [i for i in edges if len(i) not in [2, 3]]
        if wrong_edges:
            raise ValueError('Wrong edges data: {}'.format(wrong_edges))

        self.edges = [make_edge(*edge) for edge in edges]

    @property
    def vertices(self):
        return set(
            sum(
                ([edge.start, edge.end] for edge in self.edges), []
            )
        )

    @staticmethod
    def get_node_pairs(n1, n2, both_ends=True):
        if both_ends:
            node_pairs = [[n1, n2], [n2, n1]]
        else:
            node_pairs = [[n1, n2]]
        return node_pairs

    def remove_edge(self, n1, n2, both_ends=True):
        node_pairs = self.get_node_pairs(n1, n2, both_ends)
        edges = self.edges[:]
        for edge in edges:
            if [edge.start, edge.end] in node_pairs:
                self.edges.remove(edge)

    def add_edge(self, n1, n2, cost=1, both_ends=True):
        node_pairs = self.get_node_pairs(n1, n2, both_ends)
        for edge in self.edges:
            if [edge.start, edge.end] in node_pairs:
                return ValueError('Edge {} {} already exists'.format(n1, n2))

        self.edges.append(Edge(start=n1, end=n2, cost=cost))
        if both_ends:
            self.edges.append(Edge(start=n2, end=n1, cost=cost))

    @property
    def neighbours(self):
        neighbours = {vertex: set() for vertex in self.vertices}
        for edge in self.edges:
            neighbours[edge.start].add((edge.end, edge.cost))

        return neighbours

    def dijkstra(self, source, dest):
        assert source in self.vertices, 'Such source node doesn\'t exist'
        distances = {vertex: inf for vertex in self.vertices}
        previous_vertices = {
            vertex: None for vertex in self.vertices
        }
        distances[source] = 0
        vertices = self.vertices.copy()

        while vertices:
            current_vertex = min(
                vertices, key=lambda vertex: distances[vertex])
            vertices.remove(current_vertex)
            if distances[current_vertex] == inf:
                break
            for neighbour, cost in self.neighbours[current_vertex]:
                alternative_route = distances[current_vertex] + cost
                if alternative_route < distances[neighbour]:
                    distances[neighbour] = alternative_route
                    previous_vertices[neighbour] = current_vertex

        path, current_vertex = deque(), dest
        while previous_vertices[current_vertex] is not None:
            path.appendleft(current_vertex)
            current_vertex = previous_vertices[current_vertex]
        if path:
            path.appendleft(current_vertex)
        return path


def get_transform(vcd, cs_src, cs_dst, frameNum=None):
    assert(vcd.has_coordinate_system(cs_src))
    assert(vcd.has_coordinate_system(cs_dst))

    if cs_src == cs_dst:
        return np.identity(4, 4).flatten().tolist()

    # e.g.
    # odom->vehicle-is8855->{velo_top, imu}
    # velo_top->{cam_left, cam_right}
    # a) get("cam_left", "vehicle-iso8855")
    # b) get("vehicle-iso8855", "cam_left")

    # Can be tested with vcd430_kitti_tracking_0000.json
    # transform_src_dst = utils.get_transform(self.vcd, "CAM_LEFT", "VEHICLE-ISO8855", _frameNum)
    # transform_dst_src = utils.get_transform(self.vcd, "VEHICLE-ISO8855", "CAM_LEFT", _frameNum)
    # transform_src_dst_ = utils.inv(transform_dst_src)
    # Check transform_src_dst equals to transform_src_dst_

    list = []

    # Create graph with the poses defined for each coordinate_system
    # These are poses valid "statically"
    for cs_name, cs_body in vcd.data['vcd']['coordinate_systems'].items():
        for child in cs_body['children']:
            list.append((cs_name, child, 1))
            list.append((child, cs_name, 1))

    graph = Graph(list)
    result = graph.dijkstra(cs_src, cs_dst)

    # Let's build the transform using atomic transforms (which exist in VCD)
    t_4x4 = np.identity(4, dtype=float)
    for counter, value in enumerate(result):
        # e.g. a) result = {("cam_left", "velo_top"), ("velo_top", "vehicle-iso8855")}
        # e.g. b) result = {("vehicle-iso8855", "velo_top"), ("velo_top", "cam_left")}
        if counter == len(result) - 1:
            break
        cs_1 = result[counter]
        cs_2 = result[counter + 1]

        t_name = cs_1 + "_to_" + cs_2
        t_name_inv = cs_2 + "_to_" + cs_1

        # NOTE: this entire function works under the consensus that pose_src_wrt_dst = transform_src_to_dst, using
        # alias rotation of coordinate systems and linear 4x4
        if frameNum is None:
            # No frame info, let's read from coordinate_system poses
            # Check if this edge is from child to parent or viceversa
            if cs_2 == vcd.data['vcd']['coordinate_systems'][cs_1]['parent']:
                t_4x4 = (np.array([vcd.data['vcd']['coordinate_systems'][cs_1]['pose_wrt_parent']]).reshape(4, 4)).dot(t_4x4)
            elif cs_1 == vcd.data['vcd']['coordinate_systems'][cs_2]['parent']:
                temp = np.array([vcd.data['vcd']['coordinate_systems'][cs_2]['pose_wrt_parent']])
                t_4x4 = inv(temp.reshape(4, 4)).dot(t_4x4)
        else:
            # So the user has asked for a specific frame, let's look for this frame if a transform exist
            transform_at_this_frame = False
            if frameNum in vcd.data['vcd']['frames']:
                if 'transforms' in vcd.data['vcd']['frames'][frameNum]['frame_properties']:
                    if t_name in vcd.data['vcd']['frames'][frameNum]['frame_properties']['transforms']:
                        transform = vcd.data['vcd']['frames'][frameNum]['frame_properties']['transforms'][t_name]
                        t_4x4 = (np.array([transform['transform_src_to_dst_4x4']]).reshape(4, 4)).dot(t_4x4)
                        transform_at_this_frame = True
                    elif t_name_inv in vcd.data['vcd']['frames'][frameNum]['frame_properties']['transforms']:
                        transform = vcd.data['vcd']['frames'][frameNum]['frame_properties']['transforms'][t_name_inv]
                        temp = np.array([transform['transform_src_to_dst_4x4']])
                        t_4x4 = inv(temp.reshape(4, 4)).dot(t_4x4)
                        transform_at_this_frame = True
            if not transform_at_this_frame:
                # Check if this edge is from child to parent or viceversa
                if cs_2 == vcd.data['vcd']['coordinate_systems'][cs_1]['parent']:
                    t_4x4 = (np.array([vcd.data['vcd']['coordinate_systems'][cs_1]['pose_wrt_parent']]).reshape(4, 4)).dot(t_4x4)
                elif cs_1 == vcd.data['vcd']['coordinate_systems'][cs_2]['parent']:
                    temp = np.array([vcd.data['vcd']['coordinate_systems'][cs_2]['pose_wrt_parent']])
                    t_4x4 = inv(temp.reshape(4, 4)).dot(t_4x4)

    return t_4x4.flatten().tolist()


def transform_cuboid(cuboid, T_ref_to_dst):
    # All transforms are assumed to be 4x4 matrices, in the form of numpy arrays
    assert(isinstance(T_ref_to_dst, list))
    assert(isinstance(cuboid, list))
    if len(cuboid) == 10:
        raise Exception("Quaternion transforms not supported yet.")

    assert(len(cuboid) == 9)

    # 1) Obtain pose from cuboid info
    x, y, z, rx, ry, rz, sx, sy, sz = cuboid
    P_obj_wrt_ref = create_pose(R=euler2R([rz, ry, rx], seq=EulerSeq.ZYX), C=np.array([[x, y, z]]).T)  # np.array
    T_obj_to_ref = P_obj_wrt_ref  # SCL principles,   # np.array

    # 2) Concatenate transforms
    T_obj_to_dst = (np.array(T_ref_to_dst).reshape(4,4)).dot(T_obj_to_ref)    # np.array

    # 3) Obtain new rotation and translation
    P_obj_wrt_dst = T_obj_to_dst    # np.array
    R_obj_wrt_dst, C_obj_wrt_dst = decompose_pose(P_obj_wrt_dst)    # np.array

    rvec = R2rvec(R_obj_wrt_dst)

    cuboid_transformed = [C_obj_wrt_dst[0], C_obj_wrt_dst[1], C_obj_wrt_dst[2],
                          rvec[0][0], rvec[1][0], rvec[2][0],
                          sx, sy, sz]    # list
    return cuboid_transformed


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

