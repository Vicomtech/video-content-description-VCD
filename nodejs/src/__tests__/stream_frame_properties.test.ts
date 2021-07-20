import fs from 'fs'
import { VCD,OpenLABEL, ElementType, RDF, StreamType } from '../vcd.core'
import * as types from '../vcd.types'



import openlabel030_test_create_streams_simple from '../../../tests/etc/openlabel030_test_create_streams_simple.json'




test('test_create_streams_simple', () => {
    // This example shows how to introduce Stream (Intrinsics, Extrinsics), Sync and Odometry information
    // Fully detailed examples will be introduced for specific datasets such as KITTI tracking and nuScenes
    let vcd = new OpenLABEL()

    // FIRST: define all the involved coordinate systems
    vcd.addCoordinateSystem("odom", types.CoordinateSystemType.scene_cs)
    vcd.addCoordinateSystem("vehicle-iso8855", types.CoordinateSystemType.local_cs,
                              "odom",
                              new types.PoseData(
                                  [1.0, 0.0, 0.0, 0.0,
                                       0.0, 1.0, 0.0, 0.0,
                                       0.0, 0.0, 1.0, 0.0,
                                       0.0, 0.0, 0.0, 1.0],
                                  types.TransformDataType.matrix_4x4)

    )

    //SECOND: Add the streams
    vcd.addStream('Camera1',
                   './somePath/someVideo1.mp4',
                   'Description 1',
                   StreamType.camera)
    vcd.addStream('Camera2',
                   './somePath/someVideo2.mp4',
                   'Description 2',
                   StreamType.camera)

    //THIRD: Generic stream properties can be added...
    //... for the Stream
    vcd.addStreamProperties("Camera1",
                             {"someProperty": "someValue"})
    //... for the Stream at specific frame number
    vcd.addStreamProperties("Camera1",
                             {"somePropertyForThisFrame": "someValue"},
                              null,
                              new types.StreamSync(2,null,null,null,null)
                              )

    // Sensor-domain-specific information such as INTRINSICS, EXTRINSICS and ODOMETRY can be added as well
    // See schema.py for more details on Coordinate Systems
    // Extrinsics are added as coordinate systems
    vcd.addStreamProperties("Camera1",
                            null,
                            new types.IntrinsicsPinhole(
                                640,
                                480,
                                [1000.0, 0.0, 500.0, 0.0,
                                                    0.0, 1000.0, 500.0, 0.0,
                                                    0.0, 0.0, 1.0, 0.0],
                                null,null
                            ),
                            )
    vcd.addCoordinateSystem("Camera1", types.CoordinateSystemType.sensor_cs,
                            "vehicle-iso8855",
                            new types.PoseData(
                                [1.0, 0.0, 0.0, 0.0,
                                        0.0, 1.0, 0.0, 0.0,
                                        0.0, 0.0, 1.0, 0.0,
                                        0.0, 0.0, 0.0, 1.0],
                                types.TransformDataType.matrix_4x4)
                            )

    // Sync info can be added as a shift between the master vcd frame count and each of the sensors
    // e.g. Camera2 may have started 3 frames after Camera1, therefore, to label Elements for Camera2, we can use
    // frame_shift=3 for Camera2
    vcd.addStreamProperties("Camera2",
                            null,
                            new types.IntrinsicsPinhole(
                                    640,
                                    480,
                                    [1000.0, 0.0, 500.0, 0.0,
                                                        0.0, 1000.0, 500.0, 0.0,
                                                        0.0, 0.0, 1.0, 0.0],
                                    null,
                                    null
                                ),
                            new types.StreamSync(null,
                                                null,
                                                null,
                                                3,
                                                null
                                )
                            )
    vcd.addCoordinateSystem("Camera2", types.CoordinateSystemType.sensor_cs,
                                "vehicle-iso8855",
                                new types.PoseData(
                                    [1.0, 0.0, 0.0, 0.0,
                                        0.0, 1.0, 0.0, 0.0,
                                        0.0, 0.0, 1.0, 0.0,
                                        0.0, 0.0, 0.0, 1.0],
                                    types.TransformDataType.matrix_4x4)
                                )
    
    // Let's suppose we want to add a master timestamp coming from a GPS or LIDAR sensor
    // Let's create here some dummy timestamps
    let t_start= new Date("2020-04-11T12:00:01");
    let t_end= new Date("2020-04-11T12:00:31");
    
    let t_diff = (Math.abs(Number(t_end) - Number(t_start)))/1000;
    let steps = 10
    let t_step = t_diff / steps
    
    let t_data = []
    let t_start_seconds=t_start.getSeconds();
    let currentSeconds;
    let currentDate;
    for(let i in Array.from(Array(steps).keys())){
        currentDate=new Date(t_start)
        currentSeconds=Number(i)*t_step+t_start_seconds;
        currentDate.setSeconds(currentSeconds);
        t_data.push(currentDate)
    }
 

    let frame_num=0;
    let dateStr;
    for (let t of t_data){
        dateStr =t.getFullYear()+'-'+("00" + (t.getMonth() + 1)).slice(-2) + "-" +("00" + t.getDate()).slice(-2)+ " " +("00" + t.getHours()).slice(-2) + ":" +("00" + t.getMinutes()).slice(-2) + ":" +("00" + t.getSeconds()).slice(-2);      
        vcd.addFrameProperties(frame_num,new String(dateStr));
        frame_num++;
    }

    // Additionally, we may want to introduce timestamping, intrinsics and extrinsics specific for each Sensor
    // and for each frame, for increased detail
    

    frame_num=0;
    for (let t of t_data){
        dateStr =t.getFullYear()+'-'+("00" + (t.getMonth() + 1)).slice(-2) + "-" +("00" + t.getDate()).slice(-2)+ " " +("00" + t.getHours()).slice(-2) + ":" +("00" + t.getMinutes()).slice(-2) + ":" +("00" + t.getSeconds()).slice(-2);      
        vcd.addStreamProperties("Camera1",
                                    null,
                                    new types.IntrinsicsPinhole(
                                        640,
                                        480,
                                        [1001.0, 0.0, 500.0, 0.0,
                                                            0.0, 1001.0, 500.0, 0.0,
                                                            0.0, 0.0, 1.0, 0.0],
                                        null,
                                        null
                                    ),
                                    new types.StreamSync(
                                    frame_num,
                                    frame_num + 1,  // Camera1's frames are shifted wrt to master count
                                    new String(dateStr), //t.toString(),
                                    null,
                                    null
                                        )
                                    )
        vcd.addTransform(frame_num,
                         new types.Transform("vehicle-iso8855",
                                              "Camera1",
                                               new types.TransformData(
                                                        [1.0, 0.0, 0.0, 0.1,
                                                                0.0, 1.0, 0.0, 0.1,
                                                                0.0, 0.0, 1.0, 0.0,
                                                                0.0, 0.0, 0.0, 1.0],
                                                        types.TransformDataType.matrix_4x4)
                                                    )
                        )
        frame_num++;
    }   

    // Odometry information is also included as frame_properties
    // Odometry must be provided as pose_lcs_wrt_wcs (i.e. Local Coordinate System wrt World Coordinate System)
    // in the form of pose 4x4 matrices.
    // As additional properties you can include raw GPS/IMU for instance
    vcd.addTransform(6, new types.Transform(
        "odom",
        "vehicle-iso8855",
        new types.TransformData(
            [1.0, 0.0, 0.0, 20.0,
                 0.0, 1.0, 0.0, 20.0,
                 0.0, 0.0, 1.0, 0.0,
                 0.0, 0.0, 0.0, 1.0],
            types.TransformDataType.matrix_4x4),
        {"raw_gps_data":[49.011212804408, 8.4228850417969, 112.83492279053, 0.022447,1e-05,
                                               -1.2219096732051, -3.3256321640686, 1.1384311814592, 3.5147680214713,
                                               0.037625160413037, -0.03878884255623, -0.29437452763793,
                                               0.037166856911681, 9.9957015129717, -0.30581030960531,
                                               -0.19635662515203, 9.9942128010936, -0.017332142869546,
                                               0.024792163815438, 0.14511808479348, -0.017498934149631,
                                               0.021393359392165, 0.14563031426063, 0.49229361157748,
                                               0.068883960397178, 4, 10, 4, 4, 0],
        "status":"interpolated"},  // we can add any thing (it is permitted by VCD schema)
    ))


    expect(Object.keys(vcd.getStreams()).length).toBe(2)
    expect(vcd.hasStream('Camera1')).toBe(true)
    expect(vcd.getStream('Camera1')['uri']).toBe('./somePath/someVideo1.mp4')
    expect(vcd.getStream('Camera1')['description']).toBe('Description 1')
    expect(vcd.getStream('Camera1')['type']).toBe('camera')
    expect(vcd.getStream('Non-Valid_Stream')).toBe(null)

    expect(Object.keys(vcd.getCoordinateSystems()).length).toBe(4)
    expect(vcd.hasCoordinateSystem('vehicle-iso8855')).toBe(true)
    expect(vcd.getCoordinateSystem('vehicle-iso8855')['parent']).toBe('odom')
    expect(vcd.getCoordinateSystem('Non-existing-Coordinate')).toBe(null)

 
    expect(vcd.stringify(false)).toBe(new VCD(openlabel030_test_create_streams_simple, false).stringify(false))



});

