"""
VCD (Video Content Description) library v4.3.0

Project website: http://vcd.vicomtech.org

Copyright (C) 2020, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.3.0.
VCD is distributed under MIT License. See LICENSE.

"""

import numpy as np
import cv2 as cv
from collections import deque, namedtuple

from numpy import float64

import vcd.utils as utils
import math

#TODO: Review SCL principles according to VCD 4.3.0 coordiante systems and transforms
''' ######################################################    
    Basic principles of SCL (Scene Configuration Library)
    ######################################################
    SCL provides some routines and functions, but it is also a guide to produce scenes coherently.
    Read carefully these principles, and see them in practice on the samples.

    SCL is based on common conventions. In some cases, SCL allows using different conventions, but eventually
    it enforces using specific conventions, such as "right-hand" coordinate systems, homogeneous coordinates, 
    left-multiplication of matrices, alias (vs alibi) rotation matrices, etc.

    NUMPY ARRAYS
    -----------------------------
    All geometric data is expressed as numpy n-dimensional arrays.    

    HOMOGENEOUS DATA
    -----------------------------
    All geometric data (points, lines) are expressed in homogeneous coordinates (columns)
    All matrices are also expressed in homogeneous coordinates.
    E.g. 3D points are column vectors 4x1
         camera calibration matrix (K) is 3x4 matrix, where last row is all zeros and 1.0
         all poses are expressed as 4x4 matrices
         rotation matrices are 3x3
         If not specified otherwise, all one-dimensional vectors are column vectors

    POSES AND COORDINATE SYSTEMS
    -----------------------------
    Each sensor has a "static pose" defined against the Local Coordinate System (LCS). In the case of
    vehicle set-ups, this LCS is a point at the ego-vehicle located at
    the middle of the rear axle, projected to the ground, being X-to-front, Y-to-left, Z-up
    as defined in the ISO8855. There are some other coordinates systems considered in SCL:

        - LCS : Local Coordinate System (e.g. the vehicle coordinate system at the rear axis, as in ISO8855)
        - SCS : Sensor Coordinate System (e.g. the camera coordinate system, or the lidar coordinate system)        
        - WCS : World Coordinate System (a static coordinate system for the entire scene, typically equal to the first LCS)
        - GCS : Geographic Coordinate System (UTM Universal Transverse Mercator)
        - ICS : Image coordinate system (this is the 2D image plane)

    For readability, let's use the following letter conventions:        
        - P : Pose 4x4
        - T : Transform 4x4
        - R : Rotation matrix 3x3        
        - C : Position of coordinate system wrt to another 3x1        
        - K : Camera calibration matrix 3x4
        - d : Distortion coefficients 1x5 (or 1x9, or 1x14)

    All Poses are defined right-handed. A Pose encodes the rotation and position of a coordinate system
    wrt to a reference system

    Usually, P_scs_wrt_lcs = [[R_3x3, C_3x1], [0, 0, 0, 1]]

    To actually convert a point from the reference system (e.g. LCS) into another system (e.g. SCS), the 
    transformation matrix is built as the inverse of the pose  
    https://en.wikipedia.org/wiki/Active_and_passive_transformation         

    Cameras coordinate systems are defined with X-to-right, Y-to-bottom, and Z-to-front.
    This is the common practice in computer vision, so that image coordinates are defined 
    x-to-right, y-to-bottom.

    Changes in coordinate systems are carried out using right-to-left matrix multiplication:
    e.g. X_scs = T_lcs_to_scs * X_lcs (e.g. X_lcs is 4x1, Transform_lcs_to_scs is 4x4, X_scs is 4x1)
         X_scs = T_lcs_to_scs * X_lcs

    In addition, transformations can be understood as inverse Poses.
    e.g. if T_lcs_to_scs converts a point from LCS to SCS, then 
            T_lcs_to_scs = np.linalg.inv(P_scs_wrt_lcs)            

    Note that to build a Pose and Transform by knowing the rotation R and position C of a coordinate system 
    wrt to another, it is possible to do:
    (pseudo-code)
    P = (R C; 0 0 0 1)
    or
    T = (R^T -R^TC; 0 0 0 1)
    Note P = T^-1 and T=P^-1     

    Since conversion from one system to another is useful, the following equations hold true:
    P_scs_wrt_lcs = (T_lcs_to_scs)^-1
    P_scs_wrt_lcs = T_scs_to_lcs


    ODOMETRY
    -----------------------------
    The sensors of the setup can move through time (e.g. if onboarded into a moving vehicle or drone), the
    motion of the set-up is defined by the odometry information.

    As each sensor has its own capturing timestamp, not necessarily coincident with the timestamp of
    an odometry entry, odometry information may be provided associated to a specific sensor frame (this way, 
    it is possible to locate globally sensing information from that sensor). 
    The library provides tools to interpolate odometry and associate odometry entries to specific timestamps. 

    The SCL library is defined in a way it is possible to add odometry values from multiple set-ups
    e.g. V2V, a second vehicle sends location information about itself and its sensors, along with detections 


    GEO-COORDINATES
    -----------------------------
    TODO

'''

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


class Scene:
    def __init__(self, vcd):
        self.vcd = vcd
        self.cameras = dict()

    def camera_roi_z0(self, camera_name, cs, frameNum):
        """
        This function computes the region of the image which maps into the reference (cs) Z=0 plane
        by checking whether the re-projected point lies in front or behind the camera
        :param cam_name: camera name
        :param frameNum: frame num
        :return: polygon 2D
        """
        # Working on undistorted coordinates
        hline, points = self.compute_horizon_line(camera_name=camera_name, cs=cs, frameNum=frameNum)
        cam = self.get_camera(camera_name=camera_name, frameNum=frameNum)
        width = cam.img_size_undist[0]
        height = cam.img_size_undist[1]

        # Create 2 contours going through the limits of the image and using points
        # Then check which of them contains points which are projected in Z>0 in camera coordinate system
        polygon = []
        if len(points) == 0:
            # So, the line at the infinite is NOT inside the limits of the image
            # Let's then check if any point inside the image produces a Z>0 (if not, this camera is pointing to the sky)
            point2d_dist_3x1 = np.array([[width / 2, height / 2, 1]]).transpose()

            # Reproject into self.coordinate_system Z=0 plane
            point3d_4x1, valid = self.reproject_points2d_3xN(points2d_3xN=point2d_dist_3x1, plane=(0, 0, 1, 0),
                                                             cs_cam=camera_name, cs_dst=cs, frameNum=frameNum)
            # Transform back to camera coordinate system
            point3d_4x1 = self.transform_points3d_4xN(points3d_4xN=point3d_4x1, cs_src=cs, cs_dst=camera_name,
                                                      frameNum=frameNum)
            in_front = point3d_4x1[2, 0] > 0
            if in_front:
                polygon.append((0, 0))
                polygon.append((width - 1, 0))
                polygon.append((width - 1, height - 1))
                polygon.append((0, height - 1))

                return polygon
        else:
            # Ok, so the horizon line is INSIDE the limits of the undistorted domain
            # There are 6 possible configurations
            points_code = []
            U = None
            L = None
            R = None
            B = None
            for idx, point in enumerate(points):
                if point[1] == 0:  # So points[0] is U
                    points_code.append('U')
                    U = point
                elif point[0] == width:
                    points_code.append('R')
                    R = point
                elif point[1] == height:
                    points_code.append('B')
                    B = point
                else:
                    points_code.append('L')
                    L = point
            UL = (0, 0)
            UR = (width - 1, 0)
            BR = (width - 1, height - 1)
            BL = (0, height - 1)

            polygon_A = []
            polygon_B = []
            if 'U' in points_code and 'L' in points_code:
                # Case 0: LU
                polygon_A.append(UL)
                polygon_A.append(U)
                polygon_A.append(L)
                polygon_A.append(U)
                polygon_B.append(UR)
                polygon_B.append(BR)
                polygon_B.append(BL)
                polygon_B.append(L)
            elif 'U' in points_code and 'B' in points_code:
                # Case 1: BU
                polygon_A.append(UL)
                polygon_A.append(U)
                polygon_A.append(B)
                polygon_A.append(BL)
                polygon_B.append(U)
                polygon_B.append(UR)
                polygon_B.append(BR)
                polygon_B.append(B)
            elif 'U' in points_code and 'R' in points_code:
                # Case 2: RU
                polygon_A.append(U)
                polygon_A.append(UR)
                polygon_A.append(R)
                polygon_B.append(UL)
                polygon_B.append(U)
                polygon_B.append(R)
                polygon_B.append(BR)
                polygon_B.append(BL)
            elif 'L' in points_code and 'B' in points_code:
                # Case 3: LB
                polygon_A.append(L)
                polygon_A.append(B)
                polygon_A.append(BL)
                polygon_B.append(UL)
                polygon_B.append(UR)
                polygon_B.append(BR)
                polygon_B.append(B)
                polygon_B.append(L)
            elif 'L' in points_code and 'R' in points_code:
                # Case 4: LR
                polygon_A.append(UL)
                polygon_A.append(UR)
                polygon_A.append(R)
                polygon_A.append(L)
                polygon_B.append(L)
                polygon_B.append(R)
                polygon_B.append(BR)
                polygon_B.append(BL)
            else:
                # Case 5: BR
                polygon_A.append(B)
                polygon_A.append(R)
                polygon_A.append(BR)
                polygon_B.append(UL)
                polygon_B.append(UR)
                polygon_B.append(R)
                polygon_B.append(B)
                polygon_B.append(BR)

            # Now test whether polygon or polygon_other contain points which project to z>0 camera
            point_A = (sum(x for x, y in polygon_A), sum(y for x, y in polygon_A))
            point_A = (point_A[0]/len(polygon_A), point_A[1]/len(polygon_A))

            point_B = (sum(x for x, y in polygon_B), sum(y for x, y in polygon_B))
            point_B = (point_B[0] / len(polygon_B), point_B[1] / len(polygon_B))

            # Reproject into self.coordinate_system Z=0 plane
            point_A_3x1 = np.array([[point_A[0], point_A[1], 1]]).transpose()
            point_A_3d_4x1, valid = self.reproject_points2d_3xN(points2d_3xN=point_A_3x1, plane=(0, 0, 1, 0),
                                                                cs_cam=camera_name, cs_dst=cs, frameNum=frameNum)
            # Transform back to camera coordinate system
            point_A_3d_4x1 = self.transform_points3d_4xN(points3d_4xN=point_A_3d_4x1, cs_src=cs, cs_dst=camera_name,
                                                               frameNum=frameNum)
            in_front_A = point_A_3d_4x1[2, 0] > 0

            if in_front_A:
                polygon = polygon_A
            else:
                # Check if B
                point_B_3x1 = np.array([[point_B[0], point_B[1], 1]]).transpose()
                point_B_3d_4x1, valid = self.reproject_points2d_3xN(points2d_3xN=point_B_3x1, plane=(0, 0, 1, 0),
                                                                    cs_cam=camera_name, cs_dst=cs, frameNum=frameNum)
                # Transform back to camera coordinate system
                point_B_3d_4x1 = self.transform_points3d_4xN(points3d_4xN=point_B_3d_4x1, cs_src=cs, cs_dst=camera_name,
                                                               frameNum=frameNum)
                in_front_B = point_B_3d_4x1[2, 0] > 0

                if in_front_B:
                    polygon = polygon_B
                else:
                    # This should not happen... something's wrong
                    pass

        N = len(polygon)
        points2d_3xN = np.ones((3, N), dtype=np.int32)
        count = 0
        for point in polygon:
            points2d_3xN[0, count] = utils.round(point[0])
            points2d_3xN[1, count] = utils.round(point[1])
            count += 1

        return points2d_3xN

    def compute_horizon_line(self, camera_name, cs, frameNum=None):
        """
        This function computes the horizon line (as the projection of the infinite Z=0) for a camera at a certain
        frameNum, in image coordinates.
        It works by creating 2 virtual infinite points in the Z=0, and projecting them into the image and clipping
        it adequately.
        Works using undistorted coordinates (otherwise, the horizon line is not a line but a curve).
        :param camera_name: camera name
        :param frameNum: frame number
        :return: line in general form (a, b, c), and array of points, all in undistorted domain
        """
        if frameNum is None:
            f = -1
        else:
            f = frameNum

        # Perhaps already computed
        # TODO check if we really need to store this computation
        if camera_name in self.cameras:
            if f in self.cameras[camera_name]:
                if 'hline' in self.cameras[camera_name][f]:
                    return self.cameras[camera_name][f]['hline']

        # Compute
        cam = self.get_camera(camera_name=camera_name, frameNum=frameNum)
        width = cam.width
        height = cam.height

        # Select points in the infinite that belong to the Z=0 plane
        # Let's propose several infinite points in all 360º directions
        steps = 60
        step = 2*np.pi / steps
        points3d_inf = np.zeros((4, steps))
        for s in range(0, steps):
            angle = step*s
            x = np.cos(angle)
            y = np.sin(angle)
            points3d_inf[0, s] = x
            points3d_inf[1, s] = y

        # Convert from cs to camera_cs
        points3d_inf = self.transform_points3d_4xN(points3d_4xN=points3d_inf,
                                                   cs_src=cs, cs_dst=camera_name,
                                                   frameNum=frameNum)

        # Project in the camera (USING UNDISTORTED FRAME)
        points2d_inf, valid = cam.project_points3d(points3d_4xN=points3d_inf, apply_distortion=False)
        points2d_inf = points2d_inf[:, valid]
        if points2d_inf.shape[1] < 2:
            return np.array([[]]), []

        ## From here on we have at least 2 valid infinite points projected in the image
        #points2d_inf = cam.undistort_points2d(points2d_dist_3xN=points2d_inf)

        # Let's choose two points (first and last) to define the line (ideally all of them should lie in the same line)
        n = points2d_inf.shape[1]
        # TODO: test all lie in the same line

        line = np.cross(points2d_inf[:, 0], points2d_inf[:, -1])
        line = line / np.linalg.norm(line)

        a = line[0]
        b = line[1]
        c = line[2]

        # ax + by + c = 0
        num_points_touch = 0
        points_horz = []
        if abs(a) < 1e-8:
            # There is no intersection with X
            point_int_x0 = (0, -c / b)
            point_int_xW = (width, -c / b)
            if 0 <= -c / b < height:
                num_points_touch = 2
                points_horz.append(point_int_x0)
                points_horz.append(point_int_xW)

        elif abs(b) < 1e-8:
            # There is no intersection with Y
            point_int_y0 = (-c / a, 0)
            point_int_yH = (-c / a, height)
            if 0 <= -c / a < width:
                num_points_touch = 2
                points_horz.append(point_int_y0)
                points_horz.append(point_int_yH)
        else:
            P1 = (0, -c / b)
            if 0 <= P1[1] < height:
                points_horz.append(P1)
            P2 = (width, -(c + a * width) / b)
            if 0 <= P2[1] < height:
                points_horz.append(P2)
            P3 = (-c / a, 0)
            if 0 <= P3[0] < width:
                points_horz.append(P3)
            P4 = (-(c + b * height) / a, height)
            if 0 <= P4[0] < width:
                points_horz.append(P4)

            assert (len(points_horz) == 2 or len(
                points_horz) == 0)  # a line can only intersect a rectangle in 2 points! (or none)

        # Store for next time
        self.cameras.setdefault(camera_name, {})
        self.cameras[camera_name].setdefault(frameNum, {})
        self.cameras[camera_name][frameNum]['hline'] = line, points_horz

        return line, points_horz

    def get_camera(self, camera_name, frameNum=None):
        """
        This function explores the VCD content searching for the camera parameters of camera "camera_name", specific
        for frameNum if specified (or static information if None).

        The function consults and updates a store of information self.cameras, to speed up some computations (so they
        are carried out only once).

        Returns an object of type Camera, which can be used to project points, undistort images, etc.
        :param camera_name: name of the camera
        :param frameNum: frame number (if None, static camera info is requested)
        :return: Camera object
        """
        # Check if already computed
        if frameNum is None:
            f = -1
        else:
            f = frameNum

        if camera_name in self.cameras:
            if f in self.cameras[camera_name]:
                return self.cameras[camera_name][f]['cam']

        # Create camera m
        camera = None
        if 'streams' in self.vcd.data['vcd']:
            if camera_name in self.vcd.data['vcd']['streams']:
                uri = self.vcd.data['vcd']['streams'][camera_name]['uri']
                description = self.vcd.data['vcd']['streams'][camera_name]['description']
                if 'stream_properties' in self.vcd.data['vcd']['streams'][camera_name]:
                    sp = self.vcd.data['vcd']['streams'][camera_name]['stream_properties']
                    if 'intrinsics_pinhole' in sp:
                        camera = CameraPinhole(sp['intrinsics_pinhole'], camera_name, uri, description)
                    elif 'intrinsics_fisheye' in sp:
                        camera = CameraFisheye(sp['intrinsics_fisheye'], camera_name, uri, description)
        else:
            return None

        if frameNum is not None:
            vcd_frame = self.vcd.get_frame(frameNum)

            if 'frame_properties' in vcd_frame:
                if 'streams' in vcd_frame['frame_properties']:
                    if camera_name in vcd_frame['frame_properties']['streams']:
                        if 'stream_properties' in vcd_frame['frame_properties']['streams'][camera_name]:
                            sp = vcd_frame['frame_properties']['streams'][camera_name][
                                'stream_properties']
                        if 'intrinsics_pinhole' in sp:
                            camera = CameraPinhole(sp['intrinsics_pinhole'], camera_name, uri, description)
                        elif 'intrinsics_fisheye' in sp:
                            camera = CameraFisheye(sp['intrinsics_fisheye'], camera_name, uri, description)

        # Update store
        self.cameras.setdefault(camera_name, {})
        self.cameras[camera_name].setdefault(f, {})
        self.cameras[camera_name][f]['cam'] = camera

        return camera

    def __get_transform_chain(self, cs_src, cs_dst):
        # Create graph with the poses defined for each coordinate_system
        # These are poses valid "statically"
        lista = []
        for cs_name, cs_body in self.vcd.data['vcd']['coordinate_systems'].items():
            for child in cs_body['children']:
                lista.append((cs_name, child, 1))
                lista.append((child, cs_name, 1))

        graph = Graph(lista)
        result = graph.dijkstra(cs_src, cs_dst)
        return result

    def get_transform(self, cs_src, cs_dst, frameNum=None):
        """
        This function finds a 4x4 transform from the specified source coordinate system into the destination coordinate
        system, in a way points in the cs_src domain can be transformed to the cs_dst.
        The function works finding the chain of transforms needed to go from src to dst by exploring the parent-child
        dependencies declated in VCD.

        If the frameNum is specified, the function searches if any specific transform step at frameNum. If not found,
        static transforms are returned.
        :param cs_src: source coordinate frame (e.g. "CAM_LEFT", or "WORLD")
        :param cs_dst: destination coordinate frame (e.g. "VELO", or "CAM_LEFT")
        :param frameNum: frame number where to look for specific transform steps
        :return: the 4x4 transform matrix, and a boolean that specifies if the transform is static or not
        """
        assert (self.vcd.has_coordinate_system(cs_src))
        assert (self.vcd.has_coordinate_system(cs_dst))

        static = True
        if cs_src == cs_dst:
            return np.eye(4), static

        # Get chain of transforms
        chain = self.__get_transform_chain(cs_src, cs_dst)

        # Let's build the transform using atomic transforms (which exist in VCD)
        t_4x4 = np.identity(4, dtype=float)
        for counter, value in enumerate(chain):
            # e.g. a) result = {("cam_left", "velo_top"), ("velo_top", "vehicle-iso8855")}
            # e.g. b) result = {("vehicle-iso8855", "velo_top"), ("velo_top", "cam_left")}
            if counter == len(chain) - 1:
                break
            cs_1 = chain[counter]
            cs_2 = chain[counter + 1]

            t_name = cs_1 + "_to_" + cs_2
            t_name_inv = cs_2 + "_to_" + cs_1

            # NOTE: this entire function works under the consensus that pose_src_wrt_dst = transform_src_to_dst, using
            # alias rotation of coordinate systems and linear 4x4
            if frameNum is None:
                # No frame info, let's read from coordinate_system poses
                # Check if this edge is from child to parent or viceversa
                if cs_2 == self.vcd.data['vcd']['coordinate_systems'][cs_1]['parent']:
                    t_4x4 = (
                        np.array([self.vcd.data['vcd']['coordinate_systems'][cs_1]['pose_wrt_parent']]).reshape(4, 4)).dot(
                        t_4x4)
                elif cs_1 == self.vcd.data['vcd']['coordinate_systems'][cs_2]['parent']:
                    temp = np.array([self.vcd.data['vcd']['coordinate_systems'][cs_2]['pose_wrt_parent']])
                    t_4x4 = utils.inv(temp.reshape(4, 4)).dot(t_4x4)
            else:
                # So the user has asked for a specific frame, let's look for this frame if a transform exist
                transform_at_this_frame = False
                if frameNum in self.vcd.data['vcd']['frames']:
                    if 'frame_properties' in self.vcd.data['vcd']['frames'][frameNum]:
                        if 'transforms' in self.vcd.data['vcd']['frames'][frameNum]['frame_properties']:
                            if t_name in self.vcd.data['vcd']['frames'][frameNum]['frame_properties']['transforms']:
                                transform = self.vcd.data['vcd']['frames'][frameNum]['frame_properties']['transforms'][t_name]
                                t_4x4 = (np.array([transform['transform_src_to_dst_4x4']]).reshape(4, 4)).dot(t_4x4)
                                static = False  # with one non-static step the entire chain can be considered not static
                                transform_at_this_frame = True
                            elif t_name_inv in self.vcd.data['vcd']['frames'][frameNum]['frame_properties']['transforms']:
                                transform = self.vcd.data['vcd']['frames'][frameNum]['frame_properties']['transforms'][
                                    t_name_inv]
                                temp = np.array([transform['transform_src_to_dst_4x4']])
                                t_4x4 = utils.inv(temp.reshape(4, 4)).dot(t_4x4)
                                static = False
                                transform_at_this_frame = True
                if not transform_at_this_frame:
                    # Reached this point means no transforms were defined at the requested frameNum
                    # Check if this edge is from child to parent or viceversa
                    if cs_2 == self.vcd.data['vcd']['coordinate_systems'][cs_1]['parent']:
                        t_4x4 = (np.array([self.vcd.data['vcd']['coordinate_systems'][cs_1]['pose_wrt_parent']]).reshape(4,
                                                                                                                    4)).dot(
                            t_4x4)
                    elif cs_1 == self.vcd.data['vcd']['coordinate_systems'][cs_2]['parent']:
                        temp = np.array([self.vcd.data['vcd']['coordinate_systems'][cs_2]['pose_wrt_parent']])
                        t_4x4 = utils.inv(temp.reshape(4, 4)).dot(t_4x4)

        return t_4x4, static

    def transform_points3d_4xN(self, points3d_4xN, cs_src, cs_dst, frameNum=None):
        transform_src_dst, static = self.get_transform(cs_src, cs_dst, frameNum)
        if transform_src_dst is not None:
            points3d_dst_4xN = utils.transform_points3d_4xN(points3d_4xN, transform_src_dst)
            return points3d_dst_4xN
        else:
            return None

    def transform_cuboid(self, cuboid_vals, cs_src, cs_dst, frameNum=None):
        transform_src_dst, static = self.get_transform(cs_src, cs_dst, frameNum)

        if transform_src_dst is not None:
            cuboid_vals_transformed = utils.transform_cuboid(cuboid_vals, transform_src_dst)
            return cuboid_vals_transformed
        else:
            return cuboid_vals

    def transform_plane(self, plane_abcd, cs_src, cs_dst, frameNum=None):
        transform_src_dst, static = self.get_transform(cs_src, cs_dst, frameNum)
        if transform_src_dst is not None:
            plane_abcd_transformed = utils.transform_plane(plane_abcd, transform_src_dst)
            return plane_abcd_transformed
        else:
            return plane_abcd

    def project_points3d_4xN(self, points3d_4xN, cs_src, cs_cam, frameNum=None, apply_distortion=True, remove_outside=False):
        """
        This function projects 3D points into a given camera, specifying the origin coordinate system of the points,
        and a certain frame number. Optionally, distortion can be applied or not (e.g. sometimes is useful to project
        into the undistorted domain).
        :param points3d_4xN: array of 4xN 3D points in cs_src coordinate system
        :param cs_src: name of coordinate system of the points
        :param cs_cam: name of the camera
        :param frameNum: frame number (if None, static camera info is seeked)
        :param apply_distortion: default to True, if False, projection is carried out into undistorted domain
        :param remove_outside: flag to invalidate points outside the limits of the image domain
        :return: array of 3xN 2D points in image coordinates (distorted or undistorted according to apply_distortion),
        and array of boolean declaring points valid or not
        """
        points3d_camera_cs_4xN = self.transform_points3d_4xN(points3d_4xN=points3d_4xN,
                                                             cs_src=cs_src, cs_dst=cs_cam,
                                                             frameNum=frameNum)
        if points3d_camera_cs_4xN is not None:
            cam = self.get_camera(camera_name=cs_cam, frameNum=frameNum)
            points2d_3xN, idx_valid = cam.project_points3d(points3d_4xN=points3d_camera_cs_4xN,
                                                           apply_distortion=apply_distortion,
                                                           remove_outside=remove_outside)
            return points2d_3xN, idx_valid
        return np.array([[]]), []

    def reproject_points2d_3xN(self, points2d_3xN, plane, cs_cam, cs_dst, frameNum=None):
        # This function calls a camera (cs_cam) to reproject points2d in the image plane into
        # a plane defined in the cs_dst.
        # The obtained 3D points are expressed in cs_dst.
        # idx_valid identifies which points are valid 3D points (the reprojection might point to infinity)
        cam = self.get_camera(cs_cam, frameNum)
        plane_cam = self.transform_plane(plane, cs_dst, cs_cam, frameNum) # first convert plane into cam cs
        N = points2d_3xN.shape[1]
        points3d_3xN_cs_cam, idx_valid = cam.reproject_points2d(points2d_3xN, plane_cam)
        if points3d_3xN_cs_cam.shape[1] > 0:
            points3d_3xN_cs_cam_filt = points3d_3xN_cs_cam[:, idx_valid]
            points3d_4xN_cs_dst_filt = self.transform_points3d_4xN(points3d_3xN_cs_cam_filt, cs_cam, cs_dst, frameNum)
            points3d_4xN_cs_dst = np.full([4, N], np.nan)
            points3d_4xN_cs_dst[:, idx_valid] = points3d_4xN_cs_dst_filt
            return points3d_4xN_cs_dst, idx_valid
        return np.array([[]]), []


class Sensor:
    def __init__(self, name, description, uri, **properties):
        self.name = name
        self.description = description
        self.uri = uri
        self.type = type(self).__name__

        self.properties = properties  # additional properties

    def is_camera(self):
        if self.type == "CameraPinhole" or self.type == "CameraFisheye" or self.type == "CameraEquirectangular":
            return True
        return False

    def is_lidar(self):
        if self.type == "Lidar":
            return True
        return False


class Camera(Sensor):
    def __init__(self, width, height, name, description, uri):
        Sensor.__init__(self, name, description, uri)
        self.width = width
        self.height = height

        # This flags chooses between OpenCV's implementation of distort functions and manually written equations
        # They should render equal or very-similar results
        # OpenCV version might be faster (TBC)
        self.use_opencv = False
        pass

    def project_points3d(self, points3d_4xN, apply_distortion=True, remove_outside=False):
        pass

    def reproject_points2d(self, points2d_3xN, plane_cs):
        pass


class CameraPinhole(Camera):
    """
    The Pinhole camera model defines a projection mechanism composed by two steps:

    - Linear projection: using the camera_matrix (K)
    - Radial/Tangential/... distortion: using distortion coefficients

    If distortion has 4 coefficients, it is assumed to be "fisheye" type, as in:
    https://docs.opencv.org/3.4/db/d58/group__calib3d__fisheye.html
    Otherwise (5 or more), it is assumed to be traditional "radial" distortion, as in:
    https://docs.opencv.org/4.2.0/d9/d0c/group__calib3d.html
    '"""
    def __init__(self, camera_intrinsics, name, description, uri):
        self.K_3x4 = np.array(camera_intrinsics['camera_matrix_3x4']).reshape(3, 4)
        rows, cols, = self.K_3x4.shape
        assert (rows == 3 and cols == 4)
        self.K_3x3 = utils.fromCameraMatrix3x4toCameraMatrix3x3(self.K_3x4)
        d_list = camera_intrinsics['distortion_coeffs_1xN']
        self.d_1xN = np.array(d_list).reshape(1, len(d_list))

        self.is_fisheye = len(d_list) == 4

        self.r_limit = None
        if self.is_distorted() and not self.is_fisheye:
            self.r_limit = utils.get_distortion_radius(self.d_1xN)

        # Pre-compute undistortion maps (LUTs)
        self.img_size_dist = (camera_intrinsics['width_px'], camera_intrinsics['height_px'])
        self.img_size_undist = (camera_intrinsics['width_px'], camera_intrinsics['height_px'])

        if self.is_distorted():
            # TODO: Add img_size_undist to user-defined params
            if self.is_fisheye:
                self.K_und_3x3 = cv.fisheye.estimateNewCameraMatrixForUndistortRectify(self.K_3x3, self.d_1xN,
                                                                                       self.img_size_dist, np.eye(3),
                                                                                       balance=1,
                                                                                       new_size=self.img_size_undist, fov_scale=1)

                # NOTE: using m1type=cv.CV_16SC2 leads to fixed point representation, which is reported to be faster, but
                # less accurate. In addition, interpreting the maps in 16SC2 is not trivial because there are indices
                # of interpolated values (see https://docs.opencv.org/3.1.0/da/d54/group__imgproc__transform.html#gab75ef31ce5cdfb5c44b6da5f3b908ea4)
                self.mapX_to_und_16SC2, self.mapY_to_und_16SC2 = cv.fisheye.initUndistortRectifyMap(self.K_3x3, self.d_1xN, np.eye(3),
                                                                                                    self.K_und_3x3, self.img_size_undist, cv.CV_16SC2)


            else:
                # alpha = 0.0 means NO black points in undistorted image
                # alpha = 1.0 means ALL distorted points inside limits of undistorted image
                aux = cv.getOptimalNewCameraMatrix(self.K_3x3, self.d_1xN, self.img_size_dist, alpha=0.0,
                                                              newImgSize=self.img_size_undist)
                self.K_und_3x3 = aux[0]
                self.mapX_to_und_16SC2, self.mapY_to_und_16SC2 = cv.initUndistortRectifyMap(self.K_3x3, self.d_1xN,
                                                                                            R=np.eye(3),
                                                                                            newCameraMatrix=self.K_und_3x3,
                                                                                            size=self.img_size_undist, m1type=cv.CV_16SC2)
        else:
            self.K_und_3x3 = self.K_3x3

        self.K_und_3x4 = utils.fromCameraMatrix3x3toCameraMatrix3x4(self.K_und_3x3)

        Camera.__init__(self, camera_intrinsics['width_px'],
                        camera_intrinsics['height_px'],
                        name, description, uri)

    def __test_undistortion(self, img, img_und):
        # Let's test if we project a 3D point into the distorted image
        # and into the undistorted image
        # And convert from one into another
        # Conclusions would be: we can work in any domain (distorted or undistorted), and
        # keep the ability to project and reproject 3D points

        # 1.- Create some points
        N = 100
        points3d_4xN = np.ones((3, N))
        points3d_4xN[0:3, :] = points3d_4xN[0:3, :]*np.random.random((3, N))*10

        # 2.- Project points into distorted image
        points2d_3xN_dist, idx_valid = self.project_points3d(points3d_4xN)
        points2d_3xN_dist = points2d_3xN_dist[:, idx_valid]

        # 3.- Draw into image
        for i in range(0, points2d_3xN_dist.shape[1]):
            cv.circle(img, (utils.round(points2d_3xN_dist[0, i]),
                            utils.round(points2d_3xN_dist[1, i])), 2, (255, 0, 0), -1)

        # 4.- Undistort these points
        points2d_3xN_dist_und = self.undistort_points2d(points2d_3xN_dist)

    def undistort_image(self, img):
        if not self.is_distorted():
            return img
        # cv.remap works for both models cv. and cv.fisheye
        return cv.remap(img, self.mapX_to_und_16SC2, self.mapY_to_und_16SC2, interpolation=cv.INTER_LINEAR,
                        borderMode=cv.BORDER_CONSTANT)

    def get_rays3d(self, point2d_3xN, K_3x3):
        rays3d_3xN = np.matmul((np.linalg.inv(K_3x3)), point2d_3xN)
        rays3d_3xN /= np.linalg.norm(rays3d_3xN)
        #ray3d_4xN = np.vstack((ray, np.ones((1, point2d_3xN.shape[1]))))
        #return ray3d_4xN
        return rays3d_3xN

    def is_distorted(self):
        return np.count_nonzero(self.d_1xN) > 0

    def distort_points2d(self, points2d_und_3xN):
        """
        This is a function to project from undistorted to distorted images.
        :param points2d_und_3xN: undistorted points 3xN homogeneous coordinates
        :return: distorted points 3xN homogeneous coordinates
        """
        rays3d_und_3xN = utils.inv(self.K_und_3x3).dot(points2d_und_3xN)
        rays3d_dist_3xN = self.distort_rays3d(rays3d_und_3xN)
        points2d_dist_3xN = self.K_3x3.dot(rays3d_dist_3xN)
        return points2d_dist_3xN

    def undistort_points2d(self, points2d_dist_3xN):
        """
        This function provides a mechanism to transfer from the distorted domain to the undistorted domain.

        E.g.
        img_und = self.camera.undistort_image(_img)
        points2d_und_3xN = self.camera.undistort_points2d(points2d_3xN)
        rows, cols = points2d_und_3xN.shape
        for i in range(0, cols):
            cv.circle(img_und, (utils.round(points2d_und_3xN[0, i]), utils.round(points2d_und_3xN[1, i])),
                2, (255, 255, 255), -1)
        cv.namedWindow('undistorted-test', cv.WINDOW_NORMAL)
        cv.imshow('undistorted-test', img_und)
        :param points2d_3xN: array of 2d points in homogeneous coordiantes 3xN
        :return: array of undistorted 2d points in homogeneous coordinates 3xN
        """
        N = points2d_dist_3xN.shape[1]
        if N < 1 or not self.is_distorted():
            return points2d_dist_3xN

        # Change shape from (3, N) to (N, 1, 2) so we can use OpenCV, removing homogeneous coordinate
        temp1 = points2d_dist_3xN[0:2, :]
        temp2 = utils.from_MxN_to_OpenCV_Nx1xM(temp1)

        # Use OpenCV functions
        if self.is_fisheye:
            temp3 = cv.fisheye.undistortPoints(temp2, self.K_3x3, self.d_1xN)
        else:
            temp3 = cv.undistortPoints(temp2, self.K_3x3, self.d_1xN)

        # Reshape to (3, N)
        temp3.shape = (N, 2)
        points2d_und_3xN = np.vstack((temp3.T, np.ones((1, N))))

        # Map into undistorted domain by using K_3x3_und
        points2d_und_3xN = self.K_und_3x3.dot(points2d_und_3xN)

        test = False
        if test:
            points2d_dist_re_3xN = self.distort_points2d(points2d_und_3xN)
            error = np.linalg.norm(points2d_dist_re_3xN - points2d_dist_3xN)
            print("Undistortion error: ", error)

        return points2d_und_3xN

    def __filter_outside(self, points2d_3xN, img_size, idx_valid):
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

    def distort_rays3d(self, rays3d_3xN):
        """
        This function distort 3d rays according to the distortion function.
        :param rays3d_3xN: 3d rays as 3xN arrays
        :return: distorted 3d rays as 3xN arrays after applying distortion function.
        """
        N = rays3d_3xN.shape[1]
        if N == 0 or not self.is_distorted():
            rays3d_dist_3xN = np.array([[]])
            return rays3d_dist_3xN

        # Normalize so last coordinate is 1
        rays3d_3xN[0:3, :] = rays3d_3xN[0:3, :] / rays3d_3xN[2, :]

        if self.is_fisheye:
            temp0 = rays3d_3xN[0:2, :]  # remove homogeneous coordinate
            temp1 = utils.from_MxN_to_OpenCV_Nx1xM(temp0)  # Change shape to (N, 1, 2)
            temp2 = cv.fisheye.distortPoints(temp1, np.eye(3), self.d_1xN)  # apply distortion using an identity K
            temp2.shape = (N, 2)  # reshape to 2xN
            rays3d_dist_3xN = np.vstack((temp2.T, np.ones((1, temp2.shape[0]))))  # add homog. row so it is 3xN
        else:
            # NOTE: there is no cv.distortPoints() function as in cv.fisheye.distortPoints()
            # It is though possible to distort points using OpenCV by using cv.projectPoints function
            # As we don't want to use K matrices here, let's use an eye, so the results are rays and not points
            aux = cv.projectPoints(objectPoints=rays3d_3xN,
                                   rvec=np.array([[[0., 0., 0.]]]),
                                   tvec=np.array([[[0., 0., 0.]]]),
                                   cameraMatrix=np.eye(3),
                                   distCoeffs=self.d_1xN)
            rays3d_dist_3xN = utils.from_OpenCV_Nx1xM_to_MxN(aux[0])
            rays3d_dist_3xN = np.vstack((rays3d_dist_3xN.transpose(), np.ones((1, N))))

        return rays3d_dist_3xN

    def project_points3d(self, points3d_4xN, apply_distortion=True, remove_outside=False):
        """
        This function projects 3D points into 2D points using the camera projection.
        All coordinates as homogeneous coordinates, and all 3D elements expressed wrt the camera coordinate system.

        If apply_distortion is False, the projection produces points in the undistorted image.
        If apply_distortion is True, the distortion process (if any) is applied into the distorted image.

        First, the 3D points are understood as 3D rays.
        If distorted, the rays3D are distorted into distorted rays3D.

        The calibration matrix K_3x3 or K_3x3_und (according to apply_distortion) is applied to produce points.

        Points outside limits are removed if remove_outside is True.

        :param points3d_4xN: 3D points in camera cs, homogeneous coordinates
        :param apply_distortion: flag to determine whether to project into distorted or undistorted domain
        :param remove_outside: flag to remove points that fall outside the limits of the target image
        :return: 2D points in image plane, as 3xN array, in hom. coordinates, and boolean array of valid
        """

        # 0.- Pre-filter
        assert (points3d_4xN.ndim == 2)
        N = points3d_4xN.shape[1]
        if N == 0:
            return np.array([[]]), []

        # 1.- Select only those z > 0 (in front of the camera)
        idx_in_front = points3d_4xN[2, :] > 1e-8
        idx_valid = idx_in_front

        # 2.- Distort rays3d if distorted
        rays3d_3xN_filt = points3d_4xN[0:3, idx_valid]
        rays3d_3xN_filt = rays3d_3xN_filt[0:3, :] / rays3d_3xN_filt[2, :]  # so (x', y', 1), convenient for dist.
        rays3d_3xN = np.full([3, N], np.nan)
        rays3d_3xN[:, idx_valid] = rays3d_3xN_filt

        if self.is_distorted():
            if not self.is_fisheye:
                if self.r_limit is not None:
                    for i in range(0, N):
                        if idx_valid[i]:  # ignore those already filtered
                            xp = rays3d_3xN[0, i] / rays3d_3xN[2, i]  # this is x'=x/z as in opencv docs
                            yp = rays3d_3xN[1, i] / rays3d_3xN[2, i]  # this is y'=y/z
                            r = np.sqrt(xp * xp + yp * yp)

                            if r >= self.r_limit * 0.8:  # 0.8 to also remove very close to limit
                                idx_valid[i] = False
                                rays3d_3xN[:, i] = np.nan

            if apply_distortion:
                # Now distort (only non-nans)
                rays3d_3xN_filt = rays3d_3xN[:, idx_valid]
                rays3d_3xN_filt_dist = self.distort_rays3d(rays3d_3xN_filt) # no nan should go into it

                # Add nans
                rays3d_3xN = np.full([3, N], np.nan)
                rays3d_3xN[:, idx_valid] = rays3d_3xN_filt_dist

        # 3.- Project using calibration matrix
        if apply_distortion:
            points2d_3xN = self.K_3x3.dot(rays3d_3xN)
            if remove_outside:
                points2d_3xN, idx_valid = self.__filter_outside(points2d_3xN, self.img_size_dist, idx_valid)
        else:
            points2d_3xN = self.K_und_3x3.dot(rays3d_3xN)
            if remove_outside:
                points2d_3xN, idx_valid = self.__filter_outside(points2d_3xN, self.img_size_undist, idx_valid)

        return points2d_3xN, idx_valid

    def reproject_points2d(self, points2D_3xN, plane_cs):
        """
        This function takes 2D points in the (distorted) image and traces back a 3D ray from the camera optical axis
        through the point and gets the intersection with a defined world plane (in the form (a, b, c, d)).

        This function takes distortion into consideration, by first undistorting the 2D points, and then raycasting
        the 3D ray, free of distortion to apply Plücker formulation to obtain the intersection of a 3D line with
        a 3D plane.

        To manage tha case where the back-projection does not intersect the plane (which can happen for parallel set
        -ups of infinite points), the function returns an array of booleans that define the validity of the projection.

        :param points2D_3xN: array 2D points as 3XN array of homogeneous coordinates, representing points in the original
        image
        :param plane_cs: a plane expressed in general form (a, b, c, d) expressing a 3D plane in camera coordinate
        system
        :return: returns an array of 3D points (4xN array) in homogeneous coordinates, expressed in the camera
        coordinate systems, belonging to the world plane; and a 1xN array of booleans.
        """
        # First, undistort point, so we can project back linear rays
        points2D_und_3xN = points2D_3xN
        if self.is_distorted():
            points2D_und_3xN = self.undistort_points2d(points2D_3xN)

        N = points2D_und_3xN.shape[1]
        if N == 0:
            return np.array([[]]), []
        idx_valid = [True] * N

        # Get ray 3D (expressed in camera coordinate system)
        rays3d_3xN = self.get_rays3d(points2D_und_3xN, self.K_und_3x3)

        # Use Plucker intersection line-plane
        # Create Plucker line using 2 points: origin of camera and origin of camera + ray
        P1 = np.vstack((0, 0, 0, 1))
        P2array = np.vstack((rays3d_3xN, np.ones((1, N))))
        # Plane equation in plucker coordinates (wrt to world)
        P = np.asarray(plane_cs).reshape(4, 1)
        # Line equation in plucker coordinates
        p3dNx4 = np.array([])
        count = 0
        for P2 in P2array.T:
            P2 = P2.reshape(4, 1)
            L = np.matmul(P1, np.transpose(P2)) - np.matmul(P2, np.transpose(P1))
            # Intersection is a 3D point
            p3Dlcs = np.matmul(L, P)
            if p3Dlcs[3][0] != 0:
                p3Dlcs /= p3Dlcs[3][0]  # homogeneous
            else:
                # This is an infinite point: return direction vector instead
                norm = np.linalg.norm(p3Dlcs[:3][0])
                p3Dlcs /= norm
                idx_valid[count] = False
            p3dNx4 = np.append(p3dNx4, p3Dlcs)
            count += 1
        p3dNx4 = p3dNx4.reshape(p3dNx4.shape[0] // 4, 4)
        p3d_4xN = np.transpose(p3dNx4)
        return p3d_4xN, idx_valid


class CameraFisheye(Camera):
    def __init__(self, camera_intrinsics, name, description, uri):
        self.cx = camera_intrinsics['center_x']
        self.cy = camera_intrinsics['center_y']
        self.d = np.array(camera_intrinsics['lens_coeffs_1x4']).reshape(1, 4)
        self.r_limit = None
        Camera.__init__(self, camera_intrinsics['width_px'],
                        camera_intrinsics['height_px'],
                        name, description, uri)

    def is_distorted(self):
        return np.count_nonzero(self.d) > 0

    def project_points3d(self, points3d_4xN, apply_distortion=True, remove_outside=False):
        rows, cols = points3d_4xN.shape
        assert(points3d_4xN.ndim == 2)
        assert(rows == 4 and cols >= 1)
        idx_valid = points3d_4xN[2, :] > 0.0
        N = points3d_4xN.shape[1]
        points2d_3xN = np.full([3, N], np.nan)

        if N == 0:
            return None
        #idx_to_add = [True] * N
        for i in range(0, N):
            if not idx_valid[i]:
                continue
            rnorm = utils.norm([points3d_4xN[0, i], points3d_4xN[1, i]])
            a = math.atan2(rnorm, points3d_4xN[2, i])
            a2 = a * a
            a3 = a2 * a
            a4 = a3 * a
            rpnorm = (a * self.d[0, 0] + a2 * self.d[0, 1] + a3 * self.d[0, 2] + a4 * self.d[0, 3])
            pixel = [self.cx + self.width * 0.5, self.cy + self.height * 0.5, 1]
            divnorm = np.float32(rpnorm/rnorm)
            if rnorm > 1e-6:
                #pixel = [utils.round(pixel[0] + points3d_4xN[0, i]*divnorm),
                #         utils.round(pixel[1] + points3d_4xN[1, i]*divnorm),
                #         1]
                pixel = [ pixel[0] + points3d_4xN[0, i]*divnorm,
                          pixel[1] + points3d_4xN[1, i]*divnorm,
                          1]
                points2d_3xN[:, i] = pixel
            else:
                idx_valid[i] = False

        if remove_outside:
            points2d_3xN, idx_valid = self.__filter_outside(points2d_3xN, self.img_size_dist, idx_valid)

        return points2d_3xN, idx_valid


#class Lidar(Sensor):
#    # TODO
#    def __init__(self, P_scs_wrt_lcs, name, description, uri, **properties):
#        Sensor.__init__(self, P_scs_wrt_lcs, name, description, uri, **properties)