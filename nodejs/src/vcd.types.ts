/*
VCD (Video Content Description) library v5.0.0

Project website: http://vcd.vicomtech.org

Copyright (C) 2020, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a library to create and manage VCD content version 5.0.0.
VCD is distributed under MIT License. See LICENSE.

*/

import * as poly2d from './vcd.poly2d'

function isFloat(n){
    return Number(n) === n && n % 1 !== 0;
}

export enum CoordinateSystemType {
	sensor_cs = 1,  // the coordinate system of a certain sensor
    local_cs = 2,  // e.g. vehicle-ISO8855 in OpenLABEL, or "base_link" in ROS
    scene_cs = 3,  // e.g. "odom" in ROS; starting as the first local-ls
    geo_utm = 4,  // In UTM coordinates
    geo_wgs84 = 5,  // In WGS84 elliptical Earth coordinates
    custom = 6  // Any other coordinate system
}

export class Intrinsics{
	data: object ;
    constructor() {
        this.data = {};
	}
}

export class IntrinsicsPinhole extends Intrinsics{
    constructor( widthPx: number, heightPx: number, cameraMatrix3x4: Array<number>, distortionCoeffs1xN=null, additionalItems){
        super();
		if (!Number.isInteger(widthPx)){
			console.warn("WARNING: widthPx is not integer");
			return;
		}
		if (!Number.isInteger(widthPx)){
			console.warn("WARNING: heightPx is not integer");
			return;
		}
        this.data['intrinsics_pinhole'] = {};
        this.data['intrinsics_pinhole']['width_px'] = widthPx;
        this.data['intrinsics_pinhole']['height_px'] = heightPx;
		
		if(!Array.isArray(cameraMatrix3x4)){
			console.warn("WARNING: cameraMatrix3x4 not array");
			return;
		}
		if(cameraMatrix3x4.length != 12){
			console.warn("WARNING: cameraMatrix3x4 length not 12");
			return;
		}
		
        this.data['intrinsics_pinhole']['camera_matrix_3x4'] = cameraMatrix3x4;

        if (distortionCoeffs1xN == null){
            distortionCoeffs1xN = [];
		}
        else{
			if(!Array.isArray(distortionCoeffs1xN)){
				console.warn("WARNING: distortionCoeffs1xN not array");
				return;
			}
            var num_coeffs = distortionCoeffs1xN.length;
			if(num_coeffs < 5 || num_coeffs > 14){
				console.warn("WARNING: distortionCoeffs1xN length not between 5 and 14");
				return;
			}
		}
        this.data['intrinsics_pinhole']['distortion_coeffs_1xN'] = distortionCoeffs1xN;

        if (additionalItems != null){
			Object.assign(this.data['intrinsics_pinhole'], additionalItems);
		}
	}
}

export class IntrinsicsFisheye extends Intrinsics {	
    constructor( widthPx: number, heightPx: number, lensCoeffsLx4: Array<number>, fovDeg: number, centerX: number, centerY: number,
                 radiusX: number, radiusY: number, additionalItems){
		super();
		if (!Number.isInteger(widthPx)){
			console.warn("WARNING: widthPx is not integer");
			return;
		}
		if (!Number.isInteger(widthPx)){
			console.warn("WARNING: heightPx is not integer");
			return;
		}
        this.data['intrinsics_fisheye'] = {}
        this.data['intrinsics_fisheye']['width_px'] = widthPx
        this.data['intrinsics_fisheye']['height_px'] = heightPx
        this.data['intrinsics_fisheye']['center_x'] = centerX;
        this.data['intrinsics_fisheye']['center_y'] = centerY;
        this.data['intrinsics_fisheye']['radius_x'] = radiusX;
        this.data['intrinsics_fisheye']['radius_y'] = radiusY;
        this.data['intrinsics_fisheye']['fov_deg'] = fovDeg;

		var num_coeffs = lensCoeffsLx4.length;
		if(num_coeffs != 4){
			console.warn("WARNING: lensCoeffsLx4 length not 4");
			return;
		}
        this.data['intrinsics_fisheye']['lens_coeffs_1x4'] = lensCoeffsLx4;

        if(additionalItems != null){			
			Object.assign(this.data['intrinsics_fisheye'], additionalItems);
		}
	}
}

export class IntrinsicsCustom extends Intrinsics {
	constructor(additionalItems) {
		super()
		this.data['intrinsics_custom'] = {}
		if(additionalItems != null){			
			Object.assign(this.data['intrinsics_custom'], additionalItems);
		}
	}
}

export enum TransformDataType{
	matrix_4x4 = 1,
    quat_and_trans_7x1 = 2,
    euler_and_trans_6x1 = 3,
    custom = 4
}

export class TransformData {

	/*
    This class encodes the transform data in the form of 4x4 matrix, quaternion + translation, or
    Euler angles + translation
    */
	data: object
	constructor(val, type,additionalItems: object = null){
		this.data = {}
		if(type == TransformDataType.matrix_4x4){
			this.data['matrix4x4'] = val
		}else if(type == TransformDataType.quat_and_trans_7x1){
			this.data['quaternion'] = val.slice(0,4);  //val[0:4]
            this.data['translation'] = val.slice(4,7); //val[4:7]
		}else if (type == TransformDataType.euler_and_trans_6x1){
			this.data['euler_angles'] =  val.slice(0,3);  //val[0:3]
            this.data['translation'] =   val.slice(3,6);  //val[3:6]
		}

		if (additionalItems!=null){
			Object.assign(this.data, additionalItems)
		}
	}
}
export class PoseData extends TransformData{
	/** 
    Equivalente to TransformData, but intended to be used when passive rotation and translation values are provided
    */
   constructor(val, type,additionalItems: object = null ){
	   super(val,type,additionalItems)
   }
}
export class Transform {
	data: object
	data_additional: object
	constructor(srcName: string, dstName: string , transform_src_to_dst, additionalItems: object = null) {		
		this.data = {}
		this.data_additional = {}
		let name = srcName + '_to_' + dstName
		this.data[name] = {}		
		this.data[name]['src'] = srcName
		this.data[name]['dst'] = dstName
		this.data[name]['transform_src_to_dst'] = transform_src_to_dst.data
       
		if(additionalItems != null){			
			Object.assign(this.data[name], additionalItems);
			Object.assign(this.data_additional, additionalItems)
		}
	}
}

export class Pose extends Transform {
	constructor(subjectName: string, referenceName: string, additionalItems: object = null) {
		// NOTE: the pose of subject_name system wrt to reference_name system is the transform
        // from the reference_name system to the subject_name system
		super(referenceName, subjectName, additionalItems)
	}
}

export class Extrinsics extends Transform {	
    constructor(subjectName: string, referenceName: string, additionalItems: object = null) {
		// NOTE: the pose of subject_name system wrt to reference_name system is the transform
        // from the reference_name system to the subject_name system
		super(referenceName, subjectName, additionalItems)
	}
}

export class StreamSync{
	data: object;
	frameVcd: number;
    constructor( frameVcd=null, frameStream=null, timestampISO8601=null, frameShift=null, additionalItems){
        this.data = {};
        this.data['sync'] = {};
        this.frameVcd = frameVcd ; // This is the master frame at vcd (if(it == null, frameShift specifies constant shift

        if(frameShift != null){
			if (!Number.isInteger(frameShift)){
				console.warn("WARNING: frameShift is not integer");
				return;
			}
			if(frameStream != null || timestampISO8601 != null || frameVcd != null){
				console.warn("WARNING: frameStream, timestampISO8601 or frameVcd not null");
				return;
			} 
            this.data['sync']['frame_shift'] = frameShift;
		}
        else{
			if (!Number.isInteger(frameVcd)){
				console.warn("WARNING: frameVcd is not integer");
				return;
			}
            if(frameStream != null){
				if (!Number.isInteger(frameStream)){
					console.warn("WARNING: frameStream is not integer");
					return;
				}
                this.data['sync']['frame_stream'] = frameStream;
			}
            if(timestampISO8601 != null){
				if(typeof timestampISO8601 != "string" && !(timestampISO8601 instanceof String)){
					console.warn("WARNING: timestampISO8601 not string",timestampISO8601);
					return;
				}
                this.data['sync']['timestamp'] = timestampISO8601;
			}
		}
        if(additionalItems != null){			
			Object.assign(this.data['sync'], additionalItems);
		}
	}
}

export enum ObjectDataType {
	bbox = 1,
	rbbox,
	num,
	text,
	boolean,
	poly2d,
	poly3d,
	cuboid,
	image,
	mat,
	binary,
	point2d,
	point3d,
	vec,
	line_reference,
	area_reference,
	mesh
}

export enum Poly2DType {
	MODE_POLY2D_ABSOLUTE = 0,
	MODE_POLY2D_SRF6DCC = 5,
	MODE_POLY2D_RS6FCC = 6
}

export class ObjectData{
	data: object;
	type: any;
    constructor( name: string, cs=null, properties=null, type=null) {        
        this.data = {};
		if(name != null){
        	this.data['name'] = name;
		}
        if(cs != null){
			if(typeof cs != "string" && !(cs instanceof String)){
				console.warn("WARNING: coordinate_system not string", cs);
				return;
			}
            this.data['coordinate_system'] = cs;
		}
		if(properties != null){
			Object.assign(this.data, properties)
		}
		if(type!=null){
			this.data['type']=type;
		}
	}
	typeName() {
		return ObjectDataType[this.type]
	}

    addAttribute( objectData ){
		// Check if the name already exists, if so, substitute
		if(!(objectData instanceof ObjectData)){
			console.warn("WARNING: objectData not ObjectData",objectData);
			return;
		}
		if(objectData instanceof ObjectDataGeometry){
			console.warn("WARNING: objectData is ObjectDataGeometry",objectData);
			return;
		}
		this.data['attributes'] = this.data['attributes'] || {};  // Creates 'attributes' if(it does not exist
		let objectDataName = ObjectDataType[objectData.type]
        if(objectDataName in this.data['attributes']){
			this.data['attributes'][objectDataName] = this.data['attributes'][objectDataName] || [];
			
			// Find if this element_data name is already there...			
			const pos = this.data['attributes'][objectDataName].findIndex(item => item.name === objectData.data['name'])
			let found = (pos == -1)?(false):(true)
			if(!found) {
				// No: then, just push this new object data
				this.data['attributes'][objectDataName].push(objectData.data);
			}
			else {
				// Ok, exists, so let's substitute
				this.data['attributes'][objectDataName][pos] = objectData.data
			}
		}
		else {
			this.data['attributes'][objectDataName] = [objectData.data];
		}
	}
}

export class ObjectDataGeometry extends ObjectData {
    constructor( name: string, cs=null, properties=null) {
        super( name, cs, properties);  // Calling parent export class 
	}
}

export class Bbox extends ObjectDataGeometry {
    constructor( name: string, val: Array<number>, cs=null, properties=null ) {
        super( name, cs, properties );		
		if(val.length != 4){
			console.warn("WARNING: val length not 4");
			return;
		}
        this.data['val'] = val;
        this.type = ObjectDataType.bbox;
	}
}

export class Rbbox extends ObjectDataGeometry {
    constructor( name: string, val: Array<number>, cs=null, properties=null  ) {
        super( name, cs, properties );		
		if(val.length != 5){
			console.warn("WARNING: val length not 5.");
			return;
		}
        this.data['val'] = val;
        this.type = ObjectDataType.rbbox;
	}
}

export class Num extends ObjectData{
    constructor( name: string, val, cs=null, properties=null, type=null ) {
        super( name, cs, properties,type);
		if (!isFloat(val) && !Number.isInteger(val)){
			console.warn("WARNING: val is not float or integer");
			return;
		}
        this.data['val'] = val;
        this.type = ObjectDataType.num;
	}
}

export class Text extends ObjectData{
    constructor( name: string, val, cs=null, properties=null, type=null  ){
        super( name, cs, properties,type);
		if(typeof val != "string" && !(val instanceof String)){
			console.warn("WARNING: val not string",val);
			return;
		}
        this.data['val'] = val;
        this.type = ObjectDataType.text;
	}
}

export class Boolean extends ObjectData{
    constructor( name: string, val: boolean, cs=null, properties=null , type=null ){
        super( name, cs, properties,type);		
        this.data['val'] = val;
        this.type = ObjectDataType.boolean;
	}
}

export class Poly2d extends ObjectDataGeometry{
    constructor( name: string, val: Array<number>, mode: Poly2DType, closed: boolean, hierarchy=null, cs=null, properties=null ){
        super( name, cs, properties);
        if(!Array.isArray(val)){
			console.warn("WARNING: val not array");
			return;
		}
        if (typeof closed != "boolean") {
			console.warn("WARNING: closed is not boolean");
		}
		if(mode == Poly2DType.MODE_POLY2D_SRF6DCC) {			
			let vals = poly2d.computeSRF6DCC(val)
			let srf6 = vals['code']
			let xinit = vals['xinit']
			let yinit = vals['yinit']			
			let res  = poly2d.chainCodeBase64Encoder(srf6, 3)
			let encoded_poly = res['code']
			let rest = res['rest']
            this.data['val'] = [xinit.toString(), yinit.toString(), rest.toString(), encoded_poly]
		}
		else if(mode == Poly2DType.MODE_POLY2D_ABSOLUTE) {
			this.data['val'] = val;
		}
		else {
			console.warn("WARNING: mode has not accepted value");
		}
        this.data['mode'] = Poly2DType[mode];
        this.data['closed'] = closed;
        this.type = ObjectDataType.poly2d;
        if(hierarchy != null){
			if(!Array.isArray(hierarchy)){
				console.warn("WARNING: hierarchy not array");
				return;
			}
			for(var i = 0; i < hierarchy.length; i++){
				if(Number.isInteger(hierarchy[i])){
					console.warn("WARNING: " + i + "th index not integer");
					return;
				}
			}
            this.data['hierarchy'] = hierarchy;
		}
	}
}

export class Poly3d extends ObjectDataGeometry{
    constructor( name: string, val, closed, cs=null, properties=null ){
        super( name, cs, properties );
        if(!Array.isArray(val)){
			console.warn("WARNING: val not array");
			return;
		}
        if (typeof closed != "boolean"){
			console.warn("WARNING: closed is not boolean");
		}
		
        this.data['val'] = val;
        this.data['closed'] = closed
        this.type = ObjectDataType.poly3d;
	}
}

export class Cuboid extends ObjectDataGeometry {
	private use_quaternion = false
    constructor( name: string, val, cs=null, properties=null  ) {
        super( name, cs, properties);
		if(val != null) {
			if(!Array.isArray(val)){
				console.warn("WARNING: val not array");
				return;
			}				
			if(val.length == 9) {
				this.use_quaternion = false
			}
			else if(val.length == 10){
				this.use_quaternion = true
			}
			else {
				console.error("CUBOID is defined as a 9 or 10-dim vector.")
				return
			}
			this.data['val'] = val;
		}
		else {
			this.data['val'] = null
		}
        
        this.type = ObjectDataType.cuboid;
	}
}

export class Image extends ObjectData{
    /*
    This export class  hosts image data, in buffer format. It can be used with any codification, although base64 and webp
    are suggested.

    mimeType: "image/png", "image/jpeg", .. as in https://www.sitepoint.com/mime-types-complete-list/
    encoding: "base64", "ascii", .. as in https://docs.python.org/2.4/lib/standard-encodings.html

    Default is base64

    OpenCV can be used to encode:
    img = cv2.imread(file_name, 1)
    compr_params=[int(cv2.IMWRITE_PNG_COMPRESSION), 9]
    result, payload = cv2.imencode('.png', img, compr_params)
    */
    constructor( name: string, val: string, mimeType: string, encoding: string, cs=null, properties=null ) {
        super( name, cs, properties);		
        this.data['val'] = val;
        this.data['mime_type'] = mimeType;
        this.data['encoding'] = encoding;
        this.type = ObjectDataType.image;
	}
}

export class Mat extends ObjectData{
    constructor( name: string, val: Array<number>, channels: number, width: number, height: number, dataType: string, cs=null, properties=null ){
        super( name, cs, properties);        
		if(val.length != width * height * channels){
			console.warn("WARNING: val.length != width * height * channels");
			return;
		}
        this.data['val'] = val;
        this.data['channels'] = channels;
        this.data['width'] = width;
        this.data['height'] = height;
        this.data['data_type'] = dataType;
        this.type = ObjectDataType.mat;
	}
}

export class Binary extends ObjectData{
    constructor( name: string, val: string, dataType: string, encoding: string, cs=null, properties=null ){
        super( name, cs, properties);		
        this.data['val'] = val;
        this.data['data_type'] = dataType;
        this.data['encoding'] = encoding;
        this.type = ObjectDataType.binary;
	}
}

export class Vec extends ObjectData{
    constructor( name: string, val: Array<number> | Array<string>, cs=null, properties=null, type=null ) {
        super( name, cs, properties,type);        
        this.data['val'] = val;
        this.type = ObjectDataType.vec;
	}
}

export class Point2d extends ObjectDataGeometry{
    constructor( name: string, val: Array<number>, id=null, cs=null, properties=null ){
        super( name, cs, properties);		
        if(val.length != 2){
			console.warn("WARNING: val length not 2");
		}
        
        this.data['val'] = val;
        if(id != null){
			
            if (!Number.isInteger(id)){
				console.warn("WARNING: id is not integer");
				return;
			}
            this.data['id'] = id;
		}
        this.type = ObjectDataType.point2d;
	}
}

export class Point3d extends ObjectDataGeometry{
    constructor( name: string, val: Array<number>, id=null,  cs=null, properties=null ) {
        super( name, cs, properties);		
		if(val.length != 3){
			console.warn("WARNING: val length not 3");
			return;
		}
		this.data['val'] = val;
		if(id != null){
			
            if (!Number.isInteger(id)){
				console.warn("WARNING: id is not integer");
				return;
			}
            this.data['id'] = id;
		}
        this.type = ObjectDataType.point3d;
	}
}

export class GeometricReference extends ObjectDataGeometry{
    constructor( name: string, val, referenceType: ObjectDataType, cs=null, properties=null ){
        super( name, cs, properties);		
        this.data['reference_type'] = ObjectDataType[referenceType];  // this trick returns the value of the enum as a string
        if(val != null){
            if(!Array.isArray(val)){
				console.warn("WARNING: val not array");
				return;
			}
            this.data['val'] = val;
		}
	}
}

export class LineReference extends GeometricReference{
    constructor( name: string, val, referenceType: ObjectDataType, cs=null, properties=null ){
        super( name, val, referenceType, cs, properties);
	}
}

export class AreaReference extends GeometricReference{
    constructor( name: string, val, referenceType: ObjectDataType, cs=null, properties=null ){
        super( name, val, referenceType, cs, properties);
	}
}

export class VolumeReference extends GeometricReference{
    constructor( name: string, val, referenceType: ObjectDataType, cs=null, properties=null ){
        super( name, val, referenceType, cs, properties);
	}
}

export class Mesh extends ObjectDataGeometry{
	pid: number;
    eid: number;
    aid: number;
    vid: number;
    constructor( name: string, cs=null, properties=null ) {
        super( name, cs, properties);
        this.pid = 0;
        this.eid = 0;
        this.aid = 0;
        this.vid = 0;
        this.data['point3d'] = {};
        this.data['line_reference'] = {};
        this.data['area_reference'] = {};
        this.type = ObjectDataType.mesh;
	}

    // Vertex
    addVertex( p3d: Point3d, id=null){
		var idx;
        // if(an id is provided use it
        if(id != null){
            // if(it already exists, this is an update call
            if(this.data['point3d'][id]){
                // The id already exists: substitute
                idx = id;
			}
            else{
                idx = id
                this.pid = idx + 1
			}
		}
        else{
            idx = this.pid;
            this.pid += 1;
		}

        this.data['point3d'] = this.data['point3d'] || {};
        this.data['point3d'][idx] = p3d.data;
        return idx;
	}
	
    // Edge
    addEdge( lref: LineReference, id=null){
		var idx;		

        if(id != null){
            if(this.data['line_reference'][id]){
                idx = id;
			}
            else{
                idx = id;
                this.eid = idx + 1;
			}
		}
        else{
            idx = this.eid;
            this.eid += 1;
		}

        this.data['line_reference'] = this.data['line_reference'] || {};
        this.data['line_reference'][idx] = lref.data;
        return idx;
	}

    // Area
    addArea( aref: AreaReference, id=null){
		var idx;		

        if(id != null){
            if(this.data['area_reference'][id]){
                idx = id;
			}
            else{
                idx = id;
                this.aid = idx + 1;
			}
		}
        else{
            idx = this.aid;
            this.aid += 1;
		}

        this.data['area_reference'] = this.data['area_reference'] || {};
        this.data['area_reference'][idx] = aref.data;
        return idx;
	}

    getMeshGeometryAsString(){
        var result = "[[";
		for (const prop in this.data['point3d']){
            var vertex = this.data['point3d'][prop];
            var val = vertex['val'];
            result += "[";
            for(var i = 0; i < val.length; i++){
                result += val[i].toString() + ",";
			}
            result += "],";
		}
        result += "],["
		
		for (const prop in this.data['line_reference']){
            var edge = this.data['line_reference'][prop];
            var val = edge['val'];
            result += "[";
            for(var i = 0; i < val.length; i++){
                result += val[i].toString() + ",";
			}
            result += "],";
		}
        result += "],[";

		for (const prop in this.data['area_reference']){
            var area = this.data['area_reference'][prop];
            var val = area['val'];
            result += "[";
            for(var i = 0; i < val.length; i++){
                result += val[i].toString() + ",";
			}
            result += "],";
		}
        result += "]]";

        // Clean-out commas
		let re = /\,]/gi;
        result = result.replace(re, "]")

        return result;
	}
}
