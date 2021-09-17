"""
VCD (Video Content Description) library v5.0.0

Project website: http://vcd.vicomtech.org

Copyright (C) 2021, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 5.0.0.
VCD is distributed under MIT License. See LICENSE.

"""

import inspect
import unittest
import os
import vcd.core as core
import vcd.schema as schema
import vcd.types as types

from test_config import check_openlabel
from test_config import openlabel_version_name


def get_mesh_geometry_as_string(vertexMap, edgeMap, areaMap):
    result = "[["
    for vertex in vertexMap:
        val = vertex
        result += "["
        for i in range(0, len(val)):
            result += str(val[i]) + ","
        result += "],"
    result += "],["

    for edge in edgeMap:
        val = edge
        result += "["
        for i in range(0, len(val)):
            result += str(val[i]) + ","
        result += "],"
    result += "],["

    for area in areaMap:
        val = area
        result += "["
        for i in range(0, len(val)):
            result += str(val[i]) + ","
        result += "],"
    result += "]]"

    # Clean-out commas
    result_clean = result.replace(",]", "]")

    return result_clean


def generate_default_mesh(rows, cols):
    # Add vertex
    points = []
    for i in range(0, rows+1):
        for j in range(0, cols+1):
            points.append((j, i, 0))

    # Add edges
    lines = []
    for u in range(0, rows+1):
        for v in range(0, cols):
            lines.append((v + u*(cols+1), v + 1 + u*(cols+1)))

    for u in range(0, rows):
        for v in range(0, cols+1):
            lines.append((v + u*(cols+1), v+cols+1+u*(cols+1)))

    # Add areas
    areas = []
    for i in range(0, rows):
        for j in range(0, cols):
            areas.append((i * cols + j,
                          i * cols + j + cols,
                          i * (cols + 1) + j + cols * (rows + 1),
                          i * (cols + 1) + j + cols * (rows + 1) + 1)
                         )

    # Create string
    string_mesh = get_mesh_geometry_as_string(points, lines, areas)
    #print(string_mesh)
    return string_mesh


class TestBasic(unittest.TestCase):
    def test_create_default_mesh_string(self):
        rows = 2
        cols = 4
        val_4x2 = generate_default_mesh(rows, cols)
        expected_val_4x2 = "[[[0,0,0],[1,0,0],[2,0,0],[3,0,0],[4,0,0],[0,1,0],[1,1,0],[2,1,0],[3,1,0],[4,1,0]," \
                           "[0,2,0],[1,2,0],[2,2,0],[3,2,0],[4,2,0]],[[0,1],[1,2],[2,3],[3,4],[5,6],[6,7]," \
                           "[7,8],[8,9],[10,11],[11,12],[12,13],[13,14],[0,5],[1,6],[2,7],[3,8],[4,9]," \
                           "[5,10],[6,11],[7,12],[8,13],[9,14]],[[0,4,12,13],[1,5,13,14]," \
                           "[2,6,14,15],[3,7,15,16],[4,8,17,18],[5,9,18,19],[6,10,19,20]," \
                           "[7,11,20,21]]]"
        self.assertEqual(val_4x2, expected_val_4x2)

    def test_create_mesh(self):
        # 1.- Create a VCD instance
        vcd = core.OpenLABEL()
        vcd.add_coordinate_system(name='world', cs_type=types.CoordinateSystemType.local_cs)

        # Mesh sample representation
        #
        # P0 L0   P1   L4   P4
        # *--------*--------*
        # |        |        |
        # |L3  A0  |L1  A1  |L5
        # |        |        |
        # *--------*--------*
        # P3  L2   P2  L6   P5
        #
        # V0  [A0,A1]

        mesh1 = types.mesh(name="mesh1", coordinate_system='world')

        # Vertex
        # P0
        p0 = types.point3d("Vertex", (25, 25, 0))
        p0.add_attribute(types.text("T Shape", "line_ending_type"))
        p0_id = mesh1.add_vertex(p0)
        # P1
        p1 = types.point3d("Vertex", (26, 25, 0))
        p1.add_attribute(types.text("I Shape", "line_ending_type"))
        mesh1.add_vertex(p1)
        # P2
        p2 = types.point3d("Vertex", (26, 26, 0))
        p2.add_attribute(types.text("U Shape", "line_ending_type"))
        mesh1.add_vertex(p2)
        # P3
        p3 = types.point3d("Vertex", (25, 26, 0))
        p3.add_attribute(types.text("C Shape", "line_ending_type"))
        mesh1.add_vertex(p3)
        # P4
        p4 = types.point3d("Vertex", (27, 25, 0))
        p4.add_attribute(types.text("T Shape", "line_ending_type"))
        mesh1.add_vertex(p4)
        # P5
        p5 = types.point3d("Vertex", (27, 26, 0))
        p5.add_attribute(types.text("I Shape", "line_ending_type"))
        mesh1.add_vertex(p5)

        # Edges
        # L0
        l0 = types.lineReference("Edge", [0, 1], types.ObjectDataType.point3d)
        l0.add_attribute(types.text("Single Solid", "line_marking_type"))
        l0.add_attribute(types.text("White", "line_colourine_marking_typ"))
        l0_id = mesh1.add_edge(l0)
        # L1
        l1 = types.lineReference("Edge", [1, 2], types.ObjectDataType.point3d)
        l1.add_attribute(types.text("Double Solid", "line_marking_type"))
        l1.add_attribute(types.text("Blue", "line_colourine_marking_type"))
        l1_id = mesh1.add_edge(l1)
        # L2
        l2 = types.lineReference("Edge", [2, 3], types.ObjectDataType.point3d)
        l2.add_attribute(types.text("Dashed", "line_marking_type"))
        l2.add_attribute(types.text("Yellow", "line_colourine_marking_type"))
        l2_id = mesh1.add_edge(l2)
        # L3
        l3 = types.lineReference("Edge", [3, 0], types.ObjectDataType.point3d)
        l3.add_attribute(types.text("Cross", "line_marking_type"))
        l3.add_attribute(types.text("Green", "line_colourine_marking_type"))
        mesh1.add_edge(l3)
        # L4
        l4 = types.lineReference("Edge", [1, 4], types.ObjectDataType.point3d)
        l4.add_attribute(types.text("Single Solid", "line_marking_type"))
        l4.add_attribute(types.text("White", "line_colourine_marking_type"))
        mesh1.add_edge(l4)
        # L5
        l5 = types.lineReference("Edge", [4, 5], types.ObjectDataType.point3d)
        l5.add_attribute(types.text("Double Solid", "line_marking_type"))
        l5.add_attribute(types.text("Blue", "line_colourine_marking_type"))
        mesh1.add_edge(l5)
        # L6
        l6 = types.lineReference("Edge", [5, 2], types.ObjectDataType.point3d)
        l6.add_attribute(types.text("Dashed", "line_marking_type"))
        l6.add_attribute(types.text("Yellow", "line_colourine_marking_type"))
        mesh1.add_edge(l6)

        # Areas
        # A0
        a0 = types.areaReference("Slot", [0, 1, 2, 3], types.ObjectDataType.line_reference)
        a0.add_attribute(types.text("Fishbone", "park_slot_type"))
        a0.add_attribute(types.text("Empty", "park_slot_content"))
        mesh1.add_area(a0)
        a1 = types.areaReference("Slot", [4, 5, 6, 1], types.ObjectDataType.line_reference)
        a1.add_attribute(types.text("Fishbone", "park_slot_type"))
        a1.add_attribute(types.text("Empty", "park_slot_content"))
        mesh1.add_area(a1)

        mesh_id = vcd.add_object(name="parking1", semantic_type="ParkingLot")
        vcd.add_object_data(mesh_id, mesh1)

        string_mesh = mesh1.get_mesh_geometry_as_string()

        self.assertEqual(string_mesh, "[[[25,25,0],[26,25,0],[26,26,0],[25,26,0],[27,25,0],[27,26,0]],"
                                      "[[0,1],[1,2],[2,3],[3,0],[1,4],[4,5],[5,2]],[[0,1,2,3],[4,5,6,1]]]")

        # Check equal to reference JSON
        self.assertTrue(check_openlabel(vcd, './etc/' + openlabel_version_name + '_' +
                                        inspect.currentframe().f_code.co_name + '.json'))

    def test_create_mesh_with_API_frames(self):
        # Load from previous test
        vcd = core.OpenLABEL('./etc/' + openlabel_version_name + '_test_create_mesh.json')

        # Let's assume we know the structure of the mesh
        #
        # P0 L0   P1   L4   P4
        # *--------*--------*
        # |        |        |
        # |L3  A0  |L1  A1  |L5
        # |        |        |
        # *--------*--------*
        # P3  L2   P2  L6   P5
        #
        # V0  [A0,A1]

        # Let's read mesh object
        # mesh1 = vcd.get_objects_with_object_data_name("parkslot1")
        mesh1 = vcd.get_object("0")

        # Let's read static object_data
        # od_mesh = mesh1.data['object_data']['mesh']
        od_mesh = vcd.get_object_data("0", "mesh1", frame_num=None)

        vertices = od_mesh['point3d']
        edges = od_mesh['line_reference']
        areas = od_mesh['area_reference']

        # Let's add some frame-specific attributes (for line-reference and area-references)
        # Currently, only way to do it is by creating a new mesh object_data
        # and add it to the existing Object, specifying the frame

        for frame_num in range(0, 2):
            mesh1_frame = types.mesh("mesh1_dyn")
            for line_key, line_val in edges.items():
                # If we want to add a line_reference attribute: Reconstruct line_reference
                # Read existing info
                # "None" for val, so it is not copied at frame-lev.
                lX = types.lineReference(line_val['name'], reference_type=types.ObjectDataType.point3d, val=None)
                lX.add_attribute(types.text("line_colour", "not set"))
                mesh1_frame.add_edge(lX, line_key)

            for area_key, area_val in areas.items():
                # If we want to add an area_reference attribute: Reconstruct area_reference
                # Read existing info
                aX = types.areaReference(area_val['name'], reference_type=types.ObjectDataType.line_reference, val=None)
                aX.add_attribute(types.text("park_slot_content", "Empty"))
                mesh1_frame.add_area(aX, area_key)

            # We add and then update. Note we use a different name "parkslot1_dyn", because "parkslot1" is used for
            # a static object_data
            vcd.add_object_data("0", mesh1_frame, frame_num)

        # Check equal to reference JSON
        self.assertTrue(check_openlabel(vcd, './etc/' + openlabel_version_name + '_' +
                                        inspect.currentframe().f_code.co_name + '.json'))


if __name__ == '__main__':  # This changes the command-line entry point to call unittest.main()
    print("Running test_mesh.py...")
    unittest.main()





