"""
VCD (Video Content Description) library v5.0.1

Project website: http://vcd.vicomtech.org

Copyright (C) 2021, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 5.0.1.
VCD is distributed under MIT License. See LICENSE.

"""

import unittest
import os
import inspect
import vcd.core as core
import vcd.types as types

from test_config import check_openlabel
from test_config import openlabel_version_name


class TestBasic(unittest.TestCase):
    def test_bbox_simple(self):
        openlabel = core.OpenLABEL()

        # Basic objects
        car1 = openlabel.add_object(name="car1", semantic_type="Car")
        car2 = openlabel.add_object(name="car2", semantic_type="Car")
        car3 = openlabel.add_object(name="car3", semantic_type="Car")
        bus1 = openlabel.add_object(name="bus1", semantic_type="Bus")
        zebracross1 = openlabel.add_object(name="zebracross1", semantic_type="ZebraCross")
        semaphore1 = openlabel.add_object(name="semaphore1", semantic_type="Semaphore")
        semaphore2 = openlabel.add_object(name="semaphore2", semantic_type="Semaphore")

        # Bounding boxes
        openlabel.add_object_data(uid=car1, object_data=types.bbox(name="shape", val=[410 + 52/2, 280 + 47/2, 52, 47]))
        openlabel.add_object_data(uid=bus1, object_data=types.bbox(name="shape", val=[468 + 56/2, 266 + 47/2, 56, 47]))
        openlabel.add_object_data(uid=car2, object_data=types.bbox(name="shape", val=[105 + 96/2, 280 + 34/2, 96, 34]))
        openlabel.add_object_data(uid=car3, object_data=types.bbox(name="shape", val=[198 + 63/2, 280 + 42/2, 63, 42]))
        openlabel.add_object_data(uid=semaphore1, object_data=types.bbox(name="shape", val=[167 + 38/2, 80 + 80/2, 38, 81]))
        openlabel.add_object_data(uid=semaphore2, object_data=types.bbox(name="shape", val=[885 + 32/2, 145 + 63/2, 32, 63]))
        openlabel.add_object_data(uid=zebracross1, object_data=types.bbox(name="shape", val=[291 + 524/2, 358 + 55/2, 524, 55]))

        # Compare with reference
        self.assertTrue(check_openlabel(openlabel, './etc/' + openlabel_version_name + '_'
                                        + inspect.currentframe().f_code.co_name + '.json'))

    def test_bbox_simple_attributes(self):
        openlabel = core.OpenLABEL()

        # Basic objects
        car1 = openlabel.add_object(name="car1", semantic_type="Car")
        car2 = openlabel.add_object(name="car2", semantic_type="Car")
        car3 = openlabel.add_object(name="car3", semantic_type="Car")
        bus1 = openlabel.add_object(name="bus1", semantic_type="Bus")
        zebracross1 = openlabel.add_object(name="zebracross1", semantic_type="ZebraCross")
        semaphore1 = openlabel.add_object(name="semaphore1", semantic_type="Semaphore")
        semaphore2 = openlabel.add_object(name="semaphore2", semantic_type="Semaphore")

        # Bounding boxes + scores + status
        bbox = types.bbox(name="shape", val=[410 + 52/2, 280 + 47/2, 52, 47])
        bbox.add_attribute(object_data=types.num(name="confidence", val=0.99))
        bbox.add_attribute(object_data=types.boolean(name="interpolated", val=False))
        openlabel.add_object_data(uid=car1, object_data=bbox)

        bbox = types.bbox(name="shape", val=[468 + 56/2, 266 + 47/2, 56, 47])
        bbox.add_attribute(object_data=types.num(name="confidence", val=0.78))
        bbox.add_attribute(object_data=types.boolean(name="interpolated", val=False))
        openlabel.add_object_data(uid=bus1, object_data=bbox)

        bbox = types.bbox(name="shape", val=[105 + 96/2, 280 + 34/2, 96, 34])
        bbox.add_attribute(object_data=types.num(name="confidence", val=0.75))
        bbox.add_attribute(object_data=types.boolean(name="interpolated", val=False))
        openlabel.add_object_data(uid=car2, object_data=bbox)

        bbox = types.bbox(name="shape", val=[198 + 63/2, 280 + 42/2, 63, 42])
        bbox.add_attribute(object_data=types.num(name="confidence", val=0.81))
        bbox.add_attribute(object_data=types.boolean(name="interpolated", val=False))
        openlabel.add_object_data(uid=car3, object_data=bbox)

        bbox = types.bbox(name="shape", val=[167 + 38/2, 80 + 80/2, 38, 81])
        bbox.add_attribute(object_data=types.num(name="confidence", val=0.94))
        bbox.add_attribute(object_data=types.boolean(name="interpolated", val=False))
        openlabel.add_object_data(uid=semaphore1, object_data=bbox)

        bbox = types.bbox(name="shape", val=[885 + 32/2, 145 + 63/2, 32, 63])
        bbox.add_attribute(object_data=types.num(name="confidence", val=0.95))
        bbox.add_attribute(object_data=types.boolean(name="interpolated", val=False))
        openlabel.add_object_data(uid=semaphore2, object_data=bbox)

        bbox = types.bbox(name="shape", val=[291 + 524/2, 358 + 55/2, 524, 55])
        bbox.add_attribute(object_data=types.num(name="confidence", val=0.99))
        bbox.add_attribute(object_data=types.boolean(name="interpolated", val=False))
        openlabel.add_object_data(uid=zebracross1, object_data=bbox)

        # Object attributes
        color = types.text(name="color", val="white")
        brand = types.text(name="model", val="unknown")
        openlabel.add_object_data(uid=car1, object_data=color)
        openlabel.add_object_data(uid=car1, object_data=brand)

        truncated = types.boolean(name="truncated", val=True)
        openlabel.add_object_data(uid=car2, object_data=truncated)

        green = types.text(name="status", val="Green")
        green.add_attribute(object_data=types.num(name="confidence", val=0.99))
        openlabel.add_object_data(uid=semaphore1, object_data=green)

        green = types.text(name="status", val="Green")
        green.add_attribute(object_data=types.num(name="confidence", val=0.66))
        openlabel.add_object_data(uid=semaphore2, object_data=green)

        # Compare with reference
        self.assertTrue(check_openlabel(openlabel, './etc/' + openlabel_version_name + '_'
                                        + inspect.currentframe().f_code.co_name + '.json'))

    def test_bbox_simple_extreme_points(self):
        openlabel = core.OpenLABEL()

        # Basic objects
        car1 = openlabel.add_object(name="car1", semantic_type="Car")
        car2 = openlabel.add_object(name="car2", semantic_type="Car")
        car3 = openlabel.add_object(name="car3", semantic_type="Car")
        bus1 = openlabel.add_object(name="bus1", semantic_type="Bus")
        zebracross1 = openlabel.add_object(name="zebracross1", semantic_type="ZebraCross")
        semaphore1 = openlabel.add_object(name="semaphore1", semantic_type="Semaphore")
        semaphore2 = openlabel.add_object(name="semaphore2", semantic_type="Semaphore")

        # Bounding boxes
        openlabel.add_object_data(uid=car1,
                                  object_data=types.bbox(name="shape", val=[410 + 52 / 2, 280 + 47 / 2, 52, 47]))
        openlabel.add_object_data(uid=bus1,
                                  object_data=types.bbox(name="shape", val=[468 + 56 / 2, 266 + 47 / 2, 56, 47]))
        openlabel.add_object_data(uid=car2,
                                  object_data=types.bbox(name="shape", val=[105 + 96 / 2, 280 + 34 / 2, 96, 34]))
        openlabel.add_object_data(uid=car3,
                                  object_data=types.bbox(name="shape", val=[198 + 63 / 2, 280 + 42 / 2, 63, 42]))
        openlabel.add_object_data(uid=semaphore1,
                                  object_data=types.bbox(name="shape", val=[167 + 38 / 2, 80 + 80 / 2, 38, 81]))
        openlabel.add_object_data(uid=semaphore2,
                                  object_data=types.bbox(name="shape", val=[885 + 32 / 2, 145 + 63 / 2, 32, 63]))
        openlabel.add_object_data(uid=zebracross1,
                                  object_data=types.bbox(name="shape", val=[291 + 524 / 2, 358 + 55 / 2, 524, 55]))

        # Compare with reference
        self.assertTrue(check_openlabel(openlabel, './etc/' + openlabel_version_name + '_'
                                        + inspect.currentframe().f_code.co_name + '.json'))


if __name__ == '__main__':  # This changes the command-line entry point to call unittest.main()
    print("Running " + os.path.basename(__file__))
    unittest.main()
