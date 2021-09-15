import fs from 'fs'
import { VCD,OpenLABEL, ElementType, RDF, ResourceUID } from '../vcd.core'
import * as types from '../vcd.types'

import openlabel100_test_openlabel_tags_complex from '../../../tests/etc/openlabel100_test_openlabel_tags_complex.json'
import openlabel100_test_openlabel_tags_complex_2 from '../../../tests/etc/openlabel100_test_openlabel_tags_complex_2.json'


test('test_openlabel_tags_complex', () => {
    
    /*
    This test shows how to create a new OpenLABEL object.
    :return:
    */
    let openlabel = new OpenLABEL();
    openlabel.addMetadataProperties({"tagged_file": "../resources/scenarios/some_scenario_file"})
    openlabel.addOntology("https://code.asam.net/simulation/standard/openxontology/ontologies/openlabel")

    // We can add a tag
    let uid_0 = openlabel.addTag("double_roundabout",null, "0")
    //and later on, add some data to the tag
    openlabel.addTagData(uid_0, new types.Num(null, 2))

    let uid_1 = openlabel.addTag("t_intersection", null, "0")
    openlabel.addTagData(uid_1, new types.Num(null, 3))

    expect(openlabel.stringify(false)).toBe(new VCD(openlabel100_test_openlabel_tags_complex, false).stringify(false))


});

test('test_openlabel_tags_complex_2', () => {
    
    let openlabel = new OpenLABEL();

    let ont_uid_0 = openlabel.addOntology("https://code.asam.net/simulation/standard/openxontology/ontologies/domain/v1",
                                           ["motorway", "road"],
                                           ["highway", "lane", "curb"])
    let ont_uid_1 = openlabel.addOntology("https://code.asam.net/simulation/standard/openlabel/ontologies/v1")
    let ont_uid_2 = openlabel.addOntology("http://mycompany/ontologies/v1")

    // In OpenLABEL tags, tag_data don't have "name", so in this version of the API
    // we need to set it as "name"=null, because for OpenLABEL labeling "name" was mandatory, and thus
    // most functions in the API require it. In the schema, "name" is no longer mandatory
    // In this version, "type" is added as a property

    // ODD tags
    let uid_0 = openlabel.addTag("motorway",null, ont_uid_0)
    let uid_1 = openlabel.addTag("number-of-lanes",null, ont_uid_0)
    openlabel.addTagData(uid_1, new types.Vec(null, [2, 3],null,null, "values"))
    let uid_2 = openlabel.addTag("lane-widths",null, ont_uid_0)
    openlabel.addTagData(uid_2, new types.Vec(null, [3.4, 3.7],null,null, "range"))
    openlabel.addTagData(uid_2, new types.Vec(null, [3.9, 4.1],null,null, "range"))
    let uid_3 = openlabel.addTag("rainfall",null, ont_uid_0)
    openlabel.addTagData(uid_3, new types.Num(null, 1.2,null,null, "min"))

    // Behaviour tags
    let uid_4 = openlabel.addTag("walk",null, ont_uid_1)
    let uid_5 = openlabel.addTag("drive",null, ont_uid_1)

    // Administrative tags
    let uid_6 = openlabel.addTag("scenario-unique-reference",null, ont_uid_1)
    openlabel.addTagData(uid_6, new types.Text(null, "{02ed611e-a376-11eb-973f-b818cf5bef8c}",null,null, "value"))
    let uid_7 = openlabel.addTag("scenario-name",null, ont_uid_1)
    openlabel.addTagData(uid_7, new types.Text(null, "FSD01726287 Roundabout first exit",null,null, "value"))
    let uid_8 = openlabel.addTag("adas-feature",null, ont_uid_1)
    openlabel.addTagData(uid_8, new types.Vec(null, ["LCA", "LDW"],null,null, "values"))
    let uid_9 = openlabel.addTag("scenario-version",null, ont_uid_1)
    openlabel.addTagData(uid_9, new types.Text(null, "1.0.0.0",null,null, "value"))
    let uid_10 = openlabel.addTag("scenario-created-date",null, ont_uid_1)
    openlabel.addTagData(uid_10, new types.Text(null, "2021-05-25 11:00:00 UTC",null,null, "value"))
    let uid_11 = openlabel.addTag("project-id",null, ont_uid_2)
    openlabel.addTagData(uid_11, new types.Vec(null, [123456],null,null, "values"))


    expect(openlabel.stringify(false)).toBe(new VCD(openlabel100_test_openlabel_tags_complex_2, false).stringify(false))

    
});


