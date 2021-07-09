import { VCD, ElementType, RDF, OpenLABEL } from '../vcd.core'
import * as types from '../vcd.types'
import openlabel030_test_action_properties from '../../../tests/etc/openlabel030_test_action_properties.json'

test('test_action_properties', () => {
    // 1.- Create VCD
    //let vcd = new VCD()
    let vcd = new OpenLABEL()

    // 2.- Create Object
    let uid_action1 = vcd.addAction('', '#Running', [0, 10])
    vcd.addActionData(uid_action1, new types.Num('confidence', 0.98), 0)
    vcd.addActionData(uid_action1, new types.Vec('confidence_vec', [0.98, 0.97]), 0)
    vcd.addActionData(uid_action1, new types.Text('annotation', 'Manual'), 0)
    vcd.addActionData(uid_action1, new types.Boolean('validated', true), 1)

    // Same can be done with events and event data, and contexts and context_data
    // And can be done as dynamic or static info
    let uid_object1 = vcd.addObject('Marcos', '#Person')
    vcd.addObjectData(uid_object1, new types.Text('Position', '#Researcher'))

    let uid_context1 = vcd.addContext('', '#Sunny')
    vcd.addContextData(uid_context1, new types.Text('category', '#Weather'))
    vcd.addContextData(uid_context1, new types.Text('annotation', 'Manual'))

    let uid_context2 = vcd.addContext('', '#Highway', [0, 5])
    vcd.addContextData(uid_context2, new types.Num('risk', 0.7), 4)
    vcd.addContextData(uid_context2, new types.Num('weight', 0.5), 4)

    //console.log(vcd.stringify(false, false))
    //expect(vcd.stringify(false, false)).toBe('{"vcd":{"frames":{"0":{"actions":{"0":{"action_data":{"num":[{"name":"confidence","val":0.98}],"vec":[{"name":"confidence_vec","val":[0.98,0.97]}],"text":[{"name":"annotation","val":"Manual"}]}}},"contexts":{"1":{}}},"1":{"actions":{"0":{"action_data":{"boolean":[{"name":"validated","val":true}]}}},"contexts":{"1":{}}},"2":{"actions":{"0":{}},"contexts":{"1":{}}},"3":{"actions":{"0":{}},"contexts":{"1":{}}},"4":{"actions":{"0":{}},"contexts":{"1":{"context_data":{"num":[{"name":"risk","val":0.7},{"name":"weight","val":0.5}]}}}},"5":{"actions":{"0":{}},"contexts":{"1":{}}},"6":{"actions":{"0":{}}},"7":{"actions":{"0":{}}},"8":{"actions":{"0":{}}},"9":{"actions":{"0":{}}},"10":{"actions":{"0":{}}}},"schema_version":"4.3.1","frame_intervals":[{"frame_start":0,"frame_end":10}],"actions":{"0":{"name":"","type":"#Running","frame_intervals":[{"frame_start":0,"frame_end":10}],"action_data_pointers":{"confidence":{"type":"num","frame_intervals":[{"frame_start":0,"frame_end":0}]},"confidence_vec":{"type":"vec","frame_intervals":[{"frame_start":0,"frame_end":0}]},"annotation":{"type":"text","frame_intervals":[{"frame_start":0,"frame_end":0}]},"validated":{"type":"boolean","frame_intervals":[{"frame_start":1,"frame_end":1}]}}}},"objects":{"0":{"name":"Marcos","type":"#Person","object_data":{"text":[{"name":"Position","val":"#Researcher"}]},"object_data_pointers":{"Position":{"type":"text","frame_intervals":[]}}}},"contexts":{"0":{"name":"","type":"#Sunny","context_data":{"text":[{"name":"category","val":"#Weather"},{"name":"annotation","val":"Manual"}]},"context_data_pointers":{"category":{"type":"text","frame_intervals":[]},"annotation":{"type":"text","frame_intervals":[]}}},"1":{"name":"","type":"#Highway","frame_intervals":[{"frame_start":0,"frame_end":5}],"context_data_pointers":{"risk":{"type":"num","frame_intervals":[{"frame_start":4,"frame_end":4}]},"weight":{"type":"num","frame_intervals":[{"frame_start":4,"frame_end":4}]}}}}}}')
    expect(vcd.stringify(false)).toBe(new VCD(openlabel030_test_action_properties, false).stringify(false))
});