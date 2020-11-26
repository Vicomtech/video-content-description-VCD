"""
VCD (Video Content Description) library v4.3.0

Project website: http://vcd.vicomtech.org

Copyright (C) 2020, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.3.0.
VCD is distributed under MIT License. See LICENSE.

"""

import unittest
import os
import vcd.core as core
import vcd.types as types
import vcd.utils as utils


class TestBasic(unittest.TestCase):

    # Semantics
    def test_semantics(self):
        vcd = core.VCD()

        ont_uid_0 = vcd.add_ontology("http://www.vicomtech.org/viulib/ontology")
        ont_uid_1 = vcd.add_ontology("http://www.alternativeURL.org/ontology")

        # Let's create a static Context
        officeUID = vcd.add_context('Office', '#Office', frame_value=None, uid=None, ont_uid=ont_uid_0)

        for frameNum in range(0, 30):
            if frameNum == 3:
                startTalkingUID = vcd.add_event('StartTalking', '#StartTalking', frameNum, uid=None, ont_uid=ont_uid_0)
                talkingUID = vcd.add_action('Talking', '#Talking', frameNum, uid=None, ont_uid=ont_uid_0)
                noisyUID = vcd.add_context('Noisy', '', frameNum)  # No ontology

                relation1UID = vcd.add_relation_subject_object('', '#Starts',
                                                               core.ElementType.event, startTalkingUID,
                                                               core.ElementType.action, talkingUID,
                                                               relation_uid=None, ont_uid=ont_uid_0, frame_value=None)

                relation2UID = vcd.add_relation_subject_object('', '#Causes',
                                                               core.ElementType.action, talkingUID,
                                                               core.ElementType.context, noisyUID,
                                                               relation_uid=None, ont_uid=ont_uid_0, frame_value=None)

                self.assertEqual(vcd.get_num_relations(), 2, "Should be 2.")
                self.assertEqual(len(vcd.get_relation(relation2UID)['rdf_subjects']), 1, "Should be 1")
                self.assertEqual(
                    vcd.get_relation(relation2UID)['rdf_subjects'][0]['uid'], talkingUID, "Should be equal"
                )

                # print(vcd.stringify(pretty=False, validate=False))
                # print("Frame 3, dynamic only message: ", vcd.stringify_frame(frameNum, dynamic_only=True))
                # print("Frame 3, full message: ", vcd.stringify_frame(frameNum, dynamic_only=False))

            elif 3 <= frameNum <= 11:
                vcd.add_action('Talking', '#Talking', frameNum, talkingUID)
                vcd.add_context('Noisy', '', frameNum, noisyUID)

                # print("Frame ", frameNum, ", dynamic only message: ", vcd.stringify_frame(frameNum, dynamic_only=True))
                # print("Frame ", frameNum, ", full message: ", vcd.stringify_frame(frameNum, dynamic_only=False))

        if not os.path.isfile('./etc/vcd430_test_semantics.json'):
            vcd.save('./etc/vcd430_test_semantics.json', True)

        vcd_read = core.VCD('./etc/vcd430_test_semantics.json', validation=True)
        vcd_read_stringified = vcd_read.stringify()
        vcd_stringified = vcd.stringify()

        # print(vcd_stringified)
        self.assertEqual(vcd_read_stringified, vcd_stringified)

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
        uid_pedestrian1 = vcd_a.add_object(name="", semantic_type="Pedestrian", frame_value=None, ont_uid="0") # therefore its uri is "http://vcd.vicomtech.org/ontology/automotive/#Pedestrian"
        uid_car1 = vcd_a.add_object(name="", semantic_type="Car", frame_value=None, ont_uid="0")
        uid_pedestrian1 = vcd_b.add_object(name="", semantic_type="Pedestrian", frame_value=None,ont_uid="0")
        uid_car1 = vcd_b.add_object(name="", semantic_type="Car", frame_value=None, ont_uid="0")
        uid_pedestrian1 = vcd_c.add_object(name="", semantic_type="Pedestrian", frame_value=None,ont_uid="0")
        uid_car1 = vcd_c.add_object(name="", semantic_type="Car", frame_value=None, ont_uid="0")


        # 4.- Add (intransitive) Actions

        # Option a) Add (intransitive) Actions as Object attributes
        # Pro: simple, quick code, less bytes in JSON
        # Con: No explicit Relation, lack of extensibility, only valid for simple subject-predicates
        vcd_a.add_object_data(uid=uid_pedestrian1, object_data=types.text(name="action", val="Walking"))
        vcd_a.add_object_data(uid=uid_car1, object_data=types.text(name="action", val="Parked"))

        # Option b) Add (intransitive) Actions as Actions and use Relations to link to Objects
        # Pro: Action as element with entity, can add action_data, link to other Objects or complex Relations
        # Con: long to write, occupy more bytes in JSON, more difficult to parse
        uid_action1 = vcd_b.add_action(name="", semantic_type="Walking", frame_value=None, ont_uid="0")
        uid_rel1 = vcd_b.add_relation(name="", semantic_type="performsAction", ont_uid="0")
        vcd_b.add_rdf(relation_uid=uid_rel1, rdf_type=core.RDF.subject,
                    element_uid=uid_pedestrian1, element_type=core.ElementType.object)
        vcd_b.add_rdf(relation_uid=uid_rel1, rdf_type=core.RDF.object,
                    element_uid=uid_action1, element_type=core.ElementType.action)

        uid_action2 = vcd_b.add_action(name="", semantic_type="Parked", frame_value=None, ont_uid="0")
        uid_rel2 = vcd_b.add_relation(name="", semantic_type="performsAction", ont_uid="0")
        vcd_b.add_rdf(relation_uid=uid_rel2, rdf_type=core.RDF.subject,
                    element_uid=uid_car1, element_type=core.ElementType.object)
        vcd_b.add_rdf(relation_uid=uid_rel2, rdf_type=core.RDF.object,
                    element_uid=uid_action2, element_type=core.ElementType.action)

        # Option c) Add Actions as Actions, and use action_Data to point to subject Object
        # Pro: simple as option a
        # Con: sames as a
        uid_action1 = vcd_c.add_action(name="", semantic_type="Walking", frame_value=None, ont_uid="0")
        uid_action2 = vcd_c.add_action(name="", semantic_type="Parked", frame_value=None, ont_uid="0")
        vcd_c.add_action_data(uid=uid_action1, action_data=types.num(name="subject", val=int(uid_pedestrian1)))
        vcd_c.add_action_data(uid=uid_action2, action_data=types.num(name="subject", val=int(uid_car1)))

        if not os.path.isfile('./etc/vcd430_test_actions_a.json'):
            vcd_a.save('./etc/vcd430_test_actions_a.json')

        vcd_read = core.VCD('./etc/vcd430_test_actions_a.json')
        self.assertEqual(vcd_read.stringify(False, False), vcd_a.stringify(False, False))

        if not os.path.isfile('./etc/vcd430_test_actions_b.json'):
            vcd_b.save('./etc/vcd430_test_actions_b.json')

        vcd_read = core.VCD('./etc/vcd430_test_actions_b.json')
        self.assertEqual(vcd_read.stringify(False, False), vcd_b.stringify(False, False))

        if not os.path.isfile('./etc/vcd430_test_actions_c.json'):
            vcd_c.save('./etc/vcd430_test_actions_c.json')

        vcd_read = core.VCD('./etc/vcd430_test_actions_c.json')
        self.assertEqual(vcd_read.stringify(False, False), vcd_c.stringify(False, False))

    def test_relations(self):
        # This tests shows how relations can be created with and without frame interval information
        vcd = core.VCD()

        # Case 1: RDF elements don't have frame interval, but relation does
        # So objects don't appear in frames, but relation does. Reading the relation leads to the static objects
        uid1 = vcd.add_object(name="", semantic_type="Car")
        uid2 = vcd.add_object(name="", semantic_type="Pedestrian")

        vcd.add_relation_object_object(name="", semantic_type="isNear",
                                       object_uid_1=uid1, object_uid_2=uid2,
                                       frame_value=(0, 10))

        self.assertEqual(vcd.data['vcd']['frame_intervals'][0]['frame_start'], 0)
        self.assertEqual(vcd.data['vcd']['frame_intervals'][0]['frame_end'], 10)
        self.assertEqual(vcd.data['vcd']['relations']["0"]['frame_intervals'][0]['frame_start'], 0)
        self.assertEqual(vcd.data['vcd']['relations']["0"]['frame_intervals'][0]['frame_end'], 10)
        for frame in vcd.data['vcd']['frames'].values():
            self.assertEqual(len(frame['relations']), 1)

        if not os.path.isfile('./etc/vcd430_test_relations_1.json'):
            vcd.save('./etc/vcd430_test_relations_1.json')

        vcd_read = core.VCD('./etc/vcd430_test_relations_1.json')
        self.assertEqual(vcd_read.stringify(False, False), vcd.stringify(False, False))

        # Case 2: RDF elements defined with long frame intervals, and relation with smaller inner frame interval
        vcd = core.VCD()

        uid1 = vcd.add_object(name="", semantic_type="Car", frame_value=(0, 10))
        uid2 = vcd.add_object(name="", semantic_type="Pedestrian", frame_value=(5, 15))

        vcd.add_relation_object_object(name="", semantic_type="isNear",
                                       object_uid_1=uid1, object_uid_2=uid2,
                                       frame_value=(7, 9))

        self.assertEqual(vcd.data['vcd']['frame_intervals'][0]['frame_start'], 0)
        self.assertEqual(vcd.data['vcd']['frame_intervals'][0]['frame_end'], 15)
        self.assertEqual(vcd.data['vcd']['relations']["0"]['frame_intervals'][0]['frame_start'], 7)
        self.assertEqual(vcd.data['vcd']['relations']["0"]['frame_intervals'][0]['frame_end'], 9)
        for frame_key, frame_val in vcd.data['vcd']['frames'].items():
            if 7 <= frame_key <= 9:
                self.assertEqual(len(frame_val['relations']), 1)

        if not os.path.isfile('./etc/vcd430_test_relations_2.json'):
            vcd.save('./etc/vcd430_test_relations_2.json')

        vcd_read = core.VCD('./etc/vcd430_test_relations_2.json')
        self.assertEqual(vcd_read.stringify(False, False), vcd.stringify(False, False))

        # Case 3: RDF elements have frame interval and relation doesn't (so it is left frame-less)
        vcd = core.VCD()

        uid1 = vcd.add_object(name="", semantic_type="Car", frame_value=(0, 10))
        uid2 = vcd.add_object(name="", semantic_type="Pedestrian", frame_value=(5, 15))
        uid3 = vcd.add_object(name="", semantic_type="Other", frame_value=(15, 20))

        uid4 = vcd.add_relation_object_object(name="", semantic_type="isNear",
                                       object_uid_1=uid1, object_uid_2=uid2)

        # The relation does not have frame information
        self.assertEqual('frame_intervals' in vcd.get_relation(uid4), False)

        self.assertEqual(vcd.data['vcd']['frame_intervals'][0]['frame_start'], 0)
        self.assertEqual(vcd.data['vcd']['frame_intervals'][0]['frame_end'], 20)
        for frame_key, frame_val in vcd.data['vcd']['frames'].items():
            if 0 <= frame_key <= 15:
                self.assertEqual(frame_val.get('relations'), None)

        if not os.path.isfile('./etc/vcd430_test_relations_3.json'):
            vcd.save('./etc/vcd430_test_relations_3.json')

        vcd_read = core.VCD('./etc/vcd430_test_relations_3.json')
        self.assertEqual(vcd_read.stringify(False, False), vcd.stringify(False, False))

        pass

    # Add semantics to the KITTI tracking #0
    def test_scene_KITTI_Tracking_0(self):
        sequence_number = 0
        vcd_file_name = "./etc/vcd430_kitti_tracking_" + str(sequence_number).zfill(
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
        7) Ego-vehicle isSubjectOfAction following1
        8) Cyclist isObjectOfAction following1
        9) Cyclist isSubjectOfAction following2
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
        uid_ego = vcd.get_object_uid_by_name(name="Egocar")

        # The objects already labeled are the pedestrians, cars, vans, etc. Inspecting the VCD we can see the uids
        # of the main actors
        # Cyclist, van (4-5), (17) and (19)
        uid_cyclist = "2"
        uid_van = "1"

        # Driving straight (6)
        uid_action_6 = vcd.add_action(name="", semantic_type="driving-straight", frame_value=[(0, 30), (41, 153)])
        vcd.add_relation_object_action(name="", semantic_type="isSubjectOfAction", object_uid=uid_ego, action_uid=uid_action_6)

        # Ego-vehicle following Cyclist (7-8)
        uid_action_7 = vcd.add_action(name="", semantic_type="following")  # , frame_value=[(0, 153)])
        vcd.add_relation_object_action(name="", semantic_type="isSubjectOfAction", object_uid=uid_ego, action_uid=uid_action_7)
        vcd.add_relation_object_action(name="", semantic_type="isObjectOfAction", object_uid=uid_cyclist, action_uid=uid_action_7)

        # Cyclist following Van (9-10)
        uid_action_9 = vcd.add_action(name="", semantic_type="following")
        vcd.add_relation_object_action(name="", semantic_type="isSubjectOfAction",
                                       object_uid=uid_cyclist, action_uid=uid_action_9)
        vcd.add_relation_object_action(name="", semantic_type="isObjectOfAction",
                                       object_uid=uid_van, action_uid=uid_action_9)

        # Van Turn-right (11)
        uid_action_11 = vcd.add_action(name="", semantic_type="turning-right",
                                       frame_value=(31, 40))
        vcd.add_relation_object_action(name="", semantic_type="isSubjectOfAction",
                                       object_uid=uid_van, action_uid=uid_action_11)

        # Cyclist Turn-right (12)
        uid_action_12 = vcd.add_action(name="", semantic_type="turning-right", frame_value=(58, 65))
        vcd.add_relation_object_action(name="", semantic_type="isSubjectOfAction", object_uid=uid_cyclist, action_uid=uid_action_12)

        # Ego-vehicle Turn-right (13)
        uid_action_13 = vcd.add_action(name="", semantic_type="turning-right", frame_value=(76, 84))
        vcd.add_relation_object_action(name="", semantic_type="isSubjectOfAction", object_uid=uid_ego, action_uid=uid_action_13)

        # Road object (14), footwalk (15) and road attribute (16)
        uid_road = vcd.add_object(name="", semantic_type="road")
        uid_footwalk = vcd.add_object(name="", semantic_type="footwalk")
        vcd.add_object_data(uid=uid_road, object_data=types.text(name="road-type", val="single-lane"))

        # Cars (and a van) are parked (18), pedestrians are walking (20)
        # NOTE: read frame_interval from object, so the action is bounded to such limits
        for uid_obj_aux, object_ in vcd.data['vcd']['objects'].items():
            frame_intervals = object_.get('frame_intervals')
            if frame_intervals is None:  # Ignore static objects
                continue
            frame_value = utils.as_frame_intervals_array_tuples(frame_intervals)
            if object_['type'] == 'Car':
                uid_act_aux = vcd.add_action(name="", semantic_type="parked", frame_value=frame_value)
                vcd.add_relation_object_action(name="", semantic_type="isSubjectOfAction", object_uid=uid_obj_aux, action_uid=uid_act_aux)

            elif object_['type'] == 'Pedestrian':
                uid_act_aux = vcd.add_action(name="", semantic_type="walking", frame_value=frame_value)
                vcd.add_relation_object_action(name="", semantic_type="isSubjectOfAction", object_uid=uid_obj_aux, action_uid=uid_act_aux)
                vcd.add_relation_object_action(name="", semantic_type="isObjectOfAction", object_uid=uid_footwalk, action_uid=uid_act_aux)

            elif object_['type'] == "Van" and uid_obj_aux is not uid_van:
                uid_act_aux = vcd.add_action(name="", semantic_type="parked", frame_value=frame_value)
                vcd.add_relation_object_action(name="", semantic_type="isSubjectOfAction", object_uid=uid_obj_aux, action_uid=uid_act_aux)

        # Store frame 0 - static and dynamic
        if not os.path.isfile('./etc/vcd430_kitti_tracking_0000_frame_0_static-dynamic.json'):
            vcd.save_frame(frame_num=0, file_name='./etc/vcd430_kitti_tracking_0000_frame_0_static-dynamic.json', dynamic_only=False)

        # Same but dynamic only
        if not os.path.isfile('./etc/vcd430_kitti_tracking_0000_frame_0_dynamic.json'):
            vcd.save_frame(frame_num=0, file_name='./etc/vcd430_kitti_tracking_0000_frame_0_dynamic.json',
                           dynamic_only=True)

        # Store
        if not os.path.isfile('./etc/vcd430_kitti_tracking_0000_actions.json'):
            vcd.save('./etc/vcd430_kitti_tracking_0000_actions.json', False)

        vcd_read = core.VCD('./etc/vcd430_kitti_tracking_0000_actions.json')
        # vcd.save('./etc/prueba.json')
        self.assertEqual(vcd_read.stringify(False, False), vcd.stringify(False, False))

    def test_scene_KITTI_Tracking_3(self):
        sequence_number = 3
        vcd_file_name = "./etc/vcd430_kitti_tracking_" + str(sequence_number).zfill(
            4) + ".json"
        vcd = core.VCD(vcd_file_name)

        frame_num_last = vcd.get_frame_intervals().get_outer()['frame_end']

        '''
        "In a city, being sunny, the ego-vehicle drives in the left lane of a single-way two-lanes road, 
        Two other cars drive in the right lane. When the cars pass the ego-vehicle, then the ego-vehicle changes 
        to the right lane, and then the ego-vehicle drives in the right lane."
        '''
        vcd.add_metadata_properties({"cnl_text": "In a city, being sunny, the ego-vehicle drives in the left lane of a single-way two-lanes road, Two other cars drive in the right lane. When the cars pass the ego-vehicle, then the ego-vehicle changes to the right lane, and then the ego-vehicle drives in the right lane."})

        # Let's add VCD entries following the order
        # Contexts (1-2)
        vcd.add_context(name="City1", semantic_type="City")
        vcd.add_context(name="Sunny1", semantic_type="Sunny")

        # Add non-labeled actors (Ego-vehicle and lanes)
        uid_ego = vcd.get_object_uid_by_name(name="Egocar")
        uid_lane_left = vcd.add_object(name="Lane1", semantic_type="Lane")
        uid_lane_right = vcd.add_object(name="Lane2", semantic_type="Lane")
        uid_road = vcd.add_object(name="Road1", semantic_type="Road")

        vcd.add_element_data(element_type=core.ElementType.object, uid=uid_lane_left, element_data=types.text(name="Position", val="Left"))
        vcd.add_element_data(element_type=core.ElementType.object, uid=uid_lane_right, element_data=types.text(name="Position", val="Right"))
        vcd.add_element_data(element_type=core.ElementType.object, uid=uid_road, element_data=types.text(name="Direction", val="Single-way"))
        vcd.add_element_data(element_type=core.ElementType.object, uid=uid_road, element_data=types.num(name="NumberOfLanes", val=2))

        vcd.add_relation_object_object(name="", semantic_type="isPartOf", object_uid_1=uid_lane_left, object_uid_2=uid_road)
        vcd.add_relation_object_object(name="", semantic_type="isPartOf", object_uid_1=uid_lane_right, object_uid_2=uid_road)

        # Actors
        uid_car_a = "0"   # (0, 75)
        uid_car_b = "1"   # (22, 143)
        uid_car_other_a = "3"
        uid_car_other_b = "4"
        uid_van = "5"
        uid_car_other_c = "6"
        uid_car_other_d = "7"
        uid_car_other_e = "8"

        # Actions
        # Driving straight before lane change
        uid_action_drive_straight_1 = vcd.add_action(name="DriveStraight1", semantic_type="DriveStraight", frame_value=[(0, 31)])  # Approx. at frame 31, the ego vehicle starts changing lane
        vcd.add_relation_object_action(name="", semantic_type="isSubjectOfAction", object_uid=uid_ego, action_uid=uid_action_drive_straight_1)
        vcd.add_relation_object_action(name="", semantic_type="isObjectOfAction", object_uid=uid_lane_left,
                                       action_uid=uid_action_drive_straight_1)

        uid_action_drive_straight_2 = vcd.add_action(name="DriveStraight2", semantic_type="DriveStraight", frame_value=vcd.get_element_frame_intervals(element_type=core.ElementType.object, uid=uid_car_a).get())
        vcd.add_relation_object_action(name="", semantic_type="isSubjectOfAction", object_uid=uid_car_a, action_uid=uid_action_drive_straight_2)
        vcd.add_relation_object_action(name="", semantic_type="isObjectOfAction", object_uid=uid_lane_right,
                                       action_uid=uid_action_drive_straight_2)

        uid_action_drive_straight_3 = vcd.add_action(name="DriveStraight3", semantic_type="DriveStraight", frame_value=vcd.get_element_frame_intervals(element_type=core.ElementType.object, uid=uid_car_b).get())
        vcd.add_relation_object_action(name="", semantic_type="isSubjectOfAction", object_uid=uid_car_b, action_uid=uid_action_drive_straight_3)
        vcd.add_relation_object_action(name="", semantic_type="isObjectOfAction", object_uid=uid_lane_right,
                                       action_uid=uid_action_drive_straight_3)

        # Lane changing (event and action)
        uid_action_lane_change = vcd.add_action(name="LaneChange1", semantic_type="LaneChange", frame_value=[(33, 75)])
        vcd.add_relation_object_action(name="", semantic_type="isSubjectOfAction", object_uid=uid_ego, action_uid=uid_action_lane_change)
        #uid_event_pass = vcd.add_event(name="CarB_passes_EgoCar", semantic_type="Pass", frame_value=32)
        #vcd.add_relation_subject_object(name="", semantic_type="Causes", subject_type=core.ElementType.event, subject_uid=uid_event_pass,
        #                                object_type=core.ElementType.action, object_uid=uid_action_lane_change)

        uid_event_pass = vcd.add_event(name="Pass1", semantic_type="Pass", frame_value=32)
        vcd.add_relation_subject_object(name="", semantic_type="isSubjectOfEvent", subject_type=core.ElementType.object, subject_uid=uid_car_b,
                                        object_type=core.ElementType.event, object_uid=uid_event_pass)
        vcd.add_relation_subject_object(name="", semantic_type="isObjectOfEvent", subject_type=core.ElementType.object,
                                        subject_uid=uid_ego,
                                        object_type=core.ElementType.event, object_uid=uid_event_pass)
        vcd.add_relation_subject_object(name="", semantic_type="causes", subject_type=core.ElementType.event,
                                        subject_uid=uid_event_pass,
                                        object_type=core.ElementType.action, object_uid=uid_action_lane_change)


        # Driving straight after lane change
        uid_action_drive_straight_4 = vcd.add_action(name="DriveStraight1", semantic_type="DriveStraight", frame_value=[(76, frame_num_last)])  # Approx. at frame 31, the ego vehicle starts changing lane
        vcd.add_relation_object_action(name="", semantic_type="isSubjectOfAction", object_uid=uid_ego, action_uid=uid_action_drive_straight_4)
        vcd.add_relation_object_action(name="", semantic_type="isObjectOfAction", object_uid=uid_lane_right,
                                       action_uid=uid_action_drive_straight_4)

        vcd.add_relation_action_action(name="", semantic_type="meets", action_uid_1=uid_action_lane_change, action_uid_2=uid_action_drive_straight_4, frame_value=75)

        # Store
        if not os.path.isfile('./etc/vcd430_kitti_tracking_0003_actions.json'):
            vcd.save('./etc/vcd430_kitti_tracking_0003_actions.json', validate=True)

if __name__ == '__main__':  # This changes the command-line entry point to call unittest.main()
    print("Running " + os.path.basename(__file__))
    unittest.main()

