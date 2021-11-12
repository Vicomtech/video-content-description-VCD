"""
VCD (Video Content Description) library v5.0.1

Project website: http://vcd.vicomtech.org

Copyright (C) 2021, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 5.0.1.
VCD is distributed under MIT License. See LICENSE.

"""

from os import stat
import numpy as np
import warnings
import cv2 as cv
from collections import deque, namedtuple
import time

from numpy import float64
from scipy.optimize import curve_fit

import vcd.utils as utils
import math

from matplotlib import pyplot as plt

from vcd.types import areaReference, FisheyeModel

''' ######################################################    
    Basic principles of SCL (Scene Configuration Library)
    ######################################################
    SCL provides some routines and functions, but it is also a guide to produce scenes coherently.
    Read carefully these principles, and see them in practice on the samples.

    SCL is based on common conventions. In some cases, SCL allows using different conventions, but eventually
    it enforces using specific conventions, such as "right-hand" coordinate systems, homogeneous coordinates, 
    right-multiplication of matrices, alias (vs alibi) rotation matrices, etc.

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
    NOTE: Since OpenLABEL 1.0.0, quaternion + translation is also added as an option to express poses.
    Internally, SCL converts this form into 4x4 matrices

    POSES AND COORDINATE SYSTEMS
    -----------------------------
    Each coordinate system may have a pose with respect to a parent coordinate system.
    Examples of this are sensors which are installed in vehicles. The Sensor Coordinate System (SCS) then has a pose
    with respect to the Local Coordinate System (LCS) of the vehicle.
    In SCL this LCS is a point at the ego-vehicle located at the middle of the rear axle, projected to the ground,
    being X-to-front, Y-to-left, Z-up as defined in the ISO8855. 
    
    There are some other usual acronyms used in the code:

        - LCS : Local Coordinate System (e.g. the vehicle coordinate system at the rear axis, as in ISO8855)
        - SCS : Sensor Coordinate System (e.g. the camera coordinate system, or the lidar coordinate system)        
        - WCS : World Coordinate System (a static coordinate system for the entire scene, typically equal to the first LCS)
        - GCS : Geographic Coordinate System (UTM Universal Transverse Mercator)
        - ICS : Image coordinate system (this is the 2D image plane)

    NOTE: Nevertheless, in VCD and SCL, an entirely customizable graph of dependecies can be built, declaring coordinate systems
    and parent-child relations. See vcd.core functions add_coordinate_system() where static poses can be defined, and add_transform()
    which is a function to add frame-specific poses between coordinate systems.

    For readability, let's use the following letter conventions:        
        - P : Pose 4x4
        - T : Transform 4x4
        - R : Rotation matrix 3x3        
        - C : Position of coordinate system wrt to another 3x1        
        - K : Camera calibration matrix 3x4
        - d : Distortion coefficients 1x5 (or 1x9, or 1x14)

    All Poses are defined right-handed. A Pose encodes the passive rotation and position of a coordinate system
    wrt (with respect to) a reference system

    Usually, P_scs_wrt_lcs = [[R_3x3, C_3x1], [0, 0, 0, 1]], where R_3x3 is a 3x3 rotation matrix, and C_3x1 is the 
    position of the SCS expressed in the LCS.

    To actually convert a point from the reference system (e.g. LCS) into another system (e.g. SCS), the 
    transformation matrix is built as the inverse of the pose  
    https://en.wikipedia.org/wiki/Active_and_passive_transformation         

    Cameras coordinate systems are defined with X-to-right, Y-to-bottom, and Z-to-front, following usual OpenCV
    camera model convention.
    This is the common practice in computer vision, so that image coordinates are defined 
    x-to-right, y-to-bottom.

    Transforming a 3D point expressed in a given coordinate system into another coordinate system is
    carried out using right-to-left matrix multiplication:
    e.g. X_scs = T_lcs_to_scs @ X_lcs (e.g. X_lcs is 4x1, Transform_lcs_to_scs is 4x4, X_scs is 4x1)
         X_scs = T_lcs_to_scs @ X_lcs
    NOTE: @ operator in Python (>3.5) is matrix multiplication, equivalent to Numpy's dot operator

    In addition, transformations can be understood as inverse Poses.
    e.g. if T_lcs_to_scs converts a point from LCS to SCS, then 
            T_lcs_to_scs = np.linalg.inv(P_scs_wrt_lcs)  # or using utils.inv(P_scs_wrt_lcs)      
                  
    Note that to build a Pose and Transform by knowing the passive rotation R and position C of a coordinate system 
    wrt to another, it is possible to do:
    (pseudo-code)
    P_scs_wrt_lcs = (R_scs_wrt_lcs C_scs_wrt_lcs; 0 0 0 1)
    or
    T_lcs_to_scs = (transpose(R_scs_wrt_lcs) transpose(-R_scs_wrt_lcs)C_scs_wrt_lcs; 0 0 0 1)
    Note P = T^-1 and T = P^-1

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
    The library provides tools to interpolate vodometry and associate odometry entries to specific timestamps. 

    The SCL library is defined in a way it is possible to add odometry values from multiple set-ups
    e.g. V2V, a second vehicle sends location information about itself and its sensors, along with detections.

    Odometry is treated just like a normal frame-specific transform. Therefore, all previous discussion applies.
    See vcd's add_transform() function at core.py


    GEO-COORDINATES
    -----------------------------
    Just like any other coordinate system, geo-coordinates can be specified in VCD and then are supported in SCL.
    
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
    '''
    This class defines a scene by reading a VCD file that contains coordinate systems, cameras, and objects.
    The Scene object brings projection functionalities such as creating warped images, converting objects from one coordinate system to another, etc.

    # Load a VCD file and create a Scene
    vcd = core.OpenLABEL('myOpenLABELfile.json')
    scene = scl.Scene(vcd)

    # Use the scene to get cameras
    camera_front = scene.get_camera('front')

    # Use cameras
    camera_front.project_points3d(points3d_4xN)

    '''
    def __init__(self, vcd):
        self.vcd = vcd
        self.cameras = dict()

    #########################################
    # Inner functions
    #########################################
    def __get_transform_chain(self, cs_src, cs_dst):
        # Create graph with the poses defined for each coordinate_system
        # These are poses valid "statically"
        lista = []
        root = self.vcd.get_root()
        for cs_name, cs_body in root['coordinate_systems'].items():
            for child in cs_body['children']:
                lista.append((cs_name, child, 1))
                lista.append((child, cs_name, 1))

        graph = Graph(lista)
        result = graph.dijkstra(cs_src, cs_dst)
        return result

    #########################################
    # Public functions
    #########################################
    def get_camera(self, camera_name, frameNum=None, compute_remaps=False):
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

        # Read basic info about streams
        root = self.vcd.get_root()
        if 'streams' in root:
            if camera_name in root['streams']:
                uri = root['streams'][camera_name]['uri']
                description = root['streams'][camera_name]['description']

        # Check if dynamic intrinsics
        dynamic_intrinsics = False
        if frameNum is not None:
            vcd_frame = self.vcd.get_frame(frameNum)    
            if 'frame_properties' in vcd_frame:
                if 'streams' in vcd_frame['frame_properties']:
                    if camera_name in vcd_frame['frame_properties']['streams']:
                        if 'stream_properties' in vcd_frame['frame_properties']['streams'][camera_name]:
                            sp = vcd_frame['frame_properties']['streams'][camera_name][
                                'stream_properties']
                            dynamic_intrinsics = True  # SO, there are dynamic intrinsics!
        
        # Read intrinsics and create/read existing camera
        camera = None
        if dynamic_intrinsics:
            # Create new camera
            vcd_frame = self.vcd.get_frame(frameNum)
            sp = vcd_frame['frame_properties']['streams'][camera_name][
                                'stream_properties']    
            if 'intrinsics_pinhole' in sp:
                camera = CameraPinhole(sp['intrinsics_pinhole'], camera_name, description, uri, compute_remaps)
            elif 'intrinsics_fisheye' in sp:
                camera = CameraFisheye(sp['intrinsics_fisheye'], camera_name, description, uri, compute_remaps)
            elif 'intrinsics_cylindrical' in sp:
                camera = CameraCylindrical(sp['intrinsics_cylindrical'], camera_name, description, uri)
            elif 'intrinsics_orthographic' in sp:
                camera = CameraOrthographic(sp['intrinsics_orthographic'], camera_name, description, uri)
            else:
                warnings.warn("WARNING: SCL does not support customized camera models. Supported types are CameraPinhole, CameraFisheye, CameraCylindrical and CameraOrthographic. See types.py.")
        else:
            # Read already created camera, or, if first time here, create one
            # Let's use f=-1
            f = -1
            if camera_name in self.cameras:
                if f in self.cameras[camera_name]:                    
                    return self.cameras[camera_name][f]['cam']  # return the one labeled as f=-1

            # Create camera m if needed
            if 'streams' in root:
                if camera_name in root['streams']:
                    uri = root['streams'][camera_name]['uri']
                    description = root['streams'][camera_name]['description']
                    if 'stream_properties' in root['streams'][camera_name]:
                        sp = root['streams'][camera_name]['stream_properties']
                        if 'intrinsics_pinhole' in sp:
                            camera = CameraPinhole(sp['intrinsics_pinhole'], camera_name, description, uri, compute_remaps)
                        elif 'intrinsics_fisheye' in sp:
                            camera = CameraFisheye(sp['intrinsics_fisheye'], camera_name, description, uri, compute_remaps)
                        elif 'intrinsics_cylindrical' in sp:
                            camera = CameraCylindrical(sp['intrinsics_cylindrical'], camera_name, description, uri)
                        elif 'intrinsics_orthographic' in sp:
                            camera = CameraOrthographic(sp['intrinsics_orthographic'], camera_name, description, uri)
                        else:
                            warnings.warn("WARNING: SCL does not support customized camera models. Supported types are CameraPinhole, CameraFisheye, CameraCylindrical and CameraOrthographic. See types.py.")
            else:
                return None        

        # Update store (f is -1 if static intrinsics are found, otherwise, a specific frameNum is used)
        self.cameras.setdefault(camera_name, {})
        self.cameras[camera_name].setdefault(f, {})
        self.cameras[camera_name][f]['cam'] = camera

        return camera

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
        root = self.vcd.get_root()
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
                if cs_2 == root['coordinate_systems'][cs_1]['parent']:
                    #t_4x4 = (
                    #    np.array([root['coordinate_systems'][cs_1]['pose_wrt_parent']['matrix4x4']]).reshape(4, 4)).dot(
                    #    t_4x4)
                    t_4x4 = utils.get_transform_as_matrix4x4(root['coordinate_systems'][cs_1]['pose_wrt_parent']) @ t_4x4
                elif cs_1 == root['coordinate_systems'][cs_2]['parent']:
                    #temp = np.array([root['coordinate_systems'][cs_2]['pose_wrt_parent']['matrix4x4']])
                    #t_4x4 = utils.inv(temp.reshape(4, 4)).dot(t_4x4)
                    temp = utils.get_transform_as_matrix4x4(root['coordinate_systems'][cs_2]['pose_wrt_parent'])
                    t_4x4 = utils.inv(temp) @ t_4x4
                    
            else:
                # So the user has asked for a specific frame, let's look for this frame if a transform exist
                transform_at_this_frame = False
                if frameNum in root['frames']:
                    if 'frame_properties' in root['frames'][frameNum]:
                        if 'transforms' in root['frames'][frameNum]['frame_properties']:
                            if t_name in root['frames'][frameNum]['frame_properties']['transforms']:
                                transform = root['frames'][frameNum]['frame_properties']['transforms'][t_name]
                                #assert('matrix4x4' in transform['transform_src_to_dst'])
                                #t_4x4 = (np.array([transform['transform_src_to_dst']['matrix4x4']]).reshape(4, 4)).dot(t_4x4)
                                t_4x4 = (utils.get_transform_as_matrix4x4(transform['transform_src_to_dst'])).dot(t_4x4)
                                static = False  # with one non-static step the entire chain can be considered not static
                                transform_at_this_frame = True
                            elif t_name_inv in root['frames'][frameNum]['frame_properties']['transforms']:
                                transform = root['frames'][frameNum]['frame_properties']['transforms'][
                                    t_name_inv]
                                #temp = np.array([transform['transform_src_to_dst']['matrix4x4']])
                                #t_4x4 = utils.inv(temp.reshape(4, 4)).dot(t_4x4)
                                temp = utils.get_transform_as_matrix4x4(transform['transform_src_to_dst'])
                                t_4x4 = utils.inv(temp) @ t_4x4
                                static = False
                                transform_at_this_frame = True
                if not transform_at_this_frame:
                    # Reached this point means no transforms were defined at the requested frameNum
                    # Check if this edge is from child to parent or viceversa
                    if cs_2 == root['coordinate_systems'][cs_1]['parent']:
                        #t_4x4 = (np.array([root['coordinate_systems'][cs_1]['pose_wrt_parent']['matrix4x4']]).reshape(4, 4)).\
                        #    dot(t_4x4)
                        t_4x4 = utils.get_transform_as_matrix4x4(root['coordinate_systems'][cs_1]['pose_wrt_parent']) @ t_4x4
                    elif cs_1 == root['coordinate_systems'][cs_2]['parent']:
                        #temp = np.array([root['coordinate_systems'][cs_2]['pose_wrt_parent']['matrix4x4']])
                        #t_4x4 = utils.inv(temp.reshape(4, 4)).dot(t_4x4)
                        temp = utils.get_transform_as_matrix4x4(root['coordinate_systems'][cs_2]['pose_wrt_parent'])
                        t_4x4 = utils.inv(temp) @ t_4x4

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

    def project_points3d_4xN(self, points3d_4xN, cs_src, cs_cam, frameNum=None, remove_outside=False):
        """
        This function projects 3D points into a given camera, specifying the origin coordinate system of the points,
        and a certain frame number. Optionally, distortion can be applied or not (e.g. sometimes is useful to project
        into the undistorted domain).
        :param points3d_4xN: array of 4xN 3D points in cs_src coordinate system
        :param cs_src: name of coordinate system of the points
        :param cs_cam: name of the camera
        :param frameNum: frame number (if None, static camera info is seeked)
        :param remove_outside: flag to invalidate points outside the limits of the image domain
        :return: array of 3xN 2D points in image coordinates (distorted or undistorted according to apply_distortion),
        and array of boolean declaring points valid or not
        """
        points3d_camera_cs_4xN = self.transform_points3d_4xN(points3d_4xN=points3d_4xN,
                                                             cs_src=cs_src, cs_dst=cs_cam,
                                                             frameNum=frameNum)
        if points3d_camera_cs_4xN is not None:
            cam = self.get_camera(camera_name=cs_cam, frameNum=frameNum)
            points2d_3xN, idx_valid = cam.project_points3d(points3d_4xN=points3d_camera_cs_4xN, remove_outside=remove_outside)
            return points2d_3xN, idx_valid
        return np.array([[]]), []

    @staticmethod
    def __plucker_line_plane_intersection(lines_3xN, plane_abcd):
        # Plucker intersection between Line and Plane
        # Use Plucker intersection line-plane
        # Create Plucker line using 2 points: origin of camera and origin of camera + ray
        N = lines_3xN.shape[1]
        idx_valid = [True] * N
        P1 = np.vstack((0, 0, 0, 1))
        P2array = np.vstack((lines_3xN, np.ones((1, N))))
        # Plane equation in plucker coordinates (wrt to world)
        P = np.asarray(plane_abcd).reshape(4, 1)
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

    def reproject_points2d_3xN_into_plane(self, points2d_3xN, plane, cs_cam, cs_dst, frameNum=None):
        # This function calls a camera (cs_cam) to reproject points2d in the image plane into
        # a plane defined in the cs_dst.
        # The obtained 3D points are expressed in cs_dst.
        # idx_valid identifies which points are valid 3D points (the reprojection might point to infinity)
        cam = self.get_camera(cs_cam, frameNum)
        plane_cam = self.transform_plane(plane, cs_dst, cs_cam, frameNum) # first convert plane into cam cs
        N = points2d_3xN.shape[1]
        
        # Reproject points as rays with camera
        rays3d_3xN_cs_cam = cam.reproject_points2d(points2d_3xN)
        points3d_3xN_cs_cam, idx_valid = self.__plucker_line_plane_intersection(rays3d_3xN_cs_cam, plane_cam)
        
        if points3d_3xN_cs_cam.shape[1] > 0:
            points3d_3xN_cs_cam_filt = points3d_3xN_cs_cam[:, idx_valid]
            points3d_4xN_cs_dst_filt = self.transform_points3d_4xN(points3d_3xN_cs_cam_filt, cs_cam, cs_dst, frameNum)
            points3d_4xN_cs_dst = np.full([4, N], np.nan)
            points3d_4xN_cs_dst[:, idx_valid] = points3d_4xN_cs_dst_filt
            return points3d_4xN_cs_dst, idx_valid
        return np.array([[]]), []
        

    def reproject_points2d_3xN(self, points2d_3xN, cs_cam, frameNum=None):
        cam = self.get_camera(cs_cam, frameNum)        
        rays3d_3xN = cam.reproject_points2d(points2d_3xN)
        return rays3d_3xN
        
    def create_img_projection_maps(self, cam_src_name, cam_dst_name, frameNum):
        ''' In SCL, extrinsic and intrinsic parameters are detached.
            Extrinsic parameters are defined at the VCD's coordinate systems.
            Intrinsic parameters are defined as VCD's stream_properties

            To create the projection maps, we need to take 2D pixels from cam_src, convert to 3D rays,
            then transform into 3D rays in cam_dst coordinate system, and then project into 2D pixels            
        '''
        # Get cameras
        cam_src = self.get_camera(cam_src_name, frameNum)
        cam_dst = self.get_camera(cam_dst_name, frameNum)

        # Get all pixels of dst image domain as a 3xN array        
        X, Y = np.mgrid[0:cam_dst.width:1, 0:cam_dst.height:1]        

        points2d_dst_3xN = np.row_stack((X.T.ravel(), Y.T.ravel(), np.ones(cam_dst.width * cam_dst.height, dtype=int))).reshape(3, cam_dst.width * cam_dst.height)

        # Reproject as rays3d in cam_dst coordinate system
        rays3d_dst_3xN = cam_dst.reproject_points2d(points2d_dst_3xN)

        # Convert into cam_src coordinate system
        rays3d_src_4xN = self.transform_points3d_4xN(utils.add_homogeneous_row(rays3d_dst_3xN), cam_dst_name, cam_src_name, frameNum)
        rays3d_src_4xN /= rays3d_src_4xN[3, :]        

        # Project into cam_src
        points2d_src_3xN, idx_valid = cam_src.project_points3d(rays3d_src_4xN)

        # Create maps for cv2.remap
        #u_map = np.zeros((cam_dst.height, cam_dst.width, 1), dtype=np.float32)        
        #v_map = np.zeros((cam_dst.height, cam_dst.width, 1), dtype=np.float32)        

        u_map = points2d_src_3xN[0, :].reshape(cam_dst.height, cam_dst.width, 1).astype('float32')
        v_map = points2d_src_3xN[1, :].reshape(cam_dst.height, cam_dst.width, 1).astype('float32')

        # Optimization
        map_x, map_y = cv.convertMaps(u_map, v_map, dstmap1type=cv.CV_16SC2, nninterpolation=False)

        # Application would then be: cv.remap(image, map_x, map_y, interpolation=interp, borderMode=cv.BORDER_REFLECT)

        # Return
        return map_x, map_y




        """generates maps for cv2.remap to remap from one camera to another
        u_map = np.zeros((destination_cam.height, destination_cam.width, 1), dtype=np.float32)
        v_map = np.zeros((destination_cam.height, destination_cam.width, 1), dtype=np.float32)

        destination_points_b = np.arange(destination_cam.height)

        for u_px in range(destination_cam.width):
            destination_points_a = np.ones(destination_cam.height) * u_px
            destination_points = np.vstack((destination_points_a, destination_points_b)).T

            source_points = source_cam.project_3d_to_2d(
                destination_cam.project_2d_to_3d(destination_points, norm=np.array([1])))

            u_map.T[0][u_px] = source_points.T[0]
            v_map.T[0][u_px] = source_points.T[1]

        map1, map2 = cv2.convertMaps(u_map, v_map, dstmap1type=cv2.CV_16SC2, nninterpolation=False)
        return map1, map2
        """


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

    def distort_rays3d(self, rays3d_3xN):
        '''
        This function distort rays3d using the distortion parameters of the camera.
        As a result distorted rays3d are created which can then be projected using the camera calibration matrix.

        :param rays3d_3xN: Array with N 3D rays, each of them as column (rx, ry, rz) 
        :return: rays3d_dist_3xN: Array with N distorted 3D rays, each of them as column (rx', ry', rz')
        '''
        pass

    def project_points3d(self, points3d_4xN, remove_outside=False):
        pass
        
    def reproject_points2d(self, points2d_3xN):
        pass


class CameraPinhole(Camera):
    """
    The Pinhole camera model defines a projection mechanism composed by two steps:

    - Linear projection: using the camera_matrix (K)
    - Radial/Tangential/... distortion: using distortion coefficients

    Distortion is assumed to be radial, as in:
    https://docs.opencv.org/4.2.0/d9/d0c/group__calib3d.html
    """
    def __init__(self, camera_intrinsics, name, description, uri, compute_remaps=False):
        self.K_3x4 = np.array(camera_intrinsics['camera_matrix_3x4']).reshape(3, 4)
        rows, cols, = self.K_3x4.shape
        assert (rows == 3 and cols == 4)
        self.K_3x3 = utils.fromCameraMatrix3x4toCameraMatrix3x3(self.K_3x4)
        d_list = camera_intrinsics['distortion_coeffs_1xN']
        self.d_1xN = np.array(d_list).reshape(1, len(d_list)) 

        self.r_limit = None
        if self.is_distorted():
            self.r_limit = utils.get_distortion_radius(self.d_1xN)       

        # Pre-compute undistortion maps (LUTs)
        self.img_size_dist = (camera_intrinsics['width_px'], camera_intrinsics['height_px'])
        self.img_size_undist = (camera_intrinsics['width_px'], camera_intrinsics['height_px'])

        if self.is_distorted():                        
            # alpha = 0.0 means NO black points in undistorted image
            # alpha = 1.0 means ALL distorted points inside limits of undistorted image
            aux = cv.getOptimalNewCameraMatrix(self.K_3x3, self.d_1xN, self.img_size_dist, alpha=0.0,
                                                            newImgSize=self.img_size_undist)
            self.K_und_3x3 = aux[0]
            self.mapX_to_und_16SC2 = None
            self.mapY_to_und_16SC2 = None
            if compute_remaps:
                self.__compute_remaps()
        else:
            self.K_und_3x3 = self.K_3x3

        self.K_und_3x4 = utils.fromCameraMatrix3x3toCameraMatrix3x4(self.K_und_3x3)

        Camera.__init__(self, camera_intrinsics['width_px'],
                        camera_intrinsics['height_px'],
                        name, description, uri)

    #################################
    # Inherited functions
    #################################
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

    def project_points3d(self, points3d_4xN, remove_outside=False):
        """
        This function projects 3D points into 2D points using the camera projection.
        All coordinates as homogeneous coordinates, and all 3D elements expressed wrt the camera coordinate system.

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

        # 1.- Select only those z > 0 (in front of the camera) - this assumption is good for pinhole cameras
        idx_in_front = points3d_4xN[2, :] > 1e-8
        idx_valid = idx_in_front
        rays3d_3xN_filt = points3d_4xN[0:3, idx_valid]

        # 2.- Distort rays3d if distorted        
        rays3d_3xN = np.full([3, N], np.nan) # init with NaN       
        rays3d_3xN[:, idx_valid] = rays3d_3xN_filt  # copy filtered points

        if self.is_distorted():
            # Cameras with distortion: need to first apply distortion model            
            # Pinhole distortion
            if self.r_limit is not None:                    
                # Some cameras have a valid radius limit: extreme points are wierdly distorted, it is better to keep them as NaN
                for i in range(0, N):
                    if idx_valid[i]:  # ignore those already filtered
                        xp = rays3d_3xN[0, i] / rays3d_3xN[2, i]  # this is x'=x/z as in opencv docs
                        yp = rays3d_3xN[1, i] / rays3d_3xN[2, i]  # this is y'=y/z
                        r = np.sqrt(xp * xp + yp * yp)

                        if r >= self.r_limit * 0.8:  # 0.8 to also remove very close to limit
                            idx_valid[i] = False
                            rays3d_3xN[:, i] = np.nan

            # Now distort (only non-nans)
            rays3d_3xN_filt = rays3d_3xN[:, idx_valid]
            rays3d_3xN_filt_dist = self.distort_rays3d(rays3d_3xN_filt) # no nan should go into it

            # Add nans
            rays3d_3xN[:, idx_valid] = rays3d_3xN_filt_dist

        # 3.- Project using calibration matrix
        rays3d_4xN = np.vstack((rays3d_3xN, np.ones(rays3d_3xN.shape[1])))
        points2d_3xN = self.K_3x4 @ rays3d_4xN
        points2d_3xN /= points2d_3xN[2,:]

        if remove_outside:
            points2d_3xN, idx_valid = utils.filter_outside(points2d_3xN, self.img_size_dist, idx_valid)

        return points2d_3xN, idx_valid

    def reproject_points2d(self, points2d_3xN):
        '''
        This function reprojects points in the image domain as rays in 3D coordinates (camera coordinate system)
        '''
        N = points2d_3xN.shape[1]       

        # Get rays3d applying K^-1 and then undistortion
        rays3d_dist_3xN = utils.normalize(utils.inv(self.K_3x3).dot(points2d_3xN))        
        rays3d_3xN = self.undistort_rays3d(rays3d_dist_3xN=rays3d_dist_3xN)        

        return rays3d_3xN

    def undistort_rays3d(self, rays3d_dist_3xN):
        points2d_dist_3xN = rays3d_dist_3xN / rays3d_dist_3xN[2, :]          
        N = points2d_dist_3xN.shape[1]
        if N < 1 or not self.is_distorted():
            return points2d_dist_3xN

        # Change shape from (3, N) to (N, 1, 2) so we can use OpenCV, removing homogeneous coordinate
        temp1 = points2d_dist_3xN[0:2, :]
        temp2 = utils.from_MxN_to_OpenCV_Nx1xM(temp1)

        # Use OpenCV functions (using an eye instead of K to work with rays instead of points)        
        temp3 = cv.undistortPoints(temp2, np.eye(3), self.d_1xN)

        # Reshape to (3, N)
        temp3.shape = (N, 2)
        points2d_und_3xN = np.vstack((temp3.T, np.ones((1, N))))
        rays3d_und_3xN = utils.normalize(points2d_und_3xN)
        return rays3d_und_3xN

    #################################
    # Other public functions
    #################################
    def undistort_image(self, img):
        if not self.is_distorted():
            return img
        if not self.__has_remaps():
            self.__compute_remaps()
        # cv.remap works for both models cv. and cv.fisheye
        return cv.remap(img, self.mapX_to_und_16SC2, self.mapY_to_und_16SC2, interpolation=cv.INTER_LINEAR,
                        borderMode=cv.BORDER_CONSTANT)

    def is_distorted(self):
        return np.count_nonzero(self.d_1xN) > 0

    def distort_points2d(self, points2d_und_3xN):
        """
        This is a function to project from undistorted to distorted images.
        :param points2d_und_3xN: undistorted points 3xN homogeneous coordinates
        :return: distorted points 3xN homogeneous coordinates
        """
        rays3d_und_3xN = utils.inv(self.K_und_3x3) @ points2d_und_3xN
        rays3d_dist_3xN = self.distort_rays3d(rays3d_und_3xN)
        points2d_dist_3xN = self.K_3x3 @ rays3d_dist_3xN
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
        temp3 = cv.undistortPoints(temp2, self.K_3x3, self.d_1xN)

        # Reshape to (3, N)
        temp3.shape = (N, 2)
        points2d_und_3xN = np.vstack((temp3.T, np.ones((1, N))))

        # Map into undistorted domain by using K_3x3_und
        points2d_und_3xN = self.K_und_3x3 @ points2d_und_3xN

        # TODO: Add this test to test_scl.py
        test = False
        if test:
            points2d_dist_re_3xN = self.distort_points2d(points2d_und_3xN)
            error = np.linalg.norm(points2d_dist_re_3xN - points2d_dist_3xN)
            print("Undistortion error: ", error)

        return points2d_und_3xN

    #################################
    # Inner functions 
    #################################
    def __has_remaps(self):
        if self.mapX_to_und_16SC2 is None or self.mapY_to_und_16SC2 is None:
            return False
        return True

    def __compute_remaps(self):
        start = time.time()
        self.mapX_to_und_16SC2, self.mapY_to_und_16SC2 = cv.initUndistortRectifyMap(self.K_3x3, self.d_1xN,
                                                                                    R=np.eye(3),
                                                                                    newCameraMatrix=self.K_und_3x3,
                                                                                    size=self.img_size_undist,
                                                                                    m1type=cv.CV_16SC2)
        end = time.time()
        print("CameraPinhole(radial): Compute remaps for undistortion... ", end - start)

    def __test_undistortion(self, img, img_und):
        # TODO: Move this to the set of tests
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


class CameraFisheye(Camera):
    '''
    Fisheye cameras, with field of view around 180º
    Different distortion models are considered.
    For simplicity, the projection process is splitted in two steps: ray distortion, and ray linear projection.
    '''
    def __init__(self, camera_intrinsics, name, description, uri, compute_remaps=False):
        self.cx = camera_intrinsics['center_x']
        self.cy = camera_intrinsics['center_y']
        self.img_size_dist = (camera_intrinsics['width_px'], camera_intrinsics['height_px'])
        self.img_size_undist = (camera_intrinsics['width_px'], camera_intrinsics['height_px'])

        if 'focal_length_x' in camera_intrinsics:
            self.focal_length_x = camera_intrinsics['focal_length_x']
            if 'focal_length_y' in camera_intrinsics:
                self.focal_length_y = camera_intrinsics['focal_length_y']
                self.aspect_ratio = self.focal_length_x / self.focal_length_y
            elif 'aspect_ratio' in camera_intrinsics:
                self.aspect_ratio = camera_intrinsics['aspect_ratio']
                self.focal_length_y = self.focal_length_x / self.aspect_ratio
            else:
                self.focal_length_y = self.focal_length_x
                self.aspect_ratio = 1.0
        else:
            self.focal_length_x = 1.0
            self.focal_length_y = 1.0
            self.aspect_ratio = 1.0
        
        self.K_3x4 = np.array([[self.focal_length_x, 0.0, self.cx, 0.0],
                               [0.0, self.focal_length_y, self.cy, 0.0],
                               [0.0, 0.0, 1.0, 0.0]])
        self.K_3x3 = utils.fromCameraMatrix3x4toCameraMatrix3x3(self.K_3x4)

        # Direct distortion (from angle of incidence to radius in image)
        dist_lenght = len(camera_intrinsics['lens_coeffs_1xN'])
        self.d_1xN = np.array(camera_intrinsics['lens_coeffs_1xN']).reshape(1, dist_lenght)
        self.model = camera_intrinsics['model']

        # Inverse distortion (from radius in image to incidence angle)
        self.error_a_deg = 0.0
        self.d_inv_1xM = self.__invert_polynomial(self.d_1xN, self.model)  # M is not necessarily N, we can use any polynomial to invert
        if compute_remaps:
            self.K_und_3x3 = self.estimate_new_camera_matrix_for_undistort_rectify(img_size_orig=self.img_size_dist,
                                                                                balance=0.9,
                                                                                img_size_dst=self.img_size_undist,
                                                                                fov_scale=1.0)
            self.K_und_3x4 = utils.fromCameraMatrix3x3toCameraMatrix3x4(self.K_und_3x3)

            self.mapX_to_und_16SC2 = None
            self.mapY_to_und_16SC2 = None

        if compute_remaps:
            self.__compute_remaps()

        Camera.__init__(self, camera_intrinsics['width_px'],
                        camera_intrinsics['height_px'],
                        name, description, uri)

    #################################
    # Inherited functions
    #################################
    def distort_rays3d(self, rays3d_3xN):
        """
        This function projects 3d points in camera coordinate system using the angle-of-incidence projection model.
        Any 3D point in space P=(X,Y,Z,1)^T has a radius with respect to the optical axis Z
        r = ||X^2 + Y^2||
        The angle of incidence to the optical center is
        a = atan(r/Z)

        The angle of incidence then spans from 0 to pi/2
        The model of the lens relates the angle of incidence with the radius of the point in the image plane (in pixels):
        "radial_poly" (4 distortion coefficients)
            rp = k1*a + k2*a^2 + k3*a^3 + k4*a^4
        "kannala" (5 distortion coefficients)
            rp = k1*a + k2*a^3 + k3*a^5 + k4*a^7 + k5*a^9
        "opencv_fisheye" (4 distortion coefficients, equivalent to Kannala with k1=1.0, so only the last 4 terms are used
            rp = a + k1*a^3 + k2*a^5 + k3*a^7 + k4*a^9         

        Then, the distorted 3d rays are computed as:
        ray_dist = (X*rp/r, Y*rp/r, 1)

        :param rays3d_3xN: 3d rays as 3xN arrays
        :return: distorted 3d rays as 3xN arrays after applying distortion function.
        """
        N = rays3d_3xN.shape[1]
        if N == 0 or not self.is_distorted():
            rays3d_dist_3xN = np.array([[]])
            return rays3d_dist_3xN

        rays3d_dist_3xN = np.zeros((3, N))
        for i in range(0, N):
            X = rays3d_3xN[0, i]
            Y = rays3d_3xN[1, i]
            Z = rays3d_3xN[2, i]
            r = utils.norm([X, Y])
            a = math.atan2(r, Z)
            rp = self.__apply_polynomial(a, self.d_1xN.flatten().tolist(), self.model)  # direct distortion, use specified model
            rp_r = float(rp/r)
            if r > 1e-8:
                rays3d_dist_3xN[0, i] = X * rp_r
                rays3d_dist_3xN[1, i] = Y * rp_r
                rays3d_dist_3xN[2, i] = 1
            else:
                rays3d_dist_3xN[0, i] = 0
                rays3d_dist_3xN[1, i] = 0
                rays3d_dist_3xN[2, i] = 1

        return rays3d_dist_3xN

    def project_points3d(self, points3d_4xN, remove_outside=False):
        """
        This function projects 3d points in camera coordinate system into the image plane.
        First, 3d points P=(X,Y,Z,1)^T are treated as 3d rays, and distorted using the angle of incidence equation.
        Distorted 3d rays are then projected using the linear camera calibration matrix K.        

        :param points3d_4xN: 3D points in camera coordinate system        
        :param remove_outside: filter out points that fall outside the limits of the image frame.
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

        # Now distort (only non-nans)
        rays3d_3xN_filt = rays3d_3xN[:, idx_valid]
        rays3d_3xN_filt_dist = self.distort_rays3d(rays3d_3xN_filt)  # no nan should go into it

        # DEBUG
        #temp = self.undistort_rays3d(rays3d_3xN_filt_dist)
        #error = np.linalg.norm(rays3d_3xN_filt - temp)

        # Add nans
        rays3d_3xN = np.full([3, N], np.nan)
        rays3d_3xN[:, idx_valid] = rays3d_3xN_filt_dist

        # 3.- Project using calibration matrix        
        points2d_3xN = self.K_3x3.dot(rays3d_3xN)
        if remove_outside:
            points2d_3xN, idx_valid = utils.filter_outside(points2d_3xN, self.img_size_dist, idx_valid)        

        return points2d_3xN, idx_valid

    def reproject_points2d(self, points2d_3xN):
        N = points2d_3xN.shape[1]       

        # Get rays3d applying K^-1 and then undistortion
        rays3d_dist_3xN = utils.inv(self.K_3x3).dot(points2d_3xN)
        rays3d_3xN = self.undistort_rays3d(rays3d_dist_3xN=rays3d_dist_3xN)

        return rays3d_3xN

    #################################
    # Inner functions 
    #################################
    def __has_remaps(self):
        if self.mapX_to_und_16SC2 is None or self.mapY_to_und_16SC2 is None:
            return False
        return True

    def __compute_remaps(self):
        start = time.time()
        self.mapX_to_und_16SC2, self.mapY_to_und_16SC2 = self.init_undistort_rectify_map(self.K_und_3x3,
                                                                                         self.img_size_undist)
        end = time.time()
        print("CameraFisheye: Compute remaps for undistortion... ", end - start)

    def __polynomial_with_offset(self, x, k1, k2, k3, k4, k5, k6, k7, k8, k9):
        x2 = x * x
        x3 = x2 * x
        x4 = x3 * x
        x5 = x4 * x
        x6 = x5 * x
        x7 = x6 * x
        x8 = x7 * x
        return k1 + x*k2 + x2*k3 + x3*k4 + x4*k5 + x5*k6 + x6*k7 + x7*k8 + x8*k9

    def __radialpoly_model_function(self, x, k1, k2, k3, k4):
        x2 = x * x
        x3 = x2 * x
        x4 = x3 * x
        return x * k1 + x2 * k2 + x3 * k3 + x4 * k4

    def __kannala_model_function(self, x, k1, k2, k3, k4, k5):
        x2 = x * x
        x3 = x2 * x
        x5 = x3 * x2
        x7 = x5 * x2
        x9 = x7 * x2
        return x * k1 + x3 * k2 + x5 * k3 + x7 * k4 + x9 * k5

    def __apply_polynomial(self, x, k, model=None):
        if model == 'radial_poly':      
            return self.__radialpoly_model_function(x, k[0], k[1], k[2], k[3])            
        elif model == 'kannala':            
            return self.__kannala_model_function(x, k[0], k[1], k[2], k[3], k[4])   
        elif model == 'polynomial_offset':
            return self.__polynomial_with_offset(x, k[0], k[1], k[2], k[3], k[4], k[5], k[6], k[7], k[8])  
        else:
            warnings.warn('Unsupported distortion model. Use radial_poly, kannala or polynomial_offset')
            return None
    
    def __invert_polynomial(self, d, model, n=100):
        a = np.linspace(0, np.pi/2, num=n)        
        k_list = d.flatten().tolist()
        
        rp = self.__apply_polynomial(a, k_list, model)  # direct distortion, using model

        # For the inverse polynomial, we can use numpy's polyfit, which fits p(x)=p(0)*x**deg + ... + p(deg)
        dim = 9 # dimensions of the offset polynomial to represent the inverse distortion
        kp = np.polyfit(rp, a, dim-1)  # polyfit return reversed coefficients with offset
        kp_list = kp.tolist()
        kp_list.reverse()  # kp_list[-1] is the offset
        a_rep = self.__apply_polynomial(rp, kp_list, 'polynomial_offset')

        error_a = np.sum(np.abs(a-a_rep)) / n
        self.error_a_deg = error_a * 180 / np.pi

        #fig, (ax1, ax2) = plt.subplots(1, 2)
        #fig.suptitle('Distortion')
        #ax1.plot(a, rp)
        #ax1.set(xlabel='a', ylabel='rp', title='Distortion direct')
        #ax1.grid()
        #ax2.plot(a_rep, rp)
        #ax2.set(xlabel='a_rep', ylabel='rp', title='Distortion reprojected')
        #fig.savefig('distortion_ret.png')
        #plt.show()

        if self.error_a_deg > 1e-1:
            warnings.warn("WARNING: the inverse of the CameraFisheye distortion produces reprojection error > 1e-2 "
                            "(i.e. higher than tenth of degree")

        return np.array(kp_list)

    #################################
    # Other public functions
    #################################
    def undistort_image(self, img):
        if not self.is_distorted():
            return img
        if not self.__has_remaps():
            self.__compute_remaps()
        return cv.remap(img, self.mapX_to_und_16SC2, self.mapY_to_und_16SC2, interpolation=cv.INTER_LINEAR,
                        borderMode=cv.BORDER_CONSTANT)

    def undistort_points2d(self, points2d_dist_3xN):
        # This is a transfer from the distorted to the undistorted
        rays3d_dist_3xN = utils.inv(self.K_3x3).dot(points2d_dist_3xN)
        rays3d_und_3xN = self.undistort_rays3d(rays3d_dist_3xN)
        points2d_und_3xN = self.K_und_3x3.dot(rays3d_und_3xN)

        return points2d_und_3xN

    def distort_points2d(self, points2d_und_3xN):
        # This is a transfer from the undistorted domain to the distorted
        rays3d_und_3xN = utils.inv(self.K_und_3x3).dot(points2d_und_3xN)
        rays3d_dist_3xN = self.distort_rays3d(rays3d_und_3xN) # TODO: better to use self.project_points?
        points2d_dist_3xN = self.K_3x3.dot(rays3d_dist_3xN)

        return points2d_dist_3xN

    def is_distorted(self):
        return np.count_nonzero(self.d_1xN) > 0

    def undistort_rays3d(self, rays3d_dist_3xN):
        """
        This function undistort 3d rays according to the inverse polynomial function.
        :param rays3d_dist_3xN: 3d rays (connecting optical center and image plane using K)
        :return: undistorted rays as 3xN
        """
        N = rays3d_dist_3xN.shape[1]
        if N == 0 or not self.is_distorted():
            rays3d_und_3xN = np.array([[]])
            return rays3d_und_3xN

        rays3d_und_3xN = np.zeros((3, N))
        for i in range(0, N):
            X = rays3d_dist_3xN[0, i]
            Y = rays3d_dist_3xN[1, i]
            rp = utils.norm([X, Y])
            a = self.__apply_polynomial(rp, self.d_inv_1xM.flatten().tolist(), "polynomial_offset") # NOTE: the inverse polynomial is fixed to dim=4 with offset
            r = math.tan(a)
            r_rp = float(r / rp)
            if rp > 1e-8:
                rays3d_und_3xN[0, i] = X * r_rp
                rays3d_und_3xN[1, i] = Y * r_rp
                rays3d_und_3xN[2, i] = 1
            else:
                rays3d_und_3xN[0, i] = 0
                rays3d_und_3xN[1, i] = 0
                rays3d_und_3xN[2, i] = 1

        return rays3d_und_3xN

    def init_undistort_rectify_map(self, K_und_3x3, img_size_undist):
        # Create maps
        w = img_size_undist[0]
        h = img_size_undist[1]
        map1 = np.zeros((h, w), dtype=np.float32)
        map2 = np.zeros((h, w), dtype=np.float32)

        # Loop over undistorted domain
        for i in range(0, h):
            # Read all pixel pos of this row
            points2d_und_3xN = np.array([np.linspace(0, w-1, num=w),
                                    i*np.ones(w),
                                    np.ones(w)])

            # Un-apply K_und to get the undistorted ray
            ray3d_und_3xN = utils.inv(K_und_3x3).dot(points2d_und_3xN)
            ray3d_und_3xN[0:3, :] = ray3d_und_3xN[0:3, :] / ray3d_und_3xN[2, :]
            ray3d_und_4xN = np.vstack((ray3d_und_3xN, np.ones(w)))

            # Project
            points2d_dist_3xN, idx_valid = self.project_points3d(ray3d_und_4xN)

            # Assign into map
            map1[i, :] = points2d_dist_3xN[0, :]
            map2[i, :] = points2d_dist_3xN[1, :]

        # Return the maps
        return map1, map2

    def estimate_new_camera_matrix_for_undistort_rectify(self, img_size_orig, balance, img_size_dst, fov_scale):
        balance = min(max(balance, 0.0), 1.0)
        w = img_size_orig[0]
        h = img_size_orig[1]
        romboid_points = np.array([[w/2, 0, 1],
                                   [w, h/2, 1],
                                   [w/2, h, 1],
                                   [0, h/2, 1]]).transpose()

        rays3d_und_3xN = self.undistort_rays3d(romboid_points)
        center_mass = cv.mean(rays3d_und_3xN)
        cn = center_mass
        aspect_ratio = 1.0

        # Find maxima
        minx = float('inf')
        miny = float('inf')
        maxx = -float('inf')
        maxy = -float('inf')
        for i in range(0, 4):
            miny = min(miny, rays3d_und_3xN[1, i])
            maxy = max(maxy, rays3d_und_3xN[1, i])
            minx = min(minx, rays3d_und_3xN[0, i])
            maxx = max(maxx, rays3d_und_3xN[0, i])

        f1 = w *0.5/(cn[0] - minx)
        f2 = w * 0.5 / (maxx - cn[0])
        f3 = h * 0.5 * aspect_ratio / (cn[1] - miny)
        f4 = h * 0.5 * aspect_ratio / (maxy - cn[1])

        fmin = min(f1, min(f2, min(f3, f4)))
        fmax = max(f1, max(f2, max(f3, f4)))

        f = balance * fmin + (1.0 - balance)*fmax
        if fov_scale > 0:
            f *= (1.0/fov_scale)

        new_f = (f, f/aspect_ratio)
        new_c = (w*0.5 - cn[0] * f, ((h*aspect_ratio)*0.5 - cn[0] * f)/aspect_ratio)

        rx = img_size_dst[0] / img_size_orig[0]
        ry = img_size_dst[1] / img_size_orig[1]

        K_new = np.array([[new_f[0]*rx, 0, new_c[0]*rx],
                          [0, new_f[1]*ry, new_c[1]*ry],
                          [0, 0, 1]])

        return K_new


class CameraCylindrical(Camera):
    def __init__(self, camera_intrinsics, name, description, uri):
        Camera.__init__(self, camera_intrinsics['width_px'],
                        camera_intrinsics['height_px'],
                        name, description, uri)

        self.img_size = (self.width, self.height)
        self.fovh = camera_intrinsics['fov_horz_rad']
        self.fovv = camera_intrinsics['fov_vert_rad']
        
        # Converting from [fovh, 0] into [0, width]
        self.mx = -self.width / self.fovh
        self.nx = self.width
        # Converting from [fovv/2, -fovv/2] into [0, height]
        self.my = -self.height / self.fovv
        self.ny = self.height/2.0

        # Create calibration matrix
        self.K_3x4 = np.array([[self.mx, 0.0, self.nx, 0.0],
                               [0.0, self.my, self.ny, 0.0],
                               [0.0, 0.0, 1.0, 0.0]])
        self.K_3x3 = utils.fromCameraMatrix3x4toCameraMatrix3x3(self.K_3x4)
        self.K_3x3_inv = utils.inv(self.K_3x3)

    #################################
    # Inherited functions
    #################################
    def distort_rays3d(self, rays3d_3xN):
        '''
        Cylindrical cameras don't have distortion
        '''
        return rays3d_3xN

    def project_points3d(self, points3d_4xN, remove_outside=False):
        # 1.- Select only those z > 0 (in front of the camera)
        idx_in_front = points3d_4xN[2, :] > 1e-8
        idx_valid = idx_in_front
        #rays3d_3xN_filt = points3d_4xN[0:3, idx_valid]
        rays3d_3xN_filt = points3d_4xN[0:3]#, idx_valid]

        # Two-step process: use Ray2LL and the LL2Pixel
        lonlat_2xN = self.__ray2LL(rays3d_3xN_filt, idx_valid)
        points2d_3xN = self.__LL2Pixel(lonlat_2xN)

        # Declare as non-valid points outisde the limits of the image        
        N = points2d_3xN.shape[1]
        if remove_outside:
            points2d_3xN, idx_valid = utils.filter_outside(points2d_3xN, self.img_size, idx_valid)

        return points2d_3xN, idx_valid

    def reproject_points2d(self, points2d_3xN):
        lonlat_2xN = self.__pixel2LL(points2d_3xN)
        return self.__LL2ray(lonlat_2xN)

    #################################
    # Inner functions
    #################################
    # ----------------------------------------------#
    #                From 2D --> 3D                 #
    # ----------------------------------------------#
    def __LL2ray(self, lonlat_2xN):        
        lon = lonlat_2xN[0, :]
        lat = lonlat_2xN[1, :]        
        x = np.cos(lon) * np.cos(lat)
        y = -np.sin(lat)        
        z = np.sin(lon) * np.cos(lat)        

        points3d_3xN = np.vstack((np.vstack((x, y)), z))
        return points3d_3xN

    def __pixel2LL(self, points2d_3xN):
        # See LL2Ray
        #lon = (1/self.mx)*(x-self.nx)
        #lat = (1/self.my)*(y-self.ny)

        lonlat_3xN = self.K_3x3_inv @ points2d_3xN
        lonlat_3xN /= lonlat_3xN[2,:]

        return lonlat_3xN[0:2, :]    

    # ----------------------------------------------
    # From 3D -> 2D
    # ----------------------------------------------
    def __ray2LL(self, ray3d_4xN, idx_valid):
        # See http://paulbourke.net/dome/dualfish2sphere/ but modified so the camera model is z-optical axis, x-right, y-bottom
        X = ray3d_4xN[0, :]
        Y = ray3d_4xN[1, :]
        Z = ray3d_4xN[2, :]

        lon_1xN = np.zeros(X.shape)
        np.arctan2(Z, X, out=lon_1xN, where=idx_valid)
        lat_1xN = np.zeros(Y.shape)
        np.arctan2(-Y, np.sqrt(X*X + Z*Z), out=lat_1xN, where=idx_valid)

        #lon_1xN = np.arctan2(ray3d_4xN[1,:], ray3d_4xN[0,:])
        #lat_1xN = np.arctan2(ray3d_4xN[2,:], np.sqrt(ray3d_4xN[0,:]*ray3d_4xN[0,:] + ray3d_4xN[1,:]*ray3d_4xN[1,:]))
        lonlat_2xN = np.vstack((lon_1xN, lat_1xN))
        return lonlat_2xN

    def __LL2Pixel(self, lonlat_2xN):
        lonlat_3xN = np.vstack((lonlat_2xN, np.ones((1, lonlat_2xN.shape[1]))))
        points2d_3xN = self.K_3x3 @ lonlat_3xN
        #px = self.mx*lon + self.nx
        #py = self.my*lat + self.ny
        return points2d_3xN


class CameraOrthographic(Camera):
    '''
    This is a special type of camera which does not project 3d entities using a pinhole nor distorted lens.
    It does project 3d points into the Z_cam = 0 image plane keeping their X_cam and Y_cam values.
    A rectangular frustrum is created defining the (xmax, xmin, ymax, ymin) clipping planes (in camera coordinate system).
    To keep coherency with other Cameras in VCD, the camera model has Z-front, X-right, Y-bottom.

    An additional scaling and centering camera calibration matrix is used to create images with desired number of pixels.
    '''
    def __init__(self, camera_intrinsics, name, description, uri):
        Camera.__init__(self, camera_intrinsics['width_px'],
                        camera_intrinsics['height_px'],
                        name, description, uri)

        self.img_size = (self.width, self.height)
        self.xmax = camera_intrinsics['xmax']
        self.xmin = camera_intrinsics['xmin']
        self.ymax = camera_intrinsics['ymax']
        self.ymin = camera_intrinsics['ymin']

        # Create calibration matrix
        self.K_3x4 = np.array([[self.width*(1.0/(self.xmax-self.xmin)), 0.0, 0.0, self.width/2.0],
                               [0.0, self.height*(1.0/(self.ymax-self.ymin)), 0.0, self.height/2.0],
                               [0.0, 0.0, 0.0, 0.0]])
        #self.K_3x3 = utils.fromCameraMatrix3x4toCameraMatrix3x3(self.K_3x4)
        
        # Note that the orthographic projection matrix is not invertible in homogeneous form. Let's do it manually
        self.K_3x4_inv = np.array([[(self.xmax-self.xmin)/self.width, 0.0, -self.width/2.0, 0.0],
                               [0.0, (self.ymax-self.ymin)/self.height, -self.height/2.0, 0.0],
                               [0.0, 0.0, 0.0, 0.0]])                
        self.K_3x3_inv = utils.fromCameraMatrix3x4toCameraMatrix3x3(self.K_3x4_inv)

    #################################
    # Inherited functions
    #################################
    def distort_rays3d(self, rays3d_3xN):
        # Orthographic cameras don't have distortion
        return rays3d_3xN
    
    def project_points3d(self, points3d_4xN, remove_outside=False):
        # 0.- Pre-filter
        assert (points3d_4xN.ndim == 2)
        N = points3d_4xN.shape[1]
        if N == 0:
            return np.array([[]]), []

        # 1.- Select only those within limits
        idx_is_inside = (
            (points3d_4xN[0, :] > self.xmin) &
            (points3d_4xN[0, :] < self.xmax) &
            (points3d_4xN[1, :] > self.ymin) &
            (points3d_4xN[1, :] < self.ymax) &
            (points3d_4xN[2, :] > 1e-8)
        )
        
        idx_valid = idx_is_inside
        #rays3d_3xN_filt = points3d_4xN[0:3, idx_valid]
        
        # 2.- Project using calibration matrix
        #rays3d_4xN = np.vstack((rays3d_3xN_filt, np.ones(rays3d_3xN_filt.shape[1])))
        #rays3d_4xN = np.vstack((rays3d_3xN_filt, np.ones(rays3d_3xN_filt.shape[1])))
        
        points2d_3xN = self.K_3x4 @ points3d_4xN
        #points2d_3xN /= points2d_3xN[2,:] NOTE: Ortographic projection is no friend of homogeneous coordinates

        if remove_outside:
            points2d_3xN, idx_valid = utils.filter_outside(points2d_3xN, (self.width, self.height), idx_valid)

        return points2d_3xN, idx_valid

    def reproject_points2d(self, points2d_3xN):        
        rays3d_3xN = utils.normalize(utils.inv(self.K_3x3_inv) @ points2d_3xN)
        return rays3d_3xN
        
    