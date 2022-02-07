"""
VCD (Video Content Description) library v5.0.1

Project website: http://vcd.vicomtech.org

Copyright (C) 2021, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 5.0.1.
VCD is distributed under MIT License. See LICENSE.

"""

import os
import cv2 as cv
import numpy as np
from vcd import core
from vcd import draw
from vcd import scl
from vcd import schema

openlabel_version_name = "openlabel" + schema.openlabel_schema_version.replace(".", "")
vcd_version_name = openlabel_version_name


def draw_mesh(vcd):
    scene = scl.Scene(vcd)
    rangeX = (23, 28)
    rangeY = (23, 28)

    top_view_params = draw.TopView.Params(rangeX=rangeX, rangeY=rangeY)
    drawer = draw.TopView(scene=scene, coordinate_system="world", params=top_view_params)

    top_view = drawer.draw()

    cv.namedWindow('topview', cv.WINDOW_NORMAL)
    cv.imshow('topview', top_view)
    cv.waitKey(0)



if __name__ == "__main__":
    print("Running " + os.path.basename(__file__))

    vcd = core.VCD("../tests/etc/" + openlabel_version_name + "_test_create_mesh.json")

    draw_mesh(vcd)
