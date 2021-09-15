import fs from 'fs'
import { VCD,OpenLABEL, ElementType, RDF } from '../vcd.core'
import * as types from '../vcd.types'



import openlabel100_test_create_mesh from '../../../tests/etc/openlabel100_test_create_mesh.json'
import openlabel100_test_create_mesh_with_API_frames from '../../../tests/etc/openlabel100_test_create_mesh_with_API_frames.json'


function getMeshGeometryAsString(vertexMap, edgeMap, areaMap){
    let result = "[[";

    for(let vertex in vertexMap){
        let val=vertexMap[vertex];
        result += "[";
        for(let i in Array.from(Array(val.length).keys())){
            result += val[i] + ","
        }
        result += "],"
    }
    result += "],["

    for(let edge in edgeMap){
        let val = edgeMap[edge]
        result += "["
        for(let i in Array.from(Array(val.length).keys())){
            result += val[i] + ","
        }
        result += "],"
    }
    result += "],["
 
    for(let area in areaMap){
        let val = areaMap[area]
        result += "["
        for(let i in Array.from(Array(val.length).keys())){
            result += val[i] + ","
        }
        result += "],"
    }
    result += "]]"


    //Clean-out commas
    let re = /\,]/gi;
    let result_clean = result.replace(re, "]")

    return result_clean


}

function generateDefaultMesh(rows,cols){
    //Add vertex
    let points = []

    for(let i in Array.from(Array(rows+1).keys())){
       for(let j in Array.from(Array(cols+1).keys())){
            points.push([j,i,0])
       }
    }


    //Add edges
    let lines = []

    for(let u in Array.from(Array(rows+1).keys())){
        for(let v in Array.from(Array(cols).keys())){
            lines.push([Number(v) + Number(u)*(cols+1), Number(v) + 1 +Number(u) *(cols+1)])
        }
     }
    
     for(let u in Array.from(Array(rows).keys())){
        for(let v in Array.from(Array(cols+1).keys())){
            lines.push([Number(v) + Number(u)*(cols+1), Number(v)+cols+1+Number(u)*(cols+1)])
        }
     }


    //Add areas
    let areas = []

    for(let i in Array.from(Array(rows).keys())){
        for(let j in Array.from(Array(cols).keys())){
            areas.push([Number(i)* cols + Number(j),
                          Number(i)* cols + Number(j) + cols,
                          Number(i)* (cols + 1) + Number(j) + cols * (rows + 1),
                          Number(i)* (cols + 1) + Number(j) + cols * (rows + 1) + 1])
                        
        }
     }
 
    //Create string
    let string_mesh = getMeshGeometryAsString(points, lines, areas)
    
    return string_mesh
}

test('test_create_default_mesh_string', () => {

    let rows = 2
    let cols = 4
    let val_4x2 = generateDefaultMesh(rows, cols)
    let expected_val_4x2 = "[[[0,0,0],[1,0,0],[2,0,0],[3,0,0],[4,0,0],[0,1,0],[1,1,0],[2,1,0],[3,1,0],[4,1,0],"+ 
                           "[0,2,0],[1,2,0],[2,2,0],[3,2,0],[4,2,0]],[[0,1],[1,2],[2,3],[3,4],[5,6],[6,7]," +
                           "[7,8],[8,9],[10,11],[11,12],[12,13],[13,14],[0,5],[1,6],[2,7],[3,8],[4,9]," +
                           "[5,10],[6,11],[7,12],[8,13],[9,14]],[[0,4,12,13],[1,5,13,14]," +
                           "[2,6,14,15],[3,7,15,16],[4,8,17,18],[5,9,18,19],[6,10,19,20]," +
                           "[7,11,20,21]]]"
    
    
    expect(val_4x2).toBe(expected_val_4x2)


});

test('test_create_mesh', () => {
    
    //1.- Create a VCD instance
    let openlab = new OpenLABEL()
    openlab.addCoordinateSystem('world', types.CoordinateSystemType.local_cs)

     //Mesh sample representation
     //
     //P0 L0   P1   L4   P4
     // *--------*--------*
     //|        |        |
     //|L3  A0  |L1  A1  |L5
     //|        |        |
     // *--------*--------*
     //P3  L2   P2  L6   P5
     //
     //V0  [A0,A1]

     let mesh1 = new types.Mesh("mesh1",'world')

    //Vertex
    // P0
    let p0 = new types.Point3d("Vertex", [25, 25, 0])
    p0.addAttribute(new types.Text("T Shape", "line_ending_type"))
    let p0_id = mesh1.addVertex(p0)
    // P1
    let p1 =new types.Point3d("Vertex", [26, 25, 0])
    p1.addAttribute(new types.Text("I Shape", "line_ending_type"))
    mesh1.addVertex(p1)
    // P2
    let p2 = new types.Point3d("Vertex", [26, 26, 0])
    p2.addAttribute(new types.Text("U Shape", "line_ending_type"))
    mesh1.addVertex(p2)
    // P3
    let p3 = new types.Point3d("Vertex", [25, 26, 0])
    p3.addAttribute(new types.Text("C Shape", "line_ending_type"))
    mesh1.addVertex(p3)
    // P4
    let p4 = new types.Point3d("Vertex", [27, 25, 0])
    p4.addAttribute(new types.Text("T Shape", "line_ending_type"))
    mesh1.addVertex(p4)
    // P5
    let p5 = new types.Point3d("Vertex", [27, 26, 0])
    p5.addAttribute(new types.Text("I Shape", "line_ending_type"))
    mesh1.addVertex(p5)

    // Edges
    // L0
    let l0 = new types.LineReference("Edge", [0, 1], types.ObjectDataType.point3d)
    l0.addAttribute(new types.Text("Single Solid", "line_marking_type"))
    l0.addAttribute(new types.Text("White", "line_colourine_marking_typ"))
    let l0_id = mesh1.addEdge(l0)
    // L1
    let l1 = new types.LineReference("Edge", [1, 2], types.ObjectDataType.point3d)
    l1.addAttribute(new types.Text("Double Solid", "line_marking_type"))
    l1.addAttribute(new types.Text("Blue", "line_colourine_marking_type"))
    let l1_id = mesh1.addEdge(l1)
    // L2
    let l2 = new types.LineReference("Edge", [2, 3], types.ObjectDataType.point3d)
    l2.addAttribute(new types.Text("Dashed", "line_marking_type"))
    l2.addAttribute(new types.Text("Yellow", "line_colourine_marking_type"))
    let l2_id = mesh1.addEdge(l2)
    // L3
    let l3 = new types.LineReference("Edge", [3, 0], types.ObjectDataType.point3d)
    l3.addAttribute(new types.Text("Cross", "line_marking_type"))
    l3.addAttribute(new types.Text("Green", "line_colourine_marking_type"))
    mesh1.addEdge(l3)
    // L4
    let l4 = new types.LineReference("Edge", [1, 4], types.ObjectDataType.point3d)
    l4.addAttribute(new types.Text("Single Solid", "line_marking_type"))
    l4.addAttribute(new types.Text("White", "line_colourine_marking_type"))
    mesh1.addEdge(l4)
    // L5
    let l5 = new types.LineReference("Edge", [4, 5], types.ObjectDataType.point3d)
    l5.addAttribute(new types.Text("Double Solid", "line_marking_type"))
    l5.addAttribute(new types.Text("Blue", "line_colourine_marking_type"))
    mesh1.addEdge(l5)
    // L6
    let l6 = new types.LineReference("Edge", [5, 2], types.ObjectDataType.point3d)
    l6.addAttribute(new types.Text("Dashed", "line_marking_type"))
    l6.addAttribute(new types.Text("Yellow", "line_colourine_marking_type"))
    mesh1.addEdge(l6)

    // Areas
    // A0
    let a0 = new types.AreaReference("Slot", [0, 1, 2, 3], types.ObjectDataType.line_reference)
    a0.addAttribute(new types.Text("Fishbone", "park_slot_type"))
    a0.addAttribute(new types.Text("Empty", "park_slot_content"))
    mesh1.addArea(a0)
    let a1 =new types.AreaReference("Slot", [4, 5, 6, 1], types.ObjectDataType.line_reference)
    a1.addAttribute(new types.Text("Fishbone", "park_slot_type"))
    a1.addAttribute(new types.Text("Empty", "park_slot_content"))
    mesh1.addArea(a1)

    let mesh_id = openlab.addObject("parking1", "ParkingLot")
    openlab.addObjectData(mesh_id, mesh1)

    let string_mesh = mesh1.getMeshGeometryAsString()

    
   expect(string_mesh).toBe("[[[25,25,0],[26,25,0],[26,26,0],[25,26,0],[27,25,0],[27,26,0]],"+
                             "[[0,1],[1,2],[2,3],[3,0],[1,4],[4,5],[5,2]],[[0,1,2,3],[4,5,6,1]]]")

   expect(openlab.stringify(false)).toBe(new VCD(openlabel100_test_create_mesh, false).stringify(false))

});

test('test_create_mesh_with_API_frames', () => {

    
    // Load from previous test
    let openlab= new OpenLABEL(openlabel100_test_create_mesh, false)

    // Let's assume we know the structure of the mesh
    //
    // P0 L0   P1   L4   P4
    // *--------*--------*
    // |        |        |
    // |L3  A0  |L1  A1  |L5
    // |        |        |
    // *--------*--------*
    // P3  L2   P2  L6   P5
    //
    // V0  [A0,A1]

    // Let's read mesh object
    // mesh1 = openlab.get_objects_with_object_data_name("parkslot1")
    let mesh1 = openlab.getObject("0")

    // Let's read static object_data
    // od_mesh = mesh1.data['object_data']['mesh']
    let od_mesh = openlab.getObjectData("0", "mesh1",null)

    let vertices = od_mesh['point3d']
    let edges = od_mesh['line_reference']
    let areas = od_mesh['area_reference']

    // Let's add some frame-specific attributes (for line-reference and area-references)
    // Currently, only way to do it is by creating a new mesh object_data
    // and add it to the existing Object, specifying the frame

    for(let frame_num in Array.from(Array(2).keys())){
        let mesh1_frame = new types.Mesh("mesh1_dyn") 
        for(let line_key in edges){
            let line_val = edges[line_key]
            // Read existing info
            // "None" for val, so it is not copied at frame-lev.
            let lX = new types.LineReference(line_val['name'], null,types.ObjectDataType.point3d)
            lX.addAttribute(new types.Text("line_colour", "not set"))
            mesh1_frame.addEdge(lX, line_key)
        }
        for(let area_key in areas){
            let area_val = areas[area_key]
            // If we want to add an area_reference attribute: Reconstruct area_reference
            // Read existing info
            let aX = new types.AreaReference(area_val['name'],null, types.ObjectDataType.line_reference)
            aX.addAttribute(new types.Text("park_slot_content", "Empty"))
            mesh1_frame.addArea(aX, area_key)
        }

        // We add and then update. Note we use a different name "parkslot1_dyn", because "parkslot1" is used for
        // a static object_data
        openlab.addObjectData("0", mesh1_frame, Number(frame_num))
    }
    

    expect(openlab.stringify(false)).toBe(new VCD(openlabel100_test_create_mesh_with_API_frames, false).stringify(false))

});

