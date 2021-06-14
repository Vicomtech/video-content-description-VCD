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

import vcd.core as core
import vcd.types as types

from test_config import check_openlabel
from test_config import openlabel_version_name


class TestBasic(unittest.TestCase):

    def test_action_properties(self):
        # 1.- Create a VCD instance
        vcd = core.OpenLABEL()

        # 2.- Create the Object
        uid_action1 = vcd.add_action(name="", semantic_type="#Running", frame_value=(0, 10))
        vcd.add_action_data(uid=uid_action1, action_data=types.num(name="confidence", val=0.98), frame_value=0)
        vcd.add_action_data(uid=uid_action1, action_data=types.vec(name="confidence_vec", val=[0.98, 0.97]), frame_value=0)
        vcd.add_action_data(uid=uid_action1, action_data=types.text(name="annotation", val="Manual"), frame_value=0)
        vcd.add_action_data(uid=uid_action1, action_data=types.boolean(name="validated", val=True), frame_value=1)

        # Same can be done with events and event_data, and contexts and context_data
        # And can be done as dynamic or static info
        uid_object1 = vcd.add_object(name="Marcos", semantic_type="#Person")
        vcd.add_object_data(uid=uid_object1, object_data=types.text(name="Position", val="#Researcher"))

        uid_context1 = vcd.add_context(name="", semantic_type="#Sunny")
        vcd.add_context_data(uid=uid_context1, context_data=types.text(name="category", val="#Weather"))
        vcd.add_context_data(uid=uid_context1, context_data=types.text(name="annotation", val="Manual"))

        uid_context2 = vcd.add_context(name="", semantic_type="#Highway", frame_value=(0, 5))
        vcd.add_context_data(uid=uid_context2, context_data=types.num(name="risk", val=0.7), frame_value=4)
        vcd.add_context_data(uid=uid_context2, context_data=types.num(name="weight", val=0.5), frame_value=4)

        # Check equal to JSON
        self.assertTrue(check_openlabel(vcd, './etc/' + openlabel_version_name + '_' +
                                        inspect.currentframe().f_code.co_name + '.json'))


if __name__ == '__main__':  # This changes the command-line entry point to call unittest.main()
    print("Running " + os.path.basename(__file__))
    unittest.main()





