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
import sys
sys.path.insert(0, "..")
import vcd.core as core
import vcd.types as types


class TestBasic(unittest.TestCase):

    # Create some basic content, without time information, and do some basic search
    def test_create_search_simple(self):
        # 1.- Create a VCD instance
        vcd = core.VCD()

        # 2.- Create the Object
        uid_marcos = vcd.add_object(name='marcos', semantic_type="person")
        self.assertEqual(uid_marcos, "0", "Should be 0")

        # 3.- Add some data to the object
        vcd.add_object_data(uid=uid_marcos, object_data=types.bbox(name='head', val=(10, 10, 30, 30)))
        vcd.add_object_data(uid=uid_marcos, object_data=types.bbox(name='body', val=(0, 0, 60, 120)))
        vcd.add_object_data(uid=uid_marcos, object_data=types.vec(name='speed', val=(0.0, 0.2)))
        vcd.add_object_data(uid=uid_marcos, object_data=types.num(name='accel', val=0.1))

        uid_peter = vcd.add_object(name='peter', semantic_type="person")

        vcd.add_object_data(uid=uid_peter, object_data=types.num(name='age', val=38.0))
        vcd.add_object_data(uid=uid_peter, object_data=types.vec(name='eyeL', val=(0, 0, 10, 10)))
        vcd.add_object_data(uid=uid_peter, object_data=types.vec(name='eyeR', val=(0, 0, 10, 10)))

        # 4.- Write into string
        vcd_string_pretty = vcd.stringify()
        vcd_string_nopretty = vcd.stringify(False)

        # 5.- We can ask VCD
        marcos_ref = vcd.get_element(element_type=core.ElementType.object, uid=uid_marcos)
        # print('Found Object: uid = ', uid_marcos, ', name = ', marcosRef['name'])
        self.assertEqual(uid_marcos, "0", "Should be 0")
        self.assertEqual(marcos_ref['name'], 'marcos', "Should be marcos")

        peter_ref = vcd.get_element(element_type=core.ElementType.object, uid=uid_peter)
        # print('Found Object: uid = ', uid_peter, ', name = ', peterRef['name'])
        self.assertEqual(uid_peter, "1", "Should be 1")
        self.assertEqual(peter_ref['name'], 'peter', "Should be peter")

        # print('VCD string no pretty:\n', vcd_string_nopretty)
        # print('VCD string pretty:\n', vcd_string_pretty)

        if not os.path.isfile('./etc/vcd430_test_create_search_simple_nopretty.json'):
            vcd.save('./etc/vcd430_test_create_search_simple_nopretty.json')

        vcd_file_nopretty = open("./etc/vcd430_test_create_search_simple_nopretty.json", "r")
        vcd_string_nopretty_read = vcd_file_nopretty.read()
        self.assertEqual(vcd_string_nopretty_read, vcd_string_nopretty, "VCD no-pretty not equal to read file")
        vcd_file_nopretty.close()

        if not os.path.isfile('./etc/vcd430_test_create_search_simple_pretty.json'):
            vcd.save('./etc/vcd430_test_create_search_simple_pretty.json', True)

        vcd_file_pretty = open("./etc/vcd430_test_create_search_simple_pretty.json", "r")
        vcd_string_pretty_read = vcd_file_pretty.read()
        self.assertEqual(vcd_string_pretty, vcd_string_pretty_read, "VCD pretty not equal to read file")
        vcd_file_pretty.close()

    # Create some basic content, and show some basic search capabilities
    def test_create_search_mid(self):
        # 1.- Create VCD
        vcd = core.VCD()

        # 2.- Create some content
        uid_marcos = vcd.add_object(name='marcos', semantic_type='#Adult')
        uid_peter = vcd.add_object(name='peter', semantic_type='#Adult')
        uid_katixa = vcd.add_object(name='katixa', semantic_type='#Child')

        vcd.add_object_data(uid=uid_marcos, object_data=types.num('age', 37.0), frame_value=(0, 10))
        vcd.add_object_data(uid=uid_marcos, object_data=types.num('height', 1.75), frame_value=(0, 10))
        vcd.add_object_data(uid=uid_marcos, object_data=types.vec('marks', (5.0, 5.0, 5.0)), frame_value=(0, 10))
        vcd.add_object_data(uid=uid_peter, object_data=types.num('age', 40.0), frame_value=(0, 11))
        vcd.add_object_data(uid=uid_peter, object_data=types.vec('marks', (10.0, 10.0, 10.0)), frame_value=(0, 11))
        vcd.add_object_data(uid=uid_katixa, object_data=types.num('age', 9), frame_value=(5, 10))
        vcd.add_object_data(uid=uid_katixa, object_data=types.num('age', 9.01), frame_value=11)  # by default union
        vcd.add_object_data(uid=uid_katixa, object_data=types.num('age', 9.02), frame_value=12)  # by default union

        # 3.- Search Objects according to some search criteria
        # 3.1.- According to "Object::type" (also for other Elements such as Action, Event, Context)
        uids_child = vcd.get_elements_of_type(element_type=core.ElementType.object, semantic_type="#Child")
        for uid in uids_child:
            # print("Hi there! I'm ", vcd.getObject(uid)['name'], " and I am a child")
            self.assertEqual(vcd.get_object(uid)['name'], 'katixa', "Should be katixa")

        # 3.2.- According to ObjectData
        uids_age = vcd.get_objects_with_object_data_name(data_name='age')
        for uid in uids_age:
            object_ = vcd.get_object(uid=uid)
            # print("Hi there! I'm ", object['name'], " and I have ObjectData with name age")
            if uid == "0":
                self.assertEqual(object_['name'], 'marcos', "Should be marcos")
            elif uid == "1":
                self.assertEqual(object_['name'], 'peter', "Should be peter")
            elif uid == "2":
                self.assertEqual(object_['name'], 'katixa', "Should be katixa")

            frames_with_age = vcd.get_frames_with_object_data_name(uid=uid, data_name='age')
            for frame_interval in frames_with_age.get():
                for frame_num in range(frame_interval[0], frame_interval[1]+1):
                    my_age = vcd.get_object_data(uid=uid, data_name='age', frame_num=frame_num)
                    # print("I am ", myAge['val'], " years old at frame ", frameNum)

                    if uid == "0":
                        self.assertEqual(my_age['val'], 37.0, "Should be 37 for marcos")
                    elif uid == "1":
                        self.assertEqual(my_age['val'], 40.0, "Should be 40 for peter")
                    elif uid == "2" and frame_num < 11:
                        self.assertEqual(my_age['val'], 9, "Should be 9 for katixa while frameNum < 11")
                    elif uid == "2":
                        self.assertEqual(my_age['val'], 9 + 0.01*(frame_num - 10), "Should increase 0.01 per frame for katixa for frameNum >= 11")

        if not os.path.isfile('./etc/vcd430_test_create_search_mid.json'):
            vcd.save('./etc/vcd430_test_create_search_mid.json')

        test_create_search_mid_read = open('./etc/vcd430_test_create_search_mid.json', 'r')
        stringified_vcd = vcd.stringify(False)
        read_vcd = test_create_search_mid_read.read()
        self.assertEqual(read_vcd, stringified_vcd, "Should be equal")
        test_create_search_mid_read.close()

    # Create and remove some content
    def test_remove_simple(self):
        # 1.- Create VCD
        vcd = core.VCD()

        # 2.- Create some objects
        car1_uid = vcd.add_object(name='BMW', semantic_type='#Car')
        car2_uid = vcd.add_object(name='Seat', semantic_type='#Car')
        person1_uid = vcd.add_object(name='John', semantic_type='#Pedestrian')
        trafficSign1UID = vcd.add_object(name='', semantic_type='#StopSign')

        # 3.- Add some content
        # Same FrameInterval (0, 5)
        vcd.add_object_data(uid=person1_uid, object_data=types.bbox('face', (0, 0, 100, 100)), frame_value=(0, 5))
        vcd.add_object_data(uid=person1_uid, object_data=types.bbox('mouth', (0, 0, 10, 10)), frame_value=(0, 5))
        vcd.add_object_data(uid=person1_uid, object_data=types.bbox('hand', (0, 0, 30, 30)), frame_value=(0, 5))
        vcd.add_object_data(uid=person1_uid, object_data=types.bbox('eyeL', (0, 0, 10, 10)), frame_value=(0, 5))
        vcd.add_object_data(uid=person1_uid, object_data=types.bbox('eyeR', (0, 0, 10, 10)), frame_value=(0, 5))

        # A different FrameInterval (0, 10)
        vcd.add_object_data(uid=person1_uid, object_data=types.num('age', 35.0), frame_value=(0, 10))

        # Data for the other objects
        vcd.add_object_data(uid=car1_uid, object_data=types.bbox('position', (100, 100, 200, 400)), frame_value=(0, 10))
        vcd.add_object_data(uid=car1_uid, object_data=types.text('color', 'red'), frame_value=(6, 10))
        vcd.add_object_data(uid=car2_uid, object_data=types.bbox('position', (300, 1000, 200, 400)), frame_value=(0, 10))
        vcd.add_object_data(uid=trafficSign1UID, object_data=types.boolean('visible', True), frame_value=(0, 4))

        # print("Frame 5, dynamic only message: ", vcd.stringify_frame(5, dynamic_only=True))
        # print("Frame 5, full message: ", vcd.stringify_frame(5, dynamic_only=False))

        if not os.path.isfile('./etc/vcd430_test_remove_simple.json'):
            vcd.save('./etc/vcd430_test_remove_simple.json')

        self.assertEqual(vcd.get_num_objects(), 4, "Should be 4")

        # 4.- Delete some content
        vcd.rm_object(uid=car2_uid)
        self.assertEqual(vcd.get_num_objects(), 3, "Should be 3")
        vcd.rm_object_by_type(semantic_type='#StopSign')
        self.assertEqual(vcd.get_num_objects(), 2, "Should be 2")

        # 5.- Remove all content sequentially
        vcd.rm_object(uid=person1_uid)
        self.assertEqual(vcd.get_num_objects(), 1, "Should be 1")
        vcd.rm_object(uid=car1_uid)
        self.assertEqual(vcd.get_num_objects(), 0, "Should be 0")

    # Load
    def test_load(self):
        # 1.- Create VCD from file
        vcd = core.VCD('./etc/vcd430_test_create_search_mid.json', validation=True)
        vcd.save('./etc/vcd430_test_create_search_mid_saved.json')
        vcd_read = core.VCD('./etc/vcd430_test_create_search_mid_saved.json', validation=True)

        self.assertEqual(vcd_read.stringify(), vcd.stringify())

    def test_metadata(self):
        vcd = core.VCD()
        annotator = "Algorithm001"
        comment = "Annotations produced automatically - SW v0.1"
        file_version = "2.0"  # This is a versioning for the annotation file itself
        name = "vcd_" + file_version + "-" + annotator # A friendly name
        vcd.add_annotator(annotator)
        vcd.add_comment(comment)
        vcd.add_file_version(file_version)
        vcd.add_name(name)

        # Other customized metadata can be added as well
        vcd.add_metadata_properties({"target": "Test track", "origin": "synthetic"})

        # TODO: vcd.add_metadata_properties (a dictionary just like frame_properties)

        self.assertEqual(vcd.get_metadata()['annotator'], annotator)
        self.assertEqual(vcd.get_metadata()['comment'], comment)

        if not os.path.isfile('./etc/vcd430_test_add_metadata.json'):
            vcd.save('./etc/vcd430_test_add_metadata.json')

    # Ontology links
    def test_ontology_list(self):
        vcd = core.VCD()

        ont_uid_1 = vcd.add_ontology("http://www.vicomtech.org/viulib/ontology")
        ont_uid_2 = vcd.add_ontology("http://www.alternativeURL.org/ontology")

        # Let's create an object with a pointer to the ontology
        uid_car = vcd.add_object('CARLOTA', '#Car', frame_value=None, uid=None, ont_uid=ont_uid_1)
        vcd.add_object_data(uid_car, types.text('brand', 'Toyota'))
        vcd.add_object_data(uid_car, types.text('model', 'Prius'))

        uid_marcos = vcd.add_object('Marcos', '#Person', frame_value=None, uid=None, ont_uid=ont_uid_2)
        vcd.add_object_data(uid_marcos, types.bbox('head', (10, 10, 30, 30)), (2, 4))

        self.assertEqual(vcd.get_object(uid_car)['ontology_uid'], ont_uid_1)
        self.assertEqual(vcd.get_object(uid_marcos)['ontology_uid'], ont_uid_2)
        self.assertEqual(vcd.get_ontology(ont_uid_1), "http://www.vicomtech.org/viulib/ontology")
        self.assertEqual(vcd.get_ontology(ont_uid_2), "http://www.alternativeURL.org/ontology")

        if not os.path.isfile('./etc/vcd430_test_ontology.json'):
            vcd.save('./etc/vcd430_test_ontology.json', True)

        vcd_read = core.VCD('./etc/vcd430_test_ontology.json', validation=True)
        self.assertEqual(vcd_read.stringify(), vcd.stringify())

    def test_online_operation(self):
        # Simulate an online operation during 1000 frames
        # And cut-off every 100 frames into a new VCD
        vcds = []
        uid = -1
        for frame_num in range(0, 1000):
            if frame_num % 100 == 0:
                # Create new VCD
                vcds.append(core.VCD())
                vcd_current = vcds[-1]
                # Optionally we could here dump into JSON file
                if frame_num == 0:
                    uid = vcd_current.add_object('CARLOTA', 'Car')  # leave VCD to assign uid = 0
                    vcd_current.add_object_data(uid, types.bbox('', (0, frame_num, 0, 0)), frame_num)
                else:
                    uid = vcd_current.add_object('CARLOTA', 'Car', uid=uid)  # tell VCD to use last_uid
                    vcd_current.add_object_data(uid, types.bbox('', (0, frame_num, 0, 0)), frame_num)
            else:
                # Continue with current VCD
                vcd_current = vcds[-1]
                vcd_current.add_object_data(uid, types.bbox('', (0, frame_num, 0, 0)), frame_num)

        for vcd_this in vcds:
            self.assertEqual(vcd_this.get_num_objects(), 1)
            self.assertEqual(vcd_this.get_object(uid)['name'], 'CARLOTA')
            self.assertEqual(vcd_this.get_object(uid)['type'], 'Car')

    def test_objects_without_data(self):
        vcd = core.VCD()

        pedestrian_uid = vcd.add_object(name='', semantic_type='#Pedestrian', frame_value=(0, 30))
        car_uid = vcd.add_object(name='', semantic_type='#Car', frame_value=(20, 30))

        if not os.path.isfile('./etc/vcd430_test_objects_without_data.json'):
            vcd.save('./etc/vcd430_test_objects_without_data.json', True)
        vcd_read = core.VCD('./etc/vcd430_test_objects_without_data.json', validation=True)
        vcd_read_stringified = vcd_read.stringify()
        vcd_stringified = vcd.stringify()
        # print(vcd_stringified)
        self.assertEqual(vcd_read_stringified, vcd_stringified)

    def test_nested_object_data_attributes(self):
        vcd = core.VCD()

        uid_obj1 = vcd.add_object('someName1', '#Some')

        box1 = types.bbox('head', (0,0,10,10))
        box1.add_attribute(types.boolean('visible', True))

        self.assertEqual('attributes' in box1.data, True)
        self.assertEqual('boolean' in box1.data['attributes'], True)
        self.assertEqual(type(box1.data['attributes']['boolean']) is list, True)
        self.assertEqual(box1.data['attributes']['boolean'][0]['name'], "visible")
        self.assertEqual(box1.data['attributes']['boolean'][0]['val'], True)

        vcd.add_object_data(uid_obj1, box1, 0)

        if not os.path.isfile('./etc/vcd430_test_nested_object_data.json'):
            vcd.save('./etc/vcd430_test_nested_object_data.json', True)

        vcd_read = core.VCD('./etc/vcd430_test_nested_object_data.json', validation=True)
        vcd_read_stringified = vcd_read.stringify()
        vcd_stringified = vcd.stringify()
        # print(vcd_stringified)
        self.assertEqual(vcd_read_stringified, vcd_stringified)

if __name__ == '__main__':  # This changes the command-line entry point to call unittest.main()
    print("Running " + os.path.basename(__file__))
    unittest.main()





