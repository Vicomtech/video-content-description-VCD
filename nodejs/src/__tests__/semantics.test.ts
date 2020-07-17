import { VCD, ElementType, RDF } from '../vcd.core'
import * as types from '../vcd.types'

test('test_actions', () => {
    // 1.- Create VCD
    let vcd_a = new VCD()
    let vcd_b = new VCD()
    let vcd_c = new VCD()

    // 2.- Add ontology
    vcd_a.addOntology('http://vcd.vicomtech.org/ontology/automotive')
    vcd_b.addOntology('http://vcd.vicomtech.org/ontology/automotive')
    vcd_c.addOntology('http://vcd.vicomtech.org/ontology/automotive')

    // 3.- Add some objects
    let uid_pedestrian1 = vcd_a.addObject('', 'Pedestrian', null, null, "0")
    let uid_car1 = vcd_a.addObject('', 'Car', null, null, "0")
    uid_pedestrian1 = vcd_b.addObject('', 'Pedestrian', null, null, "0")
    uid_car1 = vcd_b.addObject('', 'Car', null, null, "0")
    uid_pedestrian1 = vcd_c.addObject('', 'Pedestrian', null, null, "0")
    uid_car1 = vcd_c.addObject('', 'Car', null, null, "0")

    // 4.- Add (intransitive actions)
    // Option a) Add (intransitive) Actions as Object attributes
    // Pro: simple, quick code, less bytes in JSON
    // Con: No explicit Relation, lack of extensibility, only valid for simple subject-predicates
    vcd_a.addObjectData(uid_pedestrian1, new types.Text("action", "Walking"))
    vcd_a.addObjectData(uid_car1, new types.Text("action", "Parked"))

    // Option b) Add (intransitive) Actions as Actions and use Relations to link to Objects
    // Pro: Action as element with entity, can add action_data, link to other Objects or complex Relations
    // Con: long to write, occupy more bytes in JSON, more difficult to parse
    let uid_action1 = vcd_b.addAction('', 'Walking', null, null, "0")
    let uid_rel1 = vcd_b.addRelationObjectAction('', 'performsAction', uid_pedestrian1, uid_action1, null, "0")
    let uid_action2 = vcd_b.addAction('', 'Parked', null, null, "0")
    let uid_rel2 = vcd_b.addRelationObjectAction('', 'performsAction', uid_car1, uid_action2, null, "0")

    // Option c) Add Actions as Actions, and use action_Data to point to subject Object
    // Pro: simple as option a
    // Con: sames as a
    uid_action1 = vcd_c.addAction("", "Walking", null, null, "0")
    uid_action2 = vcd_c.addAction("", "Parked", null, null, "0")
    vcd_c.addActionData(uid_action1, new types.Num("subject", +uid_pedestrian1))  // note UIDs are strings, need to convert to number
    vcd_c.addActionData(uid_action2, new types.Num("subject", +uid_car1))

    //console.log(vcd_a.stringify(false))
    expect(vcd_a.stringify(false)).toBe('{"vcd":{"frames":{},"schema_version":"4.3.0","frame_intervals":[],"ontologies":{"0":"http://vcd.vicomtech.org/ontology/automotive"},"objects":{"0":{"name":"","type":"Pedestrian","ontology_uid":"0","object_data":{"text":[{"name":"action","val":"Walking"}]},"object_data_pointers":{"action":{"type":"text","frame_intervals":[]}}},"1":{"name":"","type":"Car","ontology_uid":"0","object_data":{"text":[{"name":"action","val":"Parked"}]},"object_data_pointers":{"action":{"type":"text","frame_intervals":[]}}}}}}')
    //console.log(vcd_b.stringify(false))
    expect(vcd_b.stringify(false)).toBe('{"vcd":{"frames":{},"schema_version":"4.3.0","frame_intervals":[],"ontologies":{"0":"http://vcd.vicomtech.org/ontology/automotive"},"objects":{"0":{"name":"","type":"Pedestrian","ontology_uid":"0"},"1":{"name":"","type":"Car","ontology_uid":"0"}},"actions":{"0":{"name":"","type":"Walking","ontology_uid":"0"},"1":{"name":"","type":"Parked","ontology_uid":"0"}},"relations":{"0":{"name":"","type":"performsAction","ontology_uid":"0","rdf_subjects":[{"uid":"0","type":"object"}],"rdf_objects":[{"uid":"0","type":"action"}]},"1":{"name":"","type":"performsAction","ontology_uid":"0","rdf_subjects":[{"uid":"1","type":"object"}],"rdf_objects":[{"uid":"1","type":"action"}]}}}}')
    //console.log(vcd_c.stringify(false))
    expect(vcd_c.stringify(false)).toBe('{"vcd":{"frames":{},"schema_version":"4.3.0","frame_intervals":[],"ontologies":{"0":"http://vcd.vicomtech.org/ontology/automotive"},"objects":{"0":{"name":"","type":"Pedestrian","ontology_uid":"0"},"1":{"name":"","type":"Car","ontology_uid":"0"}},"actions":{"0":{"name":"","type":"Walking","ontology_uid":"0","action_data":{"num":[{"name":"subject","val":0}]},"action_data_pointers":{"subject":{"type":"num","frame_intervals":[]}}},"1":{"name":"","type":"Parked","ontology_uid":"0","action_data":{"num":[{"name":"subject","val":1}]},"action_data_pointers":{"subject":{"type":"num","frame_intervals":[]}}}}}}')
});

test('test_relations', () => {
    // This tests shows how relations can be created with and without frame interval information
    let vcd = new VCD()

    // Case 1: RDF elements don't have frame interval, but relation does
    // So objects don't appear in frames, but relation does. Reading the relation leads to the static objects
    let uid1 = vcd.addObject("", "Car")
    let uid2 = vcd.addObject("", "Pedestrian")

    vcd.addRelationObjectObject("", "isNear",
                                    uid1, uid2, null, null, 
                                    [0, 10])

    expect(vcd.getData()['vcd']['frame_intervals'][0]['frame_start']).toBe(0)
    expect(vcd.getData()['vcd']['frame_intervals'][0]['frame_end']).toBe(10)
    expect(vcd.getData()['vcd']['relations'][0]['frame_intervals'][0]['frame_start']).toBe(0)
    expect(vcd.getData()['vcd']['relations'][0]['frame_intervals'][0]['frame_end']).toBe(10)
    for (let frame_key in vcd.getData()['vcd']['frames']) {        
        let relations = vcd.getData()['vcd']['frames'][frame_key]['relations']        
        expect(Object.keys(relations).length).toBe(1)
    }

    //console.log(vcd.stringify(false))
    expect(vcd.stringify(false)).toBe('{"vcd":{"frames":{"0":{"relations":{"0":{}}},"1":{"relations":{"0":{}}},"2":{"relations":{"0":{}}},"3":{"relations":{"0":{}}},"4":{"relations":{"0":{}}},"5":{"relations":{"0":{}}},"6":{"relations":{"0":{}}},"7":{"relations":{"0":{}}},"8":{"relations":{"0":{}}},"9":{"relations":{"0":{}}},"10":{"relations":{"0":{}}}},"schema_version":"4.3.0","frame_intervals":[{"frame_start":0,"frame_end":10}],"objects":{"0":{"name":"","type":"Car"},"1":{"name":"","type":"Pedestrian"}},"relations":{"0":{"name":"","type":"isNear","frame_intervals":[{"frame_start":0,"frame_end":10}],"rdf_subjects":[{"uid":"0","type":"object"}],"rdf_objects":[{"uid":"1","type":"object"}]}}}}')

    // Case 2: RDF elements defined with long frame intervals, and relation with smaller inner frame interval
    vcd = new VCD()

    uid1 = vcd.addObject("", "Car", [0, 10])
    uid2 = vcd.addObject("", "Pedestrian", [5, 15])

    vcd.addRelationObjectObject("", "isNear",
                                    uid1, uid2, null, null,
                                    [7, 9])

    expect(vcd.getData()['vcd']['frame_intervals'][0]['frame_start']).toBe(0)
    expect(vcd.getData()['vcd']['frame_intervals'][0]['frame_end']).toBe(15)
    expect(vcd.getData()['vcd']['relations'][0]['frame_intervals'][0]['frame_start']).toBe(7)
    expect(vcd.getData()['vcd']['relations'][0]['frame_intervals'][0]['frame_end']).toBe(9)
    for (let frame_key in vcd.getData()['vcd']['frames']) {
        if (7 <= +frame_key && +frame_key <= 9) {  // + operator to convert from string to number
            let frame_val = vcd.getData()['vcd']['frames'][frame_key]
            let relations = frame_val['relations']
            expect(Object.keys(relations).length).toBe(1)
        }
    }

    //console.log(vcd.stringify(false))
    expect(vcd.stringify(false)).toBe('{"vcd":{"frames":{"0":{"objects":{"0":{}}},"1":{"objects":{"0":{}}},"2":{"objects":{"0":{}}},"3":{"objects":{"0":{}}},"4":{"objects":{"0":{}}},"5":{"objects":{"0":{},"1":{}}},"6":{"objects":{"0":{},"1":{}}},"7":{"objects":{"0":{},"1":{}},"relations":{"0":{}}},"8":{"objects":{"0":{},"1":{}},"relations":{"0":{}}},"9":{"objects":{"0":{},"1":{}},"relations":{"0":{}}},"10":{"objects":{"0":{},"1":{}}},"11":{"objects":{"1":{}}},"12":{"objects":{"1":{}}},"13":{"objects":{"1":{}}},"14":{"objects":{"1":{}}},"15":{"objects":{"1":{}}}},"schema_version":"4.3.0","frame_intervals":[{"frame_start":0,"frame_end":15}],"objects":{"0":{"name":"","type":"Car","frame_intervals":[{"frame_start":0,"frame_end":10}]},"1":{"name":"","type":"Pedestrian","frame_intervals":[{"frame_start":5,"frame_end":15}]}},"relations":{"0":{"name":"","type":"isNear","frame_intervals":[{"frame_start":7,"frame_end":9}],"rdf_subjects":[{"uid":"0","type":"object"}],"rdf_objects":[{"uid":"1","type":"object"}]}}}}')

    // Case 3: RDF elements have frame interval and relation doesn't (so it is left frame-less)
    vcd = new VCD()

    uid1 = vcd.addObject("", "Car", [0, 10])
    uid2 = vcd.addObject("", "Pedestrian", [5, 15])
    let uid3 = vcd.addObject("", "Other", [15, 20])

    let uid4 = vcd.addRelationObjectObject("", "isNear",
                                    uid1, uid2)

    // The relation does not have frame information
    expect('frame_intervals' in vcd.getRelation(uid4)).toBe(false)

    expect(vcd.getData()['vcd']['frame_intervals'][0]['frame_start']).toBe(0)
    expect(vcd.getData()['vcd']['frame_intervals'][0]['frame_end']).toBe(20)
    for (let frame_key in vcd.getData()['vcd']['frames']) {
        if (0 <= +frame_key && +frame_key <= 15) {
            let frame_val = vcd.getData()['vcd']['frames'][frame_key]            
            expect(!('relations' in frame_val)).toBe(true)
        }
    }

    //console.log(vcd.stringify(false))
    expect(vcd.stringify(false)).toBe('{"vcd":{"frames":{"0":{"objects":{"0":{}}},"1":{"objects":{"0":{}}},"2":{"objects":{"0":{}}},"3":{"objects":{"0":{}}},"4":{"objects":{"0":{}}},"5":{"objects":{"0":{},"1":{}}},"6":{"objects":{"0":{},"1":{}}},"7":{"objects":{"0":{},"1":{}}},"8":{"objects":{"0":{},"1":{}}},"9":{"objects":{"0":{},"1":{}}},"10":{"objects":{"0":{},"1":{}}},"11":{"objects":{"1":{}}},"12":{"objects":{"1":{}}},"13":{"objects":{"1":{}}},"14":{"objects":{"1":{}}},"15":{"objects":{"1":{},"2":{}}},"16":{"objects":{"2":{}}},"17":{"objects":{"2":{}}},"18":{"objects":{"2":{}}},"19":{"objects":{"2":{}}},"20":{"objects":{"2":{}}}},"schema_version":"4.3.0","frame_intervals":[{"frame_start":0,"frame_end":20}],"objects":{"0":{"name":"","type":"Car","frame_intervals":[{"frame_start":0,"frame_end":10}]},"1":{"name":"","type":"Pedestrian","frame_intervals":[{"frame_start":5,"frame_end":15}]},"2":{"name":"","type":"Other","frame_intervals":[{"frame_start":15,"frame_end":20}]}},"relations":{"0":{"name":"","type":"isNear","rdf_subjects":[{"uid":"0","type":"object"}],"rdf_objects":[{"uid":"1","type":"object"}]}}}}')
   
});