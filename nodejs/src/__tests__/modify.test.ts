import { VCD, ElementType, SetMode, OpenLABEL, UID, FrameIntervals } from '../vcd.core'
import * as types from '../vcd.types'
import openlabel100_test_static_dynamic_object_1_1 from '../../../tests/etc/openlabel100_test_static_dynamic_object_1_1.json'
import openlabel100_test_static_dynamic_object_1_2 from '../../../tests/etc/openlabel100_test_static_dynamic_object_1_2.json'
import openlabel100_test_static_dynamic_object_2 from '../../../tests/etc/openlabel100_test_static_dynamic_object_2.json'
import openlabel100_test_element_data_same_name from '../../../tests/etc/openlabel100_test_element_data_same_name.json'
import openlabel100_test_element_data_nested_same_name from '../../../tests/etc/openlabel100_test_element_data_nested_same_name.json'

test('test_static_dynamic_object_1', () => {
    // 1.- Create VCD
    let vcd = new VCD()

    // 2.- Let's create a static object and add some dynamic properties    
    // When the attribute is added, the frame information is propagated to the element
    let uid1 = vcd.addObject('line1', '#LaneMarking')
    vcd.addObjectData(uid1, new types.Text('type', 'dashed'), [5, 10])
    //console.log(vcd.stringify(false))
    //expect(vcd.stringify(false)).toBe('{"vcd":{"metadata":{"schema_version":"4.3.1"},"objects":{"0":{"name":"line1","type":"#LaneMarking","frame_intervals":[{"frame_start":5,"frame_end":10}],"object_data_pointers":{"type":{"type":"text","frame_intervals":[{"frame_start":5,"frame_end":10}]}}}},"frames":{"5":{"objects":{"0":{"object_data":{"text":[{"name":"type","val":"dashed"}]}}}},"6":{"objects":{"0":{"object_data":{"text":[{"name":"type","val":"dashed"}]}}}},"7":{"objects":{"0":{"object_data":{"text":[{"name":"type","val":"dashed"}]}}}},"8":{"objects":{"0":{"object_data":{"text":[{"name":"type","val":"dashed"}]}}}},"9":{"objects":{"0":{"object_data":{"text":[{"name":"type","val":"dashed"}]}}}},"10":{"objects":{"0":{"object_data":{"text":[{"name":"type","val":"dashed"}]}}}}},"frame_intervals":[{"frame_start":5,"frame_end":10}]}}')
    expect(vcd.stringify(false)).toBe(new VCD(openlabel100_test_static_dynamic_object_1_1, false).stringify(false))

    // 3.- Let's add some static attributes
    vcd.addObjectData(uid1, new types.Text('color', 'yellow'))
    //console.log(vcd.stringify(false))
    //expect(vcd.stringify(false)).toBe('{"vcd":{"metadata":{"schema_version":"4.3.1"},"objects":{"0":{"name":"line1","type":"#LaneMarking","frame_intervals":[{"frame_start":5,"frame_end":10}],"object_data_pointers":{"type":{"type":"text","frame_intervals":[{"frame_start":5,"frame_end":10}]},"color":{"type":"text","frame_intervals":[]}},"object_data":{"text":[{"name":"color","val":"yellow"}]}}},"frames":{"5":{"objects":{"0":{"object_data":{"text":[{"name":"type","val":"dashed"}]}}}},"6":{"objects":{"0":{"object_data":{"text":[{"name":"type","val":"dashed"}]}}}},"7":{"objects":{"0":{"object_data":{"text":[{"name":"type","val":"dashed"}]}}}},"8":{"objects":{"0":{"object_data":{"text":[{"name":"type","val":"dashed"}]}}}},"9":{"objects":{"0":{"object_data":{"text":[{"name":"type","val":"dashed"}]}}}},"10":{"objects":{"0":{"object_data":{"text":[{"name":"type","val":"dashed"}]}}}}},"frame_intervals":[{"frame_start":5,"frame_end":10}]}}')   
    expect(vcd.stringify(false)).toBe(new VCD(openlabel100_test_static_dynamic_object_1_2, false).stringify(false))
   
});

test('test_static_dynamic_object_2', () => {
    // 1.- Create VCD
    let vcd = new VCD()
        
    // 2.- Create a dynamic object with static information
    // The attribute is added to the objects section
    let uid1 = vcd.addObject('line1', '#BottsDots', [5, 10])
    let poly = new types.Poly2d('poly', [100, 100, 110, 110, 120, 130, 500, 560], types.Poly2DType.MODE_POLY2D_ABSOLUTE, false)
    poly.addAttribute(new types.Text('type', "single_dot"))
    vcd.addObjectData(uid1, poly)

    //console.log(vcd.stringify(false))
    //expect(vcd.stringify(false)).toBe('{"vcd":{"metadata":{"schema_version":"4.3.1"},"objects":{"0":{"name":"line1","type":"#LaneMarking","frame_intervals":[{"frame_start":5,"frame_end":10}],"object_data":{"poly2d":[{"name":"poly","val":[100,100,110,110,120,130,500,560],"mode":"MODE_POLY2D_ABSOLUTE","closed":false,"attributes":{"text":[{"name":"type","val":"dashed"}]}}]},"object_data_pointers":{"poly":{"type":"poly2d","frame_intervals":[],"attributes":{"type":"text"}}}}},"frames":{"5":{"objects":{"0":{}}},"6":{"objects":{"0":{}}},"7":{"objects":{"0":{}}},"8":{"objects":{"0":{}}},"9":{"objects":{"0":{}}},"10":{"objects":{"0":{}}}},"frame_intervals":[{"frame_start":5,"frame_end":10}]}}')
    expect(vcd.stringify(false)).toBe(new VCD(openlabel100_test_static_dynamic_object_2, false).stringify(false))
});

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
    //expect(vcd.stringify(false)).toBe('{"vcd":{"frames":{"0":{"actions":{"0":{"action_data":{"boolean":[{"name":"validated","val":false},{"name":"occluded","val":false}],"text":[{"name":"label","val":"manual"}]}}}},"1":{"actions":{"0":{"action_data":{"boolean":[{"name":"validated","val":false},{"name":"occluded","val":false}],"text":[{"name":"label","val":"manual"}]}}}},"2":{"actions":{"0":{"action_data":{"boolean":[{"name":"validated","val":false},{"name":"occluded","val":false}],"text":[{"name":"label","val":"manual"}]}}}},"3":{"actions":{"0":{"action_data":{"boolean":[{"name":"validated","val":false},{"name":"occluded","val":false}],"text":[{"name":"label","val":"manual"}]}}}},"4":{"actions":{"0":{"action_data":{"boolean":[{"name":"validated","val":false},{"name":"occluded","val":false}],"text":[{"name":"label","val":"manual"}]}}}},"5":{"actions":{"0":{"action_data":{"boolean":[{"name":"validated","val":false},{"name":"occluded","val":false}],"text":[{"name":"label","val":"manual"}]}}}}},"schema_version":"4.3.1","frame_intervals":[{"frame_start":0,"frame_end":5}],"actions":{"0":{"name":"","type":"#Walking","frame_intervals":[{"frame_start":0,"frame_end":5}],"action_data_pointers":{"validated":{"type":"boolean","frame_intervals":[{"frame_start":0,"frame_end":5}]},"occluded":{"type":"boolean","frame_intervals":[{"frame_start":0,"frame_end":5}]},"label":{"type":"text","frame_intervals":[{"frame_start":0,"frame_end":5}]}}}}}}')
    expect(vcd.stringify(false)).toBe(new VCD(openlabel100_test_element_data_same_name, false).stringify(false))
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
    //expect(vcd.stringify(false)).toBe('{"vcd":{"frames":{"0":{"objects":{"0":{"object_data":{"bbox":[{"name":"body","val":[0,0,100,150],"attributes":{"boolean":[{"name":"visible","val":false},{"name":"occluded","val":false}]}}]}}}},"1":{"objects":{"0":{"object_data":{"bbox":[{"name":"body","val":[0,0,100,150],"attributes":{"boolean":[{"name":"visible","val":false},{"name":"occluded","val":false}]}}]}}}},"2":{"objects":{"0":{"object_data":{"bbox":[{"name":"body","val":[0,0,100,150],"attributes":{"boolean":[{"name":"visible","val":false},{"name":"occluded","val":false}]}}]}}}},"3":{"objects":{"0":{"object_data":{"bbox":[{"name":"body","val":[0,0,100,150],"attributes":{"boolean":[{"name":"visible","val":false},{"name":"occluded","val":false}]}}]}}}},"4":{"objects":{"0":{"object_data":{"bbox":[{"name":"body","val":[0,0,100,150],"attributes":{"boolean":[{"name":"visible","val":false},{"name":"occluded","val":false}]}}]}}}},"5":{"objects":{"0":{"object_data":{"bbox":[{"name":"body","val":[0,0,100,150],"attributes":{"boolean":[{"name":"visible","val":false},{"name":"occluded","val":false}]}}]}}}}},"schema_version":"4.3.1","frame_intervals":[{"frame_start":0,"frame_end":5}],"objects":{"0":{"name":"mike","type":"#Pedestrian","frame_intervals":[{"frame_start":0,"frame_end":5}],"object_data_pointers":{"body":{"type":"bbox","frame_intervals":[{"frame_start":0,"frame_end":5}],"attributes":{"visible":"boolean","occluded":"boolean"}}}}}}}')
    expect(vcd.stringify(false)).toBe(new VCD(openlabel100_test_element_data_nested_same_name, false).stringify(false))
});

test('test_action_frame_interval_modification', () => {
    let vcd = new VCD()
    
    // Basic modification of element-level information, including frame-intervals
    let uid1 = vcd.addAction('Drinking_5', "distraction/Drinking", [[5, 10], [15, 20]])
    let fis = vcd.getElementFrameIntervals(ElementType.action, uid1)
    expect(fis.getDict()).toStrictEqual([{'frame_start': 5, 'frame_end': 10}, {'frame_start': 15, 'frame_end': 20}])

    // Usual "just-one-frame" update for online operation: internally updates frame interval using FUSION (UNION)
    vcd.addAction('Drinking_5', "distraction/Drinking", 21, uid1)
    fis = vcd.getElementFrameIntervals(ElementType.action, uid1)
    expect(fis.getDict()).toStrictEqual([{'frame_start': 5, 'frame_end': 10}, {'frame_start': 15, 'frame_end': 21}])

    // Entire modification with potential removal and extension
    vcd.addAction('Drinking_5', "distraction/Drinking", [[5, 11], [17, 20]], uid1, null, null, SetMode.replace)  // adding 11, and deleting 15, 16 and 21
    fis = vcd.getElementFrameIntervals(ElementType.action, uid1)
    expect(fis.getDict()).toStrictEqual([{'frame_start': 5, 'frame_end': 11}, {'frame_start': 17, 'frame_end': 20}])
    
    // Complex modification of element_data level information    
    vcd.addActionData(uid1, new types.Text('label', 'manual'), [[5, 5], [11, 11], [20, 20]])
    //vcd.stringify(false)
    vcd.addActionData(uid1, new types.Text('label', 'auto'), [[11, 11]])  // This is an update, we want to modify part of the ActionData, without the need to substitute it entirely. This function can also be used to increase element's range
        
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
    vcd.addAction('Drinking_5', "distraction/Drinking", [[5, 11], [15, 19]], uid1, null, null, SetMode.replace)  // removing frames 20 and 21, and also from 12 to 14 inclusive
    expect(vcd.getElementFrameIntervals(ElementType.action, uid1).getDict()).toStrictEqual([{'frame_start': 5, 'frame_end': 11}, {'frame_start': 15, 'frame_end': 19}])
    expect(vcd.getActionData(uid1, 'label', 20)).toBe(null)  // getActionData return null if not found

    // Action data can also be "modified", which means fully substituted    
    vcd.addActionData(uid1, new types.Text('label', 'auto'), [[7, 26], [28, 28]], SetMode.replace)  // this will remove the entries at frames 5 and 6, add 26, and also 28
    expect(vcd.getActionDataFrameIntervals(uid1, 'label').getDict()).toStrictEqual([{'frame_start': 7, 'frame_end': 26}, {'frame_start': 28, 'frame_end': 28}])
    // The Action should not be "removed" because an inner ActionData is removed
    expect(vcd.getElementFrameIntervals(ElementType.action, uid1).getDict()).toStrictEqual([{'frame_start': 5, 'frame_end': 26}, {'frame_start': 28, 'frame_end': 28}])       

    // Move an action 100 frame to the future
    let shift = 100
    vcd.addAction('Drinking_5', "distraction/Drinking", [[5 + shift, 26 + shift], [28 + shift, 28 + shift]], uid1, null, null, SetMode.replace)

    let res = vcd.getActionData(uid1, 'label', 5)
    expect(res).toStrictEqual(null)

});

test('test_object_change_from_static_to_dynamic', () => {     
    // Static->Dynamic

    // CASE A)  (when VCD has no other object with frames)
    // Let's add a static object
    let vcd_a = new VCD()
    let uid_a = vcd_a.addObject("Enara", "Child")

    // Let's add some object data
    vcd_a.addObjectData(uid_a, new types.Text("FavouriteColor", "Pink"));    
    expect(vcd_a.getObjectData(uid_a, 'FavouriteColor', 3)).toStrictEqual(null) // null, no 'FavouriteColor' at frame 3
    expect(vcd_a.getObjectData(uid_a, 'FavouriteColor')['val']).toBe('Pink')  // no frameNum provided, then, asking for root-level object-data

    // Let's modify the object so it has a certain frame Interval (object_data frame intervals remain void)
    vcd_a.addObject("Enara", "Child", [5, 10], uid_a)

    // Check that the element data is now also defined for this frame interval (and thus removed from the root)    
    expect(vcd_a.getObjectData(uid_a, 'FavouriteColor', 3)).toStrictEqual(null) // null, no 'FavouriteColor' at frame 3
    expect(vcd_a.getObjectData(uid_a, 'FavouriteColor')['val']).toBe('Pink')   // asked without specifying frameNum -> looking at root
    expect(vcd_a.getObjectData(uid_a, 'FavouriteColor', 8)['val']).toBe('Pink') // asking in a frame inside the limits of the element's fis -> return its value at root

    // CASE B (when VCD has some other frame intervals already defined): VCD's getElementData behaves differently
    // In this case, as the VCD has frames, the object is assumed to exist in all the scene
    // when the user asks for element_data at certain frame, VCD looks for element_data at that frame, and if there
    // is nothing, it then searches at the static part
    let vcd_b = new VCD()
    vcd_b.addObject("room1", "Room", [0, 10])
    let uid_b = vcd_b.addObject("Enara", "Child")
    vcd_b.addObjectData(uid_b, new types.Text("FavouriteColor", "Pink"));    
    expect(vcd_b.getObjectData(uid_b, 'FavouriteColor', 3)['val']).toStrictEqual('Pink') 
    expect(vcd_b.getObjectData(uid_b, 'FavouriteColor')['val']).toBe('Pink')   
    vcd_b.addObject("Enara", "Child", [5, 10], uid_b)
    expect(vcd_b.getObjectData(uid_b, 'FavouriteColor', 3)).toStrictEqual(null) 
    expect(vcd_b.getObjectData(uid_b, 'FavouriteColor')['val']).toBe('Pink') 
    expect(vcd_b.getObjectData(uid_b, 'FavouriteColor', 8)['val']).toBe('Pink')

});

test('test_object_change_from_dynamic_to_static', () => { 
    let vcd = new VCD()

    // Dynamic->Static
    // Let's add a static object
    let uid1 = vcd.addObject("Enara", "Child", [5, 10])

    // Let's add some object data
    vcd.addObjectData(uid1, new types.Text("FavouriteColor", "Pink"));  // defined static (but element has already frame intervals)
    vcd.addObjectData(uid1, new types.Vec("Position", [1.0, 5.0]), 8);  

    vcd.addObject("Enara", "Child", null, uid1, null, null, SetMode.replace)  // SetMode.replace to force deleting the old frame interval
    // NOTE: declaring an element as static (with null frameIntervals) when it had non-static ElementData and with SetMode.replace makes VCD to remove the non-static ElementData
    expect(vcd.getObjectData(uid1, 'FavouriteColor', 8)).toStrictEqual(null) // this object_data was never static
    expect(vcd.getObjectData(uid1, 'FavouriteColor')['val']).toBe("Pink")  // Yes, there should be the object data at the root
    
    // "Position" does not exist anymore
    expect(vcd.getObjectData(uid1, 'Position', 8)).toStrictEqual(null) // this object_data is now static-only
    expect(vcd.getObjectData(uid1, 'Position')).toStrictEqual(null)  
});

test('test_modify_relations', () => {
    let vcd = new VCD()

    // Relation without frameintervals
    let uidCar1 = vcd.addObject('car1', 'car')
    let uidCar2 = vcd.addObject('car2', 'car')
    let uidCar3 = vcd.addObject('car3', 'car')
    let uidRelation1 = vcd.addRelationObjectObject('follows1', 'follows', uidCar1, uidCar2)

    expect(vcd.getRelation(uidRelation1)['rdf_subjects'][0]['uid']).toBe(uidCar1)
    expect(vcd.getRelation(uidRelation1)['rdf_subjects'][0]['type']).toBe('object')
    expect(vcd.getRelation(uidRelation1)['rdf_objects'][0]['uid']).toBe(uidCar2)
    expect(vcd.getRelation(uidRelation1)['rdf_objects'][0]['type']).toBe('object')
    expect(vcd.getRelation(uidRelation1)['rdf_objects'].length).toBe(1)

    uidRelation1 = vcd.addRelationObjectObject('follows1', 'follows', uidCar1, uidCar3, uidRelation1, null, null, SetMode.replace)

    expect(vcd.getRelation(uidRelation1)['rdf_subjects'][0]['uid']).toBe(uidCar1)
    expect(vcd.getRelation(uidRelation1)['rdf_subjects'][0]['type']).toBe('object')
    expect(vcd.getRelation(uidRelation1)['rdf_objects'][0]['uid']).toBe(uidCar3)
    expect(vcd.getRelation(uidRelation1)['rdf_objects'][0]['type']).toBe('object')
    expect(vcd.getRelation(uidRelation1)['rdf_objects'].length).toBe(1)

    // Relation with frameintervals
    let uidPed1 = vcd.addObject('ped1', 'ped', [0, 10])
    let uidPed2 = vcd.addObject('ped2', 'ped', [3, 7])
    let uidRelation2 = vcd.addRelationObjectObject('follows2', 'follow', uidPed2, uidPed1, null, null, [5, 6])

    expect(vcd.getRelation(uidRelation2)['rdf_subjects'][0]['uid']).toBe(uidPed2)
    expect(vcd.getRelation(uidRelation2)['rdf_subjects'][0]['type']).toBe('object')
    expect(vcd.getRelation(uidRelation2)['rdf_objects'][0]['uid']).toBe(uidPed1)
    expect(vcd.getRelation(uidRelation2)['rdf_objects'][0]['type']).toBe('object')
    expect(vcd.getRelation(uidRelation2)['rdf_objects'].length).toBe(1)

    uidRelation2 = vcd.addRelationObjectObject('follows2', 'follow', uidPed2, uidCar1, uidRelation2, null, [5, 6], SetMode.replace)

    expect(vcd.getRelation(uidRelation2)['rdf_subjects'][0]['uid']).toBe(uidPed2)
    expect(vcd.getRelation(uidRelation2)['rdf_subjects'][0]['type']).toBe('object')
    expect(vcd.getRelation(uidRelation2)['rdf_objects'][0]['uid']).toBe(uidCar1)
    expect(vcd.getRelation(uidRelation2)['rdf_objects'][0]['type']).toBe('object')
    expect(vcd.getRelation(uidRelation2)['rdf_objects'].length).toBe(1)
});

test('test_rm_element_data', () => {
    let vcd = new OpenLABEL();

    // Add an object
    let uid1 = vcd.addObject("someName", "");

    // Add two bounding boxes
    let bbox1 = new types.Bbox("box_left", [0, 10, 40, 50]);
    let bbox2 = new types.Bbox("box_right", [20, 20, 25, 25]);
    vcd.addObjectData(uid1, bbox1, [0, 30])
    vcd.addObjectData(uid1, bbox2, [10, 35])

    // The object is therefore defined from 0 to 35
    let fis = vcd.getElementFrameIntervals(ElementType.object, uid1).getDict()
    expect(fis).toStrictEqual([{"frame_start": 0, "frame_end": 35}])

    // Now remove some frames    
    vcd.rmElementDataFromFramesByName(ElementType.object, uid1, "box_left", [5, 15])
    fis = vcd.getElementDataFrameIntervals(ElementType.object, uid1, "box_left").getDict()
    expect(fis).toStrictEqual([{"frame_start": 0, "frame_end": 4}, {"frame_start": 16, "frame_end": 30}])

    // The element stays the same
    fis = vcd.getElementFrameIntervals(ElementType.object, uid1).getDict()
    //expect(fis).toStrictEqual([{"frame_start": 0, "frame_end": 35}])

    // Inside the removed frames, there should not be an element data entry
    let frame_6 = vcd.getFrame(6)
    expect(frame_6['objects'][uid1]).toStrictEqual({})

    let frame_12 = vcd.getFrame(12)
    expect(frame_12['objects'][uid1]['object_data']['bbox'].length).toBe(1)
   
    console.log(vcd.stringify(false))
    

});