import { VCD, ElementType, RDF } from '../vcd.core'
import * as types from '../vcd.types'
import { v4 as uuidv4 } from 'uuid'

test('test_uuid_usage_explicit_1', () => {
    let vcd = new VCD()

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
    let vcd = new VCD()
    
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