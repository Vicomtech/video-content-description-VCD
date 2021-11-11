"""
VCD (Video Content Description) library v5.0.1

Project website: http://vcd.vicomtech.org

Copyright (C) 2021, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 5.0.1.
VCD is distributed under MIT License. See LICENSE.

"""



from builtins import bool
from enum import Enum
import vcd.poly2d as poly


class CoordinateSystemType(Enum):
    sensor_cs = 1  # the coordinate system of a certain sensor
    local_cs = 2  # e.g. vehicle-ISO8855 in OpenLABEL, or "base_link" in ROS
    scene_cs = 3  # e.g. "odom" in ROS; starting as the first local-ls
    geo_utm = 4  # In UTM coordinates
    geo_wgs84 = 5  # In WGS84 elliptical Earth coordinates
    custom = 6  # Any other coordinate system


class FisheyeModel(Enum):
    '''    
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
    '''
    radial_poly = 1  
    kannala = 2  
    opencv_fisheye = 3


class Intrinsics:
    def __init__(self):
        self.data = dict()


class IntrinsicsPinhole(Intrinsics):
    def __init__(self, width_px, height_px, camera_matrix_3x4, distortion_coeffs_1xN=None, **additional_items):
        Intrinsics.__init__(self)
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
            assert(4 <= num_coeffs <= 14)
        self.data['intrinsics_pinhole']['distortion_coeffs_1xN'] = distortion_coeffs_1xN

        if additional_items is not None:
            self.data['intrinsics_pinhole'].update(additional_items)


class IntrinsicsFisheye(Intrinsics):
    def __init__(self, width_px, height_px, lens_coeffs_1xN, center_x, center_y, focal_length_x, focal_length_y, fisheye_model=None, **additional_items):
        Intrinsics.__init__(self)
        assert (isinstance(width_px, int))
        assert (isinstance(height_px, int))
        self.data['intrinsics_fisheye'] = dict()
        self.data['intrinsics_fisheye']['width_px'] = width_px
        self.data['intrinsics_fisheye']['height_px'] = height_px
        assert (isinstance(lens_coeffs_1xN, list))
        assert (isinstance(center_x, (float, type(None))))
        assert (isinstance(center_y, (float, type(None))))
        assert (isinstance(focal_length_x, (float, type(None))))
        assert (isinstance(focal_length_y, (float, type(None))))

        self.data['intrinsics_fisheye']['center_x'] = center_x
        self.data['intrinsics_fisheye']['center_y'] = center_y
        self.data['intrinsics_fisheye']['focal_length_x'] = focal_length_x
        self.data['intrinsics_fisheye']['focal_length_y'] = focal_length_y 
        self.data['intrinsics_fisheye']['lens_coeffs_1xN'] = lens_coeffs_1xN

        if fisheye_model is not None:
            assert(isinstance(fisheye_model, FisheyeModel))            
            if fisheye_model is FisheyeModel.radial_poly:
                assert(len(lens_coeffs_1xN)==4)
            elif fisheye_model is FisheyeModel.kannala:
                assert(len(lens_coeffs_1xN)==5)
            elif fisheye_model is FisheyeModel.opencv_fisheye:
                assert(len(lens_coeffs_1xN==4))
            else:
                raise Exception("ERROR: Fisheyemodel not supported. See types.FisheyeModel enum.")            
            self.data['intrinsics_fisheye']['model'] = fisheye_model.name
        else:
            if len(lens_coeffs_1xN)==4:
                self.data['intrinsics_fisheye']['model'] = FisheyeModel.opencv_fisheye.name
            elif len(lens_coeffs_1xN) ==5:
                self.data['intrinsics_fisheye']['model'] = FisheyeModel.kannala.name

        if additional_items is not None:
            self.data['intrinsics_fisheye'].update(additional_items)


class IntrinsicsCylindrical(Intrinsics):
    def __init__(self, width_px, height_px, fov_horz_rad, fov_vert_rad, **additional_items):
        Intrinsics.__init__(self)
        assert (isinstance(width_px, int))
        assert (isinstance(height_px, int))
        self.data['intrinsics_cylindrical'] = dict()
        self.data['intrinsics_cylindrical']['width_px'] = width_px
        self.data['intrinsics_cylindrical']['height_px'] = height_px
        assert (isinstance(fov_horz_rad, float))
        assert (isinstance(fov_vert_rad, float))
        self.data['intrinsics_cylindrical']['fov_horz_rad'] = fov_horz_rad
        self.data['intrinsics_cylindrical']['fov_vert_rad'] = fov_vert_rad

        if additional_items is not None:
            self.data['intrinsics_cylindrical'].update(additional_items)


class IntrinsicsCustom(Intrinsics):
    def __init__(self, **additional_items):
        Intrinsics.__init__(self)
        self.data['intrinsics_custom'] = dict()
        if additional_items is not None:
            self.data['intrinsics_custom'].update(additional_items)


class TransformDataType(Enum):
    matrix_4x4 = 1
    quat_and_trans_7x1 = 2
    euler_and_trans_6x1 = 3
    custom = 4


class TransformData:
    """
    This class encodes the transform data in the form of 4x4 matrix, quaternion + translation, or
    Euler angles + translation
    """
    def __init__(self, val, type, **additional_items):
        assert(isinstance(val, list))
        assert(isinstance(type, TransformDataType))

        self.data = dict()
        if type == TransformDataType.matrix_4x4:
            self.data['matrix4x4'] = val
        elif type == TransformDataType.quat_and_trans_7x1:
            assert(len(val) == 7)
            self.data['quaternion'] = val[0:4]
            self.data['translation'] = val[4:7]
        elif type == TransformDataType.euler_and_trans_6x1:
            assert(len(val) == 6)
            self.data['euler_angles'] = val[0:3]
            self.data['translation'] = val[3:6]

        if additional_items is not None:
            self.data.update(additional_items)


class PoseData(TransformData):
    """
    Equivalente to TransformData, but intended to be used when passive rotation and translation values are provided
    """
    def __init__(self, val, type, **additional_items):
        TransformData.__init__(self, val, type, **additional_items)


class Transform:
    def __init__(self, src_name, dst_name, transform_src_to_dst, **additional_items):
        assert (isinstance(src_name, str))
        assert (isinstance(dst_name, str))
        assert (isinstance(transform_src_to_dst, TransformData))
        self.data = dict()
        name = src_name + "_to_" + dst_name
        self.data[name] = dict()
        self.data_additional = dict()  # this is useful to append only the additional_items
        self.data[name]['src'] = src_name
        self.data[name]['dst'] = dst_name
        self.data[name]['transform_src_to_dst'] = transform_src_to_dst.data
        if additional_items is not None:
            self.data[name].update(additional_items)
            self.data_additional.update(additional_items)


class StreamSync:
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


class ObjectDataType(Enum):
    bbox = 1
    rbbox = 2
    num = 3
    text = 4
    boolean = 5
    poly2d = 6
    poly3d = 7
    cuboid = 8
    image = 9
    mat = 10
    binary = 11
    point2d = 12
    point3d = 13
    vec = 14
    line_reference = 15
    area_reference = 16
    mesh = 17


class Poly2DType(Enum):
    MODE_POLY2D_ABSOLUTE = 0
    #MODE_POLY2D_BBOX = 1
    #MODE_POLY2D_BBOX_DIST = 2
    #MODE_POLY2D_F8DCC = 3
    #MODE_POLY2D_RF8DCC = 4
    MODE_POLY2D_SRF6DCC = 5
    MODE_POLY2D_RS6FCC = 6


class ObjectData:
    def __init__(self, name, coordinate_system=None, properties=None, type=None):
        self.data = dict()
        if name is not None:
            assert (isinstance(name, str))
            self.data['name'] = name
        if coordinate_system is not None:
            assert (isinstance(coordinate_system, str))
            self.data['coordinate_system'] = coordinate_system
        if properties is not None:
            assert (isinstance(properties, dict))
            self.data.update(properties)
        if type is not None:
            assert (isinstance(type, str))
            self.data['type'] = type

    def add_attribute(self, object_data):
        assert(isinstance(object_data, ObjectData))
        assert(not isinstance(object_data, ObjectDataGeometry))
        self.data.setdefault('attributes', {})  # Creates 'attributes' if it does not exist

        if object_data.type.name in self.data['attributes']:
            # Find if element_data already there, if so, replace, otherwise, append
            list_aux = self.data['attributes'][object_data.type.name]
            pos_list = [idx for idx, val in enumerate(list_aux) if val['name'] == object_data.data['name']]
            if len(pos_list) == 0:
                # No: then, just push this new object data
                self.data['attributes'][object_data.type.name].append(object_data.data)
            else:
                # Ok, exists, so let's substitute
                pos = pos_list[0]
                self.data['attributes'][object_data.type.name][pos] = object_data.data
        else:
            self.data['attributes'][object_data.type.name] = [object_data.data]


class ObjectDataGeometry(ObjectData):
    def __init__(self, name, coordinate_system=None, properties=None):
        ObjectData.__init__(self, name, coordinate_system, properties)  # Calling parent class


class bbox(ObjectDataGeometry):
    def __init__(self, name, val, coordinate_system=None, properties=None):
        ObjectDataGeometry.__init__(self, name, coordinate_system, properties)
        assert (isinstance(val, (tuple, list)))
        assert (len(val) == 4)
        if isinstance(val, tuple):
            self.data['val'] = val
        elif isinstance(val, list):
            self.data['val'] = tuple(val)
        self.type = ObjectDataType.bbox


class rbbox(ObjectDataGeometry):
    def __init__(self, name, val, coordinate_system=None, properties=None):
        ObjectDataGeometry.__init__(self, name, coordinate_system, properties)
        assert (isinstance(val, (tuple, list)))
        assert (len(val) == 5)
        if isinstance(val, tuple):
            self.data['val'] = val
        elif isinstance(val, list):
            self.data['val'] = tuple(val)
        self.type = ObjectDataType.rbbox


class num(ObjectData):
    def __init__(self, name, val, coordinate_system=None, properties=None, type=None):
        ObjectData.__init__(self, name, coordinate_system, properties, type)
        assert isinstance(val, (int, float))
        self.data['val'] = val
        self.type = ObjectDataType.num


class text(ObjectData):
    def __init__(self, name, val, coordinate_system=None, properties=None, type=None):
        ObjectData.__init__(self, name, coordinate_system, properties, type)
        assert(isinstance(val, str))
        self.data['val'] = val
        self.type = ObjectDataType.text


class boolean(ObjectData):
    def __init__(self, name, val, coordinate_system=None, properties=None, type=None):
        ObjectData.__init__(self, name, coordinate_system, properties, type)
        assert(isinstance(val, bool))
        self.data['val'] = val
        self.type = ObjectDataType.boolean


class poly2d(ObjectDataGeometry):
    def __init__(self, name, val, mode, closed, hierarchy=None, coordinate_system=None, properties=None):
        ObjectDataGeometry.__init__(self, name, coordinate_system, properties)
        assert (isinstance(val, (tuple, list)))
        assert(isinstance(mode, Poly2DType))
        assert(isinstance(closed, bool))
        if isinstance(val, tuple) or isinstance(val, list):
            if mode == Poly2DType.MODE_POLY2D_SRF6DCC:
                srf6, xinit, yinit = poly.computeSRF6DCC(val)
                encoded_poly, rest = poly.chainCodeBase64Encoder(srf6, 3)
                self.data['val'] = [str(xinit), str(yinit), str(rest), encoded_poly]
            elif mode == Poly2DType.MODE_POLY2D_RS6FCC:
                rs6, low, high, xinit, yinit = poly.computeRS6FCC(val)
                encoded_poly, rest = poly.chainCodeBase64Encoder(rs6, 3)
                self.data['val'] = [str(xinit), str(yinit), str(low), str(high), str(rest), encoded_poly]
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
    def __init__(self, name, val, closed, coordinate_system=None, properties=None):
        ObjectDataGeometry.__init__(self, name, coordinate_system, properties)
        assert (isinstance(val, (tuple, list)))
        assert (isinstance(closed, bool))
        if isinstance(val, tuple):
            self.data['val'] = val
        elif isinstance(val, list):
            self.data['val'] = tuple(val)
        self.data['closed'] = closed
        self.type = ObjectDataType.poly3d


class cuboid(ObjectDataGeometry):
    def __init__(self, name, val, coordinate_system=None, properties=None):
        ObjectDataGeometry.__init__(self, name, coordinate_system, properties)
        if val is not None:
            assert (isinstance(val, (tuple, list)))
            assert (len(val) == 9 or len(val) == 10)
            if len(val) == 9:
                self.use_quaternion = False
            else:
                self.use_quaternion = True
        if isinstance(val, tuple):
            self.data['val'] = list(val)
        elif isinstance(val, list):
            self.data['val'] = val
        else:
            self.data['val'] = None
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
    def __init__(self, name, val, mimeType, encoding, coordinate_system=None, properties=None):
        ObjectDataGeometry.__init__(self, name, coordinate_system, properties)
        assert(isinstance(val, str))
        assert(isinstance(mimeType, str))
        assert(isinstance(encoding, str))
        self.data['val'] = val
        self.data['mime_type'] = mimeType
        self.data['encoding'] = encoding
        self.type = ObjectDataType.image


class mat(ObjectData):
    def __init__(self, name, val, channels, width, height, dataType, coordinate_system=None, properties=None):
        ObjectData.__init__(self, name, coordinate_system, properties)
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
    def __init__(self, name, val, dataType, encoding, coordinate_system=None, properties=None):
        ObjectData.__init__(self, name, coordinate_system, properties)
        assert(isinstance(val, str))
        assert(isinstance(dataType, str))
        assert(isinstance(encoding, str))
        self.data['val'] = val
        self.data['data_type'] = dataType
        self.data['encoding'] = encoding
        self.type = ObjectDataType.binary


class vec(ObjectData):
    def __init__(self, name, val, coordinate_system=None, properties=None, type=None):
        ObjectData.__init__(self, name, coordinate_system, properties, type)
        assert (isinstance(val, (tuple, list)))
        if isinstance(val, tuple):
            self.data['val'] = val
        elif isinstance(val, list):
            self.data['val'] = tuple(val)
        self.type = ObjectDataType.vec


class point2d(ObjectDataGeometry):
    def __init__(self, name, val, id=None, coordinate_system=None, properties=None):
        ObjectDataGeometry.__init__(self, name, coordinate_system, properties)
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
    def __init__(self, name, val, id=None, coordinate_system=None, properties=None):
        ObjectDataGeometry.__init__(self, name, coordinate_system, properties)
        assert (isinstance(val, (tuple, list)) and len(val) == 3)
        if isinstance(val, tuple):
            self.data['val'] = val
        elif isinstance(val, list):
            self.data['val'] = tuple(val)
        if id is not None:
            assert (isinstance(id, int))
            self.data['id'] = id
        self.type = ObjectDataType.point3d


class GeometricReference(ObjectDataGeometry):
    def __init__(self, name, val, reference_type, coordinate_system=None, properties=None):
        ObjectDataGeometry.__init__(self, name, coordinate_system, properties)
        assert (isinstance(reference_type, ObjectDataType))
        self.data['reference_type'] = reference_type.name
        if val is not None:
            assert (isinstance(val, list))
            self.data['val'] = val


class lineReference(GeometricReference):
    def __init__(self, name, val, reference_type, coordinate_system=None, properties=None):
        GeometricReference.__init__(self, name, val, reference_type, coordinate_system, properties)


class areaReference(GeometricReference):
    def __init__(self, name, val, reference_type, coordinate_system=None, properties=None):
        GeometricReference.__init__(self, name, val, reference_type, coordinate_system, properties)


class volumeReference(GeometricReference):
    def __init__(self, name, val, reference_type, coordinate_system=None, properties=None):
        GeometricReference.__init__(self, name, val, reference_type, coordinate_system, properties)


class mesh(ObjectDataGeometry):
    def __init__(self, name, coordinate_system=None, properties=None):
        ObjectDataGeometry.__init__(self, name, coordinate_system, properties)
        self.pid = "0"
        self.eid = "0"
        self.aid = "0"
        self.vid = "0"
        self.data['point3d'] = {}
        self.data['line_reference'] = {}
        self.data['area_reference'] = {}
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
                self.pid = str(int(idx) + 1)
        else:
            idx = self.pid
            self.pid = str(int(self.pid) + 1)

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
                self.eid = str(int(idx) + 1)
        else:
            idx = self.eid
            self.eid = str(int(self.eid) + 1)

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
                self.aid = str(int(idx) + 1)
        else:
            idx = self.aid
            self.aid = str(int(self.aid) + 1)

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
