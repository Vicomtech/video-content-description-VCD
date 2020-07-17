import { VCD } from '../vcd.core'
import * as types from '../vcd.types'

test('test_polygon2D', () => {
    let vcd = new VCD()

    let uid_obj1 = vcd.addObject('someName1', '#Some')

    // Add a polygon with SRF6DCC encoding (list of strings)
    let poly1 = new types.Poly2d('poly1', [5, 5, 10, 5, 11, 6, 11, 8, 9, 10, 5, 10, 3, 8, 3, 6, 4, 5], types.Poly2DType.MODE_POLY2D_SRF6DCC, false)
    expect(poly1.data['name']).toBe('poly1')
    expect(poly1.data['mode']).toBe(types.Poly2DType[types.Poly2DType.MODE_POLY2D_SRF6DCC])
    expect(poly1.data['closed']).toBe(false)    
    expect(poly1.data['val']).toStrictEqual(['5', '5', '1', 'mBIIOIII'])
    vcd.addObjectData(uid_obj1, poly1)

    let poly2 = new types.Poly2d('poly2', [5, 5, 10, 5, 11, 6, 11, 8, 9, 10, 5, 10, 3, 8, 3, 6, 4, 5], types.Poly2DType.MODE_POLY2D_ABSOLUTE, false)
    vcd.addObjectData(uid_obj1, poly2)
    expect(poly2.data['name']).toBe('poly2')
    expect(poly2.data['mode']).toBe(types.Poly2DType[types.Poly2DType.MODE_POLY2D_ABSOLUTE])
    expect(poly2.data['closed']).toBe(false)  
    expect(poly2.data['val']).toStrictEqual([5, 5, 10, 5, 11, 6, 11, 8, 9, 10, 5, 10, 3, 8, 3, 6, 4, 5])  

    //console.log(vcd.stringify(false))
    expect(vcd.stringify(false)).toBe('{"vcd":{"frames":{},"schema_version":"4.3.0","frame_intervals":[],"objects":{"0":{"name":"someName1","type":"#Some","object_data":{"poly2d":[{"name":"poly1","val":["5","5","1","mBIIOIII"],"mode":"MODE_POLY2D_SRF6DCC","closed":false},{"name":"poly2","val":[5,5,10,5,11,6,11,8,9,10,5,10,3,8,3,6,4,5],"mode":"MODE_POLY2D_ABSOLUTE","closed":false}]},"object_data_pointers":{"poly1":{"type":"poly2d","frame_intervals":[]},"poly2":{"type":"poly2d","frame_intervals":[]}}}}}}')
});