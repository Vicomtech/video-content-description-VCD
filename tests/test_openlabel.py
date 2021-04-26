"""
VCD (Video Content Description) library v4.3.1

Project website: http://vcd.vicomtech.org

Copyright (C) 2021, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.3.1.
VCD is distributed under MIT License. See LICENSE.

"""

import unittest
import os
import inspect
import numpy as np
import vcd.core as core
import vcd.schema as schema
import vcd.types as types
import vcd.utils as utils

#vcd_version_name = "vcd" + schema.vcd_schema_version.replace(".", "")
openlabel_version_name = "openlabel" + schema.openlabel_schema_version.replace(".", "")

overwrite = False


def check_openlabel(openlabel, openlabel_file_name, force_write=False):
    if not os.path.isfile(openlabel_file_name) or force_write:
        openlabel.save(openlabel_file_name)

    openlabel_read = core.OpenLABEL(openlabel_file_name, validation=True)
    return openlabel_read.stringify() == openlabel.stringify()


class TestBasic(unittest.TestCase):
    def test_create_openlabel(self):
        """
        This test shows how to create a new OpenLABEL object.
        :return:
        """
        openlabel = core.OpenLABEL()
        openlabel.add_object(name="object1", semantic_type="car")
        openlabel.add_object(name="object2", semantic_type="pedestrian")

        # Compare with reference
        self.assertTrue(check_openlabel(openlabel, './etc/' + openlabel_version_name + '_' + inspect.currentframe().f_code.co_name + '.json', overwrite))

    def test_read_vcd431_file(self):
        """
        This test is about reading a VCD431 file and passing it to the OpenLABEL constructor.
        :return:
        """
        openlabel = core.OpenLABEL(file_name='./etc/vcd431_test_contours.json')

        self.assertTrue(check_openlabel(openlabel,
                                        './etc/' + openlabel_version_name + '_' + inspect.currentframe().f_code.co_name + '.json',
                                        overwrite))

    def test_openlabel_bounding_box_points(self):
        openlabel = core.OpenLABEL()
        uid1 = openlabel.add_object(name="object1", semantic_type="van")
        openlabel.add_object_data(uid=uid1, object_data=types.bbox(
            name="enclosing_rectangle",
            val=[182, 150, 678, 466]))
        openlabel.add_object_data(uid=uid1, object_data=types.poly2d(
            name="extreme_points",
            val=(424, 150, 860, 456, 556, 616, 182, 339),
            mode=types.Poly2DType.MODE_POLY2D_ABSOLUTE,
            closed=True))
        self.assertTrue(check_openlabel(openlabel,
                                        './etc/' + openlabel_version_name + '_' + inspect.currentframe().f_code.co_name + '.json',
                                        overwrite))


    def test_openlabel_external_data(self):
        openlabel = core.OpenLABEL()
        openlabel.add_ontology(ontology_name="https://code.asam.net/simulation/standard/openxontology/-/tree/master/standard")
        uid_road1 = openlabel.add_object(name="road1", semantic_type="road")
        uid_lane1 = openlabel.add_object(name="lane1", semantic_type="lane")

        openlabel.add_object_data(uid=uid_road1, object_data=types.num(
            name="external_id",
            val=217,
        ))
        openlabel.add_object_data(uid=uid_road1, object_data=types.text(
            name="external_uri",
            val="../resources/xodr/multi_intersections.xodr"
        ))

        openlabel.add_object_data(uid=uid_lane1, object_data=types.num(
            name="external_id",
            val=3,
        ))
        openlabel.add_object_data(uid=uid_lane1, object_data=types.text(
            name="external_uri",
            val="../resources/xodr/multi_intersections.xodr"
        ))

        openlabel.add_relation_object_object(name="isPartOf1", semantic_type="isPartOf",
                                             object_uid_1=uid_lane1, object_uid_2=uid_road1,
                                             relation_uid=None, ont_uid=0)

        self.assertTrue(check_openlabel(openlabel,
                                        './etc/' + openlabel_version_name + '_' + inspect.currentframe().f_code.co_name + '.json',
                                        overwrite))

    def test_openlabel_external_data_resource(self):
        openlabel = core.OpenLABEL()
        res_uid = openlabel.add_resource("../resources/xodr/multi_intersections.xodr")
        openlabel.add_object(name="road1", semantic_type="road", res_uid=core.ResourceUID(res_uid, 217))
        openlabel.add_object(name="lane1", semantic_type="lane", res_uid=core.ResourceUID(res_uid, 3))

        self.assertTrue(check_openlabel(openlabel,
                                        './etc/' + openlabel_version_name + '_' + inspect.currentframe().f_code.co_name + '.json',
                                        overwrite))


if __name__ == '__main__':  # This changes the command-line entry point to call unittest.main()
    print("Running " + os.path.basename(__file__))
    unittest.main()
