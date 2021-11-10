/**
VCD (Video Content Description) library v5.0.0

Project website: http://vcd.vicomtech.org

Copyright (C) 2020, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a library to create and manage VCD content version 5.0.0.
VCD is distributed under MIT License. See LICENSE.

*/

import * as utils from "./vcd.utils"
import * as types from "./vcd.types"
import * as schema from "./vcd.schema"

import * as Ajv from 'ajv'
import { v4 as uuidv4 } from 'uuid'
import { type } from "os"
import { assert } from "console"

//const Ajv = require("ajv").default 
const ajv = new Ajv.default()

export class ResourceUID{
    /*
    This is a class to add additional UIDs to an element, according to its representation
    in another resource.
    E.g. A Lane or Road object labeled in VCD can correspond to a Lane or Road element in an
    OpenDrive file.
    Then the OpenDrive file path is added with
    res_opendrive_uidopenlabel.add_resource("../resources/xodr/multi_intersections.xodr")
    And any object added can add the elment UID at the resource using this ResourceUID class
    openlabel.add_object("road1", "road", res_uid=ResourceUID(res_opendrive_uid, 217))
    */
   private resourceUid;
   private idAtResource;
   constructor(resourceUid, idAtResource){
       this.resourceUid= new UID(resourceUid) // this is the UID of the resource file
       this.idAtResource=new UID(idAtResource)  // this is the UID of the element in the resource
   }

   asDict(){
        return {[this.resourceUid.asStr()]: this.idAtResource.asStr()}
   }

}

export enum ElementType {
    object = 0,
    action = 1,
    event = 2,
    context = 3,
    relation = 4,
    tag=5
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
    getLength() {
        let length = 0
        for(let fi of this.fisNum) {
            length += fi[1] + 1 - fi[0]
        }
        return length
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

    equals(frameIntervals: FrameIntervals): boolean {
        let fisInt = this.intersection(frameIntervals)
        let fisUnion = this.union(frameIntervals)
        if(fisInt.getLength() == fisUnion.getLength()) return true
        else return false
    }
    contains(frameIntervals: FrameIntervals): boolean {
        let fisInt = this.intersection(frameIntervals)
        if(fisInt.getLength() == frameIntervals.getLength()) return true
        else return false
    }
    isContainedBy(frameIntervals: FrameIntervals): boolean {
        let fisInt = this.intersection(frameIntervals)
        if(fisInt.getLength() == this.getLength()) return true
        else return false
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
* VCD 5.0.0
*
* NOTE: This is the Typescript version of VCD 5.0.0 API. Compatibility with VCD 4.2.0 JSON files is not implemented.
*
* This class is the main manager of VCD 5.0.0 content.
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
    private schema_version = schema.openlabel_schema_version
    private schema = schema.openlabel_schema     
    //private ajv = new Ajv()  // here or as a global variate outside
    //private ajv_validate = this.ajv.compile(this.schema)
    private ajv_validate = ajv.compile(this.schema)
	
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
        this.data = { 'openlabel': {} };
        this.data['openlabel']['metadata'] = {};                
        this.data['openlabel']['metadata']['schema_version'] = this.schema_version;
        
        // Additional auxiliary structures
        this.lastUID = {};
        this.lastUID[ElementType.object] = -1;
        this.lastUID[ElementType.action] = -1;
        this.lastUID[ElementType.event] = -1;
        this.lastUID[ElementType.context] = -1;
        this.lastUID[ElementType.relation] = -1;
        this.lastUID[ElementType.tag] = -1;
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

                    // In VCD 4.3.1 uids are strings, because they can be numeric strings, or UUIDs
                    // but frames are still ints. However, it looks that in Typescript, JSON.parse reads as integer
                    //if('frames' in this.data['openlabel']){
                    //    let frames = this.data['openlabel']['frames']
                    //    if(Object.keys(frames).length > 0){                                                        
                            //let new_frames = Object.assign({}, ...Object.entries(frames).map(([k, v]) => ({[Number(k)]: v}))); // no funciona devuelve string                            
                    //        let new_frames = Object.assign({}, ...Object.keys(frames).map(k => ({[Number(k)]: frames[k]}))); 
                    //        this.data['openlabel']['frames'] = new_frames
                    //    }
                    //}

                    if(this.data['openlabel']['metadata']['schema_version'] != this.schema_version) {
                        console.error("The loaded VCD does not have key \'version\' set to " + this.schema_version + '. Unexpected behaviour may happen.')
                    }

                    this.computeLastUid();                    
                }
            }         
            else {
                this.data = vcd_json
                if(this.data['openlabel']['metadata']['schema_version'] != "1.0.0") {
                    console.error("The loaded openlabel does not have key \'version\' set to 1.0.0. Unexpected behaviour may happen.")
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
            this.data['openlabel']['frame_intervals'] = frameIntervals.getDict()
    }

    private updateVCDFrameIntervals(frameIntervals: FrameIntervals) {
        // This function creates the union of existing VCD with the input frameIntervals
        if(!frameIntervals.empty()) {
            this.data['openlabel']['frame_intervals'] = this.data['openlabel']['frame_intervals'] || []
            let fisCurrent = new FrameIntervals(this.data['openlabel']['frame_intervals'])
            let fisUnion = fisCurrent.union(frameIntervals)
            this.setVCDFrameIntervals(fisUnion)
        }        
    }  

    private addFrame(frameNum: number) {
        this.data['openlabel']['frames'] = this.data['openlabel']['frames'] || {}
        this.data['openlabel']['frames'][frameNum] = this.data['openlabel']['frames'][frameNum] || {}        
    }

    private computeLastUid() {
        this.lastUID = {};
        // Read all objects and fill lastUID
        this.lastUID[ElementType.object] = -1;
        if ('objects' in this.data['openlabel']) {
            for (const uid of Object.keys(this.data['openlabel']['objects'])) {
                if (parseInt(uid) > this.lastUID[ElementType.object]) {
                    this.lastUID[ElementType.object] = parseInt(uid);
                }
            }
        }

        this.lastUID[ElementType.action] = -1;
        if ('actions' in this.data['openlabel']) {
            for (const uid of Object.keys(this.data['openlabel']['actions'])) {
                if (parseInt(uid) > this.lastUID[ElementType.action]) {
                    this.lastUID[ElementType.action] = parseInt(uid);
                }
            }
        }

        this.lastUID[ElementType.event] = -1;
        if ('events' in this.data['openlabel']) {
            for (const uid of Object.keys(this.data['openlabel']['events'])) {
                if (parseInt(uid) > this.lastUID[ElementType.event]) {
                    this.lastUID[ElementType.event] = parseInt(uid);
                }
            }
        }

        this.lastUID[ElementType.context] = -1;
        if ('contexts' in this.data['openlabel']) {
            for (const uid of Object.keys(this.data['openlabel']['contexts'])) {
                if (parseInt(uid) > this.lastUID[ElementType.context]) {
                    this.lastUID[ElementType.context] = parseInt(uid);
                }
            }
        }

        this.lastUID[ElementType.relation] = -1;
        if ('relations' in this.data['openlabel']) {
            for (const uid of Object.keys(this.data['openlabel']['relations'])) {
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

    private setElement(elementType: ElementType, name: string, semanticType: string, frameIntervals: FrameIntervals, uid: UID, ontUid: UID, coordinateSystem: string, setMode: SetMode, resUid) {
        let fis = frameIntervals
        if(setMode == SetMode.union) {
            // Union means fusion, we are calling this function to "add" content, not to remove any
            let fis_existing = this.getElementFrameIntervals(elementType, uid.asStr())
            fis = fis_existing.union(frameIntervals)
        }

        // 0.- Get uid_to_assign
        let uidToAssign = this.getUidToAssign(elementType, uid) // NOTE: private functions use UID type for uids

        // 1.- Set the root and frames entries
        this.setElementAtRootAndFrames(elementType, name, semanticType, fis, uidToAssign, ontUid, coordinateSystem,resUid)

        return uidToAssign
    }

    private setElementAtRootAndFrames(elementType: ElementType, name: string, semanticType: string, frameIntervals: FrameIntervals, uid: UID, ontUid: UID, coordinateSystem: string, resUid) {
        // 1.- Copy from existing or create new entry (this copies everything, including element_data)
        let elementExisted = this.has(elementType, uid.asStr())
        let elementTypeName = ElementType[elementType];
        let uidstr = uid.asStr()
        this.data['openlabel'][elementTypeName + 's'] = this.data['openlabel'][elementTypeName + 's'] || {}  // creates an entry for this elementype if not existing already, e.g. "objects"
        this.data['openlabel'][elementTypeName + 's'][uidstr] = this.data['openlabel'][elementTypeName + 's'][uidstr] || {} // creates an entry for this element if not existing already
        let element = this.data['openlabel'][elementTypeName + 's'][uidstr]  // read the element at the root (might be empty if created in this call)

        //let fisOld = new FrameIntervals()
        let fisOld = new FrameIntervals()
        if('frame_intervals' in element) {
            fisOld = new FrameIntervals(element['frame_intervals']) // might be empty
        }

        // Next body of the function considers the following 3 cases
        // 1.1.- Subcase A: if it existed, but defined as static, and now we are given a non-empty frame intervals: static->dynamic        
        // 1.2.- Subcase B: if it existed, but defined as non-static (with frame intervals), and we are given now an empty frameInterval: dynamic -> static        
        // 1.3.- Subcase C: static->static, dynamic->dynamic
        // Note that "element" also may contain static element_data at root

        // 2.- Copy from arguments
        if(name != null) element['name'] = name
        if(semanticType != null) element['type'] = semanticType        
        if(!frameIntervals.empty() || (elementExisted && !fisOld.empty()))
            element['frame_intervals'] = frameIntervals.getDict()  // so, either the newFis has something, or the fisOld had something (in which case needs to be substituted)
        // Under the previous control, no 'frame_intervals' field is added to newly created static elements -> should 'frame_intervals' be mandatory?
        if(!ontUid.isNone() && this.getOntology(ontUid.asStr())) element['ontology_uid'] = ontUid.asStr()
        if(resUid != null) {
        //let resourceUid = resUid.resource_uid
        let resourceUid = resUid.resourceUid
            if(!resourceUid.isNone() && this.getResource(resourceUid.asStr()))
                element['resource_uid'] = resUid.asDict()
        }
        if(coordinateSystem != null && this.hasCoordinateSystem(coordinateSystem)) element['coordinate_system'] = coordinateSystem

        // 2.bis.- Add mandatory rdf_subjects and rdf_objects to Relation
        if (elementType == ElementType.relation)
        {
            if(!('rdf_subjects' in element)) element['rdf_subjects'] = []
            if(!('rdf_objects' in element)) element['rdf_objects'] = []
        }

        // 3.- Reshape element_data_pointers according to this new frame_intervals
        // Also if the new frameIntervals is empty, in which case, we convert all element data into static        
        if(elementTypeName + '_data_pointers' in element) {
            let edps = element[elementTypeName + '_data_pointers']
            for(let edp_name in edps) {
                // NOW, we have to UPDATE frame intervals of pointers because we have modified the frame_intervals
                // of the element itself, and
                // If we compute the intersection frame_intervals, we can copy that into
                // element_data_pointers frame intervals
                let fisInt = new FrameIntervals()
                if(!frameIntervals.empty())
                    fisInt = frameIntervals.intersection(new FrameIntervals(edps[edp_name]['frame_intervals']))
                
                // Update the pointers
                element[elementTypeName + '_data_pointers'] = element[elementTypeName + '_data_pointers'] || {}
                element[elementTypeName + '_data_pointers'][edp_name] = edps[edp_name]
                element[elementTypeName + '_data_pointers'][edp_name]['frame_intervals'] = fisInt.getDict()                
            }
        }
        
        // 4.- Now set at frames
        if(!frameIntervals.empty()) {
            // 2.1.- There is frame_intervals specified
            if(!elementExisted) {
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
                if(elementExisted && fisOld.empty()) {
                    // Ok, the element was originally static (thus with fisOld empty)
                    // so potentially there are pointers of the element in all frames (in case there are frames)
                    // Now the element is declared with a specific frame intervals. Then we first need to remove all element
                    // entries (pointers) in all OTHER frames
                    let vcdFrameIntervals = this.getFrameIntervals()
                    if(!vcdFrameIntervals.empty()) {
                        for(let fi of vcdFrameIntervals.get()) {
                            for(let f=fi[0]; f<=fi[1]; f++) {
                                if(!fisNew.hasFrame(f)) {  // Only for those OTHER frames not those just added
                                    let elementsInFrame = this.data['openlabel']['frames'][f][elementTypeName + 's']
                                    if(uidstr in elementsInFrame) {
                                        delete elementsInFrame[uidstr] // removes this element entry in this frame

                                        if (Object.keys(elementsInFrame).length == 0) {  // elements might have end up empty
                                            delete this.data['openlabel']['frames'][f][elementTypeName + 's']
                    
                                            if(Object.keys(this.data['openlabel']['frames'][f]).length == 0) { // this frame may have ended up being empty                                
                                                // So VCD now has no info in this frame, let's remove it from VCD frame interval
                                                this.rmFrame(f) // removes the frame and updates VCD frame interval accordingly
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                // Next loop for is for the case fisOld wasn't empty, so we just need to remove old content
                for(let fi of fisOld.get()) {
                    for(let f=fi[0]; f<=fi[1]; f++) {
                        let isInside = fisNew.hasFrame(f)
                        if(!isInside) {
                            // Old frame not inside new ones -> let's remove this frame
                            let elementsInFrame = this.data['openlabel']['frames'][f][elementTypeName + 's']
                            delete elementsInFrame[uidstr] // removes this element entry in this frame
                            if (Object.keys(elementsInFrame).length == 0) {  // elements might have end up empty
                                delete this.data['openlabel']['frames'][f][elementTypeName + 's']
        
                                if(Object.keys(this.data['openlabel']['frames'][f]).length == 0) { // this frame may have ended up being empty                                
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
            // If the VCD has frame intervals, then, Element needs to be added as a pointer in all VCD frames
            if(elementType != ElementType.relation) {  // frame-less relations remain frame-less
                let vcdFrameIntervals = this.getFrameIntervals()
                if(!vcdFrameIntervals.empty()) {
                    // ... but VCD has already other elements or info that have established some frame intervals
                    // The element is then assumed to exist in all frames: let's add a pointer into all frames (also for Relations!)
                    this.addFrames(vcdFrameIntervals, elementType, uid)
                }
            }            

            // But, if the element existed previously, and it was dynamic, there is already information inside frames. If there is elementData at frames, they are removed
            if(!fisOld.empty()) {
                // Let's check the elementData at those frames
                this.rmElementDataFromFrames(elementType, uid.asStr(), fisOld.get())                

                // Additionally, we need to remove element entries at frames, and frames entirely to clean-up
                for(let fi of fisOld.get()) {
                    for(let f=fi[0]; f<=fi[1]; f++) {
                        let elementsInFrame = this.data['openlabel']['frames'][f][elementTypeName + 's']
                        delete elementsInFrame[uidstr]
                        // Clean-up
                        if (Object.keys(elementsInFrame).length == 0) {  // elements might have end up empty
                            delete this.data['openlabel']['frames'][f][elementTypeName + 's']    
                            if(Object.keys(this.data['openlabel']['frames'][f]).length == 0) { // this frame may have ended up being empty                                
                                // So VCD now has no info in this frame, let's remove it from VCD frame interval
                                this.rmFrame(f) // removes the frame and updates VCD frame interval accordingly
                            }
                        }
                    }
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
        let resUid = new ResourceUID(null,null)
        let cs = null
        if('ontology_uid' in element) ontUid = new UID(element['ontology_uid'])
        if('resource_uid' in element){
            resUid = new ResourceUID(element['resource_uid'].keys()[0],element['resource_uid'].values()[0])
        }
        if('coordinate_system' in element) cs = element['coordinate_system']
        if('coordinate_system' in elementData.data) {
            if(!this.hasCoordinateSystem(elementData.data['coordinate_system'])) {
                console.warn("WARNING: Trying to set element_data with a non-declared coordinate system")
                return
            }
        }
        if(frameIntervals.empty() && setMode == SetMode.union && !(elementData instanceof types.Mesh))
            setMode = SetMode.replace

        if(setMode == SetMode.replace) {
            // Extend also the container Element just in case the frame_interval of this element_data is beyond it
            // removes/creates frames if needed
            // This call is to modify an existing element_data, which may imply removing some frames
            if(!frameIntervals.empty()) {
                let fisExisting = new FrameIntervals(element['frame_intervals'])
                let fisNew = frameIntervals
                let fisUnion = fisExisting.union(fisNew)
                this.setElement(elementType, name, semanticType, fisUnion, uid, ontUid, cs, setMode,resUid)
                this.setElementDataContentAtFrames(elementType, uid, elementData, frameIntervals)
            }
            else {
                // This is a static element_data. If it was declared dynamic BEFORE, let's remove it
                //this.setElement(elementType, name, semanticType, frameIntervals, uid, ontUid, cs, setMode)  // Why this call to set element? let's do just the modification of the elementData                
                if(this.hasElementData(elementType, uid.asStr(), elementData)) {
                    let fisOld = this.getElementDataFrameIntervals(elementType, uid.asStr(), elementData.data['name'])
                    if(!fisOld.empty())
                        this.rmElementDataFromFramesByName(elementType, uid.asStr(), elementData.data['name'], fisOld.get())
                }
                this.setElementDataContent(elementType, element, elementData)
            }
            // Set the pointers
            this.setElementDataPointers(elementType, uid, elementData, frameIntervals)
        }
        else { // setMode = SetMode.union
            // This call is to add element_data to the element, substituting content if overlap, otherwise adding
            // First, extend also the container Element just in case the frame_interval of this element_data is beyond
            // the currently existing frame_intervals of the Element
            // internally computes the union
            this.setElement(elementType, name, semanticType, frameIntervals, uid, ontUid, cs, setMode,resUid)

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
            else if (elementData instanceof types.Mesh){
                // This is only for mesh type, which can have both static and dynamic attributes
                this.setElementDataContent(elementType, element, elementData)
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
                this.setElementDataContent(elementType, element, elementData)
            }
        }
    }

    private setElementDataContent(elementType: ElementType, element: object, elementData: types.ObjectData ) {
        // Adds the element_data to the corresponding container
        // If an element_data with same name exists, it is substituted
        let elementTypeName = ElementType[elementType]
        element[elementTypeName + '_data'] = element[elementTypeName + '_data'] || {}
        element[elementTypeName + '_data'][elementData.typeName()] = element[elementTypeName + '_data'][elementData.typeName()] || []  // e.g. "bbox"

        // Find if element_data already there, if so, replace, otherwise, append
        let found;
        let pos;
        if (elementData.data['name'] !=null){
            pos = element[elementTypeName + '_data'][elementData.typeName()].findIndex(item => item.name === elementData.data['name'])
            found = (pos == -1)?(false):(true)
        }else{
            found= false;
        }
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
        //For Tags, let's ignore element_data_pointers
        if (elementType == ElementType.tag){
            return
        }

        let elementTypeName = ElementType[elementType]
        this.data['openlabel'][elementTypeName + 's'][uid.asStr()][elementTypeName + '_data_pointers'] = this.data['openlabel'][elementTypeName + 's'][uid.asStr()][elementTypeName + '_data_pointers'] || {}
        let edp = this.data['openlabel'][elementTypeName + 's'][uid.asStr()][elementTypeName + '_data_pointers']
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
        if('frames' in this.data['openlabel']){
            if(frameNum in this.data['openlabel']['frames']){
                delete this.data['openlabel']['frames'][frameNum]
            }
            if(this.data['openlabel']['frames'].length == 0)
                delete this.data['openlabel']['frames']
        }        
        // Remove from VCD frame intervals
        if('frame_intervals' in this.data['openlabel']) {
            var fisDict = this.data['openlabel']['frame_intervals'];        
            var fisDictNew = utils.rmFrameFromFrameIntervals(fisDict, frameNum)                

            // Now substitute                
            this.data['openlabel']['frame_intervals'] = fisDictNew;
            if(this.data['openlabel']['frame_intervals'].length == 0)
                delete this.data['openlabel']['frame_intervals']
        }        
    }        

    ////////////////////////////////////////////////////////////////////////////////////////////////////
    // Public API: add, update
    ////////////////////////////////////////////////////////////////////////////////////////////////////
    public addFileVersion(version: string) {
        this.data['openlabel']['metadata'] = this.data['openlabel']['metadata'] || {}
        this.data['openlabel']['metadata']['file_version'] = version
    }

    public addMetadataProperties(properties: object) {        
        this.data['openlabel']['metadata'] = this.data['openlabel']['metadata'] || {}        
        Object.assign(this.data['openlabel']['metadata'], properties);        
    }

    public addName(name: string) {      
        this.data['openlabel']['metadata'] = this.data['openlabel']['metadata'] || {}  
        this.data['openlabel']['metadata']['name'] = name;
    }

    public addAnnotator(annotator: string) {        
        this.data['openlabel']['metadata'] = this.data['openlabel']['metadata'] || {}
        this.data['openlabel']['metadata']['annotator'] = annotator;
    }

    public addComment(comment: string) {        
        this.data['openlabel']['metadata'] = this.data['openlabel']['metadata'] || {}
        this.data['openlabel']['metadata']['comment'] = comment;
    }

    public addOntology(ontologyName: string, subsetInclude=null, subsetExclude=null, additionalProperties=null): string {
        this.data['openlabel']['ontologies'] = this.data['openlabel']['ontologies'] || {};
        for (const ont_uid in this.data['openlabel']['ontologies']) {
            if (this.data['openlabel']['ontologies'][ont_uid] == ontologyName) {
                console.warn('WARNING: adding an already existing ontology');
                return null;
            }
        }
        var length = Object.keys(this.data['openlabel']['ontologies']).length;
        if (subsetInclude == null && subsetExclude == null && additionalProperties ==null){
            this.data['openlabel']['ontologies'][length.toString()] = ontologyName
        }
        else{
            this.data['openlabel']['ontologies'][length.toString()] = {"uri": ontologyName}
            if (subsetInclude != null){
                this.data['openlabel']['ontologies'][length.toString()]["subset_include"] = subsetInclude
            }
            if (subsetExclude != null){
                this.data['openlabel']['ontologies'][length.toString()]["subset_exclude"] = subsetExclude
            }
            if (additionalProperties != null) {
                if(additionalProperties instanceof Object) {
                    Object.assign(this.data['openlabel']['ontologies'][length.toString()], additionalProperties)
                }
            }   
          
           
        }
       
        return length.toString();
    }

    public addResource(resourceName){
        this.data['openlabel']['resources'] = this.data['openlabel']['resources'] || {};
        for (const ont_uid in this.data['openlabel']['resources']) {
            if (this.data['openlabel']['resources'][ont_uid] == resourceName) {
                console.warn('WARNING: adding an already existing resource');
                return null;
            }
        }
        var length = Object.keys(this.data['openlabel']['resources']).length;
        this.data['openlabel']['resources'][length.toString()] = resourceName;
        return length.toString();

    }

    public addCoordinateSystem(name: string, csType: types.CoordinateSystemType, parentName: string = "", poseWrtParent=null, uid = null) {
        // Argument pose_wrt_parent can be used to quickly add a list containing the 4x4 matrix
        // However, argument pose can be used to add any type of Pose object (created with types.Pose)
        // Both arguments co-exist to maintain backwards compatibility with VCD 4.3.1
        
        // Create entry
        this.data['openlabel']['coordinate_systems'] = this.data['openlabel']['coordinate_systems'] || {}
        this.data['openlabel']['coordinate_systems'][name] = {'type': types.CoordinateSystemType[csType],
                                                              'parent': parentName,
                                                              'children': []}
        //Add Pose data
        if(poseWrtParent!=null){
            //TODO: CHECK IF poseWrtParent IS PoseData()
            Object.assign(this.data['openlabel']['coordinate_systems'][name],{'pose_wrt_parent': poseWrtParent.data})
     
        }

        if(uid != null) {
            Object.assign(this.data['openlabel']['coordinate_systems'][name], {'uid': (new UID(uid)).asStr()})
        }

        // Update parents
        if(parentName != "") {
            let found = false
            for(let n in this.data['openlabel']['coordinate_systems']) {
                let cs = this.data['openlabel']['coordinate_systems'][n]
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
        this.data['openlabel']['frames'][frameNum]['frame_properties'] = this.data['openlabel']['frames'][frameNum]['frame_properties'] || {}
        this.data['openlabel']['frames'][frameNum]['frame_properties']['transforms'] = this.data['openlabel']['frames'][frameNum]['frame_properties']['transforms'] || {}
        Object.assign(this.data['openlabel']['frames'][frameNum]['frame_properties']['transforms'], transform.data)
    }

    public addStream(streamName: string, uri: string, description: string, streamType: StreamType) {               
        this.data['openlabel']['streams'] = this.data['openlabel']['streams'] || {};
        this.data['openlabel']['streams'][streamName] = this.data['openlabel']['streams'][streamName] || {};
        

        //typeof "uid0" === "string"
        /*this.data['openlabel']['streams'][streamName] = {
            'description': description, 'uri': uri, 'type': StreamType[streamType]
        }*/ 
        
        
        if(StreamType[streamType]!=null){
            this.data['openlabel']['streams'][streamName] = {
                'description': description, 'uri': uri, 'type': StreamType[streamType]
            }

        }else if(typeof streamType === 'string'){
            this.data['openlabel']['streams'][streamName] = {
                'description': description, 'uri': uri, 'type': streamType
            }
        }
        
    }

    public addFrameProperties(frameNum: number, timestamp = null, additionalProperties = null) {        
        this.addFrame(frameNum);  // this function internally checks if( the frame already exists
        this.updateVCDFrameIntervals(new FrameIntervals(frameNum))
        this.data['openlabel']['frames'][frameNum]['frame_properties'] = this.data['openlabel']['frames'][frameNum]['frame_properties'] || {};

        if (timestamp != null) {
            //if(timestamp instanceof String || timestamp === String) {
            if(typeof timestamp == 'string') {
                this.data['openlabel']['frames'][frameNum]['frame_properties']['timestamp'] = timestamp
            }
        }

        if (additionalProperties != null) {
            if(additionalProperties instanceof Object) {
                Object.assign(this.data['openlabel']['frames'][frameNum]['frame_properties'], additionalProperties)
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
        if ('metadata' in this.data['openlabel']) {
            if ('streams' in this.data['openlabel']) {
                if (streamName in this.data['openlabel']['streams']) {
                    if (frameNum == null) {
                        // This information is static
                        this.data['openlabel']['streams'][streamName]['stream_properties'] = this.data['openlabel']['streams'][streamName]['stream_properties'] || {};
                        
                        if (properties != null) {
                            Object.assign(this.data['openlabel']['streams'][streamName]['stream_properties'], properties)
                        }
                        if (intrinsics != null) {
                            Object.assign(this.data['openlabel']['streams'][streamName]['stream_properties'], intrinsics.data)
                        }
                        if (streamSync != null) {
                            Object.assign(this.data['openlabel']['streams'][streamName]['stream_properties'], streamSync.data)
                        }
                    }
                    else {
                        // This is information of the stream for( a specific frame
                        this.addFrame(frameNum); // to add the frame in case it does not exist
                        var frame = this.data['openlabel']['frames'][frameNum];
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
        if(!(frameNum in this.data['openlabel']['frames'])) {
            console.warn("WARNING: Trying to stringify a non-existing frame")
            return ''
        }

        if(dynamicOnly) {
            if(pretty) { 
                return JSON.stringify(this.data['openlabel']['frames'][frameNum], null, '    ')
            }
            else {
                return JSON.stringify(this.data['openlabel']['frames'][frameNum])
            }
        }
        else {
            // Need to compose dynamic and static information into a new structure
            // Copy the dynamic info first
            let frame_static_dynamic: object
            Object.assign(frame_static_dynamic, this.data['openlabel']['frames'][frameNum])

            // Now the static info for objects, actions, events, contexts and relations
            for(let elementType in ElementType) {
                let elementTypeName = ElementType[elementType]
                // First, elements explicitly defined for this frame
                if(elementTypeName + 's' in this.data['openlabel']['frames'][frameNum]) {
                    for (var [uid, content] of Object.entries(this.data['openlabel']['frames'][frameNum][elementTypeName + 's'])) {
                        Object.assign(frame_static_dynamic[elementTypeName + 's'][uid], this.data['openlabel'][elementTypeName + 's'][uid])
                        // Remove frameInterval entry
                        if('frame_intervals' in frame_static_dynamic[elementTypeName + 's'][uid]) {
                            delete frame_static_dynamic[elementTypeName + 's'][uid]['frame_intervals']
                        }
                    }
                }

                // But also other elements without frame intervals specified, which are assumed to exist during the entire sequence
                if(elementTypeName + 's' in this.data['openlabel'] && elementTypeName != 'relation') {
                    for( var [uid, element] of Object.entries(this.data['openlabel'][elementTypeName + 's'])) {
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

    public addObject(name: string, semanticType: string, frameValue = null, uid = null, ontUid = null, cs = null, setMode: SetMode = SetMode.union, resUid=null) {
        return this.setElement(ElementType.object, name, semanticType, new FrameIntervals(frameValue), new UID(uid), new UID(ontUid), cs, setMode,resUid).asStr()
    }

    public addAction(name: string, semanticType: string, frameValue = null, uid = null, ontUid = null, cs = null, setMode: SetMode = SetMode.union, resUid=null) {
        return this.setElement(ElementType.action, name, semanticType, new FrameIntervals(frameValue), new UID(uid), new UID(ontUid), cs, setMode,resUid).asStr()
    }

    public addEvent(name: string, semanticType: string, frameValue = null, uid = null, ontUid = null, cs = null, setMode: SetMode = SetMode.union, resUid=null) {
        return this.setElement(ElementType.event, name, semanticType, new FrameIntervals(frameValue), new UID(uid), new UID(ontUid), cs, setMode,resUid).asStr()
    }

    public addContext(name: string, semanticType: string, frameValue = null, uid = null, ontUid = null, cs = null, setMode: SetMode = SetMode.union, resUid=null) {
        return this.setElement(ElementType.context, name, semanticType, new FrameIntervals(frameValue), new UID(uid), new UID(ontUid), cs, setMode,resUid).asStr()
    }

    public addRelation(name: string, semanticType: string, frameValue = null, uid = null, ontUid = null, setMode: SetMode = SetMode.union, resUid=null) {
        if(setMode == SetMode.replace && uid != null)
        {            
            if(this.has(ElementType.relation, uid))
            {
                let relation = this.data['openlabel']['relations'][(new UID(uid)).asStr()]
                relation['rdf_subjects'] = []
                relation['rdf_objects'] = []
            }            
        }
        let relation_uid = this.setElement(ElementType.relation, name, semanticType, new FrameIntervals(frameValue), new UID(uid), new UID(ontUid), null, setMode,resUid)        
        return relation_uid.asStr()
    }

    public addTag( semanticType: string, uid = null, ontUid=null, resUid=null){
        return this.setElement(ElementType.tag, null, semanticType,new  FrameIntervals(null),
                                  new UID(uid), new UID(ontUid), null, SetMode.union, resUid).asStr()

    }

    public addElement(elementType: ElementType, name: string, semanticType: string, frameValue = null, uid = null, ontUid = null, setMode: SetMode = SetMode.union, resUid=null) {
        return this.setElement(elementType, name, semanticType, new FrameIntervals(frameValue), new UID(uid), new UID(ontUid), null, setMode,resUid).asStr()                
    }

    public addRdf(relationUid: string | number, rdfType: RDF, elementUid: string | number, elementType: ElementType) {
        let elementTypeName = ElementType[elementType]
        let rel_uid = new UID(relationUid)
        let el_uid = new UID(elementUid)
        if (!(rel_uid.asStr() in this.data['openlabel']['relations'])) {
            console.warn("WARNING: trying to add RDF to non-existing Relation.")
            return
        }
        else {
            let relation = this.data['openlabel']['relations'][rel_uid.asStr()]
            if (!(el_uid.asStr() in this.data['openlabel'][elementTypeName + 's'])) {
                console.warn("WARNING: trying to add RDF using non-existing Element.")
                return
            }
            else {
                if (rdfType == RDF.subject) {
                    this.data['openlabel']['relations'][rel_uid.asStr()]['rdf_subjects'] = this.data['openlabel']['relations'][rel_uid.asStr()]['rdf_subjects'] || [];
                    this.data['openlabel']['relations'][rel_uid.asStr()]['rdf_subjects'].push(
                        { 'uid': el_uid.asStr(), 'type': elementTypeName }
                    )
                }
                else {
                    this.data['openlabel']['relations'][rel_uid.asStr()]['rdf_objects'] = this.data['openlabel']['relations'][rel_uid.asStr()]['rdf_objects'] || [];
                    this.data['openlabel']['relations'][rel_uid.asStr()]['rdf_objects'].push(
                        { 'uid': el_uid.asStr(), 'type': elementTypeName }
                    )
                }                             
            }
        }
    }

    public addRelationObjectAction(name: string, semanticType: string, objectUid: string | number, actionUid: string | number, relationUid = null, ontUid = null, frameValue=null, setMode: SetMode = SetMode.union,resUid=null) {
        // Note: no need to wrap uids as UID, since all calls are public functions, and no access to dict is done.
        relationUid = this.addRelation(name, semanticType, frameValue, relationUid, ontUid, setMode,resUid)
        this.addRdf(relationUid, RDF.subject, objectUid, ElementType.object)
        this.addRdf(relationUid, RDF.object, actionUid, ElementType.action)
        return relationUid
    }

    public addRelationActionAction(name: string, semanticType: string, actionUid1: string | number, actionUid2: string | number, relationUid = null, ontUid = null, frameValue=null, setMode: SetMode = SetMode.union,resUid=null) {
        relationUid = this.addRelation(name, semanticType, frameValue, relationUid, ontUid, setMode,resUid)
        this.addRdf(relationUid, RDF.subject, actionUid1, ElementType.action)
        this.addRdf(relationUid, RDF.object, actionUid2, ElementType.action)
        return relationUid
    }

    public addRelationObjectObject(name: string, semanticType: string, objectUid1: string | number, objectUid2: string | number, relationUid = null, ontUid = null, frameValue=null, setMode: SetMode = SetMode.union,resUid=null) {
        relationUid = this.addRelation(name, semanticType, frameValue, relationUid, ontUid, setMode,resUid)
        this.addRdf(relationUid, RDF.subject, objectUid1, ElementType.object)
        this.addRdf(relationUid, RDF.object, objectUid2, ElementType.object)
        return relationUid
    }

    public addRelationActionObject(name: string, semanticType: string, actionUid: string | number, objectUid: string | number, relationUid = null, ontUid = null, frameValue=null, setMode: SetMode = SetMode.union,resUid=null) {
        relationUid = this.addRelation(name, semanticType, frameValue, relationUid, ontUid, setMode,resUid)
        this.addRdf(relationUid, RDF.subject, actionUid, ElementType.action)
        this.addRdf(relationUid, RDF.object, objectUid, ElementType.object)
        return relationUid
    }

    public addRelationSubjectObject(name: string, semanticType: string, subjectType: ElementType, subjectUid: string | number, objectType: ElementType, objectUid: string | number, relationUid= null, ontUid= null, frameValue = null, setMode: SetMode = SetMode.union, resUid=null) {
        let uid = this.addRelation(name, semanticType, frameValue, relationUid, ontUid, setMode,resUid)
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

    public addTagData(uid: string | number, tagData: types.ObjectData, frameValue = null, setMode: SetMode = SetMode.union){
        return this.setElementData(ElementType.tag, new UID(uid), tagData, new FrameIntervals(frameValue), setMode)        

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

    public hasElements(elementType: ElementType ) {
        let elementTypeName = ElementType[elementType]
        return (elementTypeName + 's' in this.data['openlabel'])
    }
    
    public hasObjects(): boolean{
        return 'objects' in this.data['openlabel']
    }

    public hasActions(): boolean {
        return 'actions' in this.data['openlabel']
    }

    public hasEvents(): boolean {
        return 'events' in this.data['openlabel']
    }

    public hasContexts(): boolean {
        return 'contexts' in this.data['openlabel']
    }

    public hasRelations(): boolean {
        return 'relations' in this.data['openlabel']
    }
    
    public has(elementType: ElementType, uid: string | number): boolean {
        let elementTypeName = ElementType[elementType]
        if (!this.data['openlabel'][elementTypeName + 's']) {
            return false;
        }
        else {
            if (this.data['openlabel'][elementTypeName + 's'][(new UID(uid)).asStr()]) {
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
            if(!(ElementType[elementType] + '_data_pointers' in this.data['openlabel'][ElementType[elementType] + 's'][uid_str])) 
                return false
            let name = elementData.data['name']
            return name in this.data['openlabel'][ElementType[elementType] + 's'][uid_str][ElementType[elementType] + '_data_pointers']
        }
    }

    public hasFrame(frameNum: number) {
        if (!this.data['openlabel']['frames']) {
            return false
        }
        else {
            if(frameNum in this.data['openlabel']['frames'])
                return true
            else
                return false
        }
    }

    public getAll(elementType: ElementType) {
        //
        //Returns all elements of the specified ElementType.
        //e.g. all Object's or Context's
        //
        let elementTypeName = ElementType[elementType]
        return this.data['openlabel'][elementTypeName + 's'];
    }

    public getAll2(elementType1: ElementType, elementType2: ElementType) {
        //
        //Returns all elements of the specified ElementType.
        //e.g. all Object's or Context's
        //
        let elementTypeName1 = ElementType[elementType1]
        let elementTypeName2 = ElementType[elementType2]

        var aux = {};
        aux[elementTypeName1 + 's'] = this.data['openlabel'][elementTypeName1 + 's'];
        aux[elementTypeName2 + 's'] = this.data['openlabel'][elementTypeName2 + 's'];

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
        aux[elementTypeName1 + 's'] = this.data['openlabel'][elementTypeName1 + 's'];
        aux[elementTypeName2 + 's'] = this.data['openlabel'][elementTypeName2 + 's'];
        aux[elementTypeName3 + 's'] = this.data['openlabel'][elementTypeName3 + 's'];

        return aux;
    }

    public getElement(elementType: ElementType, uid: string | number) {        
        let elementTypeName = ElementType[elementType]
        let uid_str = (new UID(uid)).asStr()
        if (this.data['openlabel'][elementTypeName + 's'] == null) {
            console.warn("WARNING: trying to get a " + elementTypeName + " but this VCD has none.")
            return null
        }
        if (this.data['openlabel'][elementTypeName + 's'][uid_str]) {
            return this.data['openlabel'][elementTypeName + 's'][uid_str]
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

    public getElementUidByName(elementType: ElementType, name: string) {
        if(!this.hasElements(elementType))
            return null
        let elementTypeName = ElementType[elementType]
        let elements = this.data['openlabel'][elementTypeName + 's']
        for (const uid in elements) {
            let element = elements[uid]
            let name_element = element['name']
            if(name_element == name)
                return uid
        }
        return null
    }

    public getObjectUidByName(name: string) {
        return this.getElementUidByName(ElementType.object, name)
    }

    public getActionUidByName(name: string) {
        return this.getElementUidByName(ElementType.action, name)
    }

    public getContextUidByName(name: string) {
        return this.getElementUidByName(ElementType.context, name)
    }

    public getEventUidByName(name: string) {
        return this.getElementUidByName(ElementType.event, name)
    }

    public getRelationUidByName(name: string) {
        return this.getElementUidByName(ElementType.relation, name)
    }

    public getFrame(frameNum: number) {
        if (this.data['openlabel']['frames']) {
            if(frameNum in this.data['openlabel']['frames'])
                return this.data['openlabel']['frames'][frameNum];
        }
        return null
    }

    public getElementsOfType(elementType: ElementType, type: string): string[] {
        let elementTypeName = ElementType[elementType]
 
        var uids = [];
        for (const uid in this.data['openlabel'][elementTypeName + 's']) {
            var element = this.data['openlabel'][elementTypeName + 's'][uid];
            if (element['type'] == type) {
                uids.push(uid);
            }
        }
        return uids;
    }

    public getElementsWithElementDataName(elementType: ElementType, dataName: string) {
        let uids = []
        let elementTypeName = ElementType[elementType]
        for(const uid in this.data['openlabel'][elementTypeName + 's']){
            let element = this.data['openlabel'][elementTypeName + 's'][uid]
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
        if(uid_str in this.data['openlabel'][elementTypeName + 's']) {
            let element = this.data['openlabel'][elementTypeName + 's'][uid_str]
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
        let elementExists = this.has(elementType, uid)
        let vcdHasFrames = !this.getFrameIntervals().empty()
        
        if(!elementExists){ // the element does not exist
            return null
        }

        if(!vcdHasFrames && frameNum != null) { // don't ask for frame-specific info in a VCD without frames
            return null
        }

        let elementTypeName = ElementType[elementType]
        let frameNumIsNumber = Number.isInteger(frameNum)
        let uid_str = new UID(uid).asStr()

        let elementExistInThisFrame = false
        if(frameNum != null && frameNumIsNumber) {            
            
            let foundInFrame = false;
            let frame = this.getFrame(frameNum)
            if(frame != null) {
                if(elementTypeName + 's' in frame) {
                    if(uid_str in frame[elementTypeName + 's']) {
                        elementExistInThisFrame = true
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
                    }
                }
            }
            if(!foundInFrame) {
                // The user has asked to get an ElementData for a certain Frame, but there is not info
                // about this element or elementData at this frame.
                // Let's check whether the elementData is static at the root AND the Element is defined for this frame            
                if(!elementExistInThisFrame)
                    return null                
                let element = this.data['openlabel'][elementTypeName + 's'][uid_str]  // the element exists because of previous controls
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
        else {
            // The user is asking for static attributes at the root of the element            
            let element = this.data['openlabel'][elementTypeName + 's'][uid_str]
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
            if(elementTypeName + 's' in this.data['openlabel']) {
                if(uid_str in this.data['openlabel'][elementTypeName + 's']) {
                    let element = this.data['openlabel'][elementTypeName + 's'][uid_str]
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
        if(elementTypeName + 's' in this.data['openlabel'])
            return Object.keys(this.data['openlabel'][elementTypeName + 's']).length        
        else
            return 0
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

    public getElementsUids(elementType: ElementType): string[] {
        let elementTypeName = ElementType[elementType]
        if(elementTypeName + 's' in this.data['openlabel']) {
            return Object.keys(this.data['openlabel'][elementTypeName + 's'])
        }
        else {
            return []
        }
    }

    public getOntology(ontUid: string | number) {
        let ond_uid_str = new UID(ontUid).asStr()
        if (this.data['openlabel']['ontologies']) {
            if (this.data['openlabel']['ontologies'][ond_uid_str]) {
                return this.data['openlabel']['ontologies'][ond_uid_str];
            }
        }
        return null;
    }

    public getResource(resUid) {
        let res_uid_str = new UID(resUid).asStr()
        if (this.data['openlabel']['resources']){
            if(this.data['openlabel']['resources'][res_uid_str]){
                return this.data['openlabel']['resources'][res_uid_str];
            }
        }
        
        return null;
    }    

    public getMetadata() {
        if (this.data['openlabel']['metadata']) {
            return this.data['openlabel']['metadata'];
        }
        else {
            return {};
        }
    }

    public hasCoordinateSystem(cs: string): boolean {
        if('coordinate_systems' in this.data['openlabel']) {
            if(cs in this.data['openlabel']['coordinate_systems']) return true            
        }
        return false
    }

    public getCoordinateSystems(): Array<object> {
        if('coordinate_systems' in this.data['openlabel']) {
            return this.data['openlabel']['coordinate_systems']
        }
        else return []
    }

    public getCoordinateSystem(cs: string) {
        if(this.hasCoordinateSystem(cs)) {
            //return this.data['openlabel']['streams'][cs]
            return this.data['openlabel']['coordinate_systems'][cs]
        }
        else return null
    }

    public hasStream(streamName: string): boolean {        
        if('streams' in this.data['openlabel']) {                        
            if (streamName in this.data['openlabel']['streams']) {
                return true
            }             
            else {
                return false
            }
        }
    }

    public getStreams(): Array<object> {
        if('streams' in this.data['openlabel']) {
            return this.data['openlabel']['streams']
        }
        else return []
    }

    public getStream(streamName: string) {
        if(this.hasStream(streamName)) {
            return this.data['openlabel']['streams'][streamName]
        }
        else return null
    }

    public getFrameIntervals(): FrameIntervals {
        if('frame_intervals' in this.data['openlabel']) return new FrameIntervals(this.data['openlabel']['frame_intervals'])
        else return new FrameIntervals()        
    }

    public getElementFrameIntervals(elementType: ElementType, uid: string | number) {
        let elementTypeName = ElementType[elementType]
        let uid_str = new UID(uid).asStr()
        if (!(elementTypeName + 's' in this.data['openlabel'])) {            
            return new FrameIntervals()
        }
        else {
            if(!(uid_str in this.data['openlabel'][elementTypeName + 's']))
                return new FrameIntervals()
            return new FrameIntervals(this.data['openlabel'][elementTypeName + 's'][uid_str]['frame_intervals'])
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
        var elements = this.data['openlabel'][elementTypeName + 's'];

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
        if(!this.hasElements(elementType))
            return

        
        let uid_str = new UID(uid).asStr()

        // Get Element from summary
        if(!this.has(elementType, uid)) return

        // Remove from Frames: let's read frameIntervals from summary
        var elements = this.data['openlabel'][elementTypeName + 's'];
        let element = elements[uid_str];
        if('frame_intervals' in element) {
            for (var i = 0; i < element['frame_intervals'].length; i++) {
                var fi = element['frame_intervals'][i];
                for (var frameNum = fi['frame_start']; frameNum < fi['frame_end'] + 1; frameNum++) {
                    var elementsInFrame = this.data['openlabel']['frames'][frameNum][elementTypeName + 's'];
                    if (uid in elementsInFrame) {
                        delete elementsInFrame[uid_str];
                    }
                    if (Object.keys(elementsInFrame).length == 0) {  // objects might have end up empty TODO: test this
                        delete this.data['openlabel']['frames'][frameNum][elementTypeName + 's']

                        if(Object.keys(this.data['openlabel']['frames'][frameNum]).length == 0) { // this frame may have ended up being empty
                            delete this.data['openlabel']['frames'][frameNum]
                            this.rmFrame(frameNum)
                        }
                    }
                }
            }
        }

        // Delete this element from summary
        delete elements[uid_str];
        if(elements.length==0) {
            delete this.data['openlabel'][elementTypeName + 's']
        }
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

    public rmElementDataFromFramesByName(elementType: ElementType, uid: string | number, elementDataName: string, frameIntervals = null) {        
        let uid_ = new UID(uid)
        let frameIntervals_ = new FrameIntervals(frameIntervals)
        // Quick checks
        if(this.has(elementType, uid_.asStr())) {
            let edp = this.getElementDataPointer(elementType, uid_.asStr(), elementDataName);
            let fis_ed = new FrameIntervals(edp['frame_intervals'])

            let fis_to_remove = fis_ed.intersection(frameIntervals_)
            let remove_all = false
            if(fis_to_remove.equals(fis_ed))
                remove_all = true

            // Loop over frames that we know the element data is present at
            let temp = fis_ed
            let elementTypeName = ElementType[elementType];
            for(let fi of fis_to_remove.get()) {
                for(let f=fi[0]; f<=fi[1]; f++) {
                    let frame = this.data['openlabel']['frames'][f]
                    let element = frame[elementTypeName + 's'][uid_.asStr()]
                    
                    // Delete only the elementData with the specified name
                    for (const prop in element[elementTypeName + '_data']) {
                        var valArray = element[elementTypeName + '_data'][prop];
                        let idx_to_remove = null
                        for (var i = 0; i < valArray.length; i++) {
                            var val = valArray[i];
                            if (val['name'] == elementDataName) {
                                idx_to_remove = i
                                //delete element[elementTypeName + '_data'][prop][i]
                            }
                        }
                        //delete element[elementTypeName + '_data'][prop][idx_to_remove]
                        element[elementTypeName + '_data'][prop].splice(idx_to_remove, 1)  // because we want to extract the element and not left it null
                        if (element[elementTypeName + '_data'][prop].length == 0)
                            delete element[elementTypeName + '_data'][prop]  // e.g. 'bbox': [] is empty so let's delete it
                            if (Object.keys(element[elementTypeName + '_data']).length == 0)
                                delete element[elementTypeName + '_data'] // e.g. 'object_data' : {} is empty so let's delete it
                    }
                    // Clean-up edp frame by frame
                    if(!remove_all)
                        temp = new FrameIntervals(utils.rmFrameFromFrameIntervals(temp.getDict(), f))
                }           
            }
            let element = this.getElement(elementType, uid_.asStr())
            if (remove_all) {
                // Just delete the entire element data pointer
                delete element[elementTypeName + '_data_pointers'][elementDataName]
            }
            else {
                // Update frame intervals for this edp
                let fis_ed_new = temp
                element[elementTypeName + '_data_pointers'][elementDataName]['frame_intervals'] = fis_ed_new.getDict()
            }
        }       
    }

    public rmElementDataFromFrames(elementType: ElementType, uid: string | number, frameIntervals = null) {        
        let uid_ = new UID(uid)
        let frameIntervals_ = new FrameIntervals(frameIntervals)
        let elementTypeName = ElementType[elementType];
        for(let fi of frameIntervals_.get()) {
            for(let f=fi[0]; f<=fi[1]; f++) {
                if(this.hasFrame(f)) {
                    let frame = this.data['openlabel']['frames'][f]
                    if(elementTypeName + 's' in frame) {
                        if(uid_.asStr() in frame[elementTypeName + 's']) {
                            let element = frame[elementTypeName + 's'][uid_.asStr()]
                            if(elementTypeName + '_data' in element) {
                                // delete all its former dynamic element_data entries at old fis
                                delete element[elementTypeName + '_data']  
                            }                     
                        }
                    }
                }   
            }
        }

        // Clean-up data pointers of object_data that no longer exist!
        // Note, element_data_pointers are correctly updated, but there might be some now declared as static
        // corresponding to element_data that was dynamic but now has been removed when the element changed to static
        if(this.has(elementType, uid_.asStr())) {
            let element = this.data['openlabel'][elementTypeName + 's'][uid_.asStr()]
            if(elementTypeName + '_data_pointers' in element) {
                let edps = element[elementTypeName + '_data_pointers']
                let edp_names_to_delete = []
                for(let edp_name in edps) {
                    let fis_ed = new FrameIntervals(edps[edp_name]['frame_intervals'])
                    if(fis_ed.empty()) {
                        // CHeck if element_Data exists
                        let ed_type = edps[edp_name]['type']
                        let found = false
                        if(elementTypeName + '_data' in element) {
                            if(ed_type in element[elementTypeName + '_data']) {
                                for(let ed in element[elementTypeName + '_data'][ed_type]) {
                                    if(ed['name'] == edp_name) {
                                        found = true
                                        break
                                    }
                                }
                            }
                        }
                        if(!found) {
                            edp_names_to_delete.push(edp_name)
                        }
                    }
                }
                for(let edp_name of edp_names_to_delete) {
                    delete element[elementTypeName + '_data_pointers'][edp_name]
                }
            }
        }
    }    
}

export class OpenLABEL extends VCD{
    
    //This is the OpenLABEL class, which inherites from VCD class.

    /*def __init__(self, file_name=None, validation=False):
        VCD.__init__(self, file_name, validation)*/

    constructor(vcd_json = null, validation = false) {
        super(vcd_json, validation);	
    }
        

}