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

export class UID {
    private uid_str: string
    private uid_int: number
    private uuid: boolean
    constructor(val = null) {
        if(val == null) this.__set("", -1, false)
        else {
            if(Number.isInteger(val)) this.__set(val.toString(), val, false)
            else if(typeof val === 'string') {
                if (val == "") this.__set("", -1, false)
                else {
                    if(!isNaN(Number(val))) this.__set(val, Number(val), false)
                    else if(/^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/g.test(val)) this.__set(val, -1, true)
                    else console.error("ERROR: Unsupported UID string type")
                }
            }
            else {
                console.error("ERROR: Unsupported UID type, use integer or string.")
                this.__set("", -1, false)
            }            
        }
    }
    __set(uid_str: string, uid_int: number, isUuid = false) {
        this.uid_str = uid_str
        this.uid_int = uid_int
        this.uuid = isUuid
    }
    isUuid() {
        return this.uuid
    }
    asStr() {
        return this.uid_str
    }
    asInt() {
        if (this.isUuid())
            console.warn("ERROR: This UID is not numeric, can't call asInt")
        else
            return this.uid_int
    }
    isNone() {
        if(this.uid_int == -1 && this.uid_str == "") return true
        else return false
    }
}

export enum SetMode {
    union = 1,
    replace = 2
}


/**
* VCD 4.3.0
*
* NOTE: This is the Typescript version of VCD 4.3.0 API. Compatibility with VCD 4.2.0 JSON files is not implemented.
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

    private reset() {
        // Main VCD data
        this.data = { 'vcd': {} };
        this.data['vcd']['metadata'] = {};                
        this.data['vcd']['metadata']['schema_version'] = this.schema_version;
        
        // Additional auxiliary structures
        this.lastUID = {};
        this.lastUID[ElementType.object] = -1;
        this.lastUID[ElementType.action] = -1;
        this.lastUID[ElementType.event] = -1;
        this.lastUID[ElementType.context] = -1;
        this.lastUID[ElementType.relation] = -1;
    }

	private init(vcd_json = null, validation = false) {
		if (vcd_json == null) {			
			this.reset();
		}
		else {
            // Load from json, and validate with schema
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

                    if(this.data['vcd']['metadata']['schema_version'] != this.schema_version) {
                        console.error("The loaded VCD does not have key \'version\' set to " + this.schema_version + '. Unexpected behaviour may happen.')
                    }

                    this.computeLastUid();                    
                }
            }         
            else {
                this.data = vcd_json
                if(this.data['vcd']['metadata']['schema_version'] != this.schema_version) {
                    console.error("The loaded VCD does not have key \'version\' set to " + this.schema_version + '. Unexpected behaviour may happen.')
                }
                this.computeLastUid();                    
            }   
		}
	}	
	
	////////////////////////////////////////////////////////////////////////////////////////////////////
    // Private API: inner functions
    ////////////////////////////////////////////////////////////////////////////////////////////////////    
    private getUidToAssign(elementType: ElementType, uid: UID): UID {        
        let uidToAssign
        if (uid.isNone()) {
            if(this.useUUID) {
                // Let's use UUIDs
                uidToAssign = new UID(uuidv4())
            }
            else {
                // Let's use integers
                this.lastUID[elementType] += 1;  // If null is provided, let's use the next one available
                uidToAssign = new UID(this.lastUID[elementType])
            }
        }
        else {
            // uids is not none
            if(!uid.isUuid()) {
                // User provided a number, let's proceed
                if(uid.asInt() > this.lastUID[elementType]) {
                    this.lastUID[elementType] = uid.asInt()
                    uidToAssign = new UID(this.lastUID[elementType])
                }
                else uidToAssign = uid
            }
            else {
                // This is a UUID
                this.useUUID = true
                uidToAssign = uid
            }
        }
        return uidToAssign       
    }

    private setVCDFrameIntervals(frameIntervals: FrameIntervals) {
        if(!frameIntervals.empty())
            this.data['vcd']['frame_intervals'] = frameIntervals.getDict()
    }

    private updateVCDFrameIntervals(frameIntervals: FrameIntervals) {
        // This function creates the union of existing VCD with the input frameIntervals
        if(!frameIntervals.empty()) {
            this.data['vcd']['frame_intervals'] = this.data['vcd']['frame_intervals'] || []
            let fisCurrent = new FrameIntervals(this.data['vcd']['frame_intervals'])
            let fisUnion = fisCurrent.union(frameIntervals)
            this.setVCDFrameIntervals(fisUnion)
        }        
    }  

    private addFrame(frameNum: number) {
        this.data['vcd']['frames'] = this.data['vcd']['frames'] || {}
        this.data['vcd']['frames'][frameNum] = this.data['vcd']['frames'][frameNum] || {}        
    }

    private computeLastUid() {
        this.lastUID = {};
        // Read all objects and fill lastUID
        this.lastUID[ElementType.object] = -1;
        if ('objects' in this.data['vcd']) {
            for (const uid of Object.keys(this.data['vcd']['objects'])) {
                if (parseInt(uid) > this.lastUID[ElementType.object]) {
                    this.lastUID[ElementType.object] = parseInt(uid);
                }
            }
        }

        this.lastUID[ElementType.action] = -1;
        if ('actions' in this.data['vcd']) {
            for (const uid of Object.keys(this.data['vcd']['actions'])) {
                if (parseInt(uid) > this.lastUID[ElementType.action]) {
                    this.lastUID[ElementType.action] = parseInt(uid);
                }
            }
        }

        this.lastUID[ElementType.event] = -1;
        if ('events' in this.data['vcd']) {
            for (const uid of Object.keys(this.data['vcd']['events'])) {
                if (parseInt(uid) > this.lastUID[ElementType.event]) {
                    this.lastUID[ElementType.event] = parseInt(uid);
                }
            }
        }

        this.lastUID[ElementType.context] = -1;
        if ('contexts' in this.data['vcd']) {
            for (const uid of Object.keys(this.data['vcd']['contexts'])) {
                if (parseInt(uid) > this.lastUID[ElementType.context]) {
                    this.lastUID[ElementType.context] = parseInt(uid);
                }
            }
        }

        this.lastUID[ElementType.relation] = -1;
        if ('relations' in this.data['vcd']) {
            for (const uid of Object.keys(this.data['vcd']['relations'])) {
                if (parseInt(uid) > this.lastUID[ElementType.relation]) {
                    this.lastUID[ElementType.relation] = parseInt(uid);
                }
            }
        }
    }

    private addFrames(frameIntervals: FrameIntervals, elementType: ElementType, uid: UID) {
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
                    frame[elementTypeName + 's'][uid.asStr()] = frame[elementTypeName + 's'][uid.asStr()] || {}
                }
            }
        }
    }

    private setElement(elementType: ElementType, name: string, semanticType: string, frameIntervals: FrameIntervals, uid: UID, ontUid: UID, coordinateSystem: string, setMode: SetMode) {
        let fis = frameIntervals
        if(setMode == SetMode.union) {
            // Union means fusion, we are calling this function to "add" content, not to remove any
            let fis_existing = this.getElementFrameIntervals(elementType, uid.asStr())
            fis = fis_existing.union(frameIntervals)
        }

        // 0.- Get uid_to_assign
        let uidToAssign = this.getUidToAssign(elementType, uid) // NOTE: private functions use UID type for uids

        // 1.- Set the root and frames entires
        this.setElementAtRootAndFrames(elementType, name, semanticType, fis, uidToAssign, ontUid, coordinateSystem)

        return uidToAssign
    }

    private setElementAtRootAndFrames(elementType: ElementType, name: string, semanticType: string, frameIntervals: FrameIntervals, uid: UID, ontUid: UID, coordinateSystem: string) {
        // 1.- Copy from existing or create new entry (this copies everything, including element_data)
        let elementTypeName = ElementType[elementType];
        this.data['vcd'][elementTypeName + 's'] = this.data['vcd'][elementTypeName + 's'] || {}
        this.data['vcd'][elementTypeName + 's'][uid.asStr()] = this.data['vcd'][elementTypeName + 's'][uid.asStr()] || {}
        let element = this.data['vcd'][elementTypeName + 's'][uid.asStr()]

        let fisOld = new FrameIntervals()
        if('frame_intervals' in element) {
            fisOld = new FrameIntervals(element['frame_intervals'])
        }

        // 2.- Copy from arguments
        if(name != null) element['name'] = name
        if(semanticType != null) element['type'] = semanticType
        if(!frameIntervals.empty()) element['frame_intervals'] = frameIntervals.getDict()
        if(!ontUid.isNone() && this.getOntology(ontUid.asStr())) element['ontology_uid'] = ontUid.asStr()
        if(coordinateSystem != null && this.hasCoordinateSystem(coordinateSystem)) element['coordinate_system'] = coordinateSystem

        // 3.- Reshape element_data_pointers according to this new frame_intervals
        if(!frameIntervals.empty()) {
            if(elementTypeName + '_data_pointers' in element) {
                let edps = element[elementTypeName + '_data_pointers']
                for(let edp_name in edps) {
                    // NOW, we have to UPDATE frame intervals of pointers because we have modified the frame_intervals
                    // of the element itself, adn
                    // If we compute the intersection frame_intervals, we can copy that into
                    // element_data_pointers frame intervals
                    let fisInt = frameIntervals.intersection(new FrameIntervals(edps[edp_name]['frame_intervals']))
                    if(!fisInt.empty()) {
                        element[elementTypeName + '_data_pointers'] = element[elementTypeName + '_data_pointers'] || {}
                        element[elementTypeName + '_data_pointers'][edp_name] = edps[edp_name]
                        element[elementTypeName + '_data_pointers'][edp_name]['frame_intervals'] = fisInt.getDict()
                    }
                }
            }
        }

        // 4.- Now set at frames
        let elementExists = this.has(elementType, uid.asStr())
        if(!frameIntervals.empty()) {
            // 2.1.- There is frame_intervals specified
            if(!elementExists) {
                // 2.1.a) Just create the new element
                this.addFrames(frameIntervals, elementType, uid)
                this.updateVCDFrameIntervals(frameIntervals)
            }
            else {
                // 2.1.b) This is a substitution: depending on the new frame_intervals, we may need to delete/add frames
                // Add
                let fisNew = frameIntervals                
                for(let fi of fisNew.get()) {
                    for(let f=fi[0]; f<=fi[1]; f++) {
                        let isInside = fisOld.hasFrame(f)
                        if(!isInside) {
                            // New frame is not inside -> let's add this frame
                            let fi_ = new FrameIntervals(f)
                            this.addFrames(fi_, elementType, uid)
                            this.updateVCDFrameIntervals(fi_)
                        }
                    }
                }
                // Remove
                for(let fi of fisOld.get()) {
                    for(let f=fi[0]; f<=fi[1]; f++) {
                        let isInside = fisNew.hasFrame(f)
                        if(!isInside) {
                            // Old frame not inside new ones -> let's remove this frame
                            let elementsInFrame = this.data['vcd']['frames'][f][elementTypeName + 's']
                            delete elementsInFrame[uid.asStr()] // removes this element entry in this frame
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
        }
        else {
            // 2.2.- The element is declared as static
            if(elementType != ElementType.relation) {  // frame-less relations remain frame-less
                let vcdFrameIntervals = this.getFrameIntervals()
                if(!vcdFrameIntervals.empty()) {
                    // ... but VCD has already other elements or info that have established some frame intervals
                    // The element is then assumed to exist in all frames: let's add a pointer into all frames (also for Relations!)
                    this.addFrames(vcdFrameIntervals, elementType, uid)
                }
            }            
        }
    }

    private setElementData(elementType: ElementType, uid: UID, elementData: types.ObjectData, frameIntervals: FrameIntervals, setMode: SetMode) {
        // Checks
        if(!this.has(elementType, uid.asStr())) {
            console.warn("WARNING: Trying to set element_data for a non-existing element.")
            return
        }
        let element = this.getElement(elementType, uid.asStr())

        // Read existing data about this element, so we can call setElement
        let name = element['name']
        let semanticType = element['type']
        let ontUid = new UID(null)
        let cs = null
        if('ontology_uid' in element) ontUid = new UID(element['ontology_uid'])
        if('coordinate_system' in element) cs = element['coordinate_system']
        if('coordinate_system' in elementData.data) {
            if(!this.hasCoordinateSystem(elementData.data['coordinate_system'])) {
                console.warn("WARNING: Trying to set element_data with a non-declared coordinate system")
                return
            }
        }
        if(frameIntervals.empty() && setMode == SetMode.union)
            setMode = SetMode.replace

        if(setMode == SetMode.replace) {
            // Extend also the container Element just in case the frame_interval of this element_data is beyond it
            // removes/creates frames if needed
            // This call is to modify an existing element_data, which may imply removing some frames
            if(!frameIntervals.empty()) {
                let fisExisting = new FrameIntervals(element['frame_intervals'])
                let fisNew = frameIntervals
                let fisUnion = fisExisting.union(fisNew)
                this.setElement(elementType, name, semanticType, fisUnion, uid, ontUid, cs, setMode)
                this.setElementDataContentAtFrames(elementType, uid, elementData, frameIntervals)
            }
            else {
                // This is a static element_data. If it was declared dynamic before, let's remove it
                this.setElement(elementType, name, semanticType, frameIntervals, uid, ontUid, cs, setMode)
                this.setElementDataContent(elementType, element, uid, elementData)
            }
            // Set the pointers
            this.setElementDataPointers(elementType, uid, elementData, frameIntervals)
        }
        else { // setMode = SetMode.union
            // This call is to add element_data to the element, substituting content if overlap, otherwise adding
            // First, extend also the container Element just in case the frame_interval of this element_data is beyond
            // the currently existing frame_intervals of the Element
            // internally computes the union
            this.setElement(elementType, name, semanticType, frameIntervals, uid, ontUid, cs, setMode)

            if(!frameIntervals.empty()) {
                let fisExisting = new FrameIntervals()
                let elementTypeName = ElementType[elementType]
                if(elementTypeName + '_data_pointers' in element) {
                    let edp = element[elementTypeName + '_data_pointers']
                    if(elementData.data['name'] in edp)
                        fisExisting = new FrameIntervals(edp[elementData.data['name']]['frame_intervals'])
                }
                let fisNew = frameIntervals
                let fisUnion = fisExisting.union(fisNew)

                // Dynamic
                if(element != null) {
                    // It is not a simple call with the union of frame intervals
                    // We need to substitute the content for just this frame_interval, without modifying the rest
                    // that must stay as it was
                    // Loop over the specified frame_intervals to create or substitute the content
                    this.setElementDataContentAtFrames(elementType, uid, elementData, fisNew)
                }
                // Set the pointers (but the pointers we have to update using the union)
                this.setElementDataPointers(elementType, uid, elementData, fisUnion)
            }
            else {
                // Should not reach here because in this function we are already checking this at the beginning
                // Just in case the check is removed, let's put here a second call to this function changing the set-mode
                this.setElementData(elementType, uid, elementData, frameIntervals, SetMode.replace)
            }
        }
    }

    private setElementDataContentAtFrames(elementType: ElementType, uid: UID, elementData: types.ObjectData, frameIntervals: FrameIntervals) {
        // Loop over the specified frame_intervals to create or substitute the content
        // Create entries of the element_data at frames
        let elementTypeName = ElementType[elementType]
        let fis = frameIntervals.get()
        for(let fi of fis) {
            for(let f=fi[0]; f<=fi[1]; f++) {
                // Add element_data entry
                let frame = this.getFrame(f)
                if(frame == null) {
                    this.addFrame(f)
                    frame = this.getFrame(f)
                }
                frame[elementTypeName + 's'] = frame[elementTypeName + 's'] || {}
                frame[elementTypeName + 's'][uid.asStr()] = frame[elementTypeName + 's'][uid.asStr()] || {}
                let element = frame[elementTypeName + 's'][uid.asStr()]
                this.setElementDataContent(elementType, element, uid, elementData)
            }
        }
    }

    private setElementDataContent(elementType: ElementType, element: object, uid: UID, elementData: types.ObjectData ) {
        // Adds the element_data to the corresponding container
        // If an element_data with same name exists, it is substituted
        let elementTypeName = ElementType[elementType]
        element[elementTypeName + '_data'] = element[elementTypeName + '_data'] || {}
        element[elementTypeName + '_data'][elementData.typeName()] = element[elementTypeName + '_data'][elementData.typeName()] || []  // e.g. "bbox"

        // Find if element_data already there, if so, replace, otherwise, append
        const pos = element[elementTypeName + '_data'][elementData.typeName()].findIndex(item => item.name === elementData.data['name'])
        let found = (pos == -1)?(false):(true)
        if(!found) {
            // Not found: then, just push this new element Data
            element[elementTypeName + '_data'][elementData.typeName()].push(elementData.data);
        }
        else {
            // Found: let's substitute
            element[elementTypeName + '_data'][elementData.typeName()][pos] = elementData.data
        }
    }

    private setElementDataPointers(elementType: ElementType, uid: UID, elementData: types.ObjectData, frameIntervals: FrameIntervals) {
        let elementTypeName = ElementType[elementType]
        this.data['vcd'][elementTypeName + 's'][uid.asStr()][elementTypeName + '_data_pointers'] = this.data['vcd'][elementTypeName + 's'][uid.asStr()][elementTypeName + '_data_pointers'] || {}
        let edp = this.data['vcd'][elementTypeName + 's'][uid.asStr()][elementTypeName + '_data_pointers']
        edp[elementData.data['name']] = {}
        edp[elementData.data['name']]['type'] = elementData.typeName()
        if(frameIntervals == null) {
            edp[elementData.data['name']]['frame_intervals'] = []
        }
        else {
            edp[elementData.data['name']]['frame_intervals'] = frameIntervals.getDict()
        }
        if('attributes' in elementData.data) {
            edp[elementData.data['name']]['attributes'] = {}
            for(let attr_type in elementData.data['attributes']) {  // attr_type might be boolean, text, num or vec
                for(let attr of elementData.data['attributes'][attr_type]) {
                    edp[elementData.data['name']]['attributes'][attr['name']] = attr_type
                }
            }
        }
    }

    private rmFrame(frameNum: number) {
        // This function deletes a frame entry from frames, and updates VCD accordingly        
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
        this.data['vcd']['metadata'] = this.data['vcd']['metadata'] || {}
        this.data['vcd']['metadata']['file_version'] = version
    }

    public addMetadataProperties(properties: object) {        
        this.data['vcd']['metadata'] = this.data['vcd']['metadata'] || {}        
        Object.assign(this.data['vcd']['metadata'], properties);        
    }

    public addName(name: string) {      
        this.data['vcd']['metadata'] = this.data['vcd']['metadata'] || {}  
        this.data['vcd']['metadata']['name'] = name;
    }

    public addAnnotator(annotator: string) {        
        this.data['vcd']['metadata'] = this.data['vcd']['metadata'] || {}
        this.data['vcd']['metadata']['annotator'] = annotator;
    }

    public addComment(comment: string) {        
        this.data['vcd']['metadata'] = this.data['vcd']['metadata'] || {}
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

    public addCoordinateSystem(name: string, csType: types.CoordinateSystemType, parentName: string = "", poseWrtParent: Array<number> = [], uid = null) {
        // Create entry
        this.data['vcd']['coordinate_systems'] = this.data['vcd']['coordinate_systems'] || {}
        this.data['vcd']['coordinate_systems'][name] = {
            'type': types.CoordinateSystemType[csType],
            'parent': parentName,
            'pose_wrt_parent': poseWrtParent,
            'children': []
        }

        if(uid != null) {
            Object.assign(this.data['vcd']['coordinate_systems'][name], {'uid': (new UID(uid)).asStr()})
        }

        // Update parents
        if(parentName != "") {
            let found = false
            for(let n in this.data['vcd']['coordinate_systems']) {
                let cs = this.data['vcd']['coordinate_systems'][n]
                if(n == parentName) {
                    found = true
                    cs['children'].push(name)
                }
            }
            if(!found)
                console.warn("WARNING: creating a coordinate system with a non-defined parent coordinate system. Add them in order.")
        }
    }

    public addTransform(frameNum: number, transform: types.Transform) {
        this.addFrame(frameNum)
        this.data['vcd']['frames'][frameNum]['frame_properties'] = this.data['vcd']['frames'][frameNum]['frame_properties'] || {}
        this.data['vcd']['frames'][frameNum]['frame_properties']['transforms'] = this.data['vcd']['frames'][frameNum]['frame_properties']['transforms'] || {}
        Object.assign(this.data['vcd']['frames'][frameNum]['frame_properties']['transforms'], transform.data)
    }

    public addStream(streamName: string, uri: string, description: string, sensorType: StreamType) {               
        this.data['vcd']['streams'] = this.data['vcd']['streams'] || {};
        this.data['vcd']['streams'][streamName] = this.data['vcd']['streams'][streamName] || {};
        
        this.data['vcd']['streams'][streamName] = {
            'description': description, 'uri': uri, 'type': StreamType[sensorType]
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

    public addStreamProperties(streamName: string, properties: object, intrinsics =null, streamSync = null) {
        let has_arguments = false
        let frameNum: number
        if(intrinsics != null && intrinsics instanceof types.Intrinsics) { has_arguments = true }        
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
            if ('streams' in this.data['vcd']) {
                if (streamName in this.data['vcd']['streams']) {
                    if (frameNum == null) {
                        // This information is static
                        this.data['vcd']['streams'][streamName]['stream_properties'] = this.data['vcd']['streams'][streamName]['stream_properties'] || {};
                        
                        if (properties != null) {
                            Object.assign(this.data['vcd']['streams'][streamName]['stream_properties'], properties)
                        }
                        if (intrinsics != null) {
                            Object.assign(this.data['vcd']['streams'][streamName]['stream_properties'], intrinsics.data)
                        }
                        if (streamSync != null) {
                            Object.assign(this.data['vcd']['streams'][streamName]['stream_properties'], streamSync.data)
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

    public addObject(name: string, semanticType: string, frameValue = null, uid = null, ontUid = null, cs = null, setMode: SetMode = SetMode.union) {
        return this.setElement(ElementType.object, name, semanticType, new FrameIntervals(frameValue), new UID(uid), new UID(ontUid), cs, setMode).asStr()
    }

    public addAction(name: string, semanticType: string, frameValue = null, uid = null, ontUid = null, cs = null, setMode: SetMode = SetMode.union) {
        return this.setElement(ElementType.action, name, semanticType, new FrameIntervals(frameValue), new UID(uid), new UID(ontUid), cs, setMode).asStr()
    }

    public addEvent(name: string, semanticType: string, frameValue = null, uid = null, ontUid = null, cs = null, setMode: SetMode = SetMode.union) {
        return this.setElement(ElementType.event, name, semanticType, new FrameIntervals(frameValue), new UID(uid), new UID(ontUid), cs, setMode).asStr()
    }

    public addContext(name: string, semanticType: string, frameValue = null, uid = null, ontUid = null, cs = null, setMode: SetMode = SetMode.union) {
        return this.setElement(ElementType.context, name, semanticType, new FrameIntervals(frameValue), new UID(uid), new UID(ontUid), cs, setMode).asStr()
    }

    public addRelation(name: string, semanticType: string, frameValue = null, uid = null, ontUid = null, setMode: SetMode = SetMode.union) {
        let relation_uid = this.setElement(ElementType.relation, name, semanticType, new FrameIntervals(frameValue), new UID(uid), new UID(ontUid), null, setMode)        
        return relation_uid.asStr()
    }

    public addElement(elementType: ElementType, name: string, semanticType: string, frameValue = null, uid = null, ontUid = null, setMode: SetMode = SetMode.union) {
        return this.setElement(elementType, name, semanticType, new FrameIntervals(frameValue), new UID(uid), new UID(ontUid), null, setMode).asStr()                
    }

    public addRdf(relationUid: string | number, rdfType: RDF, elementUid: string | number, elementType: ElementType) {
        let elementTypeName = ElementType[elementType]
        let rel_uid = new UID(relationUid)
        let el_uid = new UID(elementUid)
        if (!(rel_uid.asStr() in this.data['vcd']['relations'])) {
            console.warn("WARNING: trying to add RDF to non-existing Relation.")
            return
        }
        else {
            let relation = this.data['vcd']['relations'][rel_uid.asStr()]
            if (!(el_uid.asStr() in this.data['vcd'][elementTypeName + 's'])) {
                console.warn("WARNING: trying to add RDF using non-existing Element.")
                return
            }
            else {
                if (rdfType == RDF.subject) {
                    this.data['vcd']['relations'][rel_uid.asStr()]['rdf_subjects'] = this.data['vcd']['relations'][rel_uid.asStr()]['rdf_subjects'] || [];
                    this.data['vcd']['relations'][rel_uid.asStr()]['rdf_subjects'].push(
                        { 'uid': el_uid.asStr(), 'type': elementTypeName }
                    )
                }
                else {
                    this.data['vcd']['relations'][rel_uid.asStr()]['rdf_objects'] = this.data['vcd']['relations'][rel_uid.asStr()]['rdf_objects'] || [];
                    this.data['vcd']['relations'][rel_uid.asStr()]['rdf_objects'].push(
                        { 'uid': el_uid.asStr(), 'type': elementTypeName }
                    )
                }                             
            }
        }
    }

    public addRelationObjectAction(name: string, semanticType: string, objectUid: string | number, actionUid: string | number, relationUid = null, ontUid = null, frameValue=null) {
        // Note: no need to wrap uids as UID, since all calls are public functions, and no access to dict is done.
        relationUid = this.addRelation(name, semanticType, frameValue, relationUid, ontUid)
        this.addRdf(relationUid, RDF.subject, objectUid, ElementType.object)
        this.addRdf(relationUid, RDF.object, actionUid, ElementType.action)
        return relationUid
    }

    public addRelationActionAction(name: string, semanticType: string, actionUid1: string | number, actionUid2: string | number, relationUid = null, ontUid = null, frameValue=null) {
        relationUid = this.addRelation(name, semanticType, frameValue, relationUid, ontUid)
        this.addRdf(relationUid, RDF.subject, actionUid1, ElementType.action)
        this.addRdf(relationUid, RDF.object, actionUid2, ElementType.action)
        return relationUid
    }

    public addRelationObjectObject(name: string, semanticType: string, objectUid1: string | number, objectUid2: string | number, relationUid = null, ontUid = null, frameValue=null) {
        relationUid = this.addRelation(name, semanticType, frameValue, relationUid, ontUid)
        this.addRdf(relationUid, RDF.subject, objectUid1, ElementType.object)
        this.addRdf(relationUid, RDF.object, objectUid2, ElementType.object)
        return relationUid
    }

    public addRelationActionObject(name: string, semanticType: string, actionUid: string | number, objectUid: string | number, relationUid = null, ontUid = null, frameValue=null) {
        relationUid = this.addRelation(name, semanticType, frameValue, relationUid, ontUid)
        this.addRdf(relationUid, RDF.subject, actionUid, ElementType.action)
        this.addRdf(relationUid, RDF.object, objectUid, ElementType.object)
        return relationUid
    }

    public addRelationSubjectObject(name: string, semanticType: string, subjectType: ElementType, subjectUid: string | number, objectType: ElementType, objectUid: string | number, relationUid: null, ontUid: null, frameValue = null) {
        let uid = this.addRelation(name, semanticType, frameValue, relationUid, ontUid)
        this.addRdf(uid, RDF.subject, subjectUid, subjectType)
        this.addRdf(uid, RDF.object, objectUid, objectType)
        return uid
    }    

    public addObjectData(uid: string | number, objectData: types.ObjectData, frameValue = null, setMode: SetMode = SetMode.union) {        
        return this.setElementData(ElementType.object, new UID(uid), objectData, new FrameIntervals(frameValue), setMode)        
    }

    public addActionData(uid: string | number, actionData: types.ObjectData, frameValue = null, setMode: SetMode = SetMode.union) {
        return this.setElementData(ElementType.action, new UID(uid), actionData, new FrameIntervals(frameValue), setMode)                
    }

    public addContextData(uid: string | number, contextData: types.ObjectData, frameValue = null, setMode: SetMode = SetMode.union) {
        return this.setElementData(ElementType.context, new UID(uid), contextData, new FrameIntervals(frameValue), setMode)        
    }

    public addEventData(uid: string | number, eventData: types.ObjectData, frameValue = null, setMode: SetMode = SetMode.union) {
        return this.setElementData(ElementType.event, new UID(uid), eventData, new FrameIntervals(frameValue), setMode)        
    }

    public addElementData(elementType: ElementType, uid: string | number, eventData: types.ObjectData, frameValue = null, setMode: SetMode = SetMode.union) {
        return this.setElementData(elementType, new UID(uid), eventData, new FrameIntervals(frameValue), setMode)        
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////
    // Get / Read
    ////////////////////////////////////////////////////////////////////////////////////////////////////    
    public getData(): object {
        return this.data;
    }
    
    public hasObjects(): boolean{
        return 'objects' in this.data['vcd']
    }

    public hasActions(): boolean {
        return 'actions' in this.data['vcd']
    }

    public hasEvents(): boolean {
        return 'events' in this.data['vcd']
    }

    public hasContexts(): boolean {
        return 'contexts' in this.data['vcd']
    }

    public hasRelations(): boolean {
        return 'relations' in this.data['vcd']
    }
    
    public has(elementType: ElementType, uid: string | number): boolean {
        let elementTypeName = ElementType[elementType]
        if (!this.data['vcd'][elementTypeName + 's']) {
            return false;
        }
        else {
            if (this.data['vcd'][elementTypeName + 's'][(new UID(uid)).asStr()]) {
                return true;
            }
            else {
                return false;
            }
        }
    }

    public hasElementData(elementType: ElementType, uid: string | number, elementData: types.ObjectData): boolean {
        if(!this.has(elementType, uid)) return false
        else {
            let uid_str = new UID(uid).asStr()
            if(!(ElementType[elementType] + '_data_pointers' in this.data['vcd'][ElementType[elementType] + 's'][uid_str])) 
                return false
            let name = elementData.data['name']
            return name in this.data['vcd'][ElementType[elementType] + 's'][uid_str][ElementType[elementType] + '_data_pointers']
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

    public getElement(elementType: ElementType, uid: string | number) {        
        let elementTypeName = ElementType[elementType]
        let uid_str = (new UID(uid)).asStr()
        if (this.data['vcd'][elementTypeName + 's'] == null) {
            console.warn("WARNING: trying to get a " + elementTypeName + " but this VCD has none.")
            return null
        }
        if (this.data['vcd'][elementTypeName + 's'][uid_str]) {
            return this.data['vcd'][elementTypeName + 's'][uid_str]
        }
        else {
            console.warn("WARNING: trying to get non-existing " + elementTypeName + " with uid: " + uid_str)
            return null;
        }
    }

    public getObject(uid: string | number) {
        return this.getElement(ElementType.object, uid);
    }

    public getAction(uid: string | number) {
        return this.getElement(ElementType.action, uid);
    }

    public getEvent(uid: string | number) {
        return this.getElement(ElementType.event, uid);
    }

    public getContext(uid: string | number) {
        return this.getElement(ElementType.context, uid);
    }

    public getRelation(uid: string | number) {
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

    public getFramesWithElementDataName(elementType: ElementType, uid: string | number, dataName: string) {        
        let elementTypeName = ElementType[elementType]
        let uid_str = new UID(uid).asStr()
        if(uid_str in this.data['vcd'][elementTypeName + 's']) {
            let element = this.data['vcd'][elementTypeName + 's'][uid_str]
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

    public getFramesWithObjectDataName(uid: string | number, dataName: string) {
        return this.getFramesWithElementDataName(ElementType.object, uid, dataName)
    }
    public getFramesWithActionDataName(uid: string | number, dataName: string) {
        return this.getFramesWithElementDataName(ElementType.action, uid, dataName)
    }
    public getFramesWithEventDataName(uid: string | number, dataName: string) {
        return this.getFramesWithElementDataName(ElementType.event, uid, dataName)
    }
    public getFramesWithContextDataName(uid: string | number, dataName: string) {
        return this.getFramesWithElementDataName(ElementType.context, uid, dataName)
    }

    public getElementData(elementType: ElementType, uid: string | number, dataName: string, frameNum = null) {
        let uid_str = new UID(uid).asStr()
        if( this.has(elementType, uid)){
            let elementTypeName = ElementType[elementType]
            if(frameNum != null) {
                // Dynamic info
                if(!Number.isInteger(frameNum)) {
                    console.warn("WARNING: Calling getElementData with a non-integer frameNum: " + typeof frameNum)
                }
                let frame = this.getFrame(frameNum)
                if(frame != null) {
                    if(elementTypeName + 's' in frame) {
                        if(uid_str in frame[elementTypeName + 's']) {
                            let element = frame[elementTypeName + 's'][uid_str]
                            if(elementTypeName + '_data' in element) {
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
                            else {
                                // The user asked for the element data of this element for this frame,
                                // but there is no dynamic info
                                // Let's try to return static info
                                if(elementTypeName + 's' in this.data['vcd']) {
                                    if(uid_str in this.data['vcd'][elementTypeName + 's']) {
                                        let element = this.data['vcd'][elementTypeName + 's'][uid_str]
                                        if(elementTypeName + '_data' in element) {
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
                                }
                            }
                        }
                    }
                }                
            }
            else{
                // Static info
                if(elementTypeName + 's' in this.data['vcd']) {
                    if(uid_str in this.data['vcd'][elementTypeName + 's']) {
                        let element = this.data['vcd'][elementTypeName + 's'][uid_str]
                        if(elementTypeName + '_data' in element) {
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
                }
            }
        }
        else {
            console.warn("WARNING: Asking element data from a non-existing Element.")
        } 
        return null
    }

    public getObjectData(uid: string | number, dataName: string, frameNum = null) {
        return this.getElementData(ElementType.object, uid, dataName, frameNum)
    }
    public getActionData(uid: string | number, dataName: string, frameNum = null) {
        return this.getElementData(ElementType.action, uid, dataName, frameNum)
    }
    public getContextData(uid: string | number, dataName: string, frameNum = null) {
        return this.getElementData(ElementType.context, uid, dataName, frameNum)
    }
    public getEventData(uid: string | number, dataName: string, frameNum = null) {
        return this.getElementData(ElementType.event, uid, dataName, frameNum)
    }

    public getElementDataPointer(elementType: ElementType, uid: string | number, dataName: string) {
        let uid_str = new UID(uid).asStr()
        if( this.has(elementType, uid)){
            let elementTypeName = ElementType[elementType]
            if(elementTypeName + 's' in this.data['vcd']) {
                if(uid_str in this.data['vcd'][elementTypeName + 's']) {
                    let element = this.data['vcd'][elementTypeName + 's'][uid_str]
                    if(elementTypeName + '_data_pointers' in element) {
                        if(dataName in element[elementTypeName + '_data_pointers']) {
                            return element[elementTypeName + '_data_pointers'][dataName]
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

    public getElementDataFrameIntervals(elementType: ElementType, uid: string | number, dataName: string): FrameIntervals {
        return new FrameIntervals(this.getElementDataPointer(elementType, uid, dataName)['frame_intervals'])        
    }
    public getObjectDataFrameIntervals(uid: string | number, dataName: string) {
        return this.getElementDataFrameIntervals(ElementType.object, uid, dataName)
    }
    public getActionDataFrameIntervals(uid: string | number, dataName: string) {
        return this.getElementDataFrameIntervals(ElementType.action, uid, dataName)
    }
    public getEventDataFrameIntervals(uid: string | number, dataName: string) {
        return this.getElementDataFrameIntervals(ElementType.event, uid, dataName)
    }
    public getContextDataFrameIntervals(uid: string | number, dataName: string) {
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

    public getOntology(ontUid: string | number) {
        let ond_uid_str = new UID(ontUid).asStr()
        if (this.data['vcd']['ontologies']) {
            if (this.data['vcd']['ontologies'][ond_uid_str]) {
                return this.data['vcd']['ontologies'][ond_uid_str];
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

    public hasCoordinateSystem(cs: string): boolean {
        if('coordinate_systems' in this.data['vcd']) {
            if(cs in this.data['vcd']['coordinate_systems']) return true            
        }
        return false
    }

    public hasStream(stream: string): boolean {
        let md = this.getMetadata()
        if('streams' in md) {            
            let streamName = StreamType[stream] 
            if (streamName in this.data['vcd']['streams']) {
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

    public getElementFrameIntervals(elementType: ElementType, uid: string | number) {
        let elementTypeName = ElementType[elementType]
        let uid_str = new UID(uid).asStr()
        if (!(elementTypeName + 's' in this.data['vcd'])) {            
            return new FrameIntervals()
        }
        else {
            if(!(uid_str in this.data['vcd'][elementTypeName + 's']))
                return new FrameIntervals()
            return new FrameIntervals(this.data['vcd'][elementTypeName + 's'][uid_str]['frame_intervals'])
        }        
    }
    
    public relationHasFrameIntervals(uid: string | number) {
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
    
    public rmElement(elementType: ElementType, uid: string | number) {
        let elementTypeName = ElementType[elementType]
        var elements = this.data['vcd'][elementTypeName + 's'];
        let uid_str = new UID(uid).asStr()

        // Get Element from summary
        if(!this.has(elementType, uid)) return

        // Remove from Frames: let's read frameIntervals from summary
        let element = elements[uid_str];
        for (var i = 0; i < element['frame_intervals'].length; i++) {
            var fi = element['frame_intervals'][i];
            for (var frameNum = fi['frame_start']; frameNum < fi['frame_end'] + 1; frameNum++) {
                var elementsInFrame = this.data['vcd']['frames'][frameNum][elementTypeName + 's'];
                if (uid in elementsInFrame) {
                    delete elementsInFrame[uid_str];
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
        delete elements[uid_str];
    }

    public rmObject(uid: string | number) {
        this.rmElement(ElementType.object, uid);
    }

    public rmAction(uid: string | number) {
        this.rmElement(ElementType.action, uid);
    }

    public rmEvent(uid: string | number) {
        this.rmElement(ElementType.event, uid);
    }

    public rmContext(uid: string | number) {
        this.rmElement(ElementType.context, uid);
    }

    public rmRelation(uid: string | number) {
        this.rmElement(ElementType.relation, uid);
    }
}