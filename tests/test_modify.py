"""
VCD (Video Content Description) library v4.3.1

Project website: http://vcd.vicomtech.org

Copyright (C) 2021, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.3.1.
VCD is distributed under MIT License. See LICENSE.

"""

import inspect
from re import S
import unittest
import os
import vcd.core as core
import vcd.types as types

from test_config import check_openlabel
from test_config import openlabel_version_name


class TestBasic(unittest.TestCase):
    def test_static_dynamic_object_1(self):
        # 1.- Create a VCD instance
        vcd = core.OpenLABEL()

        # 2. - Let's create a static object and add some dynamic properties
        # When the attribute is added, the frame information is propagated to the element
        uid1 = vcd.add_object(name='line1', semantic_type='#LaneMarking')
        vcd.add_object_data(uid=uid1, object_data= types.text(name='type', val='dashed'), frame_value=(5, 10))
        self.assertTrue(
            check_openlabel(vcd, './etc/' + openlabel_version_name + '_test_static_dynamic_object_1_1.json'))

        # 3. - Let's add some static attributes
        vcd.add_object_data(uid=uid1, object_data= types.text(name='color', val='yellow'))

        # Check equal to reference JSON
        self.assertTrue(check_openlabel(vcd, './etc/' + openlabel_version_name + '_test_static_dynamic_object_1_2.json'))

    def test_static_dynamic_object_2(self):
        # 1.- Create a VCD instance
        vcd = core.OpenLABEL()

        # 2.- Create a dynamic object with static information
        # The attribute is added ot the objects section
        uid1 = vcd.add_object(name='line1', semantic_type='#BottsDots', frame_value=(5, 10))
        poly = types.poly2d(name='poly', val=(100, 100, 110, 110, 120, 130, 500, 560),
                            mode=types.Poly2DType.MODE_POLY2D_ABSOLUTE, closed=False)
        poly.add_attribute(object_data=types.text(name='type', val='single_dot'))
        vcd.add_object_data(uid=uid1, object_data=poly)

        # Check equal to reference JSON
        self.assertTrue(check_openlabel(vcd, './etc/' + openlabel_version_name + '_' +
                                        inspect.currentframe().f_code.co_name + '.json'))

    def test_element_data_same_name(self):
        vcd = core.OpenLABEL()
        uid1 = vcd.add_action('', '#Walking')
        vcd.add_action_data(uid1, types.boolean('validated', True), (0, 5))
        vcd.add_action_data(uid1, types.boolean('occluded', False), (0, 5))
        vcd.add_action_data(uid1, types.text('label', 'manual'), (0, 5))

        # Now try to add an Action Data with the same name
        vcd.add_action_data(uid1, types.boolean('validated', False), (0, 5))

        # The initial 'validated' Boolean, with value true is substituted by false, instead of added
        # Check equal to reference JSON
        self.assertTrue(check_openlabel(vcd, './etc/' + openlabel_version_name + '_' +
                                        inspect.currentframe().f_code.co_name + '.json'))

    def test_element_data_nested_same_name(self):
        vcd = core.OpenLABEL()
        uid1 = vcd.add_object('mike', '#Pedestrian')
        body = types.bbox('body', (0, 0, 100, 150))
        body.add_attribute(types.boolean('visible', True))
        body.add_attribute(types.boolean('occluded', False))
        body.add_attribute(types.boolean('visible', False))  # this is repeated, so it is substituted
        vcd.add_object_data(uid1, body, (0, 5))

        # Check equal to reference JSON
        self.assertTrue(check_openlabel(vcd, './etc/' + openlabel_version_name + '_' +
                                        inspect.currentframe().f_code.co_name + '.json'))

    def test_action_frame_interval_modification(self):
        vcd = core.OpenLABEL()

        # Basic modification of element-level information, including frame-intervals
        uid1 = vcd.add_action('Drinking_5', 'distraction/Drinking', [(5, 10), (15, 20)])
        fis = vcd.get_element_frame_intervals(core.ElementType.action, uid1).get_dict()
        self.assertDictEqual(fis[0], {'frame_start': 5, 'frame_end': 10})
        self.assertDictEqual(fis[1], {'frame_start': 15, 'frame_end': 20})

        # Usual "just-one-frame" update for online operation: internally updates frame interval using FUSION (UNION)
        vcd.add_action('Drinking_5', 'distraction/Drinking', 21, uid1)  # default SetMode is union
        fis = vcd.get_element_frame_intervals(core.ElementType.action, uid1).get_dict()
        self.assertDictEqual(fis[0], {'frame_start': 5, 'frame_end': 10})
        self.assertDictEqual(fis[1], {'frame_start': 15, 'frame_end': 21})

        # Entire modification with potential removal and extension
        vcd.add_action('Drinking_5', 'distraction/Drinking', [(5, 11), (17, 20)], uid1, set_mode=core.SetMode.replace)  # adding 11, and deleting 15, 16, and 21
        fis = vcd.get_element_frame_intervals(core.ElementType.action, uid1).get_dict()
        self.assertDictEqual(fis[0], {'frame_start': 5, 'frame_end': 11})
        self.assertDictEqual(fis[1], {'frame_start': 17, 'frame_end': 20})

        # Complex modification of element_data level information
        vcd.add_action_data(uid1, types.text('label', 'manual'), [(5, 5), (11, 11), (20, 20)])
        vcd.add_action_data(uid1, types.text('label', 'auto'), [(11, 11)]) # this is an update, we want to modify
        # part of the action_data, without the need to substitute it entirely. This function can alse be used to
        # increase element's range

        self.assertEqual(vcd.get_action_data(uid1, 'label', 5)['val'], 'manual')
        self.assertEqual(vcd.get_action_data(uid1, 'label', 11)['val'], 'auto')
        self.assertEqual(vcd.get_action_data(uid1, 'label', 20)['val'], 'manual')
        fis = vcd.get_element_frame_intervals(core.ElementType.action, uid1).get_dict()
        self.assertDictEqual(fis[0], {'frame_start': 5, 'frame_end': 11})
        self.assertDictEqual(fis[1], {'frame_start': 17, 'frame_end': 20})  # element should not be modified so far

        # If element-data is defined BEYOND the element limits -> Element is automatically extended
        vcd.add_action_data(uid1, types.text('label', 'manual'), [(5, 25)])
        for i in range(5, 26):
            self.assertEqual(vcd.get_action_data(uid1, 'label', i)['val'], 'manual')
        fis = vcd.get_element_frame_intervals(core.ElementType.action, uid1).get_dict()
        self.assertDictEqual(fis[0], {'frame_start': 5, 'frame_end': 25})

        # Note: any further modification of Action also modifies (e.g. removes) any action_data
        vcd.add_action('Drinking_5', 'distraction/Drinking', [(5, 11), (15, 19)], uid1, set_mode=core.SetMode.replace)  # removing frames 20 and 21, and also from 12 to 14
        fis = vcd.get_element_frame_intervals(core.ElementType.action, uid1).get_dict()
        self.assertDictEqual(fis[0], {'frame_start': 5, 'frame_end': 11})
        self.assertDictEqual(fis[1], {'frame_start': 15, 'frame_end': 19})
        self.assertEqual(vcd.get_action_data(uid1, 'label', 20), None)

        # Action data can also be "modified", which means fully substituted
        vcd.add_action_data(uid1, types.text('label', 'auto'), [(7, 26), (28, 28)], set_mode=core.SetMode.replace)  # this will remove 5, 6 and add 26 and 28
        fis_ad = vcd.get_action_data_frame_intervals(uid1, 'label').get_dict()
        self.assertDictEqual(fis_ad[0], {'frame_start': 7, 'frame_end': 26})
        self.assertDictEqual(fis_ad[1], {'frame_start': 28, 'frame_end': 28})

        # The action should not be removed because an inner action-data is removed
        fis = vcd.get_element_frame_intervals(core.ElementType.action, uid1).get_dict()
        self.assertDictEqual(fis[0], {'frame_start': 5, 'frame_end': 26})
        self.assertDictEqual(fis[1], {'frame_start': 28, 'frame_end': 28})

        # Move completely the frame intervals of an element
        shift = 100
        vcd.add_action('Drinking_5', 'distraction/Drinking', [(5 + shift, 26 + shift), (28 + shift, 28 + shift)],
                       uid1, set_mode=core.SetMode.replace)

        res = vcd.get_action_data(uid1, 'label', 5)
        self.assertEqual(res, None)

    def test_object_change_from_static_to_dynamic(self):
        # Static->Dynamic

        # Case A) (when VCD has no other object with frames)
        vcd_a = core.OpenLABEL()
        uid_a = vcd_a.add_object("Enara", "Child")

        # Let's add some object data
        vcd_a.add_object_data(uid=uid_a, object_data=types.text(name="FavouriteColor", val="Pink"))
        self.assertEqual(vcd_a.get_object_data(uid=uid_a, data_name='FavouriteColor', frame_num=3), None)
        self.assertEqual(vcd_a.get_object_data(uid=uid_a, data_name='FavouriteColor')['val'], 'Pink')

        # Check equal to reference JSON
        self.assertTrue(check_openlabel(vcd_a, './etc/' + openlabel_version_name
                                        + '_test_object_change_from_static_to_dynamic_a_before.json'))

        # Let's modify the object so it has a certain frame interval (object_data frame intervals remain void)
        vcd_a.add_object(name="Enara", semantic_type="Child", uid=uid_a, frame_value=[(5, 10)])

        self.assertTrue(check_openlabel(vcd_a, './etc/' + openlabel_version_name
                                        + '_test_object_change_from_static_to_dynamic_a_after.json'))

        # Check that the element data is now also defined for this frame interval (and thus removed from the root)
        self.assertEqual(vcd_a.get_object_data(uid=uid_a, data_name='FavouriteColor', frame_num=3), None)
        self.assertEqual(vcd_a.get_object_data(uid=uid_a, data_name='FavouriteColor')['val'], 'Pink')
        self.assertEqual(vcd_a.get_object_data(uid=uid_a, data_name='FavouriteColor', frame_num=8)['val'], 'Pink')

        # Case B (when VCD has some other frame intervals already defined): VCD's get_element_data behaves differently
        vcd_b = core.VCD()
        vcd_b.add_object(name="room1", semantic_type="Room", frame_value=[(0, 10)])
        uid_b = vcd_b.add_object(name="Enara", semantic_type="Child")
        vcd_b.add_object_data(uid=uid_b, object_data=types.text(name="FavouriteColor", val="Pink"))
        self.assertTrue(check_openlabel(vcd_b, './etc/' + openlabel_version_name
                                        + '_test_object_change_from_static_to_dynamic_b_before.json'))
        # In this case, as the VCD has frames, the object is assumed to exist in all the scene
        # when the user asks for element_data at certain frame, VCD looks for element_data at that frame, and if there
        # is nothing, it then searches at the static part
        self.assertEqual(vcd_b.get_object_data(uid=uid_b, data_name='FavouriteColor', frame_num=3)['val'], 'Pink')
        self.assertEqual(vcd_b.get_object_data(uid=uid_b, data_name='FavouriteColor')['val'], 'Pink')
        vcd_b.add_object(name="Enara", semantic_type="Child", uid=uid_b, frame_value=[(5, 10)])

        self.assertTrue(check_openlabel(vcd_b, './etc/' + openlabel_version_name
                                           + '_test_object_change_from_static_to_dynamic_b_after.json'))
        self.assertEqual(vcd_b.get_object_data(uid=uid_b, data_name='FavouriteColor', frame_num=3), None)
        self.assertEqual(vcd_b.get_object_data(uid=uid_b, data_name='FavouriteColor')['val'], 'Pink')
        self.assertEqual(vcd_b.get_object_data(uid=uid_b, data_name='FavouriteColor', frame_num=8)['val'], 'Pink')

    def test_object_change_from_dynamic_to_static(self):
        vcd = core.OpenLABEL()
        uid1 = vcd.add_object("Enara", "Child")
        vcd.add_object_data(uid=uid1, object_data=types.text(name="FavouriteColor", val="Pink"))
        vcd.add_object_data(uid=uid1, object_data=types.vec(name="Position", val=(1.0, 5.0)), frame_value=8)
        self.assertTrue(check_openlabel(vcd, './etc/' + openlabel_version_name
                                        + '_test_object_change_from_dynamic_to_static_before.json'))
        vcd.add_object(name="Enara", semantic_type="Child", uid=uid1, set_mode=core.SetMode.replace)
        self.assertTrue(check_openlabel(vcd, './etc/' + openlabel_version_name
                                        + '_test_object_change_from_dynamic_to_static_after.json'))
        self.assertEqual(vcd.get_object_data(uid=uid1, data_name='FavouriteColor', frame_num=8), None)
        self.assertEqual(vcd.get_object_data(uid=uid1, data_name='FavouriteColor')['val'], 'Pink')
        self.assertEqual(vcd.get_object_data(uid=uid1, data_name='Position', frame_num=8), None)
        self.assertEqual(vcd.get_object_data(uid=uid1, data_name='Position'), None)

    def test_modify_relations(self):
        vcd = core.OpenLABEL()

        # Relation without frameintervals
        uid_car1 = vcd.add_object('car1', 'car')
        uid_car2 = vcd.add_object('car2', 'car')
        uid_car3 = vcd.add_object('car3', 'car')
        uid_relation1 = vcd.add_relation_object_object('follows1', 'follows', uid_car1, uid_car2)

        self.assertEqual(vcd.get_relation(uid_relation1)['rdf_subjects'][0]['uid'], uid_car1)
        self.assertEqual(vcd.get_relation(uid_relation1)['rdf_subjects'][0]['type'], 'object')
        self.assertEqual(vcd.get_relation(uid_relation1)['rdf_objects'][0]['uid'], uid_car2)
        self.assertEqual(vcd.get_relation(uid_relation1)['rdf_objects'][0]['type'], 'object')
        self.assertEqual(len(vcd.get_relation(uid_relation1)['rdf_objects']), 1)

        uid_relation1 = vcd.add_relation_object_object('follows1', 'follows', uid_car1, uid_car3, uid_relation1,
                                                       set_mode=core.SetMode.replace)

        self.assertEqual(vcd.get_relation(uid_relation1)['rdf_subjects'][0]['uid'], uid_car1)
        self.assertEqual(vcd.get_relation(uid_relation1)['rdf_subjects'][0]['type'], 'object')
        self.assertEqual(vcd.get_relation(uid_relation1)['rdf_objects'][0]['uid'], uid_car3)
        self.assertEqual(vcd.get_relation(uid_relation1)['rdf_objects'][0]['type'], 'object')
        self.assertEqual(len(vcd.get_relation(uid_relation1)['rdf_objects']), 1)

        # Relation with frameintervals
        uid_ped1 = vcd.add_object('ped1', 'ped', [0, 10])
        uid_ped2 = vcd.add_object('ped2', 'ped', [3, 7])
        uid_relation2 = vcd.add_relation_object_object('follows2', 'follow', uid_ped2, uid_ped1, frame_value=[5, 6])

        self.assertEqual(vcd.get_relation(uid_relation2)['rdf_subjects'][0]['uid'], uid_ped2)
        self.assertEqual(vcd.get_relation(uid_relation2)['rdf_subjects'][0]['type'], 'object')
        self.assertEqual(vcd.get_relation(uid_relation2)['rdf_objects'][0]['uid'], uid_ped1)
        self.assertEqual(vcd.get_relation(uid_relation2)['rdf_objects'][0]['type'], 'object')
        self.assertEqual(len(vcd.get_relation(uid_relation2)['rdf_objects']), 1)

        uid_relation2 = vcd.add_relation_object_object('follows2', 'follow', uid_ped2, uid_car1, uid_relation2,
                                                       frame_value=[5, 6], set_mode=core.SetMode.replace)

        self.assertEqual(vcd.get_relation(uid_relation2)['rdf_subjects'][0]['uid'], uid_ped2)
        self.assertEqual(vcd.get_relation(uid_relation2)['rdf_subjects'][0]['type'], 'object')
        self.assertEqual(vcd.get_relation(uid_relation2)['rdf_objects'][0]['uid'], uid_car1)
        self.assertEqual(vcd.get_relation(uid_relation2)['rdf_objects'][0]['type'], 'object')
        self.assertEqual(len(vcd.get_relation(uid_relation2)['rdf_objects']), 1)

    def test_rm_element_data(self):
        vcd = core.OpenLABEL()

        # Add an object
        uid1 = vcd.add_object(name="someName")

        # Add two bounding boxes
        bbox1 = types.bbox(name="box_left", val=[0, 10, 40, 50])
        bbox2 = types.bbox(name="box_right", val=[20, 20, 25, 25])
        vcd.add_object_data(uid=uid1, object_data=bbox1, frame_value=(0, 30))
        vcd.add_object_data(uid=uid1, object_data=bbox2, frame_value=(10, 35))

        # The object is therefore defined from 0 to 35
        fis = vcd.get_element_frame_intervals(core.ElementType.object, uid1).get_dict()
        self.assertDictEqual(fis[0], {'frame_start': 0, 'frame_end': 35})

        # Now remove some frames
        vcd.rm_element_data_from_frames_by_name(core.ElementType.object, uid1, "box_left", (5, 15))
        fis = vcd.get_element_data_frame_intervals(core.ElementType.object, uid1, "box_left").get_dict()
        self.assertDictEqual(fis[0], {'frame_start': 0, 'frame_end': 4})
        self.assertDictEqual(fis[1], {'frame_start': 16, 'frame_end': 30})





if __name__ == '__main__':  # This changes the command-line entry point to call unittest.main()
    print("Running " + os.path.basename(__file__))
    unittest.main()
