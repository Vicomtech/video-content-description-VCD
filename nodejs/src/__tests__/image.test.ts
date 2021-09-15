import { VCD, OpenLABEL } from '../vcd.core'
import * as types from '../vcd.types'
import { openlabel_schema } from '../vcd.schema';


import openlabel100_test_polygon2D from '../../../tests/etc/openlabel100_test_polygon2D.json'
import openlabel100_test_create_image_png from '../../../tests/etc/openlabel100_test_create_image_png.json'
import openlabel100_test_contours from '../../../tests/etc/openlabel100_test_contours.json'

/*function drawBasicImage(classes_colors){
    img = np.zeros((640, 480, 3), np.uint8)

    cv.rectangle(img, (50, 50, 150, 150), classes_colors['class1'], -1)
    cv.circle(img, (110, 110), 50, classes_colors['class2'], -1)
    cv.rectangle(img, (60, 60, 10, 10), (0,0,0), -1)
    cv.line(img, (500, 20), (33, 450), classes_colors['class3'], 10)

    return img
}*/

//TODO: CHECK base64 encode
/*test('test_base64', () => {
    // To avoid adding OpenCV to this test suite, let's bring the chain from the VCD Python API tests
    let payload_b64_str = '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'
    
    // 5.- Insert into VCD
    let vcd = new VCD()
    let vcd_image = new types.Image('labels', payload_b64_str, 'image/png', 'base64')
    let uid = vcd.addObject('', '')
    vcd.addObjectData(uid, vcd_image)

    //console.log(vcd.stringify(false))
    //expect(vcd.stringify(false)).toBe('{"vcd":{"metadata":{"schema_version":"4.3.1"},"objects":{"0":{"name":"","type":"","object_data":{"image":[{"name":"labels","val":"iVBORw0KGgoAAAANSUhEUgAAAeAAAAKACAIAAADLqjwFAAAKu0lEQVR42u3dPW7VYBCGUSe6JWW6NCyDErEvKvaFKFkGDR0lfYiEkABFN8n9+fzOzDkFDRLgAT0a2Z/NtgEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABc0uevb25MASCwzo8/CjRAYp0FGiC0zgINEFpngQYIrbNAA4TWWaABQuss0AChdRZogMQ0CzRAbp0FGiC0zgINEFpngQYIrbNAA4TWWaABQuv84d1PgQZIrLMNGiC0zrmBfv/2o7/U0r58+2QIcE6dH90aH0BgnQUaILTOjw6GCLBvmp+ssw0aILTOAg0QWmeBBgits0ADhNZ585AQYH2dn02zDRogt85VN+jjb6nt9RbizY/vD3f3/rGCOl+kzptbHCdU+LSf1W5Q51fVWaDPLfLJv45egzoL9M5dfvbXV2pQZ4FOSfOTv51MQ9c0n1xngd4zzTIN6izQ0WmWaVBngY5Os0yDOgt0dJplGtT5b0PfJAyvc7k/J6jzxetcdYM+513BcsmzSkOhOl8qzRM36LoLqVUaptV5VqCrN06jYVSdBwW6R900GubUeUqgO3VNo2FInUcEul/RNBom1Hlrfw66a8t8exp2T/O169x8g+69adqjoXedOwd6Qr80GhrXuW2g55RLo6FrnXsGelqzNBpa1nnzNTtAnQPT3HODnrlOWqKhX527BXpypzQamtV5G/u5UUCdw+vcKtBWSBOATnW2QQPqHFrnPoG2PJoDNKvz5pgdIM2ZdW6yQVsbTQP61XlzDxpQ58w6dwi0hdFMoGWdbdCAOofWeav+kNCqeGQyvuiPOtdNsw0aUOfcOgs0oM65Cgfa/Q3zgcZ1tkED6izQAOr8Sl71BgaluVCdbdCAOgv0pXkCZkqoc+8626ABdRZoAHUWaECdG9R5c4oDaFznumm2QQPqLNAA6izQgDr3qLNAA+os0Bfl/QuzQp3b13kreorj4e5ed14+K0NgQpr71XlziwNQZ4EGUGeBBtRZoAHU+Xq86g2UrHPvNNugAXUWaAB1FmhAnQV6Z96/MCXUWaAB1HkfTnEA6WmeWWcbNKDOAg2gznMC7QmY+aDOAg2gzgINqLM6/1H7FIcv9x+ZjCFQtM7SbIMG1FmgrYpmgjqrsw0aUGeBtjCaBqizQAPqPFWTb3E4zmF9pmKa1dkGDaizQFseTQB1VmeBBtRZoK2Qrh3UeR/dPtg/82mhOlOlztI8d4MG1FmgrZOuF3VWZ4HWLFeKOgu0crlGUGeB1i9XhzozO9CNK6bOqPMEh/ZX2O/gnTqTn2Z1tkFPLJo6o84CrdGuAtRZoNVNnVFnhge6dOPUGXUe6DDtgn+XrtBjQ2mmRJ2l2QY9rnrqjDrboOc2OnaVlmbUmcPw6w/MtDSjzgh0XKalGXVGoOMyLc2oMwIdl2lpplya1VmgIzJ9vVLrMuqMQF+4pCf3WpFRZwR6aa//a7cKo85ckP80dkW7QZ0RaECd+3CLA9RZmm3QgDoj0IA6CzSgzgg0oM4CDagzCZziAGlWZxs0oM4INKizOgs0oM4INKDOw3hICHPrLM02aECdEWhQZ3UWaECdEWhAnQUaUGcEGlBnnuWYHfRPszrboAF1RqBBndVZoAF1RqABdeYfHhJCwzpLsw0aUGcEGtRZnQUaUGcEGlBnBBrUmYKc4oDaaVZnGzSgzgg0qLM6I9Cgzgg0oM4INKgzXTjFAZXqLM02aECd2d+NEYA6I9CAOiPQoM4INKDOCDTMSrM6I9Cgzgg0qLM6I9Cgzgg0oM4INHSvszQj0KDOCDSoszoj0KDOCDSgzgg0qDMCDSxOszoj0KDOCDSoszoj0KDOCDSgzgg0qDMINKyvszQj0KDOCDSoszoj0KDOCDSgzgg0qDMINCxOszoj0KDOCDSoszoj0KDOINCgzgg0dK+zNCPQoM4INKizOiPQoM4g0KDOCDSoMwg0qDMCDdKszgg0qDMINOqszgg0qDMINKgzAg3t6yzNCDSoMwg06qzOCDSoMwg0qDMCDeoMAg2L06zOCDSoMwg06qzOCDSoMwg0qDMCDeoMAg3r6yzNCDSoMwg06qzOCDSoMwg0qDMCDeoMAg2L06zOCDSoMwg06qzOCDSoMwg0qDMINN3rLM0INKgzCDTqrM4INKgzCDSoMwg06gwCDeoMAo00qzMCDeoMAo06qzMINOoMAg3qDAJN+zpLMwIN6gwCjTqrMwg06gwCDeoMAo06g0DD4jSrMwg06gwCjTqrMwg06gwCDeoMAo06g0DD+jpLMwg06gwCjTqrMwg06gwCDeoMAo06AwLN4jSrMwg06gwCjTqrMwg06gwCDeoMAk33OkszCDTqDAKNOqszCDTqDAIN6gwCjToDAs3iNKszCDTqDAKNOqszCDTqDAg06gwCjToDAs36OkszCDTqDAKNOqszCDTqDAg06gwCjToDAs3iNKszCDTqDAi0OqszCDTqDAg06gwCTfc6SzMINOoMCLQ6qzMINOoMCDTqDAKNOgMCjToDAi3N6gwCjToDAq3O6gwCjToDAo06g0DTvs7SDAKNOgMCrc7qDAKNOgMCjToDAq3OgECzOM3qDAKNOgMCrc7qDAKNOgMCjToDAq3OgECzvs7SDAKNOgMCrc7qDAJtBOoMCDTqDAi0OgMCzeI0qzMINOoMCLQ6qzMg0OoMCDTqDAh09zpLMwg06gwItDqrMyDQ6gwINOoMCLQ6AwKNOgMCLc3qDAi0OgMCrc7qDAi0OgMCjToDAt2+ztIMCLQ6AwKtzuoMCLQ6AwKNOgMCrc4AAr04zeoMCLQ6AwKtzuoMCLQ6AwKNOgMCrc4AAr2+ztIMCLQ6AwKtzuoMCLQ6Awi0OgMCrc4AAr04zeoMCLQ6AwKtzuoMCLQ6Awi0OgMC3b3O0gwItDoDAq3O6gwItDoDCLQ6AwKtzgACvTjN6gwItDoDTA20OgMCrc4AAq3OgECrM4BA71lnaQYEWp0BpgZanQGBVmcAgVZnQKDVGUCgd0uzOgMCrc4AUwOtzoBAqzOAQKszQN1AO7ABCLQ6Awi0OgPUDbQ6AwKtzgACrc4AdQOtzoBAl0+zOgMCrc4AUwOtzgCJgVZngMRAqzNAYqAd2ABIDLQ6AyQGWp0BEgOtzgCJgVZngMRAqzNAXKAdpwNIDLQ6AyQGWp0BEgOtzgCJgVZngMRAqzNAYqAdpwNIDLQ6AyQGWp0BEgOtzgCJgVZngMRAqzPAmW4T/hDqDJAYaHUGeNJVbnG8/P6GOgMsDfQLG63OAEfsdotDnQGOO0gzQKbV56DVGSDICd+xAwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAqOcXcO/DOJCe2z8AAAAASUVORK5CYII=","mime_type":"image/png","encoding":"base64"}]},"object_data_pointers":{"labels":{"type":"image","frame_intervals":[]}}}}}}')
    
    // 6.- Get and decode
    let od = vcd.getObjectData(uid, 'labels')
    expect(od['mime_type']).toBe('image/png')
    expect(od['encoding']).toBe('base64')
    let payload_b64_read = od['val']
    expect(payload_b64_read).toBe(payload_b64_str)
    let payload_read = btoa(payload_b64_read)    
});*/

/*
test('test_polygon2D', () => {
    let vcd = new OpenLABEL()

    let uid_obj1 = vcd.addObject('someName1', '//Some')

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
    expect(vcd.stringify(false)).toBe(new VCD(openlabel100_test_polygon2D, false).stringify(false))

});

test('test_create_image_png', () => {
    

    // 1.- Create a VCD instance
    let vcd = new OpenLABEL()

    // 2.- Create image
    //let colors = [[125, 32, 64], [98, 12, 65], [12, 200, 190]]
    //let classes = ["class1", "class2", "class3"]
    //let classes_colors = dict(zip(classes, colors))
    let classes_colors = "{'class1': (125, 32, 64), 'class2': (98, 12, 65), 'class3': (12, 200, 190)}"
    let img = drawBasicImage(classes_colors)


    // 3.- Encode
    let  compr_params = [int(cv.IMWRITE_PNG_COMPRESSION), 9]
    result, payload = cv.imencode('.png', img, compr_params)

    expect(result).toBe(true)

    // 4.- Convert to base64
    let payload_b64_bytes = base64.b64encode(payload)  // starts with b' (NOT SERIALIZABLE!)
    let payload_b64_str = str(base64.b64encode(payload), 'utf-8')  // starts with s'

    // 5.- Insert into VCD
    let vcd_image = new types.Image('labels', payload_b64_str, 'image/png', 'base64')
    let uid = vcd.addObject('', '')
    vcd.addObjectData(uid, vcd_image)

    // 6.- Get and decode
    let od = vcd.getObjectData(uid, 'labels')
    let mime_type = od['mime_type']
    let encoding = od['encoding']
    let payload_b64_read = od['val']
    let payload_read = base64.b64decode(payload_b64_read)
    expect(mime_type).toBe('image/png')
    expect(encoding).toBe('base64')
    let img_dec = cv.imdecode(np.frombuffer(payload_read, dtype=np.uint8), 1)

    // Check equals
    let diff_val = np.sum(cv.absdiff(img, img_dec))

    expect(diff_val).toBe(0)


    expect(vcd.stringify(false)).toBe(new VCD(openlabel100_test_create_image_png, false).stringify(false))

});

test('test_contours', () => {
    let vcd = new OpenLABEL()

    expect(vcd.stringify(false)).toBe(new VCD(openlabel100_test_contours, false).stringify(false))

});*/