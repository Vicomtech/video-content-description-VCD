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

if __name__ == '__main__':  # This changes the command-line entry point to call unittest.main()
    print("Running " + os.path.basename(__file__))
    unittest.main()
