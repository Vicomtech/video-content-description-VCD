"""
VCD (Video Content Description) library v4.1.0

Project website: http://vcd.vicomtech.org

Copyright (C) 2020, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.0.0.
VCD is distributed under MIT License. See LICENSE.

"""

from builtins import bool
from enum import Enum
import vcd.poly2d as poly


class Intrinsics():
    def __init__(self, width_px, height_px):
        self.data = dict()


class IntrinsicsPinhole(Intrinsics):
    def __init__(self, width_px, height_px, camera_matrix_3x4, distortion_coeffs_1xN=None, **additional_items):
        Intrinsics.__init__(self, width_px, height_px)
        assert (isinstance(width_px, int))
        assert (isinstance(height_px, int))
        self.data['intrinsics_pinhole'] = dict()
        self.data['intrinsics_pinhole']['width_px'] = width_px
        self.data['intrinsics_pinhole']['height_px'] = height_px
        assert (isinstance(camera_matrix_3x4, list))

        assert(len(camera_matrix_3x4) == 12)
        self.data['intrinsics_pinhole']['camera_matrix_3x4'] = camera_matrix_3x4

        if distortion_coeffs_1xN is None:
            distortion_coeffs_1xN = []
        else:
            assert (isinstance(distortion_coeffs_1xN, list))
            num_coeffs = len(distortion_coeffs_1xN)
            assert(5 <= num_coeffs <= 14)
        self.data['intrinsics_pinhole']['distortion_coeffs_1xN'] = distortion_coeffs_1xN

        if additional_items is not None:
            self.data['intrinsics_pinhole'].update(additional_items)



class IntrinsicsFisheye():
    def __init__(self, width_px, height_px, lens_coeffs_1x4, fov_deg, center_x, center_y,
                 radius_x, radius_y, **additional_items):
        Intrinsics.__init__(self, width_px, height_px)
        assert (isinstance(width_px, int))
        assert (isinstance(height_px, int))
        self.data['intrinsics_fisheye'] = dict()
        self.data['intrinsics_fisheye']['width_px'] = width_px
        self.data['intrinsics_fisheye']['height_px'] = height_px
        assert (isinstance(lens_coeffs_1x4, list))
        assert (isinstance(center_x, float))
        assert (isinstance(center_y, float))
        assert (isinstance(radius_x, float))
        assert (isinstance(radius_y, float))
        assert (isinstance(fov_deg, float))

        self.data['intrinsics_fisheye']['center_x'] = center_x
        self.data['intrinsics_fisheye']['center_y'] = center_y
        self.data['intrinsics_fisheye']['radius_x'] = radius_x
        self.data['intrinsics_fisheye']['radius_y'] = radius_y
        self.data['intrinsics_fisheye']['fov_deg'] = fov_deg

        assert (len(lens_coeffs_1x4) == 4)
        self.data['intrinsics_fisheye']['lens_coeffs_1x4'] = lens_coeffs_1x4

        if additional_items is not None:
            self.data['intrinsics_fisheye'].update(additional_items)


class Extrinsics():
    def __init__(self, pose_scs_wrt_lcs_4x4, **additional_items):
        assert(isinstance(pose_scs_wrt_lcs_4x4, list))
        assert (len(pose_scs_wrt_lcs_4x4) == 16)
        self.data = dict()
        self.data['extrinsics'] = dict()
        self.data['extrinsics']['pose_scs_wrt_lcs_4x4'] = pose_scs_wrt_lcs_4x4

        if additional_items is not None:
            self.data['extrinsics'].update(additional_items)


class StreamSync():
    def __init__(self, frame_vcd=None, frame_stream=None, timestamp_ISO8601=None, frame_shift=None, **additional_items):
        self.data = dict()
        self.data['sync'] = dict()
        self.frame_vcd = frame_vcd  # This is the master frame at vcd (if it is None, frame_shift specifies constant shift

        if frame_shift is not None:
            assert(isinstance(frame_shift, int))
            assert(frame_stream is None and timestamp_ISO8601 is None and frame_vcd is None)
            self.data['sync']['frame_shift'] = frame_shift
        else:
            assert (isinstance(frame_vcd, int))
            if frame_stream is not None:
                assert(isinstance(frame_stream, int))
                self.data['sync']['frame_stream'] = frame_stream
            if timestamp_ISO8601 is not None:
                assert(isinstance(timestamp_ISO8601, str))
                self.data['sync']['timestamp'] = timestamp_ISO8601
        if additional_items is not None:
            self.data['sync'].update(additional_items)


class Odometry():
    def __init__(self, pose_lcs_wrt_wcs_4x4, **additional_properties):
        self.data = dict()
        self.data['odometry'] = dict()
        assert (isinstance(pose_lcs_wrt_wcs_4x4, list))
        assert (len(pose_lcs_wrt_wcs_4x4) == 16)

        self.data['odometry']['pose_lcs_wrt_wcs_4x4'] = pose_lcs_wrt_wcs_4x4

        if additional_properties is not None:
            self.data['odometry'].update(additional_properties)


class ObjectDataType(Enum):
    bbox = 1
    num = 2
    text = 3
    boolean = 4
    poly2d = 5
    poly3d = 6
    cuboid = 7
    image = 8
    mat = 9
    binary = 10
    point2d = 11
    point3d = 12
    vec = 13
    line_reference = 14
    area_reference = 15
    mesh = 16


class Poly2DType(Enum):
    MODE_POLY2D_ABSOLUTE = 0
    MODE_POLY2D_SRF6DCC = 5


class ObjectData:
    def __init__(self, name, stream=None):
        assert(isinstance(name, str))
        self.data = dict()
        self.data['name'] = name
        if stream is not None:
            assert (isinstance(stream, str))
            self.data['stream'] = stream

    def add_attribute(self, object_data):
        assert(isinstance(object_data, ObjectData))
        assert(not isinstance(object_data, ObjectDataGeometry))
        self.data.setdefault('attributes', {})  # Creates 'attributes' if it does not exist
        if object_data.type.name not in self.data['attributes']:
            self.data['attributes'].setdefault(object_data.type.name, []).append(object_data.data)


class ObjectDataGeometry(ObjectData):
    def __init__(self, name, stream=None):
        ObjectData.__init__(self, name, stream)  # Calling parent class


class bbox(ObjectDataGeometry):
    def __init__(self, name, val, stream=None):
        ObjectDataGeometry.__init__(self, name, stream)
        assert (isinstance(val, (tuple, list)))
        assert (len(val) == 4)
        if isinstance(val, tuple):
            self.data['val'] = val
        elif isinstance(val, list):
            self.data['val'] = tuple(val)
        self.type = ObjectDataType.bbox


class num(ObjectData):
    def __init__(self, name, val, stream=None):
        ObjectData.__init__(self, name, stream)
        assert isinstance(val, (int, float))
        self.data['val'] = val
        self.type = ObjectDataType.num


class text(ObjectData):
    def __init__(self, name, val, stream=None):
        ObjectData.__init__(self, name, stream)
        assert(isinstance(val, str))
        self.data['val'] = val
        self.type = ObjectDataType.text


class boolean(ObjectData):
    def __init__(self, name, val, stream=None):
        ObjectData.__init__(self, name, stream)
        assert(isinstance(val, bool))
        self.data['val'] = val
        self.type = ObjectDataType.boolean


class poly2d(ObjectDataGeometry):
    def __init__(self, name, val, mode, closed, hierarchy=None, stream=None):
        ObjectDataGeometry.__init__(self, name, stream)
        assert (isinstance(val, (tuple, list)))
        assert(isinstance(mode, Poly2DType))
        assert(isinstance(closed, bool))
        if isinstance(val, tuple) or isinstance(val, list):
            if mode == Poly2DType.MODE_POLY2D_SRF6DCC:
                srfsdcc = poly.computeSRFSDCC(val)
                encoded_poly, rest = poly.chainCodeBase64Encoder(srfsdcc[2:], 3)
                self.data['val'] = [str(srfsdcc[0]), str(srfsdcc[1]), str(rest), encoded_poly]
            else:
                self.data['val'] = list(val)
        self.data['mode'] = mode.name
        self.data['closed'] = closed
        self.type = ObjectDataType.poly2d
        if hierarchy is not None:
            assert(isinstance(hierarchy, list))
            assert(all(isinstance(x, int) for x in hierarchy))
            self.data['hierarchy'] = hierarchy


class poly3d(ObjectDataGeometry):
    def __init__(self, name, val, closed, stream=None):
        ObjectDataGeometry.__init__(self, name, stream)
        assert (isinstance(val, (tuple, list)))
        assert (isinstance(closed, bool))
        if isinstance(val, tuple):
            self.data['val'] = val
        elif isinstance(val, list):
            self.data['val'] = tuple(val)
        self.data['closed'] = closed
        self.type = ObjectDataType.poly3d


class cuboid(ObjectDataGeometry):
    def __init__(self, name, val, stream=None):
        ObjectDataGeometry.__init__(self, name, stream)
        assert (isinstance(val, (tuple, list)))
        assert (len(val) == 9)
        if isinstance(val, tuple):
            self.data['val'] = val
        elif isinstance(val, list):
            self.data['val'] = tuple(val)
        self.type = ObjectDataType.cuboid


class image(ObjectData):
    '''
    This class hosts image data, in buffer format. It can be used with any codification, although base64 and webp
    are suggested.

    mimeType: "image/png", "image/jpeg", .. as in https://www.sitepoint.com/mime-types-complete-list/
    encoding: "base64", "ascii", .. as in https://docs.python.org/2.4/lib/standard-encodings.html

    Default is base64

    OpenCV can be used to encode:
    img = cv2.imread(file_name, 1)
    compr_params=[int(cv2.IMWRITE_PNG_COMPRESSION), 9]
    result, payload = cv2.imencode('.png', img, compr_params)
    '''
    def __init__(self, name, val, mimeType, encoding, stream=None):
        ObjectDataGeometry.__init__(self, name, stream)
        assert(isinstance(val, str))
        assert(isinstance(mimeType, str))
        assert(isinstance(encoding, str))
        self.data['val'] = val
        self.data['mime_type'] = mimeType
        self.data['encoding'] = encoding
        self.type = ObjectDataType.image


class mat(ObjectData):
    def __init__(self, name, val, channels, width, height, dataType, stream=None):
        ObjectData.__init__(self, name, stream)
        assert (isinstance(val, (tuple, list)))
        assert(isinstance(width, int))
        assert (isinstance(height, int))
        assert (isinstance(channels, int))
        assert(isinstance(dataType, str))
        assert (len(val) == width * height * channels)
        if isinstance(val, tuple):
            self.data['val'] = val
        elif isinstance(val, list):
            self.data['val'] = tuple(val)
        self.data['channels'] = channels
        self.data['width'] = width
        self.data['height'] = height
        self.data['data_type'] = dataType
        self.type = ObjectDataType.mat


class binary(ObjectData):
    def __init__(self, name, val, dataType, encoding, stream=None):
        ObjectData.__init__(self, name, stream)
        assert(isinstance(val, str))
        assert(isinstance(dataType, str))
        assert(isinstance(encoding, str))
        self.data['val'] = val
        self.data['data_type'] = dataType
        self.data['encoding'] = encoding
        self.type = ObjectDataType.binary


class vec(ObjectData):
    def __init__(self, name, val, stream=None):
        ObjectData.__init__(self, name, stream)
        assert (isinstance(val, (tuple, list)))
        if isinstance(val, tuple):
            self.data['val'] = val
        elif isinstance(val, list):
            self.data['val'] = tuple(val)
        self.type = ObjectDataType.vec


class point2d(ObjectDataGeometry):
    def __init__(self, name, val, id=None, stream=None):
        ObjectDataGeometry.__init__(self, name, stream)
        assert (isinstance(val, (tuple, list)) and len(val) == 2)
        if isinstance(val, tuple):
            self.data['val'] = val
        elif isinstance(val, list):
            self.data['val'] = tuple(val)
        if id is not None:
            assert(isinstance(id, int))
            self.data['id'] = id
        self.type = ObjectDataType.point2d


class point3d(ObjectDataGeometry):
    def __init__(self, name, val, stream=None):
        ObjectDataGeometry.__init__(self, name, stream)
        assert (isinstance(val, (tuple, list)) and len(val) == 3)
        if isinstance(val, tuple):
            self.data['val'] = val
        elif isinstance(val, list):
            self.data['val'] = tuple(val)
        self.type = ObjectDataType.point3d


class GeometricReference(ObjectDataGeometry):
    def __init__(self, name, val, reference_type, stream=None):
        ObjectDataGeometry.__init__(self, name, stream)
        assert (isinstance(reference_type, ObjectDataType))
        self.data['reference_type'] = reference_type.name
        if val is not None:
            assert (isinstance(val, list))
            self.data['val'] = val


class lineReference(GeometricReference):
    def __init__(self, name, val, reference_type, stream=None):
        GeometricReference.__init__(self, name, val, reference_type, stream)


class areaReference(GeometricReference):
    def __init__(self, name, val, reference_type, stream=None):
        GeometricReference.__init__(self, name, val, reference_type, stream)


class volumeReference(GeometricReference):
    def __init__(self, name, val, reference_type, stream=None):
        GeometricReference.__init__(self, name, val, reference_type, stream)


class mesh(ObjectDataGeometry):
    def __init__(self, name, stream=None):
        ObjectDataGeometry.__init__(self, name, stream)
        self.pid = 0
        self.eid = 0
        self.aid = 0
        self.vid = 0
        self.data['point3d'] = dict()
        self.data['line_reference'] = dict()
        self.data['area_reference'] = dict()
        self.type = ObjectDataType.mesh

    # Vertex
    def add_vertex(self, p3d, id=None):
        assert(isinstance(p3d, point3d))

        # If an id is provided use it
        if id is not None:
            # If it already exists, this is an update call
            if id in self.data['point3d']:
                # The id already exists: substitute
                idx = id
            else:
                idx = id
                self.pid = idx + 1
        else:
            idx = self.pid
            self.pid += 1

        self.data.setdefault('point3d', dict())
        self.data['point3d'][idx] = p3d.data
        return idx

    # Edge
    def add_edge(self, lref, id=None):
        assert(isinstance(lref, lineReference))

        if id is not None:
            if id in self.data['line_reference']:
                idx = id
            else:
                idx = id
                self.eid = idx + 1
        else:
            idx = self.eid
            self.eid += 1

        self.data.setdefault('line_reference', dict())
        self.data['line_reference'][idx] = lref.data
        return idx

    # Area
    def add_area(self, aref, id=None):
        assert(isinstance(aref, areaReference))

        if id is not None:
            if id in self.data['area_reference']:
                idx = id
            else:
                idx = id
                self.aid = idx + 1
        else:
            idx = self.aid
            self.aid += 1

        self.data.setdefault('area_reference', dict())
        self.data['area_reference'][idx] = aref.data
        return idx

    def get_mesh_geometry_as_string(self):
        result = "[["
        for vertex in self.data['point3d'].values():
            val = vertex['val']
            result += "["
            for i in range(0, len(val)):
                result += str(val[i]) + ","
            result += "],"
        result += "],["

        for edge in self.data['line_reference'].values():
            val = edge['val']
            result += "["
            for i in range(0, len(val)):
                result += str(val[i]) + ","
            result += "],"
        result += "],["

        for area in self.data['area_reference'].values():
            val = area['val']
            result += "["
            for i in range(0, len(val)):
                result += str(val[i]) + ","
            result += "],"
        result += "]]"

        # Clean-out commas
        result = result.replace(",]", "]")

        return result
