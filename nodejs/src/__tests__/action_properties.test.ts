import { VCD, ElementType, RDF } from '../vcd.core'
import * as types from '../vcd.types'

test('test_action_properties', () => {
    // 1.- Create VCD
    let vcd = new VCD()

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
    expect(vcd.stringify(false, false)).toBe('{"vcd":{"frames":{"0":{"actions":{"0":{"action_data":{"num":[{"name":"confidence","val":0.98}],"vec":[{"name":"confidence_vec","val":[0.98,0.97]}],"text":[{"name":"annotation","val":"Manual"}]}}},"objects":{"0":{}},"contexts":{"0":{},"1":{}}},"1":{"actions":{"0":{"action_data":{"boolean":[{"name":"validated","val":true}]}}},"objects":{"0":{}},"contexts":{"0":{},"1":{}}},"2":{"actions":{"0":{}},"objects":{"0":{}},"contexts":{"0":{},"1":{}}},"3":{"actions":{"0":{}},"objects":{"0":{}},"contexts":{"0":{},"1":{}}},"4":{"actions":{"0":{}},"objects":{"0":{}},"contexts":{"0":{},"1":{"context_data":{"num":[{"name":"risk","val":0.7},{"name":"weight","val":0.5}]}}}},"5":{"actions":{"0":{}},"objects":{"0":{}},"contexts":{"0":{},"1":{}}},"6":{"actions":{"0":{}},"objects":{"0":{}},"contexts":{"0":{}}},"7":{"actions":{"0":{}},"objects":{"0":{}},"contexts":{"0":{}}},"8":{"actions":{"0":{}},"objects":{"0":{}},"contexts":{"0":{}}},"9":{"actions":{"0":{}},"objects":{"0":{}},"contexts":{"0":{}}},"10":{"actions":{"0":{}},"objects":{"0":{}},"contexts":{"0":{}}}},"version":"4.2.1","frame_intervals":[{"frame_start":0,"frame_end":10}],"actions":{"0":{"name":"","type":"#Running","frame_intervals":[{"frame_start":0,"frame_end":10}]}},"objects":{"0":{"name":"Marcos","type":"#Person","frame_intervals":[],"object_data":{"text":[{"name":"Position","val":"#Researcher"}]}}},"contexts":{"0":{"name":"","type":"#Sunny","frame_intervals":[],"context_data":{"text":[{"name":"category","val":"#Weather"},{"name":"annotation","val":"Manual"}]}},"1":{"name":"","type":"#Highway","frame_intervals":[{"frame_start":0,"frame_end":5}]}}}}')
});