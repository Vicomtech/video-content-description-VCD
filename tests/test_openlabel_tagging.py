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
    def test_openlabel_tags_complex(self):
        openlabel = core.OpenLABEL()
        openlabel.add_metadata_properties({"tagged_file": "../resources/scenarios/some_scenario_file"})
        openlabel.add_ontology(ontology_name="https://code.asam.net/simulation/standard/openxontology/ontologies/openlabel")

        # We can add a tag
        uid_0 = openlabel.add_tag(semantic_type="double_roundabout", ont_uid="0")
        # and later on, add some data to the tag
        openlabel.add_tag_data(uid=uid_0, tag_data=types.num(name="number_of_entries", val=2))

        uid_1 = openlabel.add_tag(semantic_type="t_intersection", ont_uid="0")
        openlabel.add_tag_data(uid=uid_1, tag_data=types.num(name="number_of_entries", val=3))

        self.assertTrue(check_openlabel(openlabel, './etc/' + openlabel_version_name + '_'
                                        + inspect.currentframe().f_code.co_name + '.json'))

    def test_openlabel_tags_complex_2(self):
        openlabel = core.OpenLABEL()

        ont_uid_0 = openlabel.add_ontology(ontology_name="https://code.asam.net/simulation/standard/openxontology/ontologies/domain/v1",
                                           subset_include=["motorway", "road"],
                                           subset_exclude=["highway", "lane", "curb"])
        ont_uid_1 = openlabel.add_ontology(ontology_name="https://code.asam.net/simulation/standard/openlabel/ontologies/v1")
        ont_uid_2 = openlabel.add_ontology(ontology_name="http://mycompany/ontologies/v1")

        # In OpenLABEL tags, tag_data don't have "name", so in this version of the API
        # we need to set it as "name"=None, because for OpenLABEL labeling "name" was mandatory, and thus
        # most functions in the API require it. In the schema, "name" is no longer mandatory
        # In this version, "type" is added as a property

        # ODD tags
        uid_0 = openlabel.add_tag(semantic_type="motorway", ont_uid=ont_uid_0)
        uid_1 = openlabel.add_tag(semantic_type="number-of-lanes", ont_uid=ont_uid_0)
        openlabel.add_tag_data(uid=uid_1, tag_data=types.vec(name="", val=[2, 3], type="values"))
        uid_2 = openlabel.add_tag(semantic_type="lane-widths", ont_uid=ont_uid_0)
        openlabel.add_tag_data(uid=uid_2, tag_data=types.vec(name="range1", val=[3.4, 3.7], type="range"))
        openlabel.add_tag_data(uid=uid_2, tag_data=types.vec(name="range2", val=[3.9, 4.1], type="range"))
        uid_3 = openlabel.add_tag(semantic_type="rainfall", ont_uid=ont_uid_0)
        openlabel.add_tag_data(uid=uid_3, tag_data=types.num(name="", val=1.2, type="min"))

        # Behaviour tags
        uid_4 = openlabel.add_tag(semantic_type="walk", ont_uid=ont_uid_1)
        uid_5 = openlabel.add_tag(semantic_type="drive", ont_uid=ont_uid_1)

        # Administrative tags
        uid_6 = openlabel.add_tag(semantic_type="scenario-unique-reference", ont_uid=ont_uid_1)
        openlabel.add_tag_data(uid=uid_6, tag_data=types.text(name="", val="{02ed611e-a376-11eb-973f-b818cf5bef8c}", type="value"))
        uid_7 = openlabel.add_tag(semantic_type="scenario-name", ont_uid=ont_uid_1)
        openlabel.add_tag_data(uid=uid_7, tag_data=types.text(name="", val="FSD01726287 Roundabout first exit", type="value"))
        uid_8 = openlabel.add_tag(semantic_type="adas-feature", ont_uid=ont_uid_1)
        openlabel.add_tag_data(uid=uid_8, tag_data=types.vec(name="", val=["LCA", "LDW"], type="values"))
        uid_9 = openlabel.add_tag(semantic_type="version", ont_uid=ont_uid_1)
        openlabel.add_tag_data(uid=uid_9, tag_data=types.text(name="version_number", val="1.0.0.0", type="value"))
        openlabel.add_tag_data(uid=uid_9, tag_data=types.text(name="timestamp", val="2021-05-25 11:00:00 UTC", type="value"))
        uid_10 = openlabel.add_tag(semantic_type="project-id", ont_uid=ont_uid_2)
        openlabel.add_tag_data(uid=uid_10, tag_data=types.vec(name="", val=[123456], type="values"))

        self.assertTrue(check_openlabel(openlabel, './etc/' + openlabel_version_name + '_'
                                        + inspect.currentframe().f_code.co_name + '.json'))


if __name__ == '__main__':  # This changes the command-line entry point to call unittest.main()
    print("Running " + os.path.basename(__file__))
    unittest.main()
