import fs from 'fs'
import { VCD,OpenLABEL, ElementType, RDF, ResourceUID } from '../vcd.core'
import * as types from '../vcd.types'

import openlabel100_test_create_openlabel from '../../../tests/etc/openlabel100_test_create_openlabel.json'
import openlabel100_test_openlabel_bounding_box_points from '../../../tests/etc/openlabel100_test_openlabel_bounding_box_points.json'
import openlabel100_test_openlabel_external_data_resourc from '../../../tests/etc/openlabel100_test_openlabel_external_data_resource.json'
import vcd431_test_contours from '../../../tests/etc/vcd431_test_contours.json'


test('test_create_openlabel', () => {
    
    /*
    This test shows how to create a new OpenLABEL object.
    :return:
    */
    let openlabel = new OpenLABEL();
    openlabel.addObject("object1", "car")
    openlabel.addObject("object2", "pedestrian")

    expect(openlabel.stringify(false)).toBe(new VCD(openlabel100_test_create_openlabel, false).stringify(false))


});


test('test_openlabel_bounding_box_points', () => {
    let openlabel = new OpenLABEL();
    let uid1 = openlabel.addObject("object1", "van")
    openlabel.addObjectData(uid1, new types.Bbox(
            "enclosing_rectangle",
            [182, 150, 678, 466]))
    openlabel.addObjectData(uid1, new types.Poly2d(
            "extreme_points",
            [424, 150, 860, 456, 556, 616, 182, 339],
            types.Poly2DType.MODE_POLY2D_ABSOLUTE,
            true))
    expect(openlabel.stringify(false)).toBe(new VCD(openlabel100_test_openlabel_bounding_box_points, false).stringify(false))

});

test('test_openlabel_external_data_resource', () => {
    let openlabel = new OpenLABEL();

    let res_uid = openlabel.addResource('../resources/xodr/multi_intersections.xodr')
    openlabel.addObject("road1", "road",null,null,null,null,null, new ResourceUID(res_uid, 217))
    openlabel.addObject("lane1", "lane",null,null,null,null,null, new ResourceUID(res_uid, 3))

    expect(openlabel.stringify(false)).toBe(new VCD(openlabel100_test_openlabel_external_data_resourc, false).stringify(false))

});

