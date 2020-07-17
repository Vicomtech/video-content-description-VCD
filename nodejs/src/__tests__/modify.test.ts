import { VCD, ElementType, RDF } from '../vcd.core'
import * as types from '../vcd.types'

test('test_element_data_same_name', () => {
    let vcd = new VCD()

    let uid1 = vcd.addAction('', '#Walking')
    vcd.addActionData(uid1, new types.Boolean('validated', true), [0, 5])
    vcd.addActionData(uid1, new types.Boolean('occluded', false), [0, 5])
    vcd.addActionData(uid1, new types.Text('label', 'manual'), [0, 5])

    // Now try to add an Action Data with the same name
    vcd.addActionData(uid1, new types.Boolean('validated', false), [0, 5])

    // The initial 'validated' Boolean, with value true is substituted by false, instead of added
    //console.log(vcd.stringify(false))
    expect(vcd.stringify(false)).toBe('{"vcd":{"frames":{"0":{"actions":{"0":{"action_data":{"boolean":[{"name":"validated","val":false},{"name":"occluded","val":false}],"text":[{"name":"label","val":"manual"}]}}}},"1":{"actions":{"0":{"action_data":{"boolean":[{"name":"validated","val":false},{"name":"occluded","val":false}],"text":[{"name":"label","val":"manual"}]}}}},"2":{"actions":{"0":{"action_data":{"boolean":[{"name":"validated","val":false},{"name":"occluded","val":false}],"text":[{"name":"label","val":"manual"}]}}}},"3":{"actions":{"0":{"action_data":{"boolean":[{"name":"validated","val":false},{"name":"occluded","val":false}],"text":[{"name":"label","val":"manual"}]}}}},"4":{"actions":{"0":{"action_data":{"boolean":[{"name":"validated","val":false},{"name":"occluded","val":false}],"text":[{"name":"label","val":"manual"}]}}}},"5":{"actions":{"0":{"action_data":{"boolean":[{"name":"validated","val":false},{"name":"occluded","val":false}],"text":[{"name":"label","val":"manual"}]}}}}},"schema_version":"4.3.0","frame_intervals":[{"frame_start":0,"frame_end":5}],"actions":{"0":{"name":"","type":"#Walking","frame_intervals":[{"frame_start":0,"frame_end":5}],"action_data_pointers":{"validated":{"type":"boolean","frame_intervals":[{"frame_start":0,"frame_end":5}]},"occluded":{"type":"boolean","frame_intervals":[{"frame_start":0,"frame_end":5}]},"label":{"type":"text","frame_intervals":[{"frame_start":0,"frame_end":5}]}}}}}}')
});

test('test_element_data_nested_same_name', () => {
    let vcd = new VCD()

    let uid1 = vcd.addObject('mike', '#Pedestrian')
    let body = new types.Bbox('body', [0, 0, 100, 150])
    body.addAttribute(new types.Boolean('visible', true))
    body.addAttribute(new types.Boolean('occluded', false))
    body.addAttribute(new types.Boolean('visible', false))  // this is repeated, so it is substituted
    vcd.addObjectData(uid1, body, [0, 5])
      
    //console.log(vcd.stringify(false))
    expect(vcd.stringify(false)).toBe('{"vcd":{"frames":{"0":{"objects":{"0":{"object_data":{"bbox":[{"name":"body","val":[0,0,100,150],"attributes":{"boolean":[{"name":"visible","val":false},{"name":"occluded","val":false}]}}]}}}},"1":{"objects":{"0":{"object_data":{"bbox":[{"name":"body","val":[0,0,100,150],"attributes":{"boolean":[{"name":"visible","val":false},{"name":"occluded","val":false}]}}]}}}},"2":{"objects":{"0":{"object_data":{"bbox":[{"name":"body","val":[0,0,100,150],"attributes":{"boolean":[{"name":"visible","val":false},{"name":"occluded","val":false}]}}]}}}},"3":{"objects":{"0":{"object_data":{"bbox":[{"name":"body","val":[0,0,100,150],"attributes":{"boolean":[{"name":"visible","val":false},{"name":"occluded","val":false}]}}]}}}},"4":{"objects":{"0":{"object_data":{"bbox":[{"name":"body","val":[0,0,100,150],"attributes":{"boolean":[{"name":"visible","val":false},{"name":"occluded","val":false}]}}]}}}},"5":{"objects":{"0":{"object_data":{"bbox":[{"name":"body","val":[0,0,100,150],"attributes":{"boolean":[{"name":"visible","val":false},{"name":"occluded","val":false}]}}]}}}}},"schema_version":"4.3.0","frame_intervals":[{"frame_start":0,"frame_end":5}],"objects":{"0":{"name":"mike","type":"#Pedestrian","frame_intervals":[{"frame_start":0,"frame_end":5}],"object_data_pointers":{"body":{"type":"bbox","frame_intervals":[{"frame_start":0,"frame_end":5}],"attributes":{"visible":"boolean","occluded":"boolean"}}}}}}}')
});

test('test_action_frame_interval_modification', () => {
    let vcd = new VCD()
    
    // Basic modification of element-level information, including frame-intervals
    let uid1 = vcd.addAction('Drinking_5', "distraction/Drinking", [[5, 10], [15, 20]])
    let fis = vcd.getElementFrameIntervals(ElementType.action, uid1)
    expect(fis.getDict()).toStrictEqual([{'frame_start': 5, 'frame_end': 10}, {'frame_start': 15, 'frame_end': 20}])

    // Usual "just-one-frame" update for online operation: internally updates frame interval using FUSION (UNION)
    vcd.updateAction(uid1, 21)
    fis = vcd.getElementFrameIntervals(ElementType.action, uid1)
    expect(fis.getDict()).toStrictEqual([{'frame_start': 5, 'frame_end': 10}, {'frame_start': 15, 'frame_end': 21}])

    // Entire modification with potential removal and extension
    vcd.modifyAction(uid1, null, null, [[5, 11], [17, 20]])  // adding 11, and deleting 15, 16 and 21
    fis = vcd.getElementFrameIntervals(ElementType.action, uid1)
    expect(fis.getDict()).toStrictEqual([{'frame_start': 5, 'frame_end': 11}, {'frame_start': 17, 'frame_end': 20}])
    
    // Complex modification of element_data level information    
    vcd.addActionData(uid1, new types.Text('label', 'manual'), [[5, 5], [11, 11], [20, 20]])
    //vcd.stringify(false)
    vcd.updateActionData(uid1, new types.Text('label', 'auto'), [[11, 11]])  // This is an update, we want to modify part of the ActionData, without the need to substitute it entirely. This function can also be used to increase element's range
        
    expect(vcd.getActionData(uid1, 'label', 5)['val']).toBe('manual')    
    expect(vcd.getActionData(uid1, 'label', 11)['val']).toBe('auto')    
    expect(vcd.getActionData(uid1, 'label', 20)['val']).toBe('manual')
    fis = vcd.getElementFrameIntervals(ElementType.action, uid1)
    expect(fis.getDict()).toStrictEqual([{'frame_start': 5, 'frame_end': 11}, {'frame_start': 17, 'frame_end': 20}])  // element should not be modified so far

    // If element-data is defined BEYOND the element limits -> Element is automatically extended
    vcd.addActionData(uid1, new types.Text('label', 'manual'), [[5, 25]])
    for(let i=5; i<=25; i++) {
        expect(vcd.getActionData(uid1, 'label', i)['val']).toBe('manual')
    }
    expect(vcd.getElementFrameIntervals(ElementType.action, uid1).getDict()).toStrictEqual([{'frame_start': 5, 'frame_end': 25}])

    // Note: any further modification of Action also modifies (e.g. removes) any actionData
    vcd.modifyAction(uid1, null, null, [[5, 11], [15, 19]])  // removing frames 20 and 21, and also from 12 to 14 inclusive
    expect(vcd.getElementFrameIntervals(ElementType.action, uid1).getDict()).toStrictEqual([{'frame_start': 5, 'frame_end': 11}, {'frame_start': 15, 'frame_end': 19}])
    expect(vcd.getActionData(uid1, 'label', 20)).toBe(null)  // getActionData return null if not found

    // Action data can also be "modified", which means fully substituted    
    vcd.modifyActionData(uid1, new types.Text('label', 'auto'), [[7, 26], [28, 28]])  // this will remove the entries at frames 5 and 6, add 26, and also 28
    expect(vcd.getActionDataFrameIntervals(uid1, 'label').getDict()).toStrictEqual([{'frame_start': 7, 'frame_end': 26}, {'frame_start': 28, 'frame_end': 28}])
    // The Action should not be "removed" because an inner ActionData is removed
    expect(vcd.getElementFrameIntervals(ElementType.action, uid1).getDict()).toStrictEqual([{'frame_start': 5, 'frame_end': 26}, {'frame_start': 28, 'frame_end': 28}])       
});

// TODO: test modify Relation also