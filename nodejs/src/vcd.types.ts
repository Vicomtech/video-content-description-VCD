
function isFloat(n){
    return Number(n) === n && n % 1 !== 0;
}

function mergeObjects(obj1, obj2){
	let key;
	
	for (key in obj2) {
	  if(obj2.hasOwnProperty(key)){
		obj1[key] = obj2[key];
	  }
	}
}


export class Intrinsics{
	data:any;
    constructor(){
        this.data = {};
	}
}

export class IntrinsicsPinhole extends Intrinsics{
    constructor( widthPx, heightPx, cameraMatrix3x4, distortionCoeffs1xN=null, additionalItems){
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
            mergeObjects(this.data['intrinsics_pinhole'],additionalItems);
		}
	}
}

export class IntrinsicsFisheye{
	data:any;
    constructor( widthPx, heightPx, lensCoeffsLx4, fovDeg, centerX, centerY,
                 radiusX, radiusY, additionalItems){
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
		if(!Array.isArray(lensCoeffsLx4)){
			console.warn("WARNING: lensCoeffsLx4 not array");
			return;
		}
            
		if (!isFloat(centerX)){
			console.warn("WARNING: centerX is not float");
			return;
		}
		if (!isFloat(centerY)){
			console.warn("WARNING: centerY is not float");
			return;
		}
		if (!isFloat(radiusX)){
			console.warn("WARNING: radiusX is not float");
			return;
		}
		if (!isFloat(radiusY)){
			console.warn("WARNING: radiusY is not float");
			return;
		}
		if (!isFloat(fovDeg)){
			console.warn("WARNING: fovDeg is not float");
			return;
		}

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
            this.data['intrinsics_fisheye'].update(additionalItems);
		}
	}
}

export class Extrinsics{
	data:any;
    constructor( poseScsWrtLcs4x4, additionalItems){
		if(!Array.isArray(poseScsWrtLcs4x4)){
			console.warn("WARNING: poseScsWrtLcs4x4 not array");
			return;
		}
		var num_coeffs = poseScsWrtLcs4x4.length;
		if(num_coeffs != 16){
			console.warn("WARNING: poseScsWrtLcs4x4 length not 16");
			return;
		}
        this.data = {};
        this.data['extrinsics'] = {};
        this.data['extrinsics']['pose_scs_wrt_lcs_4x4'] = poseScsWrtLcs4x4;

        if(additionalItems != null){
            this.data['extrinsics'].update(additionalItems);
		}
	}
}

export class StreamSync{
	data:any;
	frameVcd:number;
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
            this.data['sync'].update(additionalItems)
		}
	}
}

export class Odometry{
	data:any;
    constructor( poseLcsWrtWcs4x4, additionalProperties){
        this.data = {};
        this.data['odometry'] = {};
		if(!Array.isArray(poseLcsWrtWcs4x4)){
			console.warn("WARNING: poseLcsWrtWcs4x4 not array");
			return;
		}
		var num_coeffs = poseLcsWrtWcs4x4.length;
		if(num_coeffs != 16){
			console.warn("WARNING: poseLcsWrtWcs4x4 length not 16");
			return;
		}

        this.data['odometry']['pose_lcs_wrt_wcs_4x4'] = poseLcsWrtWcs4x4;

        if(additionalProperties != null){
            this.data['odometry'].update(additionalProperties);
		}
	}
}

export class ObjectData{
	data:any;
	type:string;
    constructor( name, stream=null){
        if(typeof name != "string" && !(name instanceof String)){
			console.warn("WARNING: name not string",name);
			return;
		}
        this.data = {};
        this.data['name'] = name;
        if(stream != null){
			if(typeof stream != "string" && !(stream instanceof String)){
				console.warn("WARNING: stream not string",stream);
				return;
			}
            this.data['stream'] = stream;
		}
	}

    addAttribute( objectData){
		if(!(objectData instanceof ObjectData)){
			console.warn("WARNING: objectData not ObjectData",objectData);
			return;
		}
		if(objectData instanceof ObjectDataGeometry){
			console.warn("WARNING: objectData is ObjectDataGeometry",objectData);
			return;
		}
        this.data['attributes'] = this.data['attributes'] || {};  // Creates 'attributes' if(it does not exist
        if(!this.data['attributes'][objectData.type]){
            this.data['attributes'][objectData.type] = this.data['attributes'][objectData.type] || [];
			this.data['attributes'][objectData.type].push(objectData.data);
		}
		else{
			this.data['attributes'][objectData.type].push(objectData.data);
		}
	}
}

export class ObjectDataGeometry extends ObjectData{
    constructor( name, stream=null){
        super( name, stream);  // Calling parent export class 
	}
}

export class Bbox extends ObjectDataGeometry{
    constructor( name, val, stream=null){
        super( name, stream);
		if(!Array.isArray(val)){
			console.warn("WARNING: val not array");
			return;
		}
		if(val.length != 4){
			console.warn("WARNING: val length not 4");
			return;
		}
        this.data['val'] = val;
        this.type = "bbox";
	}
}

export class Num extends ObjectData{
    constructor( name, val, stream=null){
        super( name, stream);
		if (!isFloat(val) && !Number.isInteger(val)){
			console.warn("WARNING: val is not float or integer");
			return;
		}
        this.data['val'] = val;
        this.type = "num";
	}
}

export class Text extends ObjectData{
    constructor( name, val, stream=null){
        super( name, stream);
		if(typeof val != "string" && !(val instanceof String)){
			console.warn("WARNING: val not string",val);
			return;
		}
        this.data['val'] = val;
        this.type = "text";
	}
}

export class Boolean extends ObjectData{
    constructor( name, val, stream=null){
        super( name, stream);
		if (typeof val != "boolean"){
			console.warn("WARNING: val is not boolean");
		}
        this.data['val'] = val;
        this.type = "boolean";
	}
}

export class Poly2d extends ObjectDataGeometry{
    constructor( name, val, mode, closed, hierarchy=null, stream=null){
        super( name, stream);
        if(!Array.isArray(val)){
			console.warn("WARNING: val not array");
			return;
		}
        if(typeof mode != "string" && !(mode instanceof String)){
			console.warn("WARNING: mode not string",mode);
			return;
		}
        if (typeof closed != "boolean"){
			console.warn("WARNING: closed is not boolean");
		}
		if(mode == "MODE_POLY2D_SRF6DCC"){
			//not implemented yet
			/*srfsdcc = poly.computeSRFSDCC(val)
			encoded_poly, rest = poly.chainCodeBase64Encoder(srfsdcc[2:], 3)
			this.data['val'] = [str(srfsdcc[0]), str(srfsdcc[1]), str(rest), encoded_poly]*/
		}
		else if(mode == "MODE_POLY2D_ABSOLUTE"){
			this.data['val'] = val;
		}
		else{
			console.warn("WARNING: mode has not accepted value");
		}
        this.data['mode'] = mode;
        this.data['closed'] = closed;
        this.type = "poly2d";
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
    constructor( name, val, closed, stream=null){
        super( name, stream);
        if(!Array.isArray(val)){
			console.warn("WARNING: val not array");
			return;
		}
        if (typeof closed != "boolean"){
			console.warn("WARNING: closed is not boolean");
		}
		
        this.data['val'] = val;
        this.data['closed'] = closed
        this.type = "poly3d";
	}
}

export class Cuboid extends ObjectDataGeometry{
    constructor( name, val, stream=null){
        super( name, stream);
        if(!Array.isArray(val)){
			console.warn("WARNING: val not array");
			return;
		}
		if(val.length != 9){
			console.warn("WARNING: val length not 16");
		}
        this.data['val'] = val;
        this.type = "cuboid";
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
    constructor( name, val, mimeType, encoding, stream=null){
        super( name, stream);
		if(typeof val != "string" && !(val instanceof String)){
			console.warn("WARNING: val not string",val);
			return;
		}
		if(typeof mimeType != "string" && !(mimeType instanceof String)){
			console.warn("WARNING: mimeType not string",mimeType);
			return;
		}
		if(typeof encoding != "string" && !(encoding instanceof String)){
			console.warn("WARNING: encoding not string",encoding);
			return;
		}
        this.data['val'] = val;
        this.data['mime_type'] = mimeType;
        this.data['encoding'] = encoding;
        this.type = "image";
	}
}

export class Mat extends ObjectData{
    constructor( name, val, channels, width, height, dataType, stream=null){
        super( name, stream);
        if(!Array.isArray(val)){
			console.warn("WARNING: val not array");
			return;
		}
		if (!Number.isInteger(width)){
			console.warn("WARNING: width is not integer");
			return;
		}
		if (!Number.isInteger(height)){
			console.warn("WARNING: height is not integer");
			return;
		}
		if (!Number.isInteger(channels)){
			console.warn("WARNING: channels is not integer");
			return;
		}
		if(typeof dataType != "string" && !(dataType instanceof String)){
			console.warn("WARNING: dataType not string",dataType);
			return;
		}
		if(val.length != width * height * channels){
			console.warn("WARNING: val.length != width * height * channels");
			return;
		}
        this.data['val'] = val;
        this.data['channels'] = channels;
        this.data['width'] = width;
        this.data['height'] = height;
        this.data['data_type'] = dataType;
        this.type = "mat";
	}
}

export class Binary extends ObjectData{
    constructor( name, val, dataType, encoding, stream=null){
        super( name, stream);
		if(typeof val != "string" && !(val instanceof String)){
			console.warn("WARNING: val not string",val);
			return;
		}
		if(typeof dataType != "string" && !(dataType instanceof String)){
			console.warn("WARNING: dataType not string",dataType);
			return;
		}
		if(typeof encoding != "string" && !(encoding instanceof String)){
			console.warn("WARNING: encoding not string",encoding);
			return;
		}
        this.data['val'] = val;
        this.data['data_type'] = dataType;
        this.data['encoding'] = encoding;
        this.type = "binary";
	}
}

export class Vec extends ObjectData{
    constructor( name, val, stream=null){
        super( name, stream);
        if(!Array.isArray(val)){
			console.warn("WARNING: val not array");
			return;
		}
        this.data['val'] = val;
        this.type = "vec";
	}
}

export class Point2d extends ObjectDataGeometry{
    constructor( name, val, id=null, stream=null){
        super( name, stream);
		if(!Array.isArray(val)){
			console.warn("WARNING: val not array");
			return;
		}
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
        this.type = "point2d";
	}
}

export class Point3d extends ObjectDataGeometry{
    constructor( name, val, stream=null){
        super( name, stream);
		if(!Array.isArray(val)){
			console.warn("WARNING: val not array");
			return;
		}
		if(val.length != 3){
			console.warn("WARNING: val length not 3");
			return;
		}
        this.data['val'] = val;
        this.type = "point3d";
	}
}

export class GeometricReference extends ObjectDataGeometry{
    constructor( name, val, referenceType, stream=null){
        super( name, stream);
		if(referenceType != "LineReference" && referenceType != "AreaReference" && referenceType != "VolumeReference"){
			console.warn("WARNING: referenceType not valid");
			return;
		}
        this.data['reference_type'] = referenceType;
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
    constructor( name, val, referenceType, stream=null){
        super( name, val, referenceType, stream);
	}
}

export class AreaReference extends GeometricReference{
    constructor( name, val, referenceType, stream=null){
        super( name, val, referenceType, stream);
	}
}

export class VolumeReference extends GeometricReference{
    constructor( name, val, referenceType, stream=null){
        super( name, val, referenceType, stream);
	}
}

export class Mesh extends ObjectDataGeometry{
	pid:number;
    eid:number;
    aid:number;
    vid:number;
    constructor( name, stream=null){
        super( name, stream);
        this.pid = 0;
        this.eid = 0;
        this.aid = 0;
        this.vid = 0;
        this.data['point3d'] = {};
        this.data['line_reference'] = {};
        this.data['area_reference'] = {};
        this.type = "mesh";
	}

    // Vertex
    addVertex( p3d, id=null){
		var idx;
		if(!(p3d instanceof Point3d)){
			console.warn("WARNING: p3d not point3d");
			return;
		}

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
    addEdge( lref, id=null){
		var idx;
		if(!(lref instanceof LineReference)){
			console.warn("WARNING: lref not lineReference");
			return;
		}

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
    addArea( aref, id=null){
		var idx;
		if(!(aref instanceof AreaReference)){
			console.warn("WARNING: aref not areaReference");
			return;
		}

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
        result = result.replace(",]", "]")

        return result;
	}
}
