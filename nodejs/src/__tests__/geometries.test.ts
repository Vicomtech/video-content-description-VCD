import { VCD, ElementType, SetMode, StreamType, OpenLABEL } from '../vcd.core'
import * as types from '../vcd.types'
import * as utils from '../vcd.utils'
import openlabel030_test_intrinsics from '../../../tests/etc/openlabel030_test_intrinsics.json'
import openlabel030_test_poses from '../../../tests/etc/openlabel030_test_poses.json'
import openlabel030_test_transforms from '../../../tests/etc/openlabel030_test_transforms.json'
import openlabel030_test_cuboids from '../../../tests/etc/openlabel030_test_cuboids.json'


test('test_intrinsics', () => {
    // This tests aims to demonstrate that different intrinsics structures
    // can be used at VCD, including standard intrinsic_pinhole, intrinsic_fisheye,
    // a custom format for user-defined structures
    
    // Create VCD
    let vcd = new OpenLABEL()

    // Custom intrinsics
    vcd.addStream("CAM_CUSTOM", "", "Camera custom", StreamType.camera)
    vcd.addStreamProperties("CAM_CUSTOM", null, new types.IntrinsicsCustom(
        {"custom_property1":"Some text1", 
        "custom_property2":1200.0, 
        "custom_property3":[100.0, 100.0]}
    ))

    // Pinhole
    vcd.addStream("CAM_PINHOLE", "", "Camera pinhole", StreamType.camera)
    vcd.addStreamProperties("CAM_PINHOLE", null, new types.IntrinsicsPinhole(
        640, 480, [1000.0, 0.0, 500.0, 0.0, 0.0, 1000.0, 500.0, 0.0, 0.0, 0.0, 1.0, 0.0], null,
        {"custom_property1":0.99}
    ))

    // Fisheye
    vcd.addStream("CAM_FISHEYE", "", "Camera fisheye", StreamType.camera)
    vcd.addStreamProperties("CAM_FISHEYE", null, new types.IntrinsicsFisheye(
        1280, 1080, [333.437012, 0.307729989, 2.4235599, 11.0495005], null, 0.0, 0.0, 0.0, 0.0,
        {"custom_property1":0.0}
    ))
    
    expect(vcd.stringify(false)).toBe(new VCD(openlabel030_test_intrinsics, false).stringify(false))
});

test('test_poses', () => {
    // This test aims to show how to create and add extrinsic information of streams
    // In particular, how different pose formats can be used (e.g. matrix, or list of values)

    // Create VCD
    let vcd = new OpenLABEL()

    // Create reference
    vcd.addCoordinateSystem("base", types.CoordinateSystemType.local_cs)

    // Create camera 1 and compose a pose as a 4x4 matrix
    vcd.addStream("CAM_1", "", "Camera 1", StreamType.camera)
    let pitch_rad = (10.0 * Math.PI) / 180.0
    let yaw_rad = (0.0 * Math.PI) / 180.0
    let roll_rad = (0.0 * Math.PI) / 180.0
    let R_scs_wrt_lcs =  utils.euler2R([yaw_rad, pitch_rad, roll_rad])  //default is ZYX
    let C_lcs = [[2.3],  //frontal part of the car
                [0.0],  // centered in the symmetry axis of the car
                [1.3]] // at some height over the ground

    let P_scs_wrt_lcs = utils.createPose(R_scs_wrt_lcs, C_lcs)
     
   vcd.addCoordinateSystem("CAM_1", 
        types.CoordinateSystemType.sensor_cs, 
        "base", 
        (new types.PoseData(
            P_scs_wrt_lcs.reduce((accumulator, value) => accumulator.concat(value), []),
            types.TransformDataType.matrix_4x4)
        )
    )
    // Create camera 2 and add rotation and traslation instead of pose
    vcd.addStream("CAM_2", "", "Camera 2", StreamType.camera)
    vcd.addCoordinateSystem("CAM_2", 
        types.CoordinateSystemType.sensor_cs, 
        "base", 
        (new types.PoseData(
            [yaw_rad, pitch_rad, roll_rad, C_lcs.reduce((accumulator, value) => accumulator.concat(value), [])],
            types.TransformDataType.euler_and_trans_6x1,
            {"sequence":"ZYX"}
        )))

    //expect(vcd.stringify(false)).toBe(new VCD(openlabel030_test_poses, false).stringify(false))
});

/*test('test_transforms', () => {
    // Transforms are the same as Poses, but applied for a given frame
    let vcd = new OpenLABEL()

    // Create reference, base or local coordinate system
    vcd.addCoordinateSystem("base", types.CoordinateSystemType.local_cs)
    vcd.addCoordinateSystem("world", types.CoordinateSystemType.scene_cs)

    // Odometry entries would be like this one:
    vcd.addTransform(10, new types.Transform(
        "base", "world", 
        new types.TransformData(
            [1.0, 0.0, 0.0, 0.1,
                0.0, 1.0, 0.0, 0.1,
                0.0, 0.0, 1.0, 0.0,
                0.0, 0.0, 0.0, 1.0]
        ,types.TransformDataType.matrix_4x4)
    ))

    // Nevertheless in VCD 4.3.2 it is possible to customize the format of the transform
    vcd.addTransform(11, new types.Transform(
        "base", "world", 
        new types.TransformData(
            [0.0, 0.0, 0.0, 1.0, 1.0, 0.0],
            types.TransformDataType.euler_and_trans_6x1),
        {"custom_property1":"0.9",
         "custom_property2":"Some tag"})
            
    )
    
    
    expect(vcd.stringify(false)).toBe(new VCD(openlabel030_test_transforms, false).stringify(false))

});*/

test('test_cuboids', () => {
    // This test shows how to represent cuboids in various forms
    let vcd = new OpenLABEL()

    // (x, y, z, rx, ry, rz, sx, sy, sz), note (x,y,z) is the center point of the cuboid
    // the coordinates are expressed wrt to the declared coordinate_system
    vcd.addCoordinateSystem("vehicle-iso8855", types.CoordinateSystemType.local_cs)
    let uid1 = vcd.addObject("car1", "car")
    let cuboid1 = new types.Cuboid(
        "box3D",
        [0.0, 20.0, -0.85, 0, 0.3, 0, 1.5, 4.5, 1.7],
        "vehicle-iso8855"
    )
    vcd.addObjectData(uid1, cuboid1)

    let uid2 = vcd.addObject("car2", "car")
    let cuboid2 = new types.Cuboid(
        "box3D", 
        null,
        "vehicle-iso8855",
        {"quaternion": [1.0, 0.0, 0.0, 0.0], "traslation": [0.0, 10.0, -0.85], "size": [1.5, 4.5, 1.7]}
    )
    vcd.addObjectData(uid2, cuboid2)

    expect(vcd.stringify(false)).toBe(new VCD(openlabel030_test_cuboids, false).stringify(false))

});