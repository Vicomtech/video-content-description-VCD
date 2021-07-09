import { VCD, ElementType, OpenLABEL, RDF } from '../vcd.core'
import * as types from '../vcd.types'
import { v4 as uuidv4 } from 'uuid'

import openlabel030_test_uid_types from '../../../tests/etc/openlabel030_test_uid_types.json'


test('test_uid_types', () => {
    // 1.- Create a VCD instance
    let vcd = new OpenLABEL()

    // We can add elements and get UIDs as strings
    let uid0 = vcd.addObject("Mike", "Person")
    expect(typeof uid0 === "string").toBe(true)
    expect(uid0).toBe('0')


    //We can also specify which UID we will like our elements to have
    //We can use integers and stringified integers
    //Response is always string
    let uid1 = vcd.addObject('George', 'Person', null,"1")  //integer
    let uid2 = vcd.addObject("Susan", "Person", null,"2")  // stringified integer    
    expect(vcd.has(ElementType.object,uid1)).toBe(true)
    expect(vcd.has(ElementType.object,uid2)).toBe(true)
    expect(uid1).toBe("1")
    expect(uid2).toBe("2")


    //In general, the user can use integers or stringified integers for all public functions
    vcd.addObjectData(2, new types.Boolean("checked", true))
    vcd.addObjectData("2", new types.Boolean("double-checked", true))
    
    //Same happens with ontology uids
    let ont_uid_0 = vcd.addOntology("http://www.vicomtech.org/viulib/ontology")
    expect(typeof ont_uid_0 === "string").toBe(true)

    let uid3 = vcd.addObject("Mark", "#Pedestrian", null,null,ont_uid_0)
    let uid4 = vcd.addObject("Rose", "#Pedestrian",null,null, 0)
    expect(vcd.getObject(uid3)['ontology_uid']).toBe('0')
    expect(vcd.getObject(uid4)['ontology_uid']).toBe('0')


    //Check equal to reference JSON
    expect(vcd.stringify(false)).toBe(new VCD(openlabel030_test_uid_types, false).stringify(false))
})

test('test_uuid_usage_explicit_1', () => {
    let vcd = new OpenLABEL()

    // Create an UUID and inject it into VCD
    let uuid1 = uuidv4()

    // Adding an object and specifying its uid as an UUID, from here on, VCD will use UUID
    vcd.addObject('marcos', 'person', null, uuid1)
    let object = vcd.getObject(uuid1)
    expect(object['name']).toBe('marcos')    

    let uid2 = vcd.addObject('orti', 'person', null)
    expect(/^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/g.test(uid2)).toBe(true) // vcd should use UUID internally

    //console.log(vcd.stringify(false))
})

test('test_uuid_usage_explicit_2', () => {
    let vcd = new OpenLABEL()
    
    // We can ask vcd to use UUIDs
    vcd.setUseUUID(true)       
    
    let uid1 = vcd.addObject('marcos', 'person')
    let object = vcd.getObject(uid1)  // we can use this UUID to search info
    expect(object['name']).toBe('marcos')    
    expect(/^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/g.test(uid1)).toBe(true) // vcd should use UUID internally

    let uid2 = vcd.addObject('orti', 'person')
    expect(/^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/g.test(uid2)).toBe(true) // vcd should use UUID internally

    //console.log(vcd.stringify(false))
})