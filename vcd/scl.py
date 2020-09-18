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

    def get_camera(self, camera_name, frameNum=None):
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
        return camera

    def get_transform(self, cs_src, cs_dst, frameNum=None):
        assert (self.vcd.has_coordinate_system(cs_src))
        assert (self.vcd.has_coordinate_system(cs_dst))

        if cs_src == cs_dst:
            return np.identity(4, dtype=float).flatten().tolist()

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
        for cs_name, cs_body in self.vcd.data['vcd']['coordinate_systems'].items():
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
                                transform_at_this_frame = True
                            elif t_name_inv in self.vcd.data['vcd']['frames'][frameNum]['frame_properties']['transforms']:
                                transform = self.vcd.data['vcd']['frames'][frameNum]['frame_properties']['transforms'][
                                    t_name_inv]
                                temp = np.array([transform['transform_src_to_dst_4x4']])
                                t_4x4 = utils.inv(temp.reshape(4, 4)).dot(t_4x4)
                                transform_at_this_frame = True
                if not transform_at_this_frame:
                    # Check if this edge is from child to parent or viceversa
                    if cs_2 == self.vcd.data['vcd']['coordinate_systems'][cs_1]['parent']:
                        t_4x4 = (np.array([self.vcd.data['vcd']['coordinate_systems'][cs_1]['pose_wrt_parent']]).reshape(4,
                                                                                                                    4)).dot(
                            t_4x4)
                    elif cs_1 == self.vcd.data['vcd']['coordinate_systems'][cs_2]['parent']:
                        temp = np.array([self.vcd.data['vcd']['coordinate_systems'][cs_2]['pose_wrt_parent']])
                        t_4x4 = utils.inv(temp.reshape(4, 4)).dot(t_4x4)

        return t_4x4.flatten().tolist()

    def transform_points3d_4xN(self, points3d_4xN, cs_src, cs_dst, frameNum=None):
        transform_src_dst = np.array(self.get_transform(cs_src, cs_dst, frameNum)).reshape(4, 4)
        if transform_src_dst is not None:
            points3d_dst_4xN = utils.transform_points3d_4xN(points3d_4xN, transform_src_dst)
            return points3d_dst_4xN
        else:
            return None

    def transform_cuboid(self, cuboid_vals, cs_src, cs_dst, frameNum=None):
        transform_src_dst = self.get_transform(cs_src, cs_dst, frameNum)

        if transform_src_dst is not None:
            cuboid_vals_transformed = utils.transform_cuboid(cuboid_vals, transform_src_dst)
            return cuboid_vals_transformed
        else:
            return cuboid_vals

    def transform_plane(self, plane_abcd, cs_src, cs_dst, frameNum=None):
        transform_src_dst = self.get_transform(cs_src, cs_dst, frameNum)
        if transform_src_dst is not None:
            plane_abcd_transformed = utils.transform_plane(plane_abcd, transform_src_dst)
            return plane_abcd_transformed
        else:
            return plane_abcd

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
        pass

    def project_points3d(self, points3d_4xN, timestamp=None):
        pass

    def image_to_plane(self, points2d_3xN, plane_world):
        pass


class CameraPinhole(Camera):
    """
    The Pinhole camera model defines a projection mechanism composed by two steps:

    - Linear projection: using the camera_matrix (K)
    - Radial/Tangential/... distortion: using distortion coefficients

    See https://docs.opencv.org/4.2.0/d9/d0c/group__calib3d.html
    '"""
    def __init__(self, camera_intrinsics, name, description, uri):
        self.K_3x4 = np.array(camera_intrinsics['camera_matrix_3x4']).reshape(3, 4)
        rows, cols, = self.K_3x4.shape
        assert (rows == 3 and cols == 4)
        self.K_3x3 = utils.fromCameraMatrix3x4toCameraMatrix3x3(self.K_3x4)

        self.fx = self.K_3x4[0, 0]
        self.fy = self.K_3x4[1, 1]
        self.cx = self.K_3x4[0, 2]
        self.cy = self.K_3x4[1, 2]
        d_list = camera_intrinsics['distortion_coeffs_1xN']
        self.d = np.array(d_list).reshape(1, len(d_list))

        self.r_limit = None
        if self.is_distorted():
            self.r_limit = utils.get_distortion_radius(self.d)

        Camera.__init__(self, camera_intrinsics['width_px'],
                        camera_intrinsics['height_px'],
                        name, description, uri)

    # TODO
    def get_horizon_lines(self, apply_distortion=True):
        pass
    #def get_ray_intersection(self, ray ):

    # TODO
    def get_rays(self, point2d_3xN):
        ray = np.matmul((np.linalg.inv(self.K_3x3)), point2d_3xN)
        ray /= np.linalg.norm(ray)
        ray3d_4xN = np.vstack((ray, np.ones((1, point2d_3xN.shape[1]))))
        return ray3d_4xN

    def is_distorted(self):
        return np.count_nonzero(self.d) > 0

    def distort_points2d(self, points2d_und_3xN):
        # Note this function first "unproject" points, by doing (x-cx)/fx, and (y-cy)/fy
        # so it can be conveniently used after projecting 3D points into 2D image.
        # The rationale behind is that radial distortion is applied before projecting with K
        # See https://docs.opencv.org/2.4/modules/calib3d/doc/camera_calibration_and_3d_reconstruction.html
        points2d_dist_3xN = np.ones(points2d_und_3xN.shape, dtype=np.float)

        count = 0
        for point2d_und in points2d_und_3xN.transpose():
            # Apply radial distortion (using 3 radial parameters)
            x = (point2d_und[0] - self.cx) / self.fx
            y = (point2d_und[1] - self.cy) / self.fy
            r2 = x*x + y*y
            r4 = r2*r2
            r6 = r4*r2

            # Read only parameters of radial distortion
            k1 = self.d[0, 0]
            k2 = self.d[0, 1]
            p1 = self.d[0, 2]
            p2 = self.d[0, 3]
            k3 = self.d[0, 4]

            den = 1.0
            if len(self.d) == 8:
                k4 = self.d[0, 5]
                k5 = self.d[0, 6]
                k6 = self.d[0, 7]
                den = (1 + k4 * r2 + k5 * r4 + k6 * r6)

            xd = x * (1 + k1 * r2 + k2 * r4 + k3 * r6) / den
            yd = y * (1 + k1 * r2 + k2 * r4 + k3 * r6) / den

            # print(x, '*( 1.0 + ', k1*r2, ' + ', k2*r4, ' + ', k3*r6, ') = ', xd, 'dev x: ', (1 + k1*r2 + k2*r4 + k3*r6))

            if p1 != 0.0 or p2 != 0.0:
                xd += 2 * p1 * x * y + p2 * (r2 + 2 * x * x)
                yd += p1 * (r2 + 2 * y * y) + p2 * x * y

            xd = xd * self.fx + self.cx
            yd = yd * self.fy + self.cy

            points2d_dist_3xN[0, count] = utils.round(xd)
            points2d_dist_3xN[1, count] = utils.round(yd)
            count += 1

        return points2d_dist_3xN

    def undistort_points2d(self, points2d_dist_3xN):
        shape = points2d_dist_3xN.shape
        assert(points2d_dist_3xN.ndim == 2)
        assert(shape[0] == 3 and shape[1] >= 1)
        # Change shape to (N, 1, 2) so we can use OpenCV

        temp1 = np.delete(points2d_dist_3xN,(2),axis=0)
        temp1 = temp1.astype(float)

        K_3x3 = utils.fromCameraMatrix3x4toCameraMatrix3x3(self.K_3x4)
        dist_coeffs_Nx1 = self.d.transpose()  # Is this needed?
        temp2 = cv.undistortPoints(temp1, K_3x3, dist_coeffs_Nx1)
        temp2.shape = (shape[1], 2)
        points2d_und_3xN = np.vstack((temp2.T, np.ones((1, shape[1]))))
        #points2d_scs_und_3xN = np.array([[self.fx, self.fy, 1.0]]).dot(temp3)
        points2d_und_3xN[0, :] = points2d_und_3xN[0, :].dot(self.fx) + self.cx
        points2d_und_3xN[1, :] = points2d_und_3xN[1, :].dot(self.fy) + self.cy

        return points2d_und_3xN

    def project_points3d(self, points3d_4xN):
        rows, cols = points3d_4xN.shape
        assert(points3d_4xN.ndim == 2)
        assert(rows == 4 and cols >= 1)

        # Select only those z > 0 (in front of the camera)
        idx_in_front = points3d_4xN[2, :] > 0.0
        points3d_4xN = points3d_4xN[:, idx_in_front]
        N = points3d_4xN.shape[1]

        if N == 0:
            return None

        # Let's NOT use OpenCV's function, because for some distortions it maps incorrectly points which are distant
        # to the image center
        use_opencv = False
        if use_opencv:
            points3d_3xN = points3d_4xN[0:3, :]
            points3d_3xN.reshape(N, 1, 3)
            K_3x3 = utils.fromCameraMatrix3x4toCameraMatrix3x3(self.K_3x4)
            points2d_2xN = cv.projectPoints(points3d_3xN, rvec=np.zeros(3), tvec=np.zeros(3),
                                            cameraMatrix=K_3x3, distCoeffs=self.d)  # returns a list of 2 ndarrays with N entries
            points2d_2xN = np.squeeze(points2d_2xN[0]).T  # results are on [0], not sure what [1] contains
            points2d_3xN = np.vstack((points2d_2xN, np.ones((1, N))))

            return points2d_3xN
        else:
            if self.is_distorted():
                # Distortion needs to be applied
                # We can call directly distort_points2d_scs, which internally calibrates the coordinates
                # However, we can first check if the projection will yield correct values
                if self.r_limit is not None:
                    # So there is a limit we can compute, a little beyond the limits of the image
                    N = points3d_4xN.shape[1]
                    idx_to_add = [True] * N
                    for i in range(0, N):
                        xp = points3d_4xN[0, i] / points3d_4xN[2, i]  # this is x'=x/z as in opencv docs
                        yp = points3d_4xN[1, i] / points3d_4xN[2, i]  # this is y'=y/z
                        r = np.sqrt(xp*xp + yp*yp)

                        if r >= self.r_limit:
                            idx_to_add[i] = False
                    # Filter...
                    points3d_4xN = points3d_4xN[:, idx_to_add]
                    # ... project...
                    points2d_3xN = np.dot(self.K_3x4, points3d_4xN)
                    # ... and normalize
                    points2d_3xN[0:3, :] = points2d_3xN[0:3, :] / points2d_3xN[2, :]  # normalize
                else:
                    # Limit to image range
                    points2d_3xN = np.dot(self.K_3x4, points3d_4xN)
                    points2d_3xN[0:3, :] = points2d_3xN[0:3, :] / points2d_3xN[2, :]  # normalize
                    N = points3d_4xN.shape[1]
                    idx_to_add = [False] * N
                    for i in range(0, N):
                        x = points2d_3xN[0, i]
                        y = points2d_3xN[1, i]
                        if 0<=x<self.width and 0<=y<self.height:
                            idx_to_add[i] = True
                    points2d_3xN = points2d_3xN[:, idx_to_add]

                # Now distort
                return self.distort_points2d(points2d_3xN)

                return points2d_3xN
            else:
                # Simplest case: just project using K and normalize to get 2d values
                points2d_3xN = np.dot(self.K_3x4, points3d_4xN)
                points2d_3xN[0:3, :] = points2d_3xN[0:3, :] / points2d_3xN[2,:]

                return points2d_3xN

    def image_to_plane(self, p2D_3xN, plane_world):
        # Get ray (expressed in camera coordinate system)
        ray3d = self.get_rays(p2D_3xN)

        # Use Plucker intersection line-plane
        # Create Plucker line using 2 points: origin of camera and origin of camera + ray
        P1 = np.vstack((0, 0, 0, 1))
        P2array = ray3d
        # Plane equation in plucker coordinates (wrt to world)
        P = np.asarray(plane_world).reshape(4, 1)
        # Line equation in plucker coordinates
        p3dNx4 = np.array([])
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
            p3dNx4 = np.append(p3dNx4, p3Dlcs)
        p3dNx4 = p3dNx4.reshape(p3dNx4.shape[0] // 4, 4)
        return p3dNx4


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

    def project_points3d(self, points3d_4xN):
        rows, cols = points3d_4xN.shape
        assert(points3d_4xN.ndim == 2)
        assert(rows == 4 and cols >= 1)
        idx_in_front = points3d_4xN[2, :] > 0.0
        points3d_4xN = points3d_4xN[:, idx_in_front]
        N = points3d_4xN.shape[1]
        if N == 0:
            return None
        #TODO idx to add y r_limit en fisheye
        idx_to_add = [True] * N
        for i in range(0, N):
            rnorm = utils.norm([points3d_4xN[0, i], points3d_4xN[1, i]])
            a = math.atan2(rnorm, points3d_4xN[2, i])
            a2 = a * a
            a3 = a2 * a
            a4 = a3 * a
            rpnorm = (a * self.d[0, 0] + a2 * self.d[0, 1] + a3 * self.d[0, 2] + a4 * self.d[0, 3])
            pixel = [self.cx + self.width * 0.5, self.cy + self.height * 0.5, 1]
            divnorm = np.float32(rpnorm/rnorm)
            if rnorm > 1e-6:
                pixel = np.array([[int(pixel[0] + points3d_4xN[0, i]*divnorm)], [int(pixel[1] + points3d_4xN[1, i]*divnorm)], [1]])
            if i == 0:
                points2d_3xN = pixel
            else:
                points2d_3xN = np.hstack((points2d_3xN, pixel))

        return points2d_3xN


#class Lidar(Sensor):
#    # TODO
#    def __init__(self, P_scs_wrt_lcs, name, description, uri, **properties):
#        Sensor.__init__(self, P_scs_wrt_lcs, name, description, uri, **properties)