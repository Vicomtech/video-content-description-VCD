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
    let uid_pedestrian1 = vcd_a.addObject('', 'Pedestrian', null, null, 0)
    let uid_car1 = vcd_a.addObject('', 'Car', null, null, 0)
    uid_pedestrian1 = vcd_b.addObject('', 'Pedestrian', null, null, 0)
    uid_car1 = vcd_b.addObject('', 'Car', null, null, 0)
    uid_pedestrian1 = vcd_c.addObject('', 'Pedestrian', null, null, 0)
    uid_car1 = vcd_c.addObject('', 'Car', null, null, 0)

    // 4.- Add (intransitive actions)
    // Option a) Add (intransitive) Actions as Object attributes
    // Pro: simple, quick code, less bytes in JSON
    // Con: No explicit Relation, lack of extensibility, only valid for simple subject-predicates
    vcd_a.addObjectData(uid_pedestrian1, new types.Text("action", "Walking"))
    vcd_a.addObjectData(uid_car1, new types.Text("action", "Parked"))

    // Option b) Add (intransitive) Actions as Actions and use Relations to link to Objects
    // Pro: Action as element with entity, can add action_data, link to other Objects or complex Relations
    // Con: long to write, occupy more bytes in JSON, more difficult to parse
    let uid_action1 = vcd_b.addAction('', 'Walking', null, null, 0)
    let uid_rel1 = vcd_b.addRelationObjectAction('', 'performsAction', uid_pedestrian1, uid_action1, null, 0)
    let uid_action2 = vcd_b.addAction('', 'Parked', null, null, 0)
    let uid_rel2 = vcd_b.addRelationObjectAction('', 'performsAction', uid_car1, uid_action2, null, 0)

    // Option c) Add Actions as Actions, and use action_Data to point to subject Object
    // Pro: simple as option a
    // Con: sames as a
    uid_action1 = vcd_c.addAction("", "Walking", null, null, 0)
    uid_action2 = vcd_c.addAction("", "Parked", null, null, 0)
    vcd_c.addActionData(uid_action1, new types.Num("subject", uid_pedestrian1))
    vcd_c.addActionData(uid_action2, new types.Num("subject", uid_car1))

    expect(vcd_a.stringify(false, false)).toBe('{"vcd":{"frames":{},"version":"4.2.1","frame_intervals":[],"ontologies":{"0":"http://vcd.vicomtech.org/ontology/automotive"},"objects":{"0":{"name":"","type":"Pedestrian","frame_intervals":[],"ontology_uid":0,"object_data":{"text":[{"name":"action","val":"Walking"}]}},"1":{"name":"","type":"Car","frame_intervals":[],"ontology_uid":0,"object_data":{"text":[{"name":"action","val":"Parked"}]}}}}}')
    expect(vcd_b.stringify(false, false)).toBe('{"vcd":{"frames":{},"version":"4.2.1","frame_intervals":[],"ontologies":{"0":"http://vcd.vicomtech.org/ontology/automotive"},"objects":{"0":{"name":"","type":"Pedestrian","frame_intervals":[],"ontology_uid":0},"1":{"name":"","type":"Car","frame_intervals":[],"ontology_uid":0}},"actions":{"0":{"name":"","type":"Walking","frame_intervals":[],"ontology_uid":0},"1":{"name":"","type":"Parked","frame_intervals":[],"ontology_uid":0}},"relations":{"0":{"name":"","type":"performsAction","frame_intervals":[],"ontology_uid":0,"rdf_subjects":[{"uid":0,"type":"object"}],"rdf_objects":[{"uid":0,"type":"action"}]},"1":{"name":"","type":"performsAction","frame_intervals":[],"ontology_uid":0,"rdf_subjects":[{"uid":1,"type":"object"}],"rdf_objects":[{"uid":1,"type":"action"}]}}}}')
    expect(vcd_c.stringify(false, false)).toBe('{"vcd":{"frames":{},"version":"4.2.1","frame_intervals":[],"ontologies":{"0":"http://vcd.vicomtech.org/ontology/automotive"},"objects":{"0":{"name":"","type":"Pedestrian","frame_intervals":[],"ontology_uid":0},"1":{"name":"","type":"Car","frame_intervals":[],"ontology_uid":0}},"actions":{"0":{"name":"","type":"Walking","frame_intervals":[],"ontology_uid":0,"action_data":{"num":[{"name":"subject","val":0}]}},"1":{"name":"","type":"Parked","frame_intervals":[],"ontology_uid":0,"action_data":{"num":[{"name":"subject","val":1}]}}}}}')
});
