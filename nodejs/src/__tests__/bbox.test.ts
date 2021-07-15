import fs from 'fs'
import { VCD,OpenLABEL, ElementType, RDF } from '../vcd.core'
import * as types from '../vcd.types'



import openlabel030_test_bbox_simple from '../../../tests/etc/openlabel030_test_bbox_simple.json'
import openlabel030_test_bbox_simple_attributes from '../../../tests/etc/openlabel030_test_bbox_simple_attributes.json'
import openlabel030_test_bbox_simple_extreme_points from '../../../tests/etc/openlabel030_test_bbox_simple_extreme_points.json'

test('test_bbox_simple', () => {

    let openlab = new OpenLABEL();
   
    //Basic objects
    let car1 = openlab.addObject("car1", "Car")
    let car2 = openlab.addObject("car2", "Car")
    let car3 = openlab.addObject("car3", "Car")
    let bus1 = openlab.addObject("bus1", "Bus")
    let zebracross1 = openlab.addObject("zebracross1", "ZebraCross")
    let semaphore1 = openlab.addObject("semaphore1","Semaphore")
    let semaphore2 = openlab.addObject("semaphore2","Semaphore")

    //Bounding boxes
    openlab.addObjectData(car1, new types.Bbox("shape", [410 + 52/2, 280 + 47/2, 52, 47]))
    openlab.addObjectData(bus1, new types.Bbox("shape", [468 + 56/2, 266 + 47/2, 56, 47]))
    openlab.addObjectData(car2, new types.Bbox("shape", [105 + 96/2, 280 + 34/2, 96, 34]))
    openlab.addObjectData(car3, new types.Bbox("shape", [198 + 63/2, 280 + 42/2, 63, 42]))
    openlab.addObjectData(semaphore1, new types.Bbox("shape", [167 + 38/2, 80 + 80/2, 38, 81]))
    openlab.addObjectData(semaphore2, new types.Bbox("shape", [885 + 32/2, 145 + 63/2, 32, 63]))
    openlab.addObjectData(zebracross1, new types.Bbox("shape",[291 + 524/2, 358 + 55/2, 524, 55]))

    
   
    expect(openlab.stringify(false)).toBe(new VCD(openlabel030_test_bbox_simple, false).stringify(false))


});

test('test_bbox_simple_attributes', () => {
    let openlab = new OpenLABEL()

    // Basic objects
    let car1 = openlab.addObject("car1", "Car")
    let car2 = openlab.addObject("car2", "Car")
    let car3 = openlab.addObject("car3", "Car")
    let bus1 = openlab.addObject("bus1", "Bus")
    let zebracross1 = openlab.addObject("zebracross1", "ZebraCross")
    let semaphore1 = openlab.addObject("semaphore1", "Semaphore")
    let semaphore2 = openlab.addObject("semaphore2", "Semaphore")

    // Bounding boxes + scores + status
    let bbox = new types.Bbox("shape", [410 + 52/2, 280 + 47/2, 52, 47])
    bbox.addAttribute(new types.Num("confidence", 0.99))
    bbox.addAttribute(new types.Boolean("interpolated", false))
    openlab.addObjectData(car1, bbox)

    bbox = new types.Bbox("shape", [468 + 56/2, 266 + 47/2, 56, 47])
    bbox.addAttribute(new types.Num("confidence", 0.78))
    bbox.addAttribute(new types.Boolean("interpolated", false))
    openlab.addObjectData(bus1,bbox)

    bbox = new types.Bbox("shape", [105 + 96/2, 280 + 34/2, 96, 34])
    bbox.addAttribute(new types.Num("confidence", 0.75))
    bbox.addAttribute(new types.Boolean("interpolated", false))
    openlab.addObjectData(car2,bbox)

    bbox = new types.Bbox("shape", [198 + 63/2, 280 + 42/2, 63, 42])
    bbox.addAttribute(new types.Num("confidence", 0.81))
    bbox.addAttribute(new types.Boolean("interpolated",false))
    openlab.addObjectData(car3, bbox)

    bbox = new types.Bbox("shape",[167 + 38/2, 80 + 80/2, 38, 81])
    bbox.addAttribute(new types.Num("confidence", 0.94))
    bbox.addAttribute(new types.Boolean("interpolated", false))
    openlab.addObjectData(semaphore1, bbox)

    bbox = new types.Bbox("shape", [885 + 32/2, 145 + 63/2, 32, 63])
    bbox.addAttribute(new types.Num("confidence", 0.95))
    bbox.addAttribute(new types.Boolean("interpolated", false))
    openlab.addObjectData(semaphore2, bbox)

    bbox = new types.Bbox("shape", [291 + 524/2, 358 + 55/2, 524, 55])
    bbox.addAttribute(new types.Num("confidence", 0.99))
    bbox.addAttribute(new types.Boolean("interpolated", false))
    openlab.addObjectData(zebracross1, bbox)

    // Object attributes
    let color = new types.Text("color", "white")
    let brand = new types.Text("model", "unknown")
    openlab.addObjectData(car1, color)
    openlab.addObjectData(car1, brand)

    let truncated = new types.Boolean("truncated", true)
    openlab.addObjectData(car2, truncated)

    let green = new types.Text("status", "Green")
    green.addAttribute(new types.Num("confidence", 0.99))
    openlab.addObjectData(semaphore1,green)

    green = new types.Text("status", "Green")
    green.addAttribute(new types.Num("confidence", 0.66))
    openlab.addObjectData(semaphore2, green)


    expect(openlab.stringify(false)).toBe(new VCD(openlabel030_test_bbox_simple_attributes, false).stringify(false))

});

test('test_bbox_simple_extreme_points', () => {
    // 1.- Create VCD
    let openlab = new OpenLABEL()

    //Basic objects
    let car1 = openlab.addObject("car1", "Car")
    let car2 = openlab.addObject("car2", "Car")
    let car3 = openlab.addObject("car3", "Car")
    let bus1 = openlab.addObject("bus1", "Bus")
    let zebracross1 = openlab.addObject("zebracross1", "ZebraCross")
    let semaphore1 = openlab.addObject("semaphore1", "Semaphore")
    let semaphore2 = openlab.addObject("semaphore2", "Semaphore")

    //Bounding boxes
    openlab.addObjectData(car1,
        new types.Bbox("shape", [410 + 52 / 2, 280 + 47 / 2, 52, 47]))
    openlab.addObjectData(bus1,
        new types.Bbox("shape", [468 + 56 / 2, 266 + 47 / 2, 56, 47]))
    openlab.addObjectData(car2,
        new types.Bbox("shape", [105 + 96 / 2, 280 + 34 / 2, 96, 34]))
    openlab.addObjectData(car3,
        new types.Bbox("shape", [198 + 63 / 2, 280 + 42 / 2, 63, 42]))
    openlab.addObjectData(semaphore1,
        new types.Bbox("shape", [167 + 38 / 2, 80 + 80 / 2, 38, 81]))
    openlab.addObjectData(semaphore2,
        new types.Bbox("shape", [885 + 32 / 2, 145 + 63 / 2, 32, 63]))
    openlab.addObjectData(zebracross1,
        new types.Bbox("shape", [291 + 524 / 2, 358 + 55 / 2, 524, 55]))

   
    expect(openlab.stringify(false)).toBe(new VCD(openlabel030_test_bbox_simple_extreme_points, false).stringify(false))

});

