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
        # In a city, being sunny, the ego-vehicle drives straight following a cyclist, and a van.
        # The van and cyclist turn right and the ego-vehicle as well. The road is single lane, and there are
        # parked cars at both sides of it. There are some pedestrians walking at the footwalk.

        # The objects already labeled are the pedestrians, cars, vans, etc. Inspecting the VCD we can see the uids
        # of the main actors
        uid_cyclist = 2
        uid_van = 1

        # We need to add the Ego-vehicle
        uid_ego = vcd.add_object(name="Ego-vehicle", semantic_type="Car")

        # Now the actions
        # Driving straight
        vcd.add_object_data(uid=uid_van, object_data=types.text(name="action", val="Driving straight"),
                            frame_value=[(0, 30), (32, 153)])
        vcd.add_object_data(uid=uid_cyclist, object_data=types.text(name="action", val="Driving straight"),
                            frame_value=[(0, 57), (59, 153)])
        vcd.add_object_data(uid=uid_ego, object_data=types.text(name="action", val="Driving straight"),
                            frame_value=[(0, 75), (77, 153)])
        # Turning right
        vcd.add_object_data(uid=uid_van, object_data=types.text(name="action", val="Turning right"), frame_value=31)
        vcd.add_object_data(uid=uid_cyclist, object_data=types.text(name="action", val="Turning right"), frame_value=58)
        vcd.add_object_data(uid=uid_ego, object_data=types.text(name="action", val="Turning right"), frame_value=76)

        # Parked cars and vans, and walking pedestrians
        for uid_object, object_ in vcd.data['vcd']['objects'].items():
            if object_['type'] == 'Car':
                vcd.add_object_data(uid=uid_object, object_data=types.text(name="action", val="Parked"))
            elif object_['type'] == 'Pedestrian':
                vcd.add_object_data(uid=uid_object, object_data=types.text(name="action", val="Walking"))
            elif object_['type'] == "Van" and uid_object is not uid_van:
                vcd.add_object_data(uid=uid_object, object_data=types.text(name="action", val="Parked"))

        # Context
        vcd.add_context(name="", semantic_type="City")
        vcd.add_context(name="", semantic_type="Sunny")

        # Store
        if not os.path.isfile('./etc/test_kitti_tracking_0_actions.json'):
            vcd.save('./etc/test_kitti_tracking_0_actions.json', False)

if __name__ == '__main__':  # This changes the command-line entry point to call unittest.main()
    print("Running " + os.path.basename(__file__))
    unittest.main()
