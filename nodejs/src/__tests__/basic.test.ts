import { VCD, ElementType, RDF } from '../vcd.core'
import * as types from '../vcd.types'

test('test_create_search_simple', () => {
    let vcd = new VCD();

    let uid_marcos = vcd.addObject("marcos", "")
    expect(uid_marcos).toBe(0)
    expect(vcd.getNumObjects()).toBe(1)

    vcd.addObjectData(uid_marcos, new types.Bbox('head', [10, 10, 30, 30]))
    vcd.addObjectData(uid_marcos, new types.Bbox('body', [0, 0, 60, 120]))
    vcd.addObjectData(uid_marcos, new types.Vec('speed', [0.0, 0.2]))
    vcd.addObjectData(uid_marcos, new types.Num('accel', 0.1))

    expect(vcd.getObject(uid_marcos)['object_data']['bbox'][0]['name']).toBe('head')
    expect(vcd.getObject(uid_marcos)['object_data']['bbox'][0]['val']).toStrictEqual([10, 10, 30, 30])

    let uid_peter = vcd.addObject("peter", "")
    vcd.addObjectData(uid_peter, new types.Num('age', 38.0))
    vcd.addObjectData(uid_peter, new types.Vec('eyeL', [0, 0, 10, 10]))
    vcd.addObjectData(uid_peter, new types.Vec('eyeR', [0, 0, 10, 10]))

    let vcd_string_pretty = vcd.stringify()
    let vcd_string_nopretty = vcd.stringify(false)

    expect(vcd_string_nopretty).toBe('{"vcd":{"frames":{},"version":"4.2.1","frame_intervals":[],"objects":{"0":{"name":"marcos","type":"","frame_intervals":[],"object_data":{"bbox":[{"name":"head","val":[10,10,30,30]},{"name":"body","val":[0,0,60,120]}],"vec":[{"name":"speed","val":[0,0.2]}],"num":[{"name":"accel","val":0.1}]}},"1":{"name":"peter","type":"","frame_intervals":[],"object_data":{"num":[{"name":"age","val":38}],"vec":[{"name":"eyeL","val":[0,0,10,10]},{"name":"eyeR","val":[0,0,10,10]}]}}}}}')

    let marcos_ref = vcd.getObject(uid_marcos)
    let peter_ref = vcd.getObject(uid_peter)
    expect(marcos_ref['name']).toBe('marcos')
    expect(peter_ref['name']).toBe('peter')

    // Let's load data into another vcd
    let vcd_data = vcd.getData()

    let vcd_copy = new VCD(vcd_data, true)
    let vcd_copy_string_nopretty = vcd_copy.stringify(false)

    expect(vcd_string_nopretty).toBe(vcd_copy_string_nopretty)

});

test('test_create_search_mid', () => {
    let vcd = new VCD()

    let uid_marcos = vcd.addObject('marcos', '#Adult')
    let uid_peter = vcd.addObject('peter', '#Adult')
    let uid_katixa = vcd.addObject('katixa', '#Child')

    vcd.addObjectData(uid_marcos, new types.Num('age', 38.0))
    vcd.addObjectData(uid_marcos, new types.Num('height', 1.75))
    vcd.addObjectData(uid_marcos, new types.Vec('pos', [0.0, 1.0, 8.0]), [0, 10])
    vcd.addObjectData(uid_peter, new types.Vec('pos', [0.0, 2.0, 6.0]), [0, 11])
    vcd.addObjectData(uid_peter, new types.Num('age', 40.0))
    vcd.addObjectData(uid_katixa, new types.Vec('pos', [0.0, 5.0, 1.0]), [5, 12])
    vcd.addObjectData(uid_katixa, new types.Num('age', 10.0))

    //console.log(vcd.stringify(false))
    expect(vcd.stringify(false)).toBe('{"vcd":{"frames":{"0":{"objects":{"0":{"object_data":{"vec":[{"name":"pos","val":[0,1,8]}]}},"1":{"object_data":{"vec":[{"name":"pos","val":[0,2,6]}]}},"2":{}}},"1":{"objects":{"0":{"object_data":{"vec":[{"name":"pos","val":[0,1,8]}]}},"1":{"object_data":{"vec":[{"name":"pos","val":[0,2,6]}]}},"2":{}}},"2":{"objects":{"0":{"object_data":{"vec":[{"name":"pos","val":[0,1,8]}]}},"1":{"object_data":{"vec":[{"name":"pos","val":[0,2,6]}]}},"2":{}}},"3":{"objects":{"0":{"object_data":{"vec":[{"name":"pos","val":[0,1,8]}]}},"1":{"object_data":{"vec":[{"name":"pos","val":[0,2,6]}]}},"2":{}}},"4":{"objects":{"0":{"object_data":{"vec":[{"name":"pos","val":[0,1,8]}]}},"1":{"object_data":{"vec":[{"name":"pos","val":[0,2,6]}]}},"2":{}}},"5":{"objects":{"0":{"object_data":{"vec":[{"name":"pos","val":[0,1,8]}]}},"1":{"object_data":{"vec":[{"name":"pos","val":[0,2,6]}]}},"2":{"object_data":{"vec":[{"name":"pos","val":[0,5,1]}]}}}},"6":{"objects":{"0":{"object_data":{"vec":[{"name":"pos","val":[0,1,8]}]}},"1":{"object_data":{"vec":[{"name":"pos","val":[0,2,6]}]}},"2":{"object_data":{"vec":[{"name":"pos","val":[0,5,1]}]}}}},"7":{"objects":{"0":{"object_data":{"vec":[{"name":"pos","val":[0,1,8]}]}},"1":{"object_data":{"vec":[{"name":"pos","val":[0,2,6]}]}},"2":{"object_data":{"vec":[{"name":"pos","val":[0,5,1]}]}}}},"8":{"objects":{"0":{"object_data":{"vec":[{"name":"pos","val":[0,1,8]}]}},"1":{"object_data":{"vec":[{"name":"pos","val":[0,2,6]}]}},"2":{"object_data":{"vec":[{"name":"pos","val":[0,5,1]}]}}}},"9":{"objects":{"0":{"object_data":{"vec":[{"name":"pos","val":[0,1,8]}]}},"1":{"object_data":{"vec":[{"name":"pos","val":[0,2,6]}]}},"2":{"object_data":{"vec":[{"name":"pos","val":[0,5,1]}]}}}},"10":{"objects":{"0":{"object_data":{"vec":[{"name":"pos","val":[0,1,8]}]}},"1":{"object_data":{"vec":[{"name":"pos","val":[0,2,6]}]}},"2":{"object_data":{"vec":[{"name":"pos","val":[0,5,1]}]}}}},"11":{"objects":{"1":{"object_data":{"vec":[{"name":"pos","val":[0,2,6]}]}},"2":{"object_data":{"vec":[{"name":"pos","val":[0,5,1]}]}}}},"12":{"objects":{"2":{"object_data":{"vec":[{"name":"pos","val":[0,5,1]}]}}}}},"version":"4.2.1","frame_intervals":[{"frame_start":0,"frame_end":12}],"objects":{"0":{"name":"marcos","type":"#Adult","frame_intervals":[{"frame_start":0,"frame_end":10}],"object_data":{"num":[{"name":"age","val":38},{"name":"height","val":1.75}]}},"1":{"name":"peter","type":"#Adult","frame_intervals":[{"frame_start":0,"frame_end":11}],"object_data":{"num":[{"name":"age","val":40}]}},"2":{"name":"katixa","type":"#Child","frame_intervals":[{"frame_start":5,"frame_end":12}],"object_data":{"num":[{"name":"age","val":10}]}}}}}')
    
    let uids_child = vcd.getElementsOfType(ElementType.object, '#Child')
    for (let uid of uids_child) {        
        expect(vcd.getObject(uid)['name']).toBe('katixa')
    }

    let uids_age = vcd.getObjectsWithObjectDataName('age')
    for (let uid of uids_age) {
        let object_ = vcd.getObject(uid)

        if (uid == 0) {
            expect(object_['name']).toBe('marcos')
        }
        else if (uid == 1) {
            expect(object_['name']).toBe('peter')
        }
        else if (uid == 2) {
            expect(object_['name']).toBe('katixa')
        }

        let frames_with_pos = vcd.getFramesWithObjectDataName(uid, 'pos')
        for (let frameNum of frames_with_pos) {
            let my_pos = vcd.getObjectData(uid, 'pos', frameNum)
            if (uid == 0) {
                expect(my_pos['val']).toStrictEqual([0.0, 1.0, 8.0])
            }
            else if (uid == 1) {
                expect(my_pos['val']).toStrictEqual([0.0, 2.0, 6.0])
            }
            else if (uid == 2) {
                expect(my_pos['val']).toStrictEqual([0.0, 5.0, 1.0])
            }               
        }
    }

    // Load and save data
    let vcd_string_nopretty = vcd.stringify(false)
    let vcd_data = vcd.getData()
    let vcd_copy = new VCD(vcd_data, true)
    let vcd_copy_string_nopretty = vcd_copy.stringify(false)
    expect(vcd_string_nopretty).toBe(vcd_copy_string_nopretty)

});

test('test_parse_string', () => {
    let vcd_string = '{"vcd":{"frames":{"0":{"objects":{"0":{"object_data":{"vec":[{"name":"pos","val":[0,1,8]}]}},"1":{"object_data":{"vec":[{"name":"pos","val":[0,2,6]}]}}}},"1":{"objects":{"0":{"object_data":{"vec":[{"name":"pos","val":[0,1,8]}]}},"1":{"object_data":{"vec":[{"name":"pos","val":[0,2,6]}]}}}},"2":{"objects":{"0":{"object_data":{"vec":[{"name":"pos","val":[0,1,8]}]}},"1":{"object_data":{"vec":[{"name":"pos","val":[0,2,6]}]}}}},"3":{"objects":{"0":{"object_data":{"vec":[{"name":"pos","val":[0,1,8]}]}},"1":{"object_data":{"vec":[{"name":"pos","val":[0,2,6]}]}}}},"4":{"objects":{"0":{"object_data":{"vec":[{"name":"pos","val":[0,1,8]}]}},"1":{"object_data":{"vec":[{"name":"pos","val":[0,2,6]}]}}}},"5":{"objects":{"0":{"object_data":{"vec":[{"name":"pos","val":[0,1,8]}]}},"1":{"object_data":{"vec":[{"name":"pos","val":[0,2,6]}]}},"2":{"object_data":{"vec":[{"name":"pos","val":[0,5,1]}]}}}},"6":{"objects":{"0":{"object_data":{"vec":[{"name":"pos","val":[0,1,8]}]}},"1":{"object_data":{"vec":[{"name":"pos","val":[0,2,6]}]}},"2":{"object_data":{"vec":[{"name":"pos","val":[0,5,1]}]}}}},"7":{"objects":{"0":{"object_data":{"vec":[{"name":"pos","val":[0,1,8]}]}},"1":{"object_data":{"vec":[{"name":"pos","val":[0,2,6]}]}},"2":{"object_data":{"vec":[{"name":"pos","val":[0,5,1]}]}}}},"8":{"objects":{"0":{"object_data":{"vec":[{"name":"pos","val":[0,1,8]}]}},"1":{"object_data":{"vec":[{"name":"pos","val":[0,2,6]}]}},"2":{"object_data":{"vec":[{"name":"pos","val":[0,5,1]}]}}}},"9":{"objects":{"0":{"object_data":{"vec":[{"name":"pos","val":[0,1,8]}]}},"1":{"object_data":{"vec":[{"name":"pos","val":[0,2,6]}]}},"2":{"object_data":{"vec":[{"name":"pos","val":[0,5,1]}]}}}},"10":{"objects":{"0":{"object_data":{"vec":[{"name":"pos","val":[0,1,8]}]}},"1":{"object_data":{"vec":[{"name":"pos","val":[0,2,6]}]}},"2":{"object_data":{"vec":[{"name":"pos","val":[0,5,1]}]}}}},"11":{"objects":{"1":{"object_data":{"vec":[{"name":"pos","val":[0,2,6]}]}},"2":{"object_data":{"vec":[{"name":"pos","val":[0,5,1]}]}}}},"12":{"objects":{"2":{"object_data":{"vec":[{"name":"pos","val":[0,5,1]}]}}}}},"version":"4.2.1","frame_intervals":[{"frame_start":0,"frame_end":12}],"objects":{"0":{"name":"marcos","type":"#Adult","frame_intervals":[{"frame_start":0,"frame_end":10}],"object_data":{"num":[{"name":"age","val":38},{"name":"height","val":1.75}]}},"1":{"name":"peter","type":"#Adult","frame_intervals":[{"frame_start":0,"frame_end":11}],"object_data":{"num":[{"name":"age","val":40}]}},"2":{"name":"katixa","type":"#Child","frame_intervals":[{"frame_start":5,"frame_end":12}],"object_data":{"num":[{"name":"age","val":10}]}}}}}';

    let vcd_object = JSON.parse(vcd_string)
    let vcd_copy = new VCD(vcd_object, true)

    let vcd_copy_string = vcd_copy.stringify(false)
    expect(vcd_string).toBe(vcd_copy_string)
});

test('test_remove_simple', () => {
    // 1.- Create VCD
    let vcd = new VCD()

    // 2.- Create Some objects
    let car1_uid = vcd.addObject('BMW', '#Car')
    let car2_uid = vcd.addObject('Seat', '#Car')
    let person1_uid = vcd.addObject('John', '#Pedestrian')
    let trafficSign1_uid = vcd.addObject('', '#StopSign')

    // 3.- Add some data at frame interval (0, 5)
    vcd.addObjectData(person1_uid, new types.Bbox('face', [0, 0, 100, 100]), [0, 5])
    vcd.addObjectData(person1_uid, new types.Bbox('mouth', [0, 0, 10, 10]), [0, 5])
    vcd.addObjectData(person1_uid, new types.Bbox('hand', [0, 0, 30, 30]), [0, 5])
    vcd.addObjectData(person1_uid, new types.Bbox('eyeL', [0, 0, 10, 10]), [0, 5])
    vcd.addObjectData(person1_uid, new types.Bbox('eyeR', [0, 0, 10, 10]), [0, 5])

    // a different frame interval
    vcd.addObjectData(person1_uid, new types.Num('age', 35.0), [0, 10])

    // data for the other objects
    vcd.addObjectData(car1_uid,  new types.Bbox('position', [100, 100, 200, 400]), [0, 10])
    vcd.addObjectData(car1_uid, new types.Text('color', 'red'), [6, 10])
    vcd.addObjectData(car2_uid, new types.Bbox('position', [300, 1000, 200, 400]), [0, 10])
    vcd.addObjectData(trafficSign1_uid, new types.Boolean('visible', true), [0, 4])

    expect(vcd.stringify(false)).toBe('{"vcd":{"frames":{"0":{"objects":{"0":{"object_data":{"bbox":[{"name":"position","val":[100,100,200,400]}]}},"1":{"object_data":{"bbox":[{"name":"position","val":[300,1000,200,400]}]}},"2":{"object_data":{"bbox":[{"name":"face","val":[0,0,100,100]},{"name":"mouth","val":[0,0,10,10]},{"name":"hand","val":[0,0,30,30]},{"name":"eyeL","val":[0,0,10,10]},{"name":"eyeR","val":[0,0,10,10]}],"num":[{"name":"age","val":35}]}},"3":{"object_data":{"boolean":[{"name":"visible","val":true}]}}}},"1":{"objects":{"0":{"object_data":{"bbox":[{"name":"position","val":[100,100,200,400]}]}},"1":{"object_data":{"bbox":[{"name":"position","val":[300,1000,200,400]}]}},"2":{"object_data":{"bbox":[{"name":"face","val":[0,0,100,100]},{"name":"mouth","val":[0,0,10,10]},{"name":"hand","val":[0,0,30,30]},{"name":"eyeL","val":[0,0,10,10]},{"name":"eyeR","val":[0,0,10,10]}],"num":[{"name":"age","val":35}]}},"3":{"object_data":{"boolean":[{"name":"visible","val":true}]}}}},"2":{"objects":{"0":{"object_data":{"bbox":[{"name":"position","val":[100,100,200,400]}]}},"1":{"object_data":{"bbox":[{"name":"position","val":[300,1000,200,400]}]}},"2":{"object_data":{"bbox":[{"name":"face","val":[0,0,100,100]},{"name":"mouth","val":[0,0,10,10]},{"name":"hand","val":[0,0,30,30]},{"name":"eyeL","val":[0,0,10,10]},{"name":"eyeR","val":[0,0,10,10]}],"num":[{"name":"age","val":35}]}},"3":{"object_data":{"boolean":[{"name":"visible","val":true}]}}}},"3":{"objects":{"0":{"object_data":{"bbox":[{"name":"position","val":[100,100,200,400]}]}},"1":{"object_data":{"bbox":[{"name":"position","val":[300,1000,200,400]}]}},"2":{"object_data":{"bbox":[{"name":"face","val":[0,0,100,100]},{"name":"mouth","val":[0,0,10,10]},{"name":"hand","val":[0,0,30,30]},{"name":"eyeL","val":[0,0,10,10]},{"name":"eyeR","val":[0,0,10,10]}],"num":[{"name":"age","val":35}]}},"3":{"object_data":{"boolean":[{"name":"visible","val":true}]}}}},"4":{"objects":{"0":{"object_data":{"bbox":[{"name":"position","val":[100,100,200,400]}]}},"1":{"object_data":{"bbox":[{"name":"position","val":[300,1000,200,400]}]}},"2":{"object_data":{"bbox":[{"name":"face","val":[0,0,100,100]},{"name":"mouth","val":[0,0,10,10]},{"name":"hand","val":[0,0,30,30]},{"name":"eyeL","val":[0,0,10,10]},{"name":"eyeR","val":[0,0,10,10]}],"num":[{"name":"age","val":35}]}},"3":{"object_data":{"boolean":[{"name":"visible","val":true}]}}}},"5":{"objects":{"0":{"object_data":{"bbox":[{"name":"position","val":[100,100,200,400]}]}},"1":{"object_data":{"bbox":[{"name":"position","val":[300,1000,200,400]}]}},"2":{"object_data":{"bbox":[{"name":"face","val":[0,0,100,100]},{"name":"mouth","val":[0,0,10,10]},{"name":"hand","val":[0,0,30,30]},{"name":"eyeL","val":[0,0,10,10]},{"name":"eyeR","val":[0,0,10,10]}],"num":[{"name":"age","val":35}]}}}},"6":{"objects":{"0":{"object_data":{"bbox":[{"name":"position","val":[100,100,200,400]}],"text":[{"name":"color","val":"red"}]}},"1":{"object_data":{"bbox":[{"name":"position","val":[300,1000,200,400]}]}},"2":{"object_data":{"num":[{"name":"age","val":35}]}}}},"7":{"objects":{"0":{"object_data":{"bbox":[{"name":"position","val":[100,100,200,400]}],"text":[{"name":"color","val":"red"}]}},"1":{"object_data":{"bbox":[{"name":"position","val":[300,1000,200,400]}]}},"2":{"object_data":{"num":[{"name":"age","val":35}]}}}},"8":{"objects":{"0":{"object_data":{"bbox":[{"name":"position","val":[100,100,200,400]}],"text":[{"name":"color","val":"red"}]}},"1":{"object_data":{"bbox":[{"name":"position","val":[300,1000,200,400]}]}},"2":{"object_data":{"num":[{"name":"age","val":35}]}}}},"9":{"objects":{"0":{"object_data":{"bbox":[{"name":"position","val":[100,100,200,400]}],"text":[{"name":"color","val":"red"}]}},"1":{"object_data":{"bbox":[{"name":"position","val":[300,1000,200,400]}]}},"2":{"object_data":{"num":[{"name":"age","val":35}]}}}},"10":{"objects":{"0":{"object_data":{"bbox":[{"name":"position","val":[100,100,200,400]}],"text":[{"name":"color","val":"red"}]}},"1":{"object_data":{"bbox":[{"name":"position","val":[300,1000,200,400]}]}},"2":{"object_data":{"num":[{"name":"age","val":35}]}}}}},"version":"4.2.1","frame_intervals":[{"frame_start":0,"frame_end":10}],"objects":{"0":{"name":"BMW","type":"#Car","frame_intervals":[{"frame_start":0,"frame_end":10}]},"1":{"name":"Seat","type":"#Car","frame_intervals":[{"frame_start":0,"frame_end":10}]},"2":{"name":"John","type":"#Pedestrian","frame_intervals":[{"frame_start":0,"frame_end":10}]},"3":{"name":"","type":"#StopSign","frame_intervals":[{"frame_start":0,"frame_end":4}]}}}}')
    expect(vcd.getNumObjects()).toBe(4)

    // 4.- Delete some content
    vcd.rmObject(car2_uid)
    expect(vcd.getNumObjects()).toBe(3)
    vcd.rmObjectByType('#StopSign')
    expect(vcd.getNumObjects()).toBe(2)

    vcd.rmObjectByFrame(person1_uid, [0, 5])  // after this call, this person has data only between 6 and 10
    expect(vcd.getObject(person1_uid)['frame_intervals'][0]['frame_start']).toBe(6)
    expect(vcd.getObject(person1_uid)['frame_intervals'][0]['frame_end']).toBe(10)

    // 5.- Remove all content sequentially
    vcd.rmObject(person1_uid)
    expect(vcd.getNumObjects()).toBe(1)
    vcd.rmObject(car1_uid)
    expect(vcd.getNumObjects()).toBe(0)

});

test('test_metadata', () => {
    let vcd = new VCD()
    vcd.addAnnotator('Algorithm01')
    vcd.addComment('Annotations produced automatically - SW v0.1')

    expect(vcd.stringify(false)).toBe('{"vcd":{"frames":{},"version":"4.2.1","frame_intervals":[],"metadata":{"annotator":"Algorithm01","comment":"Annotations produced automatically - SW v0.1"}}}')
    // See more examples about Streams in stream_frame_properties.test.ts
});

test('test_ontology_list', () => {
    let vcd = new VCD()
    
    let ont_uid_1 = vcd.addOntology('http://vcd.vicomtech.org/ontology/automotive')
    let ont_uid_2 = vcd.addOntology('http://www.anotherURL.org/ontology')

    // Let's create an object with a pointer to the ontology
    let uid_car = vcd.addObject('CARLOTA', '#Car', null, null, ont_uid_1)
    vcd.addObjectData(uid_car, new types.Text('brand', 'Toyota'))
    vcd.addObjectData(uid_car, new types.Text('model', 'Prius'))

    let uid_marcos = vcd.addObject('Marcos', '#Person', null, null, ont_uid_2)
    vcd.addObjectData(uid_marcos, new types.Bbox('head', [10, 10, 30, 30]), [2, 4])

    expect(vcd.getObject(uid_car)['ontology_uid']).toBe(ont_uid_1)
    expect(vcd.getObject(uid_marcos)['ontology_uid']).toBe(ont_uid_2)
    expect(vcd.getOntology(ont_uid_1)).toBe('http://vcd.vicomtech.org/ontology/automotive')
    expect(vcd.getOntology(ont_uid_2)).toBe('http://www.anotherURL.org/ontology')

    expect(vcd.stringify(false)).toBe('{"vcd":{"frames":{"2":{"objects":{"1":{"object_data":{"bbox":[{"name":"head","val":[10,10,30,30]}]}}}},"3":{"objects":{"1":{"object_data":{"bbox":[{"name":"head","val":[10,10,30,30]}]}}}},"4":{"objects":{"1":{"object_data":{"bbox":[{"name":"head","val":[10,10,30,30]}]}}}}},"version":"4.2.1","frame_intervals":[{"frame_start":2,"frame_end":4}],"ontologies":{"0":"http://vcd.vicomtech.org/ontology/automotive","1":"http://www.anotherURL.org/ontology"},"objects":{"0":{"name":"CARLOTA","type":"#Car","frame_intervals":[],"ontology_uid":0,"object_data":{"text":[{"name":"brand","val":"Toyota"},{"name":"model","val":"Prius"}]}},"1":{"name":"Marcos","type":"#Person","frame_intervals":[{"frame_start":2,"frame_end":4}],"ontology_uid":1}}}}')
});

test('test_semantics', () => {
    let vcd = new VCD()

    // Let's create some contexts, actions, and events
    let officeUID = vcd.addContext('Room1', '#Office')

    let talking_uid, start_talking_uid, noisy_uid, relation1_uid, relation2_uid;
    for(let frameNum=0; frameNum<30; frameNum++) {
        if (frameNum == 3) {
            start_talking_uid = vcd.addEvent('', '#StartTalking', frameNum)
            talking_uid = vcd.addAction('', '#Talking', frameNum)
            noisy_uid = vcd.addContext('', '#Noisy', frameNum)

            let relation1_uid = vcd.addRelation('', '#Starts')
            vcd.addRdf(relation1_uid, RDF.subject, start_talking_uid, ElementType.event)
            vcd.addRdf(relation1_uid, RDF.object, talking_uid, ElementType.action)

            let relation2_uid = vcd.addRelation('', '#Causes')
            vcd.addRdf(relation2_uid, RDF.subject, talking_uid, ElementType.action)
            vcd.addRdf(relation2_uid, RDF.object, noisy_uid, ElementType.context)

            expect(vcd.getNumRelations()).toBe(2)
            expect(vcd.getRelation(relation2_uid)['rdf_subjects'].length).toBe(1)
            expect(vcd.getRelation(relation2_uid)['rdf_subjects'][0]['uid']).toBe(talking_uid)
        }

        else if( frameNum >= 3 && frameNum <= 11) {
            vcd.updateAction(talking_uid, frameNum)
            vcd.updateContext(noisy_uid, frameNum)
        }
    }

    //console.log(vcd.stringify(false))
    expect(vcd.stringify(false)).toBe('{"vcd":{"frames":{"3":{"events":{"0":{}},"actions":{"0":{}},"contexts":{"1":{}}},"4":{"actions":{"0":{}},"contexts":{"1":{}}},"5":{"actions":{"0":{}},"contexts":{"1":{}}},"6":{"actions":{"0":{}},"contexts":{"1":{}}},"7":{"actions":{"0":{}},"contexts":{"1":{}}},"8":{"actions":{"0":{}},"contexts":{"1":{}}},"9":{"actions":{"0":{}},"contexts":{"1":{}}},"10":{"actions":{"0":{}},"contexts":{"1":{}}},"11":{"actions":{"0":{}},"contexts":{"1":{}}}},"version":"4.2.1","frame_intervals":[{"frame_start":3,"frame_end":11}],"contexts":{"0":{"name":"Room1","type":"#Office","frame_intervals":[]},"1":{"name":"","type":"#Noisy","frame_intervals":[{"frame_start":3,"frame_end":11}]}},"events":{"0":{"name":"","type":"#StartTalking","frame_intervals":[{"frame_start":3,"frame_end":3}]}},"actions":{"0":{"name":"","type":"#Talking","frame_intervals":[{"frame_start":3,"frame_end":11}]}},"relations":{"0":{"name":"","type":"#Starts","frame_intervals":[],"rdf_subjects":[{"uid":0,"type":"event"}],"rdf_objects":[{"uid":0,"type":"action"}]},"1":{"name":"","type":"#Causes","frame_intervals":[],"rdf_subjects":[{"uid":0,"type":"action"}],"rdf_objects":[{"uid":1,"type":"context"}]}}}}')
});

test('test_online_operation', () => {
    // Simulate an online operation during 1000 frames
    // And cut-off every 100 frames into a new VCD
    let vcds = []
    let uid = -1
    for(let frameNum = 0; frameNum<1000; frameNum++) {
        if (frameNum % 100 == 0) {
            // Create new VCD
            vcds.push(new VCD())
            let vcd_current = vcds[vcds.length - 1]

            // optionally we could here dump into JSON file
            if(frameNum == 0) {
                uid = vcd_current.addObject('CARLOTA', 'Car')  // leave VCD to assign uid=0
                vcd_current.addObjectData(uid, new types.Bbox('', [0, frameNum, 0, 0]), frameNum)                
            }
            else{
                uid = vcd_current.addObject('CARLOTA', 'Car', uid)  // tell VCD to use last_uid
                vcd_current.addObjectData(uid, new types.Bbox('', [0, frameNum, 0, 0]), frameNum)                
            }
        }
        else {
            // Continue current VCD
            let vcd_current = vcds[vcds.length - 1]
            vcd_current.addObjectData(uid, new types.Bbox('', [0, frameNum, 0, 0]), frameNum)
        }        
    }
    for(let vcd_this of vcds) {
        expect(vcd_this.getNumObjects()).toBe(1)
        expect(vcd_this.getObject(uid)['name']).toBe('CARLOTA')
        expect(vcd_this.getObject(uid)['type']).toBe('Car')
    }
});

test('test_objects_without_data', () => {
    let vcd = new VCD()
    vcd.addObject('', '#Pedestrian', [0, 30])
    vcd.addObject('', '#Car', [20, 30])

    expect(vcd.stringify(false)).toBe('{"vcd":{"frames":{"0":{"objects":{"0":{}}},"1":{"objects":{"0":{}}},"2":{"objects":{"0":{}}},"3":{"objects":{"0":{}}},"4":{"objects":{"0":{}}},"5":{"objects":{"0":{}}},"6":{"objects":{"0":{}}},"7":{"objects":{"0":{}}},"8":{"objects":{"0":{}}},"9":{"objects":{"0":{}}},"10":{"objects":{"0":{}}},"11":{"objects":{"0":{}}},"12":{"objects":{"0":{}}},"13":{"objects":{"0":{}}},"14":{"objects":{"0":{}}},"15":{"objects":{"0":{}}},"16":{"objects":{"0":{}}},"17":{"objects":{"0":{}}},"18":{"objects":{"0":{}}},"19":{"objects":{"0":{}}},"20":{"objects":{"0":{},"1":{}}},"21":{"objects":{"0":{},"1":{}}},"22":{"objects":{"0":{},"1":{}}},"23":{"objects":{"0":{},"1":{}}},"24":{"objects":{"0":{},"1":{}}},"25":{"objects":{"0":{},"1":{}}},"26":{"objects":{"0":{},"1":{}}},"27":{"objects":{"0":{},"1":{}}},"28":{"objects":{"0":{},"1":{}}},"29":{"objects":{"0":{},"1":{}}},"30":{"objects":{"0":{},"1":{}}}},"version":"4.2.1","frame_intervals":[{"frame_start":0,"frame_end":30}],"objects":{"0":{"name":"","type":"#Pedestrian","frame_intervals":[{"frame_start":0,"frame_end":30}]},"1":{"name":"","type":"#Car","frame_intervals":[{"frame_start":20,"frame_end":30}]}}}}')
});

test('test_nested_data_attributes', () => {
    let vcd = new VCD()
    let uid_obj1 = vcd.addObject('someName1', '#Some')
    let box1 = new types.Bbox('head', [0, 0, 10, 10])
    box1.addAttribute(new types.Boolean('visible', true))

    expect('attributes' in box1.data).toBe(true)
    expect('boolean' in box1.data['attributes']).toBe(true)
    expect(box1.data['attributes']['boolean'].length).toBe(1)
    expect(box1.data['attributes']['boolean'][0]['name']).toBe('visible')
    expect(box1.data['attributes']['boolean'][0]['val']).toBe(true)

    vcd.addObjectData(uid_obj1, box1, 0)

    expect(vcd.stringify(false, false)).toBe('{"vcd":{"frames":{"0":{"objects":{"0":{"object_data":{"bbox":[{"name":"head","val":[0,0,10,10],"attributes":{"boolean":[{"name":"visible","val":true}]}}]}}}}},"version":"4.2.1","frame_intervals":[{"frame_start":0,"frame_end":0}],"objects":{"0":{"name":"someName1","type":"#Some","frame_intervals":[{"frame_start":0,"frame_end":0}]}}}}')
});