"""
VCD (Video Content Description) library v4.1.0

Project website: http://vcd.vicomtech.org

Copyright (C) 2020, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.1.0.
VCD is distributed under MIT License. See LICENSE.

"""

import unittest
import os
import sys
sys.path.insert(0, "..")
import vcd.core as core
import vcd.types as types
import vcd.utils as utils


class TestBasic(unittest.TestCase):

    # Create some basic content, without time information, and do some basic search
    def test_actions(self):
        # 1.- Create a VCD instance
        vcd_a = core.VCD()
        vcd_b = core.VCD()
        vcd_c = core.VCD()

        # 2.- Add ontology
        vcd_a.add_ontology(ontology_name="http://vcd.vicomtech.org/ontology/automotive")
        vcd_b.add_ontology(ontology_name="http://vcd.vicomtech.org/ontology/automotive")
        vcd_c.add_ontology(ontology_name="http://vcd.vicomtech.org/ontology/automotive")


        # 3.- Add some objects
        uid_pedestrian1 = vcd_a.add_object(name="", semantic_type="Pedestrian", frame_value=None, ont_uid=0) # therefore its uri is "http://vcd.vicomtech.org/ontology/automotive/#Pedestrian"
        uid_car1 = vcd_a.add_object(name="", semantic_type="Car", frame_value=None, ont_uid=0)
        uid_pedestrian1 = vcd_b.add_object(name="", semantic_type="Pedestrian", frame_value=None,ont_uid=0)
        uid_car1 = vcd_b.add_object(name="", semantic_type="Car", frame_value=None, ont_uid=0)
        uid_pedestrian1 = vcd_c.add_object(name="", semantic_type="Pedestrian", frame_value=None,ont_uid=0)
        uid_car1 = vcd_c.add_object(name="", semantic_type="Car", frame_value=None, ont_uid=0)


        # 4.- Add (intransitive) Actions

        # Option a) Add (intransitive) Actions as Object attributes
        # Pro: simple, quick code, less bytes in JSON
        # Con: No explicit Relation, lack of extensibility, only valid for simple subject-predicates
        vcd_a.add_object_data(uid=uid_pedestrian1, object_data=types.text(name="action", val="Walking"))
        vcd_a.add_object_data(uid=uid_car1, object_data=types.text(name="action", val="Parked"))

        # Option b) Add (intransitive) Actions as Actions and use Relations to link to Objects
        # Pro: Action as element with entity, can add action_data, link to other Objects or complex Relations
        # Con: long to write, occupy more bytes in JSON, more difficult to parse
        uid_action1 = vcd_b.add_action(name="", semantic_type="Walking", frame_value=None, ont_uid=0)
        uid_rel1 = vcd_b.add_relation(name="", semantic_type="performsAction", ont_uid=0)
        vcd_b.add_rdf(relation_uid=uid_rel1, rdf_type=core.RDF.subject,
                    element_uid=uid_pedestrian1, element_type=core.ElementType.object)
        vcd_b.add_rdf(relation_uid=uid_rel1, rdf_type=core.RDF.object,
                    element_uid=uid_action1, element_type=core.ElementType.action)

        uid_action2 = vcd_b.add_action(name="", semantic_type="Parked", frame_value=None, ont_uid=0)
        uid_rel2 = vcd_b.add_relation(name="", semantic_type="performsAction", ont_uid=0)
        vcd_b.add_rdf(relation_uid=uid_rel2, rdf_type=core.RDF.subject,
                    element_uid=uid_car1, element_type=core.ElementType.object)
        vcd_b.add_rdf(relation_uid=uid_rel2, rdf_type=core.RDF.object,
                    element_uid=uid_action2, element_type=core.ElementType.action)

        # Option c) Add Actions as Actions, and use action_Data to point to subject Object
        # Pro: simple as option a
        # Con: sames as a
        uid_action1 = vcd_c.add_action(name="", semantic_type="Walking", frame_value=None, ont_uid=0)
        uid_action2 = vcd_c.add_action(name="", semantic_type="Parked", frame_value=None, ont_uid=0)
        vcd_c.add_action_data(uid=uid_action1, action_data=types.num(name="subject", val=uid_pedestrian1))
        vcd_c.add_action_data(uid=uid_action2, action_data=types.num(name="subject", val=uid_car1))

        if not os.path.isfile('./etc/test_actions_a.json'):
            vcd_a.save('./etc/test_actions_a.json')

        if not os.path.isfile('./etc/test_actions_b.json'):
            vcd_b.save('./etc/test_actions_b.json')

        if not os.path.isfile('./etc/test_actions_c.json'):
            vcd_c.save('./etc/test_actions_c.json')

    # Add semantics to the KITTI tracking #0
    def test_scene_KITTI_Tracking_0(self):
        sequence_number = 0
        vcd_file_name = "../converters/kittiConverter/etc/vcd_410_kitti_tracking_" + str(sequence_number).zfill(
            4) + ".json"
        vcd = core.VCD(vcd_file_name)

        # Natural language scene description:
        # In a city, being sunny, the ego-vehicle drives straight following a cyclist, and a van. The van, cyclist
        # and ego-vehicle turn right. The road is single lane, and there are parked cars at both sides of it. There
        # are some pedestrians walking along the footwalk.

        '''
        1) City is a Context
        2) Sunny is a Context
        3) Ego-vehicle is an Object
        4) Cyclist is an Object
        5) Van is an Object
        6) Ego-vehicle isSubjectOfAction drives-straight
        7) Ego-vehicle performsAction following1
        8) Cyclist isObjectOfAction following1
        9) Cyclist performsAction following2
        10) Van isObjectOfAction following2
        11) Van isObjectOfAction turn-right
        12) Cyclist isObjectOfAction turn-right
        13) Ego-vehicle isObjectOfAction turn-right 
        14) Road is an Object
        15) Footwalk is an Object
        16) Road hasAttribute single-lane
        17) Cars are Objects (multiple Car is Object)
        18) Cars performAction Parked
        19) Pedestrians are Objects
        20) Pedestrians isSubjectOfAction Walking
        21) Footwalk isObjectOfAction Walking
        '''
        # Let's add VCD entries following the order
        # Contexts (1-2)
        vcd.add_context(name="", semantic_type="City")
        vcd.add_context(name="", semantic_type="Sunny")

        # Ego-vehicle (3)
        uid_ego = vcd.add_object(name="Ego-vehicle", semantic_type="Car")

        # The objects already labeled are the pedestrians, cars, vans, etc. Inspecting the VCD we can see the uids
        # of the main actors
        # Cyclist, van (4-5), (17) and (19)
        uid_cyclist = 2
        uid_van = 1

        # Driving straight (6)
        uid_action_6 = vcd.add_action(name="", semantic_type="driving-straight", frame_value=[(0, 30), (41, 153)])
        uid_rel_6 = vcd.add_relation(name="", semantic_type="isSubjectOfAction")
        vcd.add_rdf(relation_uid=uid_rel_6, rdf_type=core.RDF.subject, element_uid=uid_ego, element_type=core.ElementType.object)
        vcd.add_rdf(relation_uid=uid_rel_6, rdf_type=core.RDF.object, element_uid=uid_action_6, element_type=core.ElementType.action)

        # Ego-vehicle following Cyclist (7-8)
        uid_action_7 = vcd.add_action(name="", semantic_type="following")  # , frame_value=[(0, 153)])
        uid_rel_7 = vcd.add_relation(name="", semantic_type="isSubjectOfAction")
        vcd.add_rdf(relation_uid=uid_rel_7, rdf_type=core.RDF.subject, element_uid=uid_ego, element_type=core.ElementType.object)
        vcd.add_rdf(relation_uid=uid_rel_7, rdf_type=core.RDF.object, element_uid=uid_action_7, element_type=core.ElementType.action)
        uid_rel_8 = vcd.add_relation(name="", semantic_type="isObjectOfAction")
        vcd.add_rdf(relation_uid=uid_rel_8, rdf_type=core.RDF.subject, element_uid=uid_cyclist, element_type=core.ElementType.object)
        vcd.add_rdf(relation_uid=uid_rel_8, rdf_type=core.RDF.object, element_uid=uid_action_7, element_type=core.ElementType.action)

        # Cyclist following Van (9-10)
        uid_action_9 = vcd.add_action(name="", semantic_type="following")  # , frame_value=[(0, 153)])
        uid_rel_9 = vcd.add_relation(name="", semantic_type="isSubjectOfAction")
        vcd.add_rdf(uid_rel_9, rdf_type=core.RDF.subject, element_uid=uid_cyclist, element_type=core.ElementType.object)
        vcd.add_rdf(uid_rel_9, rdf_type=core.RDF.object, element_uid=uid_action_9, element_type=core.ElementType.action)
        uid_rel_10 = vcd.add_relation(name="", semantic_type="isObjectOfAction")
        vcd.add_rdf(relation_uid=uid_rel_10, rdf_type=core.RDF.subject, element_uid=uid_van, element_type=core.ElementType.object)
        vcd.add_rdf(relation_uid=uid_rel_10, rdf_type=core.RDF.object, element_uid=uid_action_9, element_type=core.ElementType.action)

        # Van Turn-right (11)
        uid_action_11 = vcd.add_action(name="", semantic_type="turning-right", frame_value=(31, 40))
        uid_rel_11 = vcd.add_relation(name="", semantic_type="isSubjectOfAction")
        vcd.add_rdf(relation_uid=uid_rel_11, rdf_type=core.RDF.subject, element_uid=uid_van, element_type=core.ElementType.object)
        vcd.add_rdf(relation_uid=uid_rel_11, rdf_type=core.RDF.object, element_uid=uid_action_11, element_type=core.ElementType.action)

        # Cyclist Turn-right (12)
        uid_action_12 = vcd.add_action(name="", semantic_type="turning-right", frame_value=(58, 65))
        uid_rel_12 = vcd.add_relation(name="", semantic_type="isSubjectOfAction")
        vcd.add_rdf(relation_uid=uid_rel_12, rdf_type=core.RDF.subject, element_uid=uid_cyclist, element_type=core.ElementType.object)
        vcd.add_rdf(relation_uid=uid_rel_12, rdf_type=core.RDF.object, element_uid=uid_action_12,element_type=core.ElementType.action)

        # Ego-vehicle Turn-right (13)
        uid_action_13 = vcd.add_action(name="", semantic_type="turning-right", frame_value=(76, 84))
        uid_rel_13 = vcd.add_relation(name="", semantic_type="isSubjectOfAction")
        vcd.add_rdf(relation_uid=uid_rel_13, rdf_type=core.RDF.subject, element_uid=uid_ego, element_type=core.ElementType.object)
        vcd.add_rdf(relation_uid=uid_rel_13, rdf_type=core.RDF.object, element_uid=uid_action_13,element_type=core.ElementType.action)

        # Road object (14), footwalk (15) and road attribute (16)
        uid_road = vcd.add_object(name="", semantic_type="road")
        uid_footwalk = vcd.add_object(name="", semantic_type="footwalk")
        vcd.add_object_data(uid=uid_road, object_data=types.text(name="road-type", val="single-lane"))

        # Cars (and a van) are parked (18), pedestrians are walking (20)
        # NOTE: read frame_interval from object, so the action is bounded to such limits
        for uid_obj_aux, object_ in vcd.data['vcd']['objects'].items():
            frame_intervals = object_['frame_intervals']
            frame_value = utils.as_frame_intervals_array_tuples(frame_intervals)
            if object_['type'] == 'Car':
                uid_act_aux = vcd.add_action(name="", semantic_type="parked", frame_value=frame_value)
                uid_rel_aux = vcd.add_relation(name="", semantic_type="isSubjectOfAction")
                vcd.add_rdf(relation_uid=uid_rel_aux, rdf_type=core.RDF.subject, element_uid=uid_obj_aux, element_type=core.ElementType.object)
                vcd.add_rdf(relation_uid=uid_rel_aux, rdf_type=core.RDF.object, element_uid=uid_act_aux, element_type=core.ElementType.action)

            elif object_['type'] == 'Pedestrian':
                uid_act_aux = vcd.add_action(name="", semantic_type="walking", frame_value=frame_value)
                uid_rel_aux = vcd.add_relation(name="", semantic_type="isSubjectOfAction")
                vcd.add_rdf(relation_uid=uid_rel_aux, rdf_type=core.RDF.subject, element_uid=uid_obj_aux, element_type=core.ElementType.object)
                vcd.add_rdf(relation_uid=uid_rel_aux, rdf_type=core.RDF.object, element_uid=uid_act_aux, element_type=core.ElementType.action)

                uid_rel_aux2 = vcd.add_relation(name="", semantic_type="isObjectOfAction")
                vcd.add_rdf(relation_uid=uid_rel_aux2, rdf_type=core.RDF.subject, element_uid=uid_footwalk, element_type=core.ElementType.object)
                vcd.add_rdf(relation_uid=uid_rel_aux2, rdf_type=core.RDF.object, element_uid=uid_act_aux, element_type=core.ElementType.action)

            elif object_['type'] == "Van" and uid_obj_aux is not uid_van:
                uid_act_aux = vcd.add_action(name="", semantic_type="parked", frame_value=frame_value)
                uid_rel_aux = vcd.add_relation(name="", semantic_type="isSubjectOfAction")
                vcd.add_rdf(relation_uid=uid_rel_aux, rdf_type=core.RDF.subject, element_uid=uid_obj_aux, element_type=core.ElementType.object)
                vcd.add_rdf(relation_uid=uid_rel_aux, rdf_type=core.RDF.object, element_uid=uid_act_aux, element_type=core.ElementType.action)

        # Store frame 0 - static and dynamic
        if not os.path.isfile('./etc/test_kitti_tracking_0_frame_0_static-dynamic.json'):
            vcd.save_frame(frame_num=0, file_name='./etc/test_kitti_tracking_0_frame_0_static-dynamic.json', dynamic_only=False)

        # Same but dynamic only
        if not os.path.isfile('./etc/test_kitti_tracking_0_frame_0_dynamic.json'):
            vcd.save_frame(frame_num=0, file_name='./etc/test_kitti_tracking_0_frame_0_dynamic.json',
                           dynamic_only=True)

        # Store
        if not os.path.isfile('./etc/test_kitti_tracking_0_actions.json'):
            vcd.save('./etc/test_kitti_tracking_0_actions.json', False)

if __name__ == '__main__':  # This changes the command-line entry point to call unittest.main()
    print("Running " + os.path.basename(__file__))
    unittest.main()
