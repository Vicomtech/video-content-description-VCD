/**
VCD (Video Content Description) library v4.3.0

Project website: http://vcd.vicomtech.org

Copyright (C) 2020, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a library to create and manage VCD content version 4.2.1.
VCD is distributed under MIT License. See LICENSE.

*/

import * as utils from "./vcd.utils"
import * as types from "./vcd.types"
import * as schema from "./vcd.schema"

import Ajv from 'ajv'
import { v4 as uuidv4 } from 'uuid'

export enum ElementType {
    object = 0,
    action = 1,
    event = 2,
    context = 3,
    relation = 4
}

export enum StreamType {    
    camera = 1,
    lidar = 2,
    radar = 3,
    gps_imu = 4,
    other = 5
}

export enum RDF {
    subject = 1,
    object = 2
}

export class FrameIntervals {
    private fisDict: Array<object>
    private fisNum: Array<Array<number>>
    constructor(frameValue = null) {        
        this.fisDict = []
        this.fisNum = []
        if(frameValue != null) {
            if(Number.isInteger(frameValue)) {
                this.fisDict = [{'frame_start': frameValue, 'frame_end': frameValue}]
                this.fisNum = [[frameValue, frameValue]]
            }
            else if(Array.isArray(frameValue)) {
                if(frameValue.length == 0) return
                if(frameValue.every(function(x) { return Array.isArray(x); })) {
                    // Then, frameValue is Array<Array<number> >, e.g. [[0, 10], [26, 29]]
                    this.fisDict = utils.asFrameIntervalsArrayDict(frameValue)    
                    this.fisDict = utils.fuseFrameIntervals(this.fisDict)
                    this.fisNum = utils.asFrameIntervalsArrayTuples(this.fisDict)           
                       
                }
                else if (frameValue.every(function(x) { return Number.isInteger(x); })) {
                    // Then, frameValue is a single frame interval, e.g. [0, 10]
                    this.fisNum = [frameValue]                    
                    this.fisDict = utils.asFrameIntervalsArrayDict(this.fisNum)
                }
                else if (frameValue.every(function(x) { return (typeof x === 'object' && x !== null && 'frame_start' in x && 'frame_end' in x) })) {
                    // User provided an Array of dict, e.g. [{'frame_start': 0, 'frame_end':10}]
                    this.fisDict = frameValue
                    this.fisDict = utils.fuseFrameIntervals(this.fisDict)
                    this.fisNum = utils.asFrameIntervalsArrayTuples(this.fisDict)   
                }
            }        
            else if(typeof frameValue === 'object' && frameValue !== null && 'frame_start' in frameValue && 'frame_end' in frameValue) {
                // User provided a singld dict, e.g. {'frame_start': 0, 'frame_end':10}
                this.fisDict = [frameValue]
                this.fisNum = utils.asFrameIntervalsArrayTuples(this.fisDict)
            }
            else {
                console.warn("ERROR: Unsupported FrameInterval format.")
            }
        }
    }
    empty(): boolean {        
        if(this.fisDict.length == 0 || this.fisNum.length == 0) return true
        else return false
    }
    getDict() {
        return this.fisDict
    }
    get() {
        return this.fisNum
    }

    rmFrame(frameNum: number) {
        this.fisDict = utils.rmFrameFromFrameIntervals(this.fisDict, frameNum)
        this.fisNum = utils.asFrameIntervalsArrayTuples(this.fisDict)
    }

    union(frameIntervals: FrameIntervals): FrameIntervals {
        let fisUnion = utils.fuseFrameIntervals(frameIntervals.getDict().concat(this.fisDict))
        return new FrameIntervals(fisUnion)
    }

    intersection(frameIntervals: FrameIntervals): FrameIntervals {
        let fisInt = utils.intersectionBetweenFrameIntervalArrays(this.fisNum, frameIntervals.get())
        return new FrameIntervals(fisInt)
    }

    getOuter() {
        return utils.getOuterFrameInterval(this.fisDict)
    }

    hasFrame(frameNum: number) {
        return utils.isInsideFrameIntervals(frameNum, this.fisNum)
    }
}


/**
* VCD
*
* This class is the main manager of VCD 4 content.
* It can be created void, and add content (e.g. Objects) using the API
* It can also be created by providing a JSON file.
* ```
* import { VCD } from 'vcd'
* let vcd_a = new VCD() // created void
* let vcd_b = new VCD(vcd_string) // vcd_string is a read JSON string from a file
* ```
*/
export class VCD {
    private data = {}  
    private schema_version = schema.vcd_schema_version
    private schema = schema.vcd_schema     
    private ajv = new Ajv()
    private ajv_validate = this.ajv.compile(this.schema)
	
    private lastUID = {}
    private useUUID = false
	
	constructor(vcd_json = null, validation = false) {
		this.init(vcd_json, validation);		
    }
    
    setUseUUID(val: boolean) {
        this.useUUID = val
    }
	
	printInfo() {
		console.log("This is a VCD4 content\n");
		console.log("\tversion: " + this.schema_version);
	}

    private reset() {
        // Main VCD data
        this.data = { 'vcd': {} };
        this.data['vcd']['frames'] = {};
        this.data['vcd']['schema_version'] = this.schema_version;
        this.data['vcd']['frame_intervals'] = [];

        // Additional auxiliary structures
        this.lastUID = {};
        this.lastUID['object'] = -1;
        this.lastUID['action'] = -1;
        this.lastUID['event'] = -1;
        this.lastUID['context'] = -1;
        this.lastUID['relation'] = -1;
    }

	private init(vcd_json = null, validation = false) {
		if (vcd_json == null) {			
			this.reset();
		}
		else {
            // Load from file, and validate with schema
            if (validation) {
                let validation_errors = this.validate(vcd_json)
                if (validation_errors.length != 0) {
                    console.log("ERROR: loading VCD content not compliant with schema " + this.schema_version);
                    console.warn("Creating an empty VCD instead.");
                    for(var i = 0; i <validation_errors.length; i++){
                        console.log(validation_errors[i].message);
                    }   
                    this.reset();                 
                }
                else {
                    // Copy the VCD content into this.data
                    this.data = vcd_json

                    // In VCD 4.3.0 uids are strings, because they can be numeric strings, or UUIDs
                    // but frames are still ints. However, it looks that in Typescript, JSON.parse reads as integer
                    //if('frames' in this.data['vcd']){
                    //    let frames = this.data['vcd']['frames']
                    //    if(Object.keys(frames).length > 0){                                                        
                            //let new_frames = Object.assign({}, ...Object.entries(frames).map(([k, v]) => ({[Number(k)]: v}))); // no funciona devuelve string                            
                    //        let new_frames = Object.assign({}, ...Object.keys(frames).map(k => ({[Number(k)]: frames[k]}))); 
                    //        this.data['vcd']['frames'] = new_frames
                    //    }
                    //}

                    if(this.data['vcd']['schema_version'] != this.schema_version) {
                        console.warn("The loaded VCD does not have key \'version\' set to " + this.schema_version + '. Unexpected behaviour may happen.')
                    }

                    this.computeLastUid();                    
                }
            }         
            else {
                this.data = vcd_json
                if(this.data['vcd']['schema_version'] != this.schema_version) {
                    console.warn("The loaded VCD does not have key \'version\' set to " + this.schema_version + '. Unexpected behaviour may happen.')
                }
                this.computeLastUid();                    
            }   
		}
	}	
	
	////////////////////////////////////////////////////////////////////////////////////////////////////
    // Private API: inner functions
    ////////////////////////////////////////////////////////////////////////////////////////////////////    
    private getUidToAssign(elementType: ElementType, uid = null): string {
        let uid_string: string      
        let elementTypeName = ElementType[elementType]
        if (uid == null) {
            if(this.useUUID) {
                // Let's use UUIDs
                uid_string = uuidv4()
            }
            else {
                // Let's use integers, and return a string
                this.lastUID[elementTypeName] += 1;  // If null is provided, let's use the next one available            
                uid_string = this.lastUID[elementTypeName].toString();
            }
            
        }
        else {
            // uid is not null, let's see if it's a string, and then if it's a number inside or a UUID (32 chars)
            
            if(typeof uid == "number") {
                // Ok, user provided a number, let's convert into string and proceed
                let uid_number = uid    
                if (uid_number > this.lastUID[elementTypeName]) {
                    this.lastUID[elementTypeName] = uid_number;
                    uid_string = this.lastUID[elementTypeName].toString();
                }
                else {
                    uid_string = uid_number.toString();
                }
            }
            else if(typeof uid == "string") {
                // User provided a string, let's inspect it
                let asNumber = Number(uid)
                if(!isNaN(asNumber)) {
                    // So, it is a number, let's proceed normally
                    uid_string = uid
                }
                else if (/^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/g.test(uid)) {
                    // This looks like a UUID
                    uid_string = uid
                    this.useUUID = true // so next calls automatically create new UUIDs
                }
                else {
                    console.error("ERROR: User provided UID of unsupported type, please use string, either a quoted number or a UUID.")    
                }
            }    
            else {
                console.error("ERROR: User provided UID of unsupported type, please use string, either a quoted number or a UUID.")
            }
        }
                
        return uid_string;
    }

    private setVCDFrameIntervals(frameIntervals: FrameIntervals) {
        if(!frameIntervals.empty())
            this.data['vcd']['frame_intervals'] = frameIntervals.getDict()
    }

    private updateVCDFrameIntervals(frameIntervals: FrameIntervals) {
        // This function creates the union of existing VCD with the input frameIntervals
        if(!frameIntervals.empty()) {
            let fisCurrent = new FrameIntervals(this.data['vcd']['frame_intervals'])
            let fisUnion = fisCurrent.union(frameIntervals)
            this.setVCDFrameIntervals(fisUnion)
        }        
    }  

    private addFrame(frameNum: number) {
        if (!this.data['vcd']['frames'][frameNum]) {
            this.data['vcd']['frames'][frameNum] = {};
        }
    }

    private computeLastUid() {
        this.lastUID = {};
        // Read all objects and fill lastUID
        this.lastUID['object'] = -1;
        if ('objects' in this.data['vcd']) {
            for (const uid of Object.keys(this.data['vcd']['objects'])) {
                if (parseInt(uid) > this.lastUID['object']) {
                    this.lastUID['object'] = parseInt(uid);
                }
            }
        }

        this.lastUID['action'] = -1;
        if ('actions' in this.data['vcd']) {
            for (const uid of Object.keys(this.data['vcd']['actions'])) {
                if (parseInt(uid) > this.lastUID['action']) {
                    this.lastUID['action'] = parseInt(uid);
                }
            }
        }

        this.lastUID['event'] = -1;
        if ('events' in this.data['vcd']) {
            for (const uid of Object.keys(this.data['vcd']['events'])) {
                if (parseInt(uid) > this.lastUID['event']) {
                    this.lastUID['event'] = parseInt(uid);
                }
            }
        }

        this.lastUID['context'] = -1;
        if ('contexts' in this.data['vcd']) {
            for (const uid of Object.keys(this.data['vcd']['contexts'])) {
                if (parseInt(uid) > this.lastUID['context']) {
                    this.lastUID['context'] = parseInt(uid);
                }
            }
        }

        this.lastUID['relation'] = -1;
        if ('relations' in this.data['vcd']) {
            for (const uid of Object.keys(this.data['vcd']['relations'])) {
                if (parseInt(uid) > this.lastUID['relation']) {
                    this.lastUID['relation'] = parseInt(uid);
                }
            }
        }
    }

    private addFrames(frameIntervals: FrameIntervals, elementType: ElementType, uid: string) {
        if(frameIntervals.empty()) return
        else {
            let elementTypeName = ElementType[elementType]
            // Loop over frames and add
            let fis = frameIntervals.get()
            for(let fi of fis) {
                for(let f=fi[0]; f<=fi[1]; f++)
                {
                    // Add frame
                    this.addFrame(f)
                    // Add element entry
                    let frame = this.getFrame(f)  // TODO: check if this actually returns a pointer and not a copy
                    frame[elementTypeName + 's'] = frame[elementTypeName + 's'] || {}
                    frame[elementTypeName + 's'][uid] = frame[elementTypeName + 's'][uid] || {}
                }
            }
        }
    }

    private addElement(elementType: ElementType, name: string, semanticType: string, frameIntervals = null, uid_ = null, ontUid_ = null, stream = null) {        
        let uid = null
        let ontUid = null
        if (uid_ != null) {
            if(typeof uid_ == "number") {
                console.warn("WARNING: UIDs should be provided as strings, with quotes.")
                uid = uid_.toString()
            }
            else if(typeof uid_ == "string") {
                uid = uid_
            }
            else { console.error("ERROR: Unsupported UID format. Must be string."); return }
        }

        if(ontUid_ != null) {
            if(typeof ontUid_ == "number") {
                console.warn("WARNING: UIDs should be provided as strings, with quotes.")
                ontUid = ontUid_.toString()
            }
            else if(typeof ontUid_ == "string") {
                ontUid = ontUid_
            }
            else { console.error("ERROR: Unsupported UID format. Must be string."); return }
        }
        
        
        // 0.- Check if element already exists
        let elementTypeName = ElementType[elementType];
        let elementExists = this.has(elementType, uid)
        
        // 1.- Get uid to assign
        // This function checks gets the neext UID to assign
        var uidToAssign = this.getUidToAssign(elementType, uid);        

        // 2.- Update Root Element (['vcd']['element']), overwrites content.
        let fisOld = this.getElementFrameIntervals(elementType, uid)  // get it here before this elements' frame_intervals are overwritten
        this.createUpdateElement(elementType, name, semanticType, frameIntervals, uidToAssign, ontUid, stream)
        
        // 3.- Update Frames entries and VCD frame intervals
        if(!frameIntervals.empty()) {
            // 3.1.- Element with explicit frame interval argument, let's study if we need to remove or add
            if(elementExists) {                
                // 3.1.1.- Loop over new to add if not inside olf
                let fisNew = frameIntervals                
                for(let fi of fisNew.get()) {
                    for(let f=fi[0]; f<=fi[1]; f++) {
                        let isInside = fisOld.hasFrame(f)
                        if(!isInside) {
                            // New frame is not inside -> let's add this frame
                            let fi = new FrameIntervals(f)
                            this.addFrames(fi, elementType, uid) // Creates frame and also the (empty) pointer to this element
                            this.updateVCDFrameIntervals(fi)
                        }
                    }
                }
                // 3.1.2.- Remove frames: loop over old to delete old if not inside new
                for(let fi of fisOld.get()) {
                    for(let f=fi[0]; f<=fi[1]; f++) {
                        let isInside = fisNew.hasFrame(f)
                        if(!isInside) {
                            // Old frame not isnide new ones -> let's remove this frame
                            let elementsInFrame = this.data['vcd']['frames'][f][elementTypeName + 's']
                            delete elementsInFrame[uid] // removes this element entry in this frame
                            if (Object.keys(elementsInFrame).length == 0) {  // elements might have end up empty
                                delete this.data['vcd']['frames'][f][elementTypeName + 's']
        
                                if(Object.keys(this.data['vcd']['frames'][f]).length == 0) { // this frame may have ended up being empty                                
                                    // So VCD now has no info in this frame, let's remove it from VCD frame interval
                                    this.rmFrame(f) // removes the frame and updates VCD frame interval accordingly
                                }
                            }
                        }
                    }
                }
            }
            else {
                // As the Element didn't exist before this call, we just need to addFrames
                //let fisElementExisting = this.getElementFrameIntervals(elementType, uidToAssign)
                //let fisElementUnion = frameValue.union(fisElementExisting)
                this.addFrames(frameIntervals, elementType, uidToAssign)
                this.updateVCDFrameIntervals(frameIntervals)
            }
            
        }
        else {
            // 3.2.- This element does not have a specific FrameInterval...
            let vcdFrameIntervals = this.getFrameIntervals()
            if(vcdFrameIntervals.empty()) {
                // ... but VCD has already other elements or info that have established some frame intervals
                // The element is then assumed to exist in all frames: let's add a pointer into all frames (also for Relations!)
                this.addFrames(vcdFrameIntervals, elementType, uidToAssign)
            }
        }   
        return uidToAssign
    }

    private updateElement(elementType: ElementType, uid: string, frameIntervals: FrameIntervals) {
        // This function updates an Element by providing NEW frame intervals
        // It is useful for online processing, as an alternative to using modifyElement()        
        let elementTypeName = ElementType[elementType];
        // Check if this uid exists
        if (!this.data['vcd'][elementTypeName + 's'][uid]) {
            console.warn("WARNING: trying to update a non-existing Element.")
            return false;
        }        

        // Read existing data about this element, so we can call addElement
        var name = this.data['vcd'][elementTypeName + 's'][uid]['name'];
        var semanticType = this.data['vcd'][elementTypeName + 's'][uid]['type'];
        var ontUid = null;
        var stream = null;
        if ('ontology_uid' in this.data['vcd'][elementTypeName + 's'][uid]) {
            ontUid = this.data['vcd'][elementTypeName + 's'][uid]['ontology_uid'];
        }
        if ('stream' in this.data['vcd'][elementTypeName + 's'][uid]) {
            stream = this.data['vcd'][elementTypeName + 's'][uid]['stream'];
        }

        // Call addElement (which internally creates OR updates)
        let fisExisting = this.getElementFrameIntervals(elementType, uid)
        let fisUnion = fisExisting.union(frameIntervals)
        this.addElement(elementType, name, semanticType, fisUnion, uid, ontUid, stream);
        return true
    }

    private modifyElement(elementType: ElementType, uid: string, name= null, semanticType= null, frameInterval = null, ontUid = null, stream = null) {
        this.addElement(elementType, name, semanticType, frameInterval, uid, ontUid, stream)
    }

    private createUpdateElement(elementType: ElementType, name: string, semanticType: string, frameIntervals: FrameIntervals, uid: string, ontUid: string, stream: string) {        
        // 1.- Copy from existing or create new entry (this copies everything, including element_data, element_data_pointers, and frame intervals)
        let elementTypeName = ElementType[elementType];  
        this.data['vcd'][elementTypeName + 's'] = this.data['vcd'][elementTypeName + 's'] || {}
        this.data['vcd'][elementTypeName + 's'][uid] = this.data['vcd'][elementTypeName + 's'][uid] || {}
        let element = this.data['vcd'][elementTypeName + 's'][uid]
        
        // 2.- Copy from arguments
        element['name'] = name
        if(semanticType != null)  element['type'] = semanticType
        if(!frameIntervals.empty())  element['frame_intervals'] = frameIntervals.getDict()
        if(ontUid != null && this.getOntology(ontUid)) element['ontology_uid'] = ontUid
        if(stream != null && this.hasStream(stream)) element['stream'] = stream

        // 3.- Reshape element_data_pointers according to this new FrameIntervals        
        if(!frameIntervals.empty()) {
            if (elementTypeName + '_data_pointers' in element) {
                let edps = element[elementTypeName + '_data_pointers']
                for(let edp_name in edps) { // e.g. edp is 'head'
                    // NOW, we have to UPDATE frame intervals of pointers: NOT ADDING (to add use MODIFY_ELEMENT_DATA) BUT REMOVING
                    // If we compute the intersection frame_intervals, we can copy that into element_data_pointers frame intervals
                    let fisInt = frameIntervals.intersection(new FrameIntervals(edps[edp_name]['frame_intervals']))
                    if(!fisInt.empty()) {
                        element[elementTypeName + '_data_pointers'] = element[elementTypeName + '_data_pointers'] || {}
                        element[elementTypeName + '_data_pointers'][edp_name] = edps[edp_name]
                        element[elementTypeName + '_data_pointers'][edp_name]['frame_intervals'] = fisInt.getDict()
                    }
                }
            }
        }
    }

    private addElementData(elementType: ElementType, uid: string, elementData: types.ObjectData, frameIntervals: FrameIntervals) {
        // 0.- Check if Element
        if(!this.has(elementType, uid)) return
        
        // 1.- If new FrameInterval, update Root Element, frames, and VCD
        // As this frame interval refers to an element_data, we need to NOT delete frames from Element
        if(frameIntervals != null && !frameIntervals.empty()) {
            let element = this.getElement(elementType, uid)
            let ontUid = null
            let stream = null
            if('ontology_uid' in element) ontUid = element['ontology_uid']
            if('stream' in element) stream = element['stream']

            // Prepare union of frame intervals to update element
            let fisElement = this.getElementFrameIntervals(elementType, uid)
            let fisUnion = fisElement.union(frameIntervals)
            this.addElement(elementType, element['name'], element['type'], fisUnion, uid, ontUid, stream)               
        }

        // 2.- Inject/Substitute Element_data
        this.createUpdateElementData(elementType, uid, elementData, frameIntervals)   

        // 3.- Update element_data_pointers
        this.createUpdateElementDataPointers(elementType, uid, elementData, frameIntervals)
    }

    private createUpdateElementDataPointers(elementType: ElementType, uid: string, elementData: types.ObjectData, frameIntervals: FrameIntervals) {
        let elementTypeName = ElementType[elementType]        
        this.data['vcd'][elementTypeName + 's'][uid][elementTypeName + '_data_pointers'] = this.data['vcd'][elementTypeName + 's'][uid][elementTypeName + '_data_pointers'] || {}
        let edp = this.data['vcd'][elementTypeName + 's'][uid][elementTypeName + '_data_pointers']
        edp[elementData.data['name']] = {}  // clean out if already the same element data name
        edp[elementData.data['name']]['type'] = elementData.typeName()
        if(frameIntervals == null){
            edp[elementData.data['name']]['frame_intervals'] = []
        }
        else {
            edp[elementData.data['name']]['frame_intervals'] = frameIntervals.getDict()
        }
        if('attributes' in elementData.data) {
            edp[elementData.data['name']]['attributes'] = {}
            for(let attr_type in elementData.data['attributes']) {  // attr_type might be 'boolean', 'text', 'num', or 'vec'
                for(let attr of elementData.data['attributes'][attr_type]) {
                    edp[elementData.data['name']]['attributes'][attr['name']] = attr_type    
                }               
            }
        }
    }

    private createUpdateElementData(elementType: ElementType, uid: string, elementData: types.ObjectData, frameIntervals: FrameIntervals) {        
        let elementTypeName = ElementType[elementType]
        let elementsTypeName = ElementType[elementType] + 's'        

        // 0.- Check if elementData coherent
        if ('in_stream' in elementData.data) {
            if(!this.hasStream(elementData.data['in_stream'])) { return }               
        }

        // 1.- At "root" XOR "frames", copy from existing or create new entry
        if(frameIntervals.empty()) {
            // 1.1.- Static
            let element = this.getElement(elementType, uid)
            if(element != null) {
                element[elementTypeName + '_data'] = element[elementTypeName + '_data'] || {}
                element[elementTypeName + '_data'][elementData.typeName()] = element[elementTypeName + '_data'][elementData.typeName()] || []  // e.g. "bbox"

                // Find if element_data already there, if so, replace, otherwise, append
                const pos = element[elementTypeName + '_data'][elementData.typeName()].findIndex(item => item.name === elementData.data['name'])
                let found = (pos == -1)?(false):(true)
                if(!found) {
                    // No: then, just push this new element Data
                    element[elementTypeName + '_data'][elementData.typeName()].push(elementData.data);
                }
                else {
                    // Yes: let's substitute
                    element[elementTypeName + '_data'][elementData.typeName()][pos] = elementData.data
                }
            }
            else {
                console.warn("WARNING: Trying to add ObjectData to non-existing Object, uid: " + uid)
            }
        }
        else {
            // 1.2.- Dynamic (create at frames, which already exist because this function is called after addElement())            
            let fis = frameIntervals.get()
            for(let fi of fis) {
                for(let f=fi[0]; f<=fi[1]; f++)
                {                   
                    // Add element_data entry
                    let frame = this.getFrame(f)  // TODO: check if this actually returns a pointer and not a copy
                    if(frame == null) {
                        console.warn("WARNING: createUpdateElementData reaches a frame that does not exist. Inner data flow may be broken.")
                        this.addFrame(f)
                    }
                    frame[elementTypeName + 's'] = frame[elementTypeName + 's'] || {}  // just in case!
                    frame[elementTypeName + 's'][uid] = frame[elementTypeName + 's'][uid] || {}  // just in case!
                    let element = frame[elementTypeName + 's'][uid]
                    element[elementTypeName + '_data'] = element[elementTypeName + '_data'] || {}                    
                    element[elementTypeName + '_data'][elementData.typeName()] = element[elementTypeName + '_data'][elementData.typeName()] || []  // e.g. "bbox"
                    
                    // Find if element_data already there
                    const pos = element[elementTypeName + '_data'][elementData.typeName()].findIndex(item => item.name === elementData.data['name'])
                    let found = (pos == -1)?(false):(true)
                    if(!found) {
                        // No: then, just push this new element Data
                        element[elementTypeName + '_data'][elementData.typeName()].push(elementData.data);
                    }
                    else {
                        // Ok, this is either an error, or a call from "modify", let's substitute
                        element[elementTypeName + '_data'][elementData.typeName()][pos] = elementData.data
                    }
                }
            }            
        }
        // NOTE: Don't update here element_data_pointers, they are updated in createUpdateElementDataPointers
    }

    private rmFrame(frameNum: number) {
        // This function deletes a frame entry from frames, and updates VCD accordingly
        // NOTE: This function does not updates corresponding element or element data entries for this frame (use modifyElement or modifyElementData for such functionality)
        // this function is left private so users can't use it directly: they have to use modifyElement or modifyElementData or other of the removal functions
        if('frames' in this.data['vcd']){
            if(frameNum in this.data['vcd']['frames']){
                delete this.data['vcd']['frames'][frameNum]
                                
                // Remove from VCD frame intervals
                var fisDict = this.data['vcd']['frame_intervals'] || [];        
                var fisDictNew = utils.rmFrameFromFrameIntervals(fisDict, frameNum)                

                // Now substitute                
                this.data['vcd']['frame_intervals'] = fisDictNew;
            }
        }        
    }    

    ////////////////////////////////////////////////////////////////////////////////////////////////////
    // Public API: add, update
    ////////////////////////////////////////////////////////////////////////////////////////////////////
    public addFileVersion(version: string) {
        this.data['vcd']['file_version'] = version
    }

    public addMetadataProperties(properties: object) {        
        var prop = this.data['vcd']['metadata']['properties'] || {};
        Object.assign(prop, properties);        
    }

    public addName(name: string) {        
        this.data['vcd']['name'] = name;
    }

    public addAnnotator(annotator: string) {        
        if (!this.data['vcd']['metadata']) {
            this.data['vcd']['metadata'] = {};
        }
        this.data['vcd']['metadata']['annotator'] = annotator;
    }

    public addComment(comment: string) {        
        if (!this.data['vcd']['metadata']) {
            this.data['vcd']['metadata'] = {};
        }
        this.data['vcd']['metadata']['comment'] = comment;
    }

    public addOntology(ontologyName: string): string {
        this.data['vcd']['ontologies'] = this.data['vcd']['ontologies'] || {};
        for (const ont_uid in this.data['vcd']['ontologies']) {
            if (this.data['vcd']['ontologies'][ont_uid] == ontologyName) {
                console.warn('WARNING: adding an already existing ontology');
                return null;
            }
        }
        var length = Object.keys(this.data['vcd']['ontologies']).length;
        this.data['vcd']['ontologies'][length.toString()] = ontologyName;
        return length.toString();
    }

    public addStream(streamName: string, uri: string, description: string, sensorType: StreamType) {       
        this.data['vcd']['metadata'] = this.data['vcd']['metadata'] || {};
        this.data['vcd']['metadata']['streams'] = this.data['vcd']['metadata']['streams'] || {};
        this.data['vcd']['metadata']['streams'][streamName] = this.data['vcd']['metadata']['streams'][streamName] || {};
        
        this.data['vcd']['metadata']['streams'][streamName] = {
            'description': description, 'uri': uri, 'type': sensorType
        }        
    }

    public addFrameProperties(frameNum: number, timestamp = null, additionalProperties = null) {        
        this.addFrame(frameNum);  // this function internally checks if( the frame already exists
        this.data['vcd']['frames'][frameNum]['frame_properties'] = this.data['vcd']['frames'][frameNum]['frame_properties'] || {};

        if (timestamp != null) {
            if(timestamp instanceof String) {
                this.data['vcd']['frames'][frameNum]['frame_properties']['timestamp'] = timestamp
            }
        }

        if (additionalProperties != null) {
            if(additionalProperties instanceof Object) {
                Object.assign(this.data['vcd']['frames'][frameNum]['frame_properties'], additionalProperties)
            }
        }     
    }

    public addOdometry(frameNum: number, odometry: types.Odometry) {
        this.addFrame(frameNum) // this function internally checks if the frame already exists
        this.data['vcd']['frames'][frameNum]['frame_properties'] = this.data['vcd']['frames'][frameNum]['frame_properties'] || {};
        Object.assign(this.data['vcd']['frames'][frameNum]['frame_properties'], odometry.data)  // internally odometry.data has 'odometry' entry
    }

    public addStreamProperties(streamName: string, properties: object, intrinsics =null, extrinsics = null, streamSync = null) {
        let has_arguments = false
        let frameNum: number
        if(intrinsics != null && intrinsics instanceof types.Intrinsics) { has_arguments = true }
        if(extrinsics != null && extrinsics instanceof types.Extrinsics) { has_arguments = true }
        if(properties != null && properties instanceof Object) { has_arguments = true }
        if(streamSync != null && streamSync instanceof types.StreamSync) {
            has_arguments = true
            if( streamSync.frameVcd != null) { frameNum = streamSync.frameVcd }
            else { frameNum = null }
        }
        else { frameNum = null }

        if (!has_arguments) {
            return
        }
                
        // This function can be used to add stream properties. if( frame_num is defined, the information is embedded
        // inside 'frame_properties' of the specified frame. Otherwise, the information is embedded into
        // 'stream_properties' inside 'metadata'.

        // Find if( this stream is declared
        if ('metadata' in this.data['vcd']) {
            if ('streams' in this.data['vcd']['metadata']) {
                if (streamName in this.data['vcd']['metadata']['streams']) {
                    if (frameNum == null) {
                        // This information is static
                        this.data['vcd']['metadata']['streams'][streamName]['stream_properties'] = this.data['vcd']['metadata']['streams'][streamName]['stream_properties'] || {};
                        
                        if (properties != null) {
                            Object.assign(this.data['vcd']['metadata']['streams'][streamName]['stream_properties'], properties)
                        }
                        if (intrinsics != null) {
                            Object.assign(this.data['vcd']['metadata']['streams'][streamName]['stream_properties'], intrinsics.data)
                        }
                        if (extrinsics != null) {
                            Object.assign(this.data['vcd']['metadata']['streams'][streamName]['stream_properties'], extrinsics.data)
                        }
                        if (streamSync != null) {
                            Object.assign(this.data['vcd']['metadata']['streams'][streamName]['stream_properties'], streamSync.data)
                        }
                    }
                    else {
                        // This is information of the stream for( a specific frame
                        this.addFrame(frameNum); // to add the frame in case it does not exist
                        var frame = this.data['vcd']['frames'][frameNum];
                        frame['frame_properties'] = frame['frame_properties'] || {};
                        frame['frame_properties']['streams'] = frame['frame_properties']['streams'] || {};
                        frame['frame_properties']['streams'][streamName] = frame['frame_properties']['streams'][streamName] || {};
                        frame['frame_properties']['streams'][streamName]['stream_properties'] = frame['frame_properties']['streams'][streamName]['stream_properties'] || {};
                        
                        if (properties != null) {
                            Object.assign(frame['frame_properties']['streams'][streamName]['stream_properties'], properties)
                        }
                        if (intrinsics != null) {
                            Object.assign(frame['frame_properties']['streams'][streamName]['stream_properties'], intrinsics.data)
                        }
                        if (extrinsics != null) {
                            Object.assign(frame['frame_properties']['streams'][streamName]['stream_properties'], extrinsics.data)
                        }
                        if (streamSync != null) {
                            Object.assign(frame['frame_properties']['streams'][streamName]['stream_properties'], streamSync.data)
                        }
                    }
                }
                else {
                    console.warn('WARNING: Trying to add frame sync about non-existing stream');
                }
            }
        }
    }

    public validate(vcd: object) {
        let valid = this.ajv_validate(vcd)
        if (!valid)
            return this.ajv_validate.errors
        else
            return []
    }

    public stringify(pretty = true, validate = true) {
        let stringified_vcd = ''
        if (pretty) {
            stringified_vcd = JSON.stringify(this.data, null, '    ')
        }
        else {
            stringified_vcd = JSON.stringify(this.data)
        }
        if (validate) {
            let validation_errors = this.validate(this.data)
            if(validation_errors.length != 0) {
                console.log("ERROR: loading VCD content not compliant with schema " + this.schema_version);
                console.warn("Creating an empty VCD instead.");
                for(var i = 0; i <validation_errors.length; i++){
                    console.log(validation_errors[i].message);
                }               
            }
        }
        return stringified_vcd
    }

    public stringifyFrame(frameNum: number, dynamicOnly = true, pretty = false) {
        if(!(frameNum in this.data['vcd']['frames'])) {
            console.warn("WARNING: Trying to stringify a non-existing frame")
            return ''
        }

        if(dynamicOnly) {
            if(pretty) { 
                return JSON.stringify(this.data['vcd']['frames'][frameNum], null, '    ')
            }
            else {
                return JSON.stringify(this.data['vcd']['frames'][frameNum])
            }
        }
        else {
            // Need to compose dynamic and static information into a new structure
            // Copy the dynamic info first
            let frame_static_dynamic: object
            Object.assign(frame_static_dynamic, this.data['vcd']['frames'][frameNum])

            // Now the static info for objects, actions, events, contexts and relations
            for(let elementType in ElementType) {
                let elementTypeName = ElementType[elementType]
                // First, elements explicitly defined for this frame
                if(elementTypeName + 's' in this.data['vcd']['frames'][frameNum]) {
                    for (var [uid, content] of Object.entries(this.data['vcd']['frames'][frameNum][elementTypeName + 's'])) {
                        Object.assign(frame_static_dynamic[elementTypeName + 's'][uid], this.data['vcd'][elementTypeName + 's'][uid])
                        // Remove frameInterval entry
                        if('frame_intervals' in frame_static_dynamic[elementTypeName + 's'][uid]) {
                            delete frame_static_dynamic[elementTypeName + 's'][uid]['frame_intervals']
                        }
                    }
                }

                // But also other elements without frame intervals specified, which are assumed to exist during the entire sequence
                if(elementTypeName + 's' in this.data['vcd'] && elementTypeName != 'relation') {
                    for( var [uid, element] of Object.entries(this.data['vcd'][elementTypeName + 's'])) {
                        let frame_intervals_dict = element['frame_intervals']
                        if(Object.keys(frame_intervals_dict).length == 0) {
                            // So the list of frame intervals is empty -> this element lives the entire scene
                            // Let's add it to frame_static_dynamic
                            frame_static_dynamic[elementTypeName + 's'] = frame_static_dynamic[elementTypeName + 's'] || {}  // in case there are no such type of elements already in this frame
                            frame_static_dynamic[elementTypeName + 's'][uid] = {}
                            Object.assign(frame_static_dynamic[elementTypeName + 's'][uid], element)

                            // Remove frameInterval entry
                            if('frame_intervals' in frame_static_dynamic[elementTypeName + 's'][uid]) {
                                delete frame_static_dynamic[elementTypeName + 's'][uid]['frame_intervals']
                            }
                        }
                    }
                }
            }

            if(pretty) { 
                return JSON.stringify(frame_static_dynamic, null, '    ')
            }
            else {
                return JSON.stringify(frame_static_dynamic)
            }
        }
    }


    public updateObject(uid: string, frameValue) {
        // This function is only needed if( no add_object_data calls are used, but the object needs to be kept alive
        return this.updateElement(ElementType.object, uid, new FrameIntervals(frameValue));
    }

    public updateAction(uid: string, frameValue) {
        return this.updateElement(ElementType.action, uid, new FrameIntervals(frameValue));
    }

    public updateContext(uid: string, frameValue) {
        return this.updateElement(ElementType.context, uid, new FrameIntervals(frameValue));
    }

    public updateRelation(uid: string, frameValue) {
        if (this.getRelation(uid) != null) {
            if (!this.relationHasFrameIntervals(uid)) {
                console.warn("WARNING: Trying to update the frame information of a Relation defined as frame-less. Ignoring.")
            }
            else {
                return this.updateElement(ElementType.relation, uid, new FrameIntervals(frameValue));
            }
        }        
    }    

    public addObject(name: string, semanticType: string, frameValue = null, uid = null, ontUid = null, stream = null) {
        return this.addElement(ElementType.object, name, semanticType, new FrameIntervals(frameValue), uid, ontUid, stream);
    }

    public addAction(name: string, semanticType: string, frameValue = null, uid = null, ontUid = null, stream = null) {
        return this.addElement(ElementType.action, name, semanticType, new FrameIntervals(frameValue), uid, ontUid, stream);
    }

    public addEvent(name: string, semanticType: string, frameValue = null, uid = null, ontUid = null, stream = null) {
        return this.addElement(ElementType.event, name, semanticType, new FrameIntervals(frameValue), uid, ontUid, stream);
    }

    public addContext(name: string, semanticType: string, frameValue = null, uid = null, ontUid = null, stream = null) {
        return this.addElement(ElementType.context, name, semanticType, new FrameIntervals(frameValue), uid, ontUid, stream);
    }

    public addRelation(name: string, semanticType: string, frameValue = null, uid = null, ontUid = null) {
        return this.addElement(ElementType.relation, name, semanticType, new FrameIntervals(frameValue), uid, ontUid);        
    }

    public addRdf(relationUid: string, rdfType: RDF, elementUid: string, elementType: ElementType) {
        let elementTypeName = ElementType[elementType]
        if (!this.data['vcd']['relations'][relationUid]) {
            console.warn("WARNING: trying to add RDF to non-existing Relation.")
            return;
        }
        else {
            let relation = this.data['vcd']['relations'][relationUid]
            if (!this.data['vcd'][elementTypeName + 's'][elementUid]) {
                console.warn("WARNING: trying to add RDF using non-existing Element.")
                return;
            }
            else {
                if (rdfType == RDF.subject) {
                    this.data['vcd']['relations'][relationUid]['rdf_subjects'] = this.data['vcd']['relations'][relationUid]['rdf_subjects'] || [];
                    this.data['vcd']['relations'][relationUid]['rdf_subjects'].push(
                        { 'uid': elementUid, 'type': elementTypeName }
                    );
                }
                else {
                    this.data['vcd']['relations'][relationUid]['rdf_objects'] = this.data['vcd']['relations'][relationUid]['rdf_objects'] || [];
                    this.data['vcd']['relations'][relationUid]['rdf_objects'].push(
                        { 'uid': elementUid, 'type': elementTypeName }
                    );
                }                             
            }
        }
    }

    public addRelationObjectAction(name: string, semanticType: string, objectUid: string, actionUid: string, relationUid = null, ontUid = null, frameValue=null) {
        relationUid = this.addRelation(name, semanticType, frameValue, relationUid, ontUid)
        this.addRdf(relationUid, RDF.subject, objectUid, ElementType.object)
        this.addRdf(relationUid, RDF.object, actionUid, ElementType.action)
        return relationUid
    }

    public addRelationActionAction(name: string, semanticType: string, actionUid1: string, actionUid2: string, relationUid = null, ontUid = null, frameValue=null) {
        relationUid = this.addRelation(name, semanticType, frameValue, relationUid, ontUid)
        this.addRdf(relationUid, RDF.subject, actionUid1, ElementType.action)
        this.addRdf(relationUid, RDF.object, actionUid2, ElementType.action)
        return relationUid
    }

    public addRelationObjectObject(name: string, semanticType: string, objectUid1: string, objectUid2: string, relationUid = null, ontUid = null, frameValue=null) {
        relationUid = this.addRelation(name, semanticType, frameValue, relationUid, ontUid)
        this.addRdf(relationUid, RDF.subject, objectUid1, ElementType.object)
        this.addRdf(relationUid, RDF.object, objectUid2, ElementType.object)
        return relationUid
    }

    public addRelationActionObject(name: string, semanticType: string, actionUid: string, objectUid: string, relationUid = null, ontUid = null, frameValue=null) {
        relationUid = this.addRelation(name, semanticType, frameValue, relationUid, ontUid)
        this.addRdf(relationUid, RDF.subject, actionUid, ElementType.action)
        this.addRdf(relationUid, RDF.object, objectUid, ElementType.object)
        return relationUid
    }

    public addRelationSubjectObject(name: string, semanticType: string, subjectType: ElementType, subjectUid: string, objectType: ElementType, objectUid: string, relationUid: null, ontUid: null, frameValue = null) {
        let uid = this.addRelation(name, semanticType, frameValue, relationUid, ontUid)
        this.addRdf(uid, RDF.subject, subjectUid, subjectType)
        this.addRdf(uid, RDF.object, objectUid, objectType)
        return uid
    }    

    public addObjectData(uid: string, objectData: types.ObjectData, frameValue = null) {        
        return this.addElementData(ElementType.object, uid, objectData, new FrameIntervals(frameValue))        
    }

    public addActionData(uid: string, actionData: types.ObjectData, frameValue = null) {
        return this.addElementData(ElementType.action, uid, actionData, new FrameIntervals(frameValue))                
    }

    public addContextData(uid: string, contextData: types.ObjectData, frameValue = null) {
        return this.addElementData(ElementType.context, uid, contextData, new FrameIntervals(frameValue))        
    }

    public addEventData(uid: string, eventData: types.ObjectData, frameValue = null) {
        return this.addElementData(ElementType.event, uid, eventData, new FrameIntervals(frameValue))        
    }

    public modifyAction(uid: string, name= null, semanticType= null, frameValue = null, ontUid = null, stream = null) {
        return this.modifyElement(ElementType.action, uid, name, semanticType, new FrameIntervals(frameValue), ontUid, stream)
    }

    public modifyObject(uid: string, name= null, semanticType= null, frameValue = null, ontUid = null, stream = null) {
        return this.modifyElement(ElementType.object, uid, name, semanticType, new FrameIntervals(frameValue), ontUid, stream)
    }
    public modifyEvent(uid: string, name= null, semanticType= null, frameValue = null, ontUid = null, stream = null) {
        return this.modifyElement(ElementType.event, uid, name, semanticType, new FrameIntervals(frameValue), ontUid, stream)
    }
    public modifyContext(uid: string, name= null, semanticType= null, frameValue = null, ontUid = null, stream = null) {
        return this.modifyElement(ElementType.context, uid, name, semanticType, new FrameIntervals(frameValue), ontUid, stream)
    }
    public modifyRelation(uid: string, name= null, semanticType= null, frameValue = null, ontUid = null, stream = null) {
        return this.modifyElement(ElementType.relation, uid, name, semanticType, new FrameIntervals(frameValue), ontUid, stream)
    }

    public modifyActionData(uid: string, actionData: types.ObjectData, frameValue = null) {        
        return this.addActionData(uid, actionData, frameValue)
    }
    public modifyObjectData(uid: string, objectData: types.ObjectData, frameValue = null) {
        return this.addObjectData(uid, objectData, frameValue)
    }
    public modifyContextData(uid: string, contextData: types.ObjectData, frameValue = null) {
        return this.addContextData(uid, contextData, frameValue)
    }
    public modifyEventData(uid: string, eventData: types.ObjectData, frameValue = null) {
        return this.addEventData(uid, eventData, frameValue)
    }

    public updateElementData(elementType: ElementType, uid: string, elementData: types.ObjectData, frameValue = null) {
        let elementTypeName = ElementType[elementType]
        let element = this.getElement(elementType, uid)
        if(frameValue != null) {
            // Dynamic
            if (element != null) {
                if(elementTypeName + '_data_pointers' in element) {
                    if(elementData.data['name'] in element[elementTypeName + '_data_pointers']) {
                        // It is not a simple call to addElementData with the union of frame intervals
                        // We need to substitute the content for just frameValue, without modifying the rest that must stay as it was
                        
                        // Similar to what is done in addElementData:
                        // 1.- Update Root element, farmes and VCD (just in case this call to updateElementData just adds one frame)
                        let fisExisting = new FrameIntervals(element['frame_intervals'])
                        let fisNew = new FrameIntervals(frameValue)
                        let fisUnion = fisExisting.union(fisNew)
                        let ontUid = null
                        let stream = null
                        if('ontology_uid' in element) ontUid = element['ontology_uid']
                        if('stream' in element) stream = element['stream']
                        this.addElement(elementType, element['name'], element['type'], fisUnion, uid, ontUid, stream)
                        
                        // 2.- Inject the new elementData using the frameValue
                        this.createUpdateElementData(elementType, uid, elementData, fisNew) // this will replace existing content at such frames, or create new entries

                        // 3.- Update element_data_pointers
                        this.createUpdateElementDataPointers(elementType, uid, elementData, fisNew)
                    }
                }
            }
        }
        else {
            // Static: So we can't fuse frame intervals, this is a substitution
            if (element != null) {
                this.addElementData(elementType, uid, elementData, new FrameIntervals(frameValue))
            }
        }       
    }

    public updateActionData(uid: string, actionData: types.ObjectData, frameValue = null) {        
        return this.updateElementData(ElementType.action, uid, actionData, frameValue)
    }
    public updateObjectData(uid: string, objectData: types.ObjectData, frameValue = null) {        
        return this.updateElementData(ElementType.object, uid, objectData, frameValue)
    }
    public updateContextData(uid: string, contextData: types.ObjectData, frameValue = null) {        
        return this.updateElementData(ElementType.context, uid, contextData, frameValue)
    }
    public updateEventData(uid: string, eventData: types.ObjectData, frameValue = null) {        
        return this.updateElementData(ElementType.event, uid, eventData, frameValue)
    }


    ////////////////////////////////////////////////////////////////////////////////////////////////////
    // Get / Read
    ////////////////////////////////////////////////////////////////////////////////////////////////////    
    public getData(): object {
        return this.data;
    }
    
    public hasObjects() {
        return 'objects' in this.data['vcd']
    }

    public hasActions() {
        return 'actions' in this.data['vcd']
    }

    public hasEvents() {
        return 'events' in this.data['vcd']
    }

    public hasContexts() {
        return 'contexts' in this.data['vcd']
    }

    public hasRelations() {
        return 'relations' in this.data['vcd']
    }
    
    public has(elementType: ElementType, uid: string) {
        let elementTypeName = ElementType[elementType]
        if (!this.data['vcd'][elementTypeName + 's']) {
            return false;
        }
        else {
            if (this.data['vcd'][elementTypeName + 's'][uid]) {
                return true;
            }
            else {
                return false;
            }
        }
    }

    public getAll(elementType: ElementType) {
        //
        //Returns all elements of the specified ElementType.
        //e.g. all Object's or Context's
        //
        let elementTypeName = ElementType[elementType]
        return this.data['vcd'][elementTypeName + 's'];
    }

    public getAll2(elementType1: ElementType, elementType2: ElementType) {
        //
        //Returns all elements of the specified ElementType.
        //e.g. all Object's or Context's
        //
        let elementTypeName1 = ElementType[elementType1]
        let elementTypeName2 = ElementType[elementType2]

        var aux = {};
        aux[elementTypeName1 + 's'] = this.data['vcd'][elementTypeName1 + 's'];
        aux[elementTypeName2 + 's'] = this.data['vcd'][elementTypeName2 + 's'];

        return aux;
    }

    public getAll3(elementType1: ElementType, elementType2: ElementType, elementType3: ElementType) {
        //
        //Returns all elements of the specified ElementType.
        //e.g. all Object's or Context's
        //
        let elementTypeName1 = ElementType[ElementType[elementType1]]
        let elementTypeName2 = ElementType[ElementType[elementType2]]
        let elementTypeName3 = ElementType[ElementType[elementType3]]

        var aux = {};
        aux[elementTypeName1 + 's'] = this.data['vcd'][elementTypeName1 + 's'];
        aux[elementTypeName2 + 's'] = this.data['vcd'][elementTypeName2 + 's'];
        aux[elementTypeName3 + 's'] = this.data['vcd'][elementTypeName3 + 's'];

        return aux;
    }

    public getElement(elementType: ElementType, uid: string) {        
        let elementTypeName = ElementType[elementType]

        if (this.data['vcd'][elementTypeName + 's'] == null) {
            console.warn("WARNING: trying to get a " + elementTypeName + " but this VCD has none.")
            return null
        }
        if (this.data['vcd'][elementTypeName + 's'][uid]) {
            return this.data['vcd'][elementTypeName + 's'][uid]
        }
        else {
            console.warn("WARNING: trying to get non-existing " + elementTypeName + " with uid: " + uid)
            return null;
        }
    }

    public getObject(uid: string) {
        return this.getElement(ElementType.object, uid);
    }

    public getAction(uid: string) {
        return this.getElement(ElementType.action, uid);
    }

    public getEvent(uid: string) {
        return this.getElement(ElementType.event, uid);
    }

    public getContext(uid: string) {
        return this.getElement(ElementType.context, uid);
    }

    public getRelation(uid: string) {
        return this.getElement(ElementType.relation, uid);
    }

    public getFrame(frameNum: number) {
        if (this.data['vcd']['frames']) {
            if(frameNum in this.data['vcd']['frames'])
            return this.data['vcd']['frames'][frameNum];
        }
        return null
    }

    public getElementsOfType(elementType: ElementType, type: string): string[] {
        let elementTypeName = ElementType[elementType]
 
        var uids = [];
        for (const uid in this.data['vcd'][elementTypeName + 's']) {
            var element = this.data['vcd'][elementTypeName + 's'][uid];
            if (element['type'] == type) {
                uids.push(uid);
            }
        }
        return uids;
    }

    public getElementsWithElementDataName(elementType: ElementType, dataName: string) {
        let uids = []
        let elementTypeName = ElementType[elementType]
        for(const uid in this.data['vcd'][elementTypeName + 's']){
            let element = this.data['vcd'][elementTypeName + 's'][uid]
            if(elementTypeName + '_data_pointers' in element) {
                for(let name in element[elementTypeName + '_data_pointers']) {
                    if(name == dataName) {
                        uids.push(uid)
                        break
                    }
                }
            }
        }
        return uids
    }

    public getObjectsWithObjectDataName(dataName: string) {
        return this.getElementsWithElementDataName(ElementType.object, dataName)
    }
    public getActionsWithActionDataName(dataName: string) {
        return this.getElementsWithElementDataName(ElementType.action, dataName)
    }
    public getEventsWithEventDataName(dataName: string) {
        return this.getElementsWithElementDataName(ElementType.event, dataName)
    }
    public getContextsWithContextDataName(dataName: string) {
        return this.getElementsWithElementDataName(ElementType.context, dataName)
    }

    public getFramesWithElementDataName(elementType: ElementType, uid: string, dataName: string) {        
        let elementTypeName = ElementType[elementType]
        if(uid in this.data['vcd'][elementTypeName + 's']) {
            let element = this.data['vcd'][elementTypeName + 's'][uid]
            if(elementTypeName + '_data_pointers' in element) {
                for(let name in element[elementTypeName + '_data_pointers']) {
                    if(name == dataName) {
                        return new FrameIntervals(element[elementTypeName + '_data_pointers'][name]['frame_intervals'])
                    }
                }
            }
        }
        return null
    }

    public getFramesWithObjectDataName(uid: string, dataName: string) {
        return this.getFramesWithElementDataName(ElementType.object, uid, dataName)
    }
    public getFramesWithActionDataName(uid: string, dataName: string) {
        return this.getFramesWithElementDataName(ElementType.action, uid, dataName)
    }
    public getFramesWithEventDataName(uid: string, dataName: string) {
        return this.getFramesWithElementDataName(ElementType.event, uid, dataName)
    }
    public getFramesWithContextDataName(uid: string, dataName: string) {
        return this.getFramesWithElementDataName(ElementType.context, uid, dataName)
    }

    public getElementData(elementType: ElementType, uid: string, dataName: string, frameNum = null) {
        if( this.has(elementType, uid)){
            let elementTypeName = ElementType[elementType]
            if(frameNum != null) {
                // Dynamic info
                if(!Number.isInteger(frameNum)) {
                    console.warn("WARNING: Calling getElementData with a non-integer frameNum: " + typeof frameNum)
                }
                let frame = this.getFrame(frameNum)
                if(frame != null) {
                    let element = frame[elementTypeName + 's'][uid]
                    for (const prop in element[elementTypeName + '_data']) {
                        var valArray = element[elementTypeName + '_data'][prop];
                        for (var i = 0; i < valArray.length; i++) {
                            var val = valArray[i];
                            if (val['name'] == dataName) {
                                return val;
                            }
                        }
                    }
                }                
            }
            else{
                // Static info
                let element = this.data['vcd'][elementTypeName + 's'][uid]
                for (const prop in element[elementTypeName + '_data']) {
                    var valArray = element[elementTypeName + '_data'][prop];
                    for (var i = 0; i < valArray.length; i++) {
                        var val = valArray[i];
                        if (val['name'] == dataName) {
                            return val;
                        }
                    }
                }
            }
        }
        else {
            console.warn("WARNING: Asking element data from a non-existing Element.")
        } 
        return null
    }

    public getObjectData(uid: string, dataName: string, frameNum = null) {
        return this.getElementData(ElementType.object, uid, dataName, frameNum)
    }
    public getActionData(uid: string, dataName: string, frameNum = null) {
        return this.getElementData(ElementType.action, uid, dataName, frameNum)
    }
    public getContextData(uid: string, dataName: string, frameNum = null) {
        return this.getElementData(ElementType.context, uid, dataName, frameNum)
    }
    public getEventData(uid: string, dataName: string, frameNum = null) {
        return this.getElementData(ElementType.event, uid, dataName, frameNum)
    }

    public getElementDataPointer(elementType: ElementType, uid: string, dataName: string) {
        if( this.has(elementType, uid)){
            let elementTypeName = ElementType[elementType]
            let element = this.data['vcd'][elementTypeName + 's'][uid]
            if(elementTypeName + '_data_pointers' in element) {
                if( dataName in element[elementTypeName + '_data_pointers']) {
                    return element[elementTypeName + '_data_pointers'][dataName]
                }
            }
        }
        else {
            console.warn("WARNING: Asking element data from a non-existing Element.")
        }
        return null
    }

    public getElementDataFrameIntervals(elementType: ElementType, uid: string, dataName: string): FrameIntervals {
        return new FrameIntervals(this.getElementDataPointer(elementType, uid, dataName)['frame_intervals'])        
    }
    public getObjectDataFrameIntervals(uid: string, dataName: string) {
        return this.getElementDataFrameIntervals(ElementType.object, uid, dataName)
    }
    public getActionDataFrameIntervals(uid: string, dataName: string) {
        return this.getElementDataFrameIntervals(ElementType.action, uid, dataName)
    }
    public getEventDataFrameIntervals(uid: string, dataName: string) {
        return this.getElementDataFrameIntervals(ElementType.event, uid, dataName)
    }
    public getContextDataFrameIntervals(uid: string, dataName: string) {
        return this.getElementDataFrameIntervals(ElementType.context, uid, dataName)
    }

    public getNumElements(elementType: ElementType) {
        let elementTypeName = ElementType[elementType]
        return Object.keys(this.data['vcd'][elementTypeName + 's']).length        
    }

    public getNumObjects() {
        return this.getNumElements(ElementType.object);
    }

    public getNumActions() {
        return this.getNumElements(ElementType.action);
    }

    public getNumEvents() {
        return this.getNumElements(ElementType.event);
    }

    public getNumContexts() {
        return this.getNumElements(ElementType.context);
    }

    public getNumRelations() {
        return this.getNumElements(ElementType.relation);
    }

    public getOntology(ontUid: string) {
        if (this.data['vcd']['ontologies']) {
            if (this.data['vcd']['ontologies'][ontUid]) {
                return this.data['vcd']['ontologies'][ontUid];
            }
        }
        return null;
    }

    public getMetadata() {
        if (this.data['vcd']['metadata']) {
            return this.data['vcd']['metadata'];
        }
        else {
            return {};
        }
    }

    public hasStream(stream: string) {
        let md = this.getMetadata()
        if('streams' in md) {            
            let streamName = StreamType[stream] 
            if (streamName in this.data['vcd']['metadata']['streams']) {
                return true
            }             
            else {
                return false
            }
        }
    }

    public getFrameIntervals(): FrameIntervals {
        if('frame_intervals' in this.data['vcd']) return new FrameIntervals(this.data['vcd']['frame_intervals'])
        else return new FrameIntervals()        
    }

    public getElementFrameIntervals(elementType: ElementType, uid: string) {
        let elementTypeName = ElementType[elementType]
        if (!(elementTypeName + 's' in this.data['vcd'])) {            
            return new FrameIntervals()
        }
        else {
            if(!(uid in this.data['vcd'][elementTypeName + 's']))
                return new FrameIntervals()
            return new FrameIntervals(this.data['vcd'][elementTypeName + 's'][uid]['frame_intervals'])
        }        
    }
    
    public relationHasFrameIntervals(uid: string) {
        let relation = this.getRelation(uid)
        if(relation == null) {
            console.warn("WARNING: Non-existing relation.")
        }
        else {
            if(!('frame_intervals' in relation)) {
                return false
            }
            else {
                if(relation['frame_intervals'].length == 0) {
                    return false
                }
                else return true
            }
        }
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////
    // Remove
    ////////////////////////////////////////////////////////////////////////////////////////////////////    
    public rmElementByType(elementType: ElementType, semanticType: string) {
        // This function removes all Elements of input semanticType
        let elementTypeName = ElementType[elementType]
        var elements = this.data['vcd'][elementTypeName + 's'];

        let uidsToRemove = []
        for (let uid in elements) {
            let element = elements[uid]
            if(element['type'] == semanticType) {
                uidsToRemove.push(uid)
            }
        }

        for(let uid of uidsToRemove) {
            this.rmElement(elementType, uid)
        }
    }

    public rmObjectByType(semanticType: string) {
        this.rmElementByType(ElementType.object, semanticType);
    }

    public rmActionByType(semanticType: string) {
        this.rmElementByType(ElementType.action, semanticType);
    }

    public rmEventByType(semanticType: string) {
        this.rmElementByType(ElementType.event, semanticType);
    }

    public rmContextByType(semanticType: string) {
        this.rmElementByType(ElementType.context, semanticType);
    }

    public rmRelationByType(semanticType: string) {
        this.rmElementByType(ElementType.relation, semanticType);
    }
    
    public rmElement(elementType: ElementType, uid: string) {
        let elementTypeName = ElementType[elementType]
        var elements = this.data['vcd'][elementTypeName + 's'];

        // Get Element from summary
        if(!this.has(elementType, uid)) return

        // Remove from Frames: let's read frameIntervals from summary
        let element = elements[uid];
        for (var i = 0; i < element['frame_intervals'].length; i++) {
            var fi = element['frame_intervals'][i];
            for (var frameNum = fi['frame_start']; frameNum < fi['frame_end'] + 1; frameNum++) {
                var elementsInFrame = this.data['vcd']['frames'][frameNum][elementTypeName + 's'];
                if (uid in elementsInFrame) {
                    delete elementsInFrame[uid];
                }
                if (Object.keys(elementsInFrame).length == 0) {  // objects might have end up empty TODO: test this
                    delete this.data['vcd']['frames'][frameNum][elementTypeName + 's']

                    if(Object.keys(this.data['vcd']['frames'][frameNum]).length == 0) { // this frame may have ended up being empty
                        delete this.data['vcd']['frames'][frameNum]
                    }
                }
            }
        }

        // Delete this element from summary
        delete elements[uid];
    }

    public rmObject(uid: string) {
        this.rmElement(ElementType.object, uid);
    }

    public rmAction(uid: string) {
        this.rmElement(ElementType.action, uid);
    }

    public rmEvent(uid: string) {
        this.rmElement(ElementType.event, uid);
    }

    public rmContext(uid: string) {
        this.rmElement(ElementType.context, uid);
    }

    public rmRelation(uid: string) {
        this.rmElement(ElementType.relation, uid);
    }
}