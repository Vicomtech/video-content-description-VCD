/**
* VCD (Video Content Description) 4.x.x
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

import * as utils from "./vcd.utils";
import * as types from "./vcd.types";
import * as schema from "./vcd.schema";

import { Validator } from 'jsonschema';

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
    
export class VCD {
	private data: Object = {}
    private schema: Object = schema.vcd_schema;
	
	private lastUID: Object = {}
	private objectDataNames: Object = {}
	private actionDataNames: Object = {}
	
	constructor(vcd_json = null, validation = false) {
		this.init(vcd_json, validation);		
	}
	
	printInfo() {
		console.log("This is a VCD4 content\n");
		console.log("\tversion: " + this.data['vcd']['version']);
	}

    private reset() {
        // Main VCD data
        this.data = { 'vcd': {} };
        this.data['vcd']['frames'] = {};
        this.data['vcd']['version'] = "4.2.0";
        this.data['vcd']['frame_intervals'] = [];

        // Schema information
        this.schema = schema.vcd_schema;

        // Additional auxiliary structures
        this.lastUID = {};
        this.lastUID['object'] = -1;
        this.lastUID['action'] = -1;
        this.lastUID['event'] = -1;
        this.lastUID['context'] = -1;
        this.lastUID['relation'] = -1;

        this.objectDataNames = {};  // Stores names of ObjectData, e.g. "age", or "width" per Object
        this.actionDataNames = {};  // Stores names of ActionData, e.g. "age", or "width" per Action
    }

	private init(vcd_json = null, validation = false) {
		if (vcd_json == null) {			
			this.reset();
		}
		else {
            // Load from file, and validate with schema
            if (validation) {
                let validationResult = this.validate(vcd_json)

                if (!validationResult.valid) {
                    console.log("ERROR: loading VCD content not compliant with schema 4.2.0.");
                    console.warn("Creating an empty VCD instead.");
                    for(var i = 0; i <validationResult.errors.length; i++){
                        console.log(validationResult.errors[i].message);
                    }   
                    this.reset();                 
                }
                else {
                    this.data = vcd_json
                    this.computeLastUid();
                    this.computeObjectDataNames();
                    this.computeActionDataNames();
                    // TODO: Context, Event data names?
                }
            }            
		}
	}	
	
	////////////////////////////////////////////////////////////////////////////////////////////////////
    // Private API: inner functions
    ////////////////////////////////////////////////////////////////////////////////////////////////////    
    private getUidToAssign(elementType: ElementType, uid = null) {
        var uidToAssign        
        let elementTypeName = ElementType[elementType]
        if (uid == null) {
            this.lastUID[elementTypeName] += 1;  // If null is provided, let's use the next one available            
            uidToAssign = this.lastUID[elementTypeName];
            return uidToAssign;
        }
        // uid is not null
        // There are already this type of elements in vcd
        if (uid > this.lastUID[elementTypeName]) {
            this.lastUID[elementTypeName] = uid;
            var uidToAssign = this.lastUID[elementTypeName];
        }
        else {
            uidToAssign = uid;
        }
        return uidToAssign;
    }
        
    private updateFrameIntervalsOfVcd(frameIntervals: Array<object>) {
        // frameIntervals is an array of dicts
        if (!Array.isArray(frameIntervals)) {
            console.warn("frameIntervals not array");
            return;
        }
        if (frameIntervals.length == 0) {
            return;
        }

        // Fuse with existing        
        var fis = this.data['vcd']['frame_intervals'] = this.data['vcd']['frame_intervals'] || [];        
        var fit = frameIntervals.concat(fis)

        // Now substitute
        var fitFused = utils.fuseFrameIntervals(fit);
        this.data['vcd']['frame_intervals'] = fitFused;
    }

    private removeElementFrameInterval(elementType: ElementType, uid, frameIntervalDict) {
        // This function removes a frameInterval from an element
        let elementTypeName = ElementType[elementType];
        if (this.data['vcd'][elementTypeName + 's'][uid]) {
            var fis = this.data['vcd'][elementTypeName + 's'][uid]['frame_intervals'];

            var fiDictArrayToAdd = [];
            for (var i = 0; i < fis.length; i++) {
                // Three options{ 1) no intersection 2) one inside 3) intersection
                var maxStartVal = Math.max(frameIntervalDict['frame_start'], fis[i]['frame_start']);
                var minEndVal = Math.min(frameIntervalDict['frame_end'], fis[i]['frame_end']);

                if (frameIntervalDict['frame_start'] <= fis[i]['frame_start'] && frameIntervalDict['frame_end'] >= fis[i]['frame_end']) {
                    // Case c) equal tuples -> delete or Case f) interval to delete covers completely target interval
                    delete fis[i];
                }

                if (maxStartVal <= minEndVal) {
                    // There is some intersection{ cases a, b, d and e

                    if (maxStartVal == fis[i]['frame_start']) {  // cases a, b
                        var newFi1 = { 'frame_start': minEndVal + 1, 'frame_end': fis[i]['frame_end'] };
                        fis[i] = newFi1;
                    }
                    else if (minEndVal == fis[i]['frame_end']) {  // case e
                        var newFi2 = { 'frame_start': fis[i]['frame_start'], 'frame_end': maxStartVal - 1 };
                        fis[i] = newFi2;
                    }
                    else {  // case d maxStartVal > fiTuple[0] and minEndVal < fiTuple[1]
                        // Inside{ then we need to split into two frame intervals
                        var newFi3 = { 'frame_start': fis[i]['frame_start'], 'frame_end': maxStartVal - 1 };
                        var newFi4 = { 'frame_start': minEndVal + 1, 'frame_end': fis[i]['frame_end'] };
                        fis[i] = newFi3;
                        fiDictArrayToAdd.push(newFi4);
                    }
                }
            }
            for (var i = 0; i < fiDictArrayToAdd.length; i++) {
                fis.push(fiDictArrayToAdd[i]);
            }
        }
    }

    private computeFrameIntervals() {
        for (const prop in this.data['vcd']['frames']) {
            var frameNum = parseInt(prop);
            var found = false;
            for (var i = 0; i < this.data['vcd']['frame_intervals'].length; i++) {
                var fi = this.data['vcd']['frame_intervals'][i];
                //if (this.isInside(frameNum, fi)) {
                if( utils.isInside(frameNum, fi)) {
                    found = true;
                }
            }
            if (!found) {
                // This frame is not included in the frameIntervals, let's modify them
                var idxToFuse = [];
                for (var i = 0; i < this.data['vcd']['frame_intervals'].length; i++) {
                    var fi = this.data['vcd']['frame_intervals'][i];
                    if (utils.intersects(fi, utils.asFrameIntervalDict(frameNum)) || utils.consecutive(fi, utils.asFrameIntervalDict(frameNum))) {
                        idxToFuse.push(i);
                    }
                }
                if (idxToFuse.length == 0) {
                    // New frameInterval, separated
                    this.data['vcd']['frame_intervals'].push({ 'frame_start': frameNum, 'frame_end': frameNum });
                }
                else {
                    var newList = [];
                    var fusedFi = utils.asFrameIntervalDict(frameNum);
                    for (var i = 0; i < this.data['vcd']['frame_intervals'].length; i++) {
                        var fi = this.data['vcd']['frame_intervals'][i];
                        if (idxToFuse.indexOf(i) > -1) {
                            fusedFi = { 'frame_start': Math.min(fusedFi['frame_start'], fi['frame_start']), 'frame_end': Math.max(fusedFi['frame_end'], fi['frame_end']) };
                        }
                        else {
                            newList.push(fi);  // also add those not affected by fusion
                        }
                    }
                    newList.push(fusedFi);
                    this.data['vcd']['frame_intervals'] = newList;
                }
            }
        }
    }

    private addFrame(frameNum: number) {
        // this.data['vcd']['frames'].setdefault(frameNum, {}) // 3.8 secs - 10.000 times
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

    private computeObjectDataNames() {
        this.objectDataNames = {};
        if (this.data['vcd']['objects']) {
            for (const uid of Object.keys(this.data['vcd']['objects'])) {
                this.objectDataNames[uid] = this.objectDataNames[uid] || [];
                this.computeObjectDataNamesUid(uid);
            }
        }
    }

    private computeActionDataNames() {
        this.actionDataNames = {};
        if (this.data['vcd']['actions']) {
            for (const uid of Object.keys(this.data['vcd']['actions'])) {
                this.actionDataNames[uid] = this.actionDataNames[uid] || [];
                this.computeActionDataNamesUid(uid);
            }
        }
    }

    private computeObjectDataNamesUid(uid) {
        // This function recomputes the this.objectDataNames entry for uid
        if (!this.objectDataNames[uid]) {
            return;
        }
        delete this.objectDataNames[uid];  // Clear list
        if (this.data['vcd']['objects'][uid]) {
            var object = this.data['vcd']['objects'][uid];
            this.objectDataNames[uid] = this.objectDataNames[uid] || [];
            if (object['frame_intervals']) {
                // There is dynamic content
                var fis = object['frame_intervals'];
                for (var i = 0; i < fis.length; i++) {
                    for (var j = fis[i]['frame_start']; j < fis[i]['frame_end'] + 1; j++) {
                        for (const objectInFrame in this.data['vcd']['frames'][j]['objects']) {
                            for (const valList in this.data['vcd']['frames'][j]['objects'][objectInFrame]['object_data']) {
                                for (const val of this.data['vcd']['frames'][j]['objects'][objectInFrame]['object_data'][valList]) {
                                    if (val['name']) {
                                        this.objectDataNames[uid].push(val['name']);
                                    }
                                }
                            }
                        }
                    }
                }
            }
            if (object['object_data']) {
                // There is also static content
                for (const valArray in object['object_data']) {
                    for (const val of object['object_data'][valArray]) {
                        if (val['name']) {
                            this.objectDataNames[uid].push(val['name']);
                        }
                    }
                }
            }
        }
    }

    private computeActionDataNamesUid(uid) {
        // This function recomputes the this.actionDataNames entry for uid
        if (!this.actionDataNames[uid]) {
            return;
        }
        delete this.actionDataNames[uid];  // Clear list
        if (this.data['vcd']['actions'][uid]) {
            var action = this.data['vcd']['actions'][uid];
            this.actionDataNames[uid] = this.actionDataNames[uid] || [];
            if (action['frame_intervals']) {
                // There is dynamic content
                var fis = action['frame_intervals'];
                for (var i = 0; i < fis.length; i++) {
                    for (var j = fis[i]['frame_start']; j < fis[i]['frame_end'] + 1; j++) {
                        for (const actionInFrame in this.data['vcd']['frames'][j]['actions']) {
                            for (const valList in this.data['vcd']['frames'][j]['actions'][actionInFrame]['action_data']) {
                                for (const val of this.data['vcd']['frames'][j]['actions'][actionInFrame]['action_data'][valList]) {
                                    if (val['name']) {
                                        this.actionDataNames[uid].push(val['name']);
                                    }
                                }
                            }
                        }
                    }
                }
            }
            if (action['action_data']) {
                // There is also static content
                for (const valArray in action['action_data']) {
                    for (const val of action['action_data'][valArray]) {
                        if (val['name']) {
                            this.actionDataNames[uid].push(val['name']);
                        }
                    }
                }
            }
        }
    }

    private clean() {
        // This function recomputes LUTs and other structures used by VCD
        this.cleanUpFrames();
        this.cleanUpVcd();
        this.computeFrameIntervals();
    }

    private cleanUpFrames() {
        // This function explores this.data['vcd']['frames'] and removes entries which are empty
        var frames = this.data['vcd']['frames'];

        var frameNumsToRemove = [];
        for (const frameNum in frames) {
            var frameContent = frames[frameNum];
            // so there is an 'objects' key, but its an empty list
            if (frameContent['objects'] && frameContent['objects'].constructor === Object && Object.keys(frameContent['objects']).length != 0) {
                continue;
            }
            if (frameContent['actions'] && frameContent['actions'].constructor === Object && Object.keys(frameContent['actions']).length != 0) {
                continue;
            }
            if (frameContent['events'] && frameContent['events'].constructor === Object && Object.keys(frameContent['events']).length != 0) {
                continue;
            }
            if (frameContent['contexts'] && frameContent['contexts'].constructor === Object && Object.keys(frameContent['contexts']).length != 0) {
                continue;
            }
            if (frameContent['relations'] && frameContent['relations'].constructor === Object && Object.keys(frameContent['relations']).length != 0) {
                continue;
            }
            if (frameContent['objects'] && frameContent['objects'].constructor === Object && Object.keys(frameContent['objects']).length != 0) {
                continue;
            }
            if (frameContent['frameProperties'] && frameContent['frameProperties'].constructor === Object && Object.keys(frameContent['frameProperties']).length != 0) {
                continue;
            }
            frameNumsToRemove.push(frameNum);
        }

        // Update LUTs only modifying values changed
        for (const j in frameNumsToRemove) {
            delete frames[frameNumsToRemove[j]];
        }
    }

    private cleanUpVcd() {
        if (this.data['vcd']['objects']) {
            if (Object.keys(this.data['vcd']['objects']).length === 0) {  // So there is 'objects', but empty
                delete this.data['vcd']['objects'];
            }
        }

        if (this.data['vcd']['actions']) {
            if (Object.keys(this.data['vcd']['actions']).length === 0) {  // So there is 'actions', but empty
                delete this.data['vcd']['actions'];
            }
        }

        if (this.data['vcd']['events']) {
            if (Object.keys(this.data['vcd']['events']).length === 0) {  // So there is 'events', but empty
                delete this.data['vcd']['events'];
            }
        }

        if (this.data['vcd']['contexts']) {
            if (Object.keys(this.data['vcd']['contexts']).length === 0) {  // So there is 'contexts', but empty
                delete this.data['vcd']['contexts'];
            }
        }

        if (this.data['vcd']['relations']) {
            if (Object.keys(this.data['vcd']['relations']).length === 0) {  // So there is 'relations', but empty
                delete this.data['vcd']['relations'];
            }
        }
    }

    private addFrames(frameValue: any, elementType: ElementType, uidToAssign) {        
        // This functions add frame structures to root vcd
        let elementTypeName = ElementType[elementType];
        if (Number.isInteger(frameValue)) {
            this.addFrame(frameValue);
            this.data['vcd']['frames'][frameValue][elementTypeName + 's'] = this.data['vcd']['frames'][frameValue][elementTypeName + 's'] || {};
            this.data['vcd']['frames'][frameValue][elementTypeName + 's'][uidToAssign] = this.data['vcd']['frames'][frameValue][elementTypeName + 's'][uidToAssign] || {};
        }
        else if (Array.isArray(frameValue)) {
            for (var frameNum = frameValue[0]; frameNum < frameValue[1] + 1; frameNum++) {
                this.addFrame(frameNum);                
                this.data['vcd']['frames'][frameNum][elementTypeName + 's'] = this.data['vcd']['frames'][frameNum][elementTypeName + 's'] || {};
                this.data['vcd']['frames'][frameNum][elementTypeName + 's'][uidToAssign] = this.data['vcd']['frames'][frameNum][elementTypeName + 's'][uidToAssign] || {};
            }
        }
        else if (frameValue.constructor == Object) {
            for (const key in frameValue) {
                var frameInterval = frameValue[key];
                for (var frameNum = frameInterval[0]; frameNum < frameInterval[1] + 1; frameNum++) {
                    // 1/3 Create the frame if it doesn't already exist
                    this.addFrame(frameNum);
                    // 2/3 Fill with entries for this element
                    this.data['vcd']['frames'][frameNum][elementTypeName + 's'] = this.data['vcd']['frames'][frameNum][elementTypeName + 's'] || {};
                    // 3/3 Create an empty entry (we only need the pointer at 'frames')
                    // If the entry already exists, it is overwritten to {}
                    this.data['vcd']['frames'][frameNum][elementTypeName + 's'][uidToAssign] = this.data['vcd']['frames'][frameNum][elementTypeName + 's'][uidToAssign] || {};
                }
            }
        }
        else {
            console.warn("WARNING: calling addFrames with " + typeof frameValue);
        }
    }

    private updateFrameIntervals(fisDictExisting: Array<object>, frameValue) {
        // This function receives a frameValue (int, tuple or list) and fuses with existing fis
        // This function also updates frame intervals of root VCD
        if (frameValue == null) {
            console.warn("WARNING: frameValue is null");
            return;
        }  // So this control should be external to this function

        if (fisDictExisting == null) {
            fisDictExisting = [];
        }

        if (fisDictExisting.length == 0) {
            // This can happen when a new object/action/... is created
            var fisDictNew = utils.asFrameIntervalsArrayDict(frameValue);
            this.updateFrameIntervalsOfVcd(fisDictNew);
            return fisDictNew;
        }
        // Up to this point, fisExisting has something        
        var lastFrameEnd = fisDictExisting[fisDictExisting.length - 1]['frame_end'];

        // Next code is about speeding up the updating process
        var fisDictFused = fisDictExisting;
        var isSingleFrame = Number.isInteger(frameValue);
        var callFullFusion;
        if (isSingleFrame && lastFrameEnd != null) {
            if (lastFrameEnd == frameValue) {
                // Same frameValue, so no need to update anything
                callFullFusion = false;
                null;
            }
            else {
                if (frameValue == lastFrameEnd + 1) {
                    // So this is the next frame, let's skip all fusing computation and simply sum 1 to last value
                    if (fisDictFused[fisDictFused.length - 1]['frame_end'] == lastFrameEnd) {

                        // Confirmed this element was updated last time
                        fisDictFused[fisDictFused.length - 1] = {
                            'frame_start': fisDictFused[fisDictFused.length - 1]['frame_start'],
                            'frame_end': fisDictFused[fisDictFused.length - 1]['frame_end'] + 1
                        }

                        // Now global frameIntervals at VCD (it is guaranteed that last entry was lastFrame)
                        var lastVcdFiDict = this.data['vcd']['frame_intervals'][this.data['vcd']['frame_intervals'].length -1];

                        // VCD frame intervals need to be updated as well
                        if (lastVcdFiDict['frame_end'] == lastFrameEnd) {
                            // This is the first object updating this frame
                            this.data['vcd']['frame_intervals'][this.data['vcd']['frame_intervals'].length - 1] = {
                                'frame_start': lastVcdFiDict['frame_start'],
                                'frame_end': lastVcdFiDict['frame_end'] + 1
                            }
                        }
                        else if (lastVcdFiDict['frame_end'] == frameValue) {
                            // No need to update
                            null;
                        }
                        else {
                            // Ok, need to update VCD frame intervals analyzing it entirely
                            this.updateFrameIntervalsOfVcd(fisDictFused);
                        }
                        callFullFusion = false;
                    }
                    else {
                        // This element wasn't updated last time
                        callFullFusion = true;
                    }
                }
                else {
                    // Let's compute fusion normally
                    callFullFusion = true;
                }
            }
        }
        else {
            // So we are given a tuple or list, let's go through the entire fusion process
            callFullFusion = true
        }

        if (callFullFusion) {
            if (frameValue != null) {
                if (isSingleFrame) {
                    var fiDictNew = { 'frame_start': frameValue, 'frame_end': frameValue }
                    fisDictFused = utils.fuseFrameIntervalDict(fiDictNew, fisDictExisting)
                }
                else {
                    var fisDictNew = utils.asFrameIntervalsArrayDict(frameValue)
                    fisDictExisting = fisDictExisting.concat(fisDictNew)
                    fisDictFused = utils.fuseFrameIntervals(fisDictExisting)
                }
            }
            else {
                fisDictFused = fisDictExisting  // Use those existing
            }
            // Update also intervals of VCD
            this.updateFrameIntervalsOfVcd(fisDictFused);
        }
        return fisDictFused;
    }

    private addElement(elementType: ElementType, name: string, semanticType = '', frameValue = null, uid = null, ontUid = null, stream = null) {
        let elementTypeName = ElementType[elementType];        
        if (frameValue != null) {
            if (!Number.isInteger(frameValue) && !Array.isArray(frameValue) && frameValue.constructor != Object) {
                console.warn("WARNING: frameValue has no valid format (int, array or object)");
            }
        }

        // 1/5 Get uid to assign
        // This function checks if the uid exists (keeps it), or if not, and if it is null
        var uidToAssign = this.getUidToAssign(elementType, uid);
        // Get existing frame intervals
        var fisDictsExisting = [];  // array of object
        if (elementTypeName + 's' in this.data['vcd']) {
            if (this.data['vcd'][elementTypeName + 's'][uidToAssign]) {
                // This element already exists{ we need to fuse frameValue with the existing frameIntervals
                var element = this.data['vcd'][elementTypeName + 's'][uidToAssign];
                fisDictsExisting = element['frame_intervals'] || [];
            }
        }

        var fisDictsUpdated = []
        if (frameValue != null) {
            // 2/5 Update elements frameIntervals
            fisDictsUpdated = this.updateFrameIntervals(fisDictsExisting, frameValue);

            // 3/5 Create 'frames' for newly added frames with pointers
            this.addFrames(frameValue, elementType, uidToAssign);
        }
        else {
            // Nothing about frame intervals to be updated
            fisDictsUpdated = fisDictsExisting;
        }

        // 4/5 Create/update Element
        this.createUpdateElement(elementType, name, semanticType, fisDictsUpdated, uidToAssign, ontUid, stream);

        return uidToAssign;
    }

    private updateElement(elementType: ElementType, uid: number, frameValue) {
        let elementTypeName = ElementType[elementType];
        // Check if this uid exists
        if (!this.data['vcd'][elementTypeName + 's'][uid]) {
            console.warn("WARNING: trying to update a non-existing Element.")
            return;
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
        this.addElement(elementType, name, semanticType, frameValue, uid, ontUid, stream);
    }

    private createUpdateElement(elementType: ElementType, name: string, semanticType: string, frameIntervalsDicts, uid, ontUid = null, stream = null) {
        // This function creates OR updates an element at the root of VCD using the given information
        var elementData = { 'name': name, 'type': semanticType, 'frame_intervals': frameIntervalsDicts };

        // Check existing data and push to elementData
        if (ontUid != null && this.getOntology(ontUid) != null) {
            elementData['ontology_uid'] = ontUid;
        }

        // Check Stream codename existence
        if (stream != null) {
            if (this.data['vcd']['metadata']) {
                if (this.data['vcd']['metadata']['streams']) {
                    if (this.data['vcd']['metadata']['streams'][stream]) {
                        elementData['stream'] = stream;
                    }
                }
            }
            else {
                console.warn('WARNING: trying to add ObjectData for non-declared Stream. Use vcd.addStream.');
            }
        }

        // Check data if object
        if (elementType == ElementType.object) {
            if (this.data['vcd']['objects']) {
                if (this.data['vcd']['objects'][uid]) {
                    if (this.data['vcd']['objects'][uid]['object_data']) {
                        elementData['object_data'] = this.data['vcd']['objects'][uid]['object_data'];
                    }
                }
            }
        }

        // Check data if action
        if (elementType == ElementType.action) {
            if (this.data['vcd']['actions']) {
                if (this.data['vcd']['actions'][uid]) {
                    if (this.data['vcd']['actions'][uid]['action_data']) {
                        elementData['action_data'] = this.data['vcd']['actions'][uid]['action_data'];
                    }
                }
            }
        }

        // Check if relation
        else if (elementType == ElementType.relation) {
            if (this.data['vcd']['relations']) {
                if (this.data['vcd']['relations'][uid]) {
                    if (this.data['vcd']['relations'][uid]['rdfSubjects']) {
                        elementData['rdfSubjects'] = this.data['vcd']['relations'][uid]['rdfSubjects'];
                    }
                    if (this.data['vcd']['relations'][uid]['rdfObjects']) {
                        elementData['rdfObjects'] = this.data['vcd']['relations'][uid]['rdfObjects'];
                    }
                }
            }
        }

        let elementTypeName = ElementType[elementType];
        this.data['vcd'][elementTypeName + 's'] = this.data['vcd'][elementTypeName + 's'] || {};
        this.data['vcd'][elementTypeName + 's'][uid] = elementData;  // This call creates or updates the element data
    }

    private updateObjectData(uid: number, objectData, frameIntervals) {
        // 1/2 Check Stream codename existence
        var streamValid = false;
        if (objectData.data['inStream']) {
            if (this.data['vcd']['metadata']) {
                if (this.data['vcd']['metadata']['streams']) {
                    for (const prop in this.data['vcd']['metadata']['streams']) {
                        var stream = this.data['vcd']['metadata']['streams'][prop];
                        if (objectData.data['inStream'] == stream['name']) {
                            streamValid = true;
                        }
                    }
                }
            }
            if (!streamValid) {
                console.warn('WARNING: trying to add ObjectData for non-declared Stream. Use vcd.addStream.');
            }
        }

        // 2/2 Fill-in object data...
        // 2.1/2 As "static" content at ['vcd']['objects']...
        if (frameIntervals.length == 0) {
            if (this.data['vcd']['objects'][uid]) {
                var object = this.data['vcd']['objects'][uid];
                // This is static content that goes into static part of Object
                object['object_data'] = object['object_data'] || {}; // Creates 'object_data' if it does not exist
                object['object_data'][objectData.typeName()] = object['object_data'][objectData.typeName()] || [];
                object['object_data'][objectData.typeName()].push(objectData.data);
            }
            else {
                console.warn("WARNING: Trying to add ObjectData to non-existing Object, uid: " + uid);
            }
        }
        // 2.2/2 OR as "dynamic" content at ['vcd']['frames']...
        else {
            // Create frames (if already existing addFrames manages the situation
            // Loop and fill
            for (var i = 0; i < frameIntervals.length; i++) {
                var fi = frameIntervals[i];
                for (var frameNum = fi['frame_start']; frameNum < fi['frame_end'] + 1; frameNum++) {
                    this.data['vcd']['frames'][frameNum]['objects'] = this.data['vcd']['frames'][frameNum]['objects'] || {};
                    if (this.data['vcd']['frames'][frameNum]['objects'][uid]) {
                        object = this.data['vcd']['frames'][frameNum]['objects'][uid];
                        object['object_data'] = object['object_data'] || {};  // Creates 'object_data' if it does not exist
                        object['object_data'][objectData.typeName()] = object['object_data'][objectData.typeName()] || [];
                        object['object_data'][objectData.typeName()].push(objectData.data);
                    }
                    else {  // need to create this entry, only with the pointer (uid) and the data
                        this.data['vcd']['frames'][frameNum]['objects'][uid] = {};
                        this.data['vcd']['frames'][frameNum]['objects'][uid]['object_data'] = {};
                        this.data['vcd']['frames'][frameNum]['objects'][uid]['object_data'][objectData.typeName()] = [objectData.data];
                    }
                }
            }
        }
    }

    private updateActionData(uid: number, actionData, frameIntervals) {
        // 1/2 Check Stream codename existence
        var streamValid = false;
        if (actionData.data['inStream']) {
            if (this.data['vcd']['metadata']) {
                if (this.data['vcd']['metadata']['streams']) {
                    for (const prop in this.data['vcd']['metadata']['streams']) {
                        var stream = this.data['vcd']['metadata']['streams'][prop];
                        if (actionData.data['inStream'] == stream['name']) {
                            streamValid = true;
                        }
                    }
                }
            }
            if (!streamValid) {
                console.warn('WARNING: trying to add actionData for non-declared Stream. Use vcd.addStream.');
            }
        }

        // 2/2 Fill-in action data...
        // 2.1/2 As "static" content at ['vcd']['actions']...
        if (!frameIntervals) {
            if (this.data['vcd']['actions'][uid]) {
                var action = this.data['vcd']['actions'][uid];
                // This is static content that goes into static part of action
                action['action_data'] = action['action_data'] || {}; // Creates 'action_data' if it does not exist
                action['action_data'][actionData.typeName()] = action['action_data'][actionData.typeName()] || [];
                action['action_data'][actionData.typeName()].push(actionData.data);
            }
            else {
                console.warn("WARNING: Trying to add actionData to non-existing action, uid: " + uid);
            }
        }
        // 2.2/2 OR as "dynamic" content at ['vcd']['frames']...
        else {
            // Create frames (if already existing addFrames manages the situation
            // Loop and fill
            for (var i = 0; i < frameIntervals.length; i++) {
                var fi = frameIntervals[i];
                for (var frameNum = fi['frame_start']; frameNum < fi['frame_end'] + 1; frameNum++) {
                    this.data['vcd']['frames'][frameNum]['actions'] = this.data['vcd']['frames'][frameNum]['actions'] || {};
                    if (this.data['vcd']['frames'][frameNum]['actions'][uid]) {
                        action = this.data['vcd']['frames'][frameNum]['actions'][uid];
                        action['action_data'] = action['action_data'] || {};  // Creates 'action_data' if it does not exist
                        action['action_data'][actionData.typeName()] = action['action_data'][actionData.typeName()] || [];
                        action['action_data'][actionData.typeName()].push(actionData.data);
                    }
                    else {  // need to create this entry, only with the pointer (uid) and the data
                        this.data['vcd']['frames'][frameNum]['actions'][uid] = {};
                        this.data['vcd']['frames'][frameNum]['actions'][uid]['action_data'] = {};
                        this.data['vcd']['frames'][frameNum]['actions'][uid]['action_data'][actionData.typeName()] = [actionData.data];
                    }
                }
            }
        }
    }
    
    private updateContextData(uid: number, contextData, frameIntervals) {
        //TODO
    }

    private updateEventData(uid: number, eventData, frameIntervals) {
        //TODO
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////
    // Public API: add, update
    ////////////////////////////////////////////////////////////////////////////////////////////////////
    public addMetadataProperties(properties: object) {        
        var prop = this.data['vcd']['metadata']['properties'] || {};
        Object.assign(prop, properties);        
    }

    public addName(name) {

        if (typeof name != 'string' && !(name instanceof String)) {
            console.warn("name not string");
            return;
        }
        this.data['vcd']['name'] = name;
    }

    public addAnnotator(annotator) {
        if (typeof annotator != 'string' && !(annotator instanceof String)) {
            console.warn("annotator not string");
            return;
        }
        if (!this.data['vcd']['metadata']) {
            this.data['vcd']['metadata'] = {};
        }
        this.data['vcd']['metadata']['annotator'] = annotator;
    }

    public addComment(comment) {
        if (typeof comment != 'string' && !(comment instanceof String)) {
            console.warn("comment not string");
            return;
        }
        if (!this.data['vcd']['metadata']) {
            this.data['vcd']['metadata'] = {};
        }
        this.data['vcd']['metadata']['comment'] = comment;
    }

    public addOntology(ontologyName: string) {
        this.data['vcd']['ontologies'] = this.data['vcd']['ontologies'] || {};
        for (const ont_uid in this.data['vcd']['ontologies']) {
            if (this.data['vcd']['ontologies'][ont_uid] == ontologyName) {
                console.warn('WARNING: adding an already existing ontology');
                return null;
            }
        }
        var length = Object.keys(this.data['vcd']['ontologies']).length;
        this.data['vcd']['ontologies'][length] = ontologyName;
        return length;
    }

    public addStream(streamName: string, uri: string, description: string, sensorType: StreamType) {       
        this.data['vcd']['metadata'] = this.data['vcd']['metadata'] || {};
        this.data['vcd']['metadata']['streams'] = this.data['vcd']['metadata']['streams'] || {};
        this.data['vcd']['metadata']['streams'][streamName] = this.data['vcd']['metadata']['streams'][streamName] || {};
        
        this.data['vcd']['metadata']['streams'][streamName] = {
            'description': description, 'uri': uri, 'type': sensorType
        }
        
    }

    public addFrameProperties(frameNum: number, properties: object) {        
        this.addFrame(frameNum);  // this function internally checks if( the frame already exists
        this.data['vcd']['frames'][frameNum]['frame_properties'] = this.data['vcd']['frames'][frameNum]['frame_properties'] || {};
        this.data['vcd']['frames'][frameNum]['frame_properties']['properties'] = this.data['vcd']['frames'][frameNum]['frame_properties']['properties'] || {};
        Object.assign(this.data['vcd']['frames'][frameNum]['frame_properties']['properties'], properties);        
    }

    public addOdometry(frameNum: number, odometry: types.Odometry) {
        // TODO
    }

    public addStreamProperties(streamName: string, properties: object, frameNum = null) {
        // This function can be used to add stream properties. if( frame_num is defined, the information is embedded
        // inside 'frame_properties' of the specified frame. Otherwise, the information is embedded into
        // 'stream_properties' inside 'metadata'.

        // Find if( this stream is declared
        if (this.data['vcd']['metadata']) {
            if (this.data['vcd']['metadata']['streams']) {
                if (this.data['vcd']['metadata']['streams'][streamName]) {
                    if (frameNum == null) {
                        // This information is static
                        this.data['vcd']['metadata']['streams'][streamName]['stream_properties'] = this.data['vcd']['metadata']['streams'][streamName]['stream_properties'] || {};
                        Object.assign(this.data['vcd']['metadata']['streams'][streamName]['stream_properties'], properties);
                    }
                    else {
                        // This is information of the stream for( a specific frame
                        this.addFrame(frameNum); // to add the frame in case it does not exist
                        var frame = this.data['vcd']['frames'][frameNum];
                        frame['frame_properties'] = frame['frame_properties'] || {};
                        frame['frame_properties']['streams'] = frame['frame_properties']['streams'] || {};
                        frame['frame_properties']['streams'][streamName] = frame['frame_properties']['streams'][streamName] || {};
                        frame['frame_properties']['streams'][streamName]['stream_properties'] = frame['frame_properties']['streams'][streamName]['stream_properties'] || {};
                        Object.assign(frame['frame_properties']['streams'][streamName]['stream_properties'], properties);
                    }
                }
                else {
                    console.warn('WARNING: Trying to add frame sync about non-existing stream');
                }
            }
        }
    }

    public validate(vcd: object) {
        let v = new Validator();
        var validationResult = v.validate(vcd, this.schema);

        return validationResult
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
            let validationResult = this.validate(this.data)
            for(var i = 0; i <validationResult.errors.length; i++){
                console.log(validationResult.errors[i].message);
            }
        }
        return stringified_vcd
    }

    public stringifyFrame(frameNum: number, dynamicOnly = true, pretty = false) {
        // TODO
    }

    public updateObject(uid: number, frameValue) {
        // This function is only needed if( no add_object_data calls are used, but the object needs to be kept alive
        return this.updateElement(ElementType.object, uid, frameValue);
    }

    public updateAction(uid: number, frameValue) {
        return this.updateElement(ElementType.action, uid, frameValue);
    }

    public updateContext(uid: number, frameValue) {
        return this.updateElement(ElementType.context, uid, frameValue);
    }

    public updateRelation(uid: number, frameValue) {
        return this.updateElement(ElementType.relation, uid, frameValue);
    }

    public addObject(name: string, semanticType: string, frameValue = null, uid = null, ontUid = null, stream = null) {
        return this.addElement(ElementType.object, name, semanticType, frameValue, uid, ontUid, stream);
    }

    public addAction(name: string, semanticType: string, frameValue = null, uid = null, ontUid = null, stream = null) {
        return this.addElement(ElementType.action, name, semanticType, frameValue, uid, ontUid, stream);
    }

    public addEvent(name: string, semanticType: string, frameValue = null, uid = null, ontUid = null, stream = null) {
        return this.addElement(ElementType.event, name, semanticType, frameValue, uid, ontUid, stream);
    }

    public addContext(name: string, semanticType: string, frameValue = null, uid = null, ontUid = null, stream = null) {
        return this.addElement(ElementType.context, name, semanticType, frameValue, uid, ontUid, stream);
    }

    public addRelation(name: string, semanticType: string, frameValue = null, uid = null, ontUid = null) {
        return this.addElement(
            ElementType.relation, name, semanticType, frameValue, uid = uid, ontUid = ontUid
        );
    }

    public addRdf(relationUid: number, rdfType: RDF, elementUid: number, elementType: ElementType) {
        let elementTypeName = ElementType[elementType]
        if (!this.data['vcd']['relations'][relationUid]) {
            console.warn("WARNING: trying to add RDF to non-existing Relation.")
            return;
        }
        else {
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

    public addRelationObjectAction(name: string, semanticType: string, objectUid: number, actionUid: number, relationUid = null, ontUid = null, frameValue=null) {
        // TODO
    }

    public addRelationActionAction(name: string, semanticType: string, objectUid: number, actionUid: number, relationUid = null, ontUid = null, frameValue=null) {
        // TODO
    }

    public addRelationObjectObject(name: string, semanticType: string, objectUid: number, actionUid: number, relationUid = null, ontUid = null, frameValue=null) {
        // TODO
    }

    public addRelationActionObject(name: string, semanticType: string, objectUid: number, actionUid: number, relationUid = null, ontUid = null, frameValue=null) {
        // TODO
    }

    public addObjectData(uid: number, objectData, frameValue = null) {        
        // 1/3 Update element at vcd (internally, this fuses the frame intervals, etc.
        this.updateElement(ElementType.object, uid, frameValue);

        // 2/3 Update object data
        var frameIntervals = utils.asFrameIntervalsArrayDict(frameValue);  // returns [] if frameValue is null
        this.updateObjectData(uid, objectData, frameIntervals);

        // 3/3 Update auxiliary array
        this.objectDataNames[uid] = this.objectDataNames[uid] || [];
        this.objectDataNames[uid].push(objectData.data['name']);
    }

    public addActionData(uid: number, actionData, frameValue = null) {
        // 1/3 Update element at vcd (internally, this fuses the frame intervals, etc.
        this.updateElement(ElementType.action, uid, frameValue);

        // 2/3 Update action data
        var frameIntervals = utils.asFrameIntervalsArrayDict(frameValue);
        this.updateActionData(uid, actionData, frameIntervals);

        // 3/3 Update auxiliary array
        this.actionDataNames[uid] = this.actionDataNames[uid] || [];
        this.actionDataNames[uid].push(actionData.data['name']);
    }

    public addContextData(uid: number, contextData, frameValue = null) {
        // TODO
    }

    public addEventData(uid: number, eventData, frameValue = null) {
        // TODO
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////
    // Get / Read
    ////////////////////////////////////////////////////////////////////////////////////////////////////
    
    /*public setData(schema: any, data: any) {
        // TODO: Is this function necessary?
        this.lastUID = {};
        this.schema = schema;
        this.data = data;
        this.init();
    }*/

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
    
    public has(elementType: ElementType, uid: number) {
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

    public getElement(elementType: ElementType, uid: number) {        
        let elementTypeName = ElementType[elementType]

        if (this.data['vcd'][elementTypeName + 's'] == null) {
            console.warn("WARNING: trying to get a " + elementTypeName + " but this VCD has none.");
            return null;
        }
        if (this.data['vcd'][elementTypeName + 's'][uid]) {
            return this.data['vcd'][elementTypeName + 's'][uid];
        }
        else {
            console.warn("WARNING: trying to get non-existing " + elementTypeName + " with uid: " + uid);
            return null;
        }
    }

    public getObject(uid: number) {
        return this.getElement(ElementType.object, uid);
    }

    public getAction(uid: number) {
        return this.getElement(ElementType.action, uid);
    }

    public getEvent(uid: number) {
        return this.getElement(ElementType.event, uid);
    }

    public getContext(uid: number) {
        return this.getElement(ElementType.context, uid);
    }

    public getRelation(uid: number) {
        return this.getElement(ElementType.relation, uid);
    }

    public getFrame(frameNum: number) {
        if (this.data['vcd']['frames']) {
            return this.data['vcd']['frames'][frameNum];
        }
    }

    public getElementsOfType(elementType: ElementType, type: string): number[] {
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

    public getObjectsWithObjectDataName(dataName: string) {
        var uids = [];
        for (const uid in this.data['vcd']['objects']) {
            if (this.objectDataNames[uid]) {
                if (this.objectDataNames[uid][dataName]) {
                    uids.push(uid);
                }
            }
        }
        return uids;
    }

    public hasFrameObjectDataName(frameNum: number, dataName: string, uid_ = -1) {
        if (this.data['vcd']['frames'][frameNum]) {
            for (const uid in this.data['vcd']['frames'][frameNum]['objects']) {
                var obj = this.data['vcd']['frames'][frameNum]['objects'][uid];
                if (uid_ == -1 || parseInt(uid) == uid_) {  // if( uid == -1 means we want to loop over all objects
                    for (const prop in obj['object_data']) {
                        var valArray = obj['object_data'][prop];
                        for (var i = 0; i < valArray.length; i++) {
                            var val = valArray[i];
                            if (val['name'] == dataName) {
                                return true;
                            }
                        }
                    }
                }
            }
        }
        return false;
    }

    public hasFrameActionDataName(frameNum: number, dataName: string, uid_ = -1) {
        if (this.data['vcd']['frames'][frameNum]) {
            for (const uid in this.data['vcd']['frames'][frameNum]['actions']) {
                var obj = this.data['vcd']['frames'][frameNum]['actions'][uid];
                if (uid_ == -1 || parseInt(uid) == uid_) {  // if( uid == -1 means we want to loop over all actions
                    for (const prop in obj['action_data']) {
                        var valArray = obj['action_data'][prop];
                        for (var i = 0; i < valArray.length; i++) {
                            var val = valArray[i];
                            if (val['name'] == dataName) {
                                return true;
                            }
                        }
                    }
                }
            }
        }
        return false;
    }

    public getFramesWithObjectDataName(uid: number, dataName: string) {
        var frames = [];
        if (this.data['vcd']['objects'][uid] && this.objectDataNames[uid]) {
            var object = this.data['vcd']['objects'][uid];
            if (this.objectDataNames[uid][dataName]) {
                // Now look into Frames
                var fis = object['frame_intervals'];
                for (var i = 0; i < fis.length; i++) {
                    var fi = fis[i];
                    var fi_tuple = [fi['frame_start'], fi['frame_end']];
                    for (var frameNum = fi_tuple[0]; frameNum < fi_tuple[1] + 1; frameNum++) {
                        if (this.hasFrameObjectDataName(frameNum, dataName, uid)) {
                            frames.push(frameNum);
                        }
                    }
                }
            }
        }
        return frames;
    }

    public getObjectData(uid: number, dataName: string, frameNum = null) {
        if (this.data['vcd']['objects'][uid]) {
            if (this.objectDataNames[uid][dataName]) {
                // Frame-specific information
                if (frameNum != null) {
                    if (this.data['vcd']['frames'][frameNum]['objects'][uid]) {
                        var object = this.data['vcd']['frames'][frameNum]['objects'][uid];
                        for (const prop in object['object_data']) {
                            var valArray = object['object_data'][prop];
                            for (var i = 0; i < valArray.length; i++) {
                                var val = valArray[i];
                                if (val['name'] == dataName) {
                                    return val;
                                }
                            }
                        }
                    }
                }
                // Static information
                else {
                    var object = this.data['vcd']['objects'][uid];
                    if (object["object_data"]) {
                        for (const prop in object['object_data']) {
                            var valArray = object['object_data'][prop];
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
        return {};
    }

    public getActionData(uid: number, dataName: string, frameNum = null) {
        if (this.data['vcd']['actions'][uid]) {
            if (this.actionDataNames[uid][dataName]) {
                // Frame-specific information
                if (frameNum != null) {
                    if (this.data['vcd']['frames'][frameNum]['actions'][uid]) {
                        var action = this.data['vcd']['frames'][frameNum]['actions'][uid];
                        for (const prop in action['action_data']) {
                            var valArray = action['action_data'][prop];
                            for (var i = 0; i < valArray.length; i++) {
                                var val = valArray[i];
                                if (val['name'] == dataName) {
                                    return val;
                                }
                            }
                        }
                    }
                }
                // Static information
                else {
                    var action = this.data['vcd']['actions'][uid];
                    if (action["action_data"]) {
                        for (const prop in action['action_data']) {
                            var valArray = action['action_data'][prop];
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
        return {};
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

    public getOntology(ontUid: number) {
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

    public getFrameIntervals() {
        return this.data['vcd']['frame_intervals'];
    }

    public getFrameIntervalsOfElement(elementType: ElementType, uid: number) {
        let elementTypeName = ElementType[elementType]
        if (!this.data['vcd'][elementTypeName + 's']) {
            console.warn(elementTypeName + 's' + " not in this.data['vcd']");
        }
        return this.data['vcd'][elementTypeName + 's'][uid]['frame_intervals'];
    }

    public isRelationAtFrame(relation: object, frame: number) {
        // TODO
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////
    // Remove
    ////////////////////////////////////////////////////////////////////////////////////////////////////
    public rmElementByType(elementType: ElementType, semanticType: string) {
        let elementTypeName = ElementType[elementType]
        var elements = this.data['vcd'][elementTypeName + 's'];
        var index = null;

        // Get Element from summary
        var element = null;
        for (uid in elements) {
            element = elements[uid];
            if (element['type'] == semanticType) {
                index = uid;
                break;
            }
        }

        if (index == null) {  // not found
            console.warn("WARNING: can't remove Element with semantic type: " + semanticType + ": no Element found");
            return;
        }

        // Update indexes and other member variables
        var uid = index;
        if (elementType == ElementType.object) {
            delete this.objectDataNames[uid];
        }
        if (elementType == ElementType.action) {
            delete this.actionDataNames[uid];
        }

        // Remove from Frames{ let's read frameIntervals from summary
        for (var i = 0; i < element['frame_intervals'].length; i++) {
            var fi = element['frame_intervals'][i];
            for (var frameNum = fi['frame_start']; frameNum < fi['frame_end'] + 1; frameNum++) {
                var elementsInFrame = this.data['vcd']['frames'][frameNum][elementTypeName + 's'];
                if (elementsInFrame[uid]) {
                    delete elementsInFrame[uid];
                }
                if (Object.keys(elementsInFrame).length == 0) {  // objects might have end up empty TODO{ test this
                    elementsInFrame = null;
                }
            }
        }

        // Remove from summary
        delete elements[uid];

        // Clean-up Frames and Elements
        this.clean();
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

    public rmElementByFrame(elementType: ElementType, uid: number, frameIntervalTuple: number | Array<number>) {
        let elementTypeName = ElementType[elementType]
        var frameIntervalDict = utils.asFrameIntervalDict(frameIntervalTuple);
        var elements = this.data['vcd'][elementTypeName + 's'];
        var element;

        if (elements[uid]) {
            element = elements[uid];
        }
        else {  // not found
            console.warn("WARNING: trying to remove non-existing Element of type: ", elementTypeName, " and uid: ", uid);
            return;
        }
        // Remove from Frames{ let's read frameIntervals from summary
        for (var i = 0; i < element['frame_intervals'].length; i++) {
            var fi = element['frame_intervals'][i];
            for (var frameNum = fi['frame_start']; frameNum < fi['frame_end'] + 1; frameNum++) {
                if (frameIntervalDict['frame_start'] <= frameNum <= frameIntervalDict['frame_end']) {
                    var elementsInFrame = this.data['vcd']['frames'][frameNum][elementTypeName + 's'];
                    if (elementsInFrame[uid]) {
                        delete elementsInFrame[uid];
                    }
                    if (Object.keys(elementsInFrame).length == 0) {  // objects might have end up empty TODO{ test this
                        elementsInFrame = null;
                    }
                }
            }
        }

        // Substract this frameInterval from this element
        this.removeElementFrameInterval(elementType, uid, frameIntervalDict);

        // Clean-up Frames and Elements
        this.clean();

        // Update indexes and other member variables
        this.computeObjectDataNamesUid(uid);
        this.computeActionDataNamesUid(uid);

        var outerInterval = utils.getOuterFrameInterval(element['frame_intervals'])
        if (frameIntervalDict['frame_start'] <= outerInterval['frame_start'] && frameIntervalDict['frame_end'] >= outerInterval['frame_end']) {
            // The deleted frame interval covers the entire element, so let's delete it from the summary
            delete elements[uid];
        }
    }

    public rmObjectByFrame(uid: number, frameIntervalTuple: number | Array<number>) {
        return this.rmElementByFrame(ElementType.object, uid, frameIntervalTuple);
    }

    public rmActionByFrame(uid: number, frameIntervalTuple: number | Array<number>) {
        return this.rmElementByFrame(ElementType.action, uid, frameIntervalTuple);
    }

    public rmEventByFrame(uid: number, frameIntervalTuple: number | Array<number>) {
        return this.rmElementByFrame(ElementType.event, uid, frameIntervalTuple);
    }

    public rmContextByFrame(uid: number, frameIntervalTuple: number | Array<number>) {
        return this.rmElementByFrame(ElementType.context, uid, frameIntervalTuple);
    }

    public rmRelationByFrame(uid: number, frameIntervalTuple: number | Array<number>) {
        return this.rmElementByFrame(ElementType.relation, uid, frameIntervalTuple);
    }

    public rmElement(elementType: ElementType, uid: number) {
        let elementTypeName = ElementType[elementType]
        var elements = this.data['vcd'][elementTypeName + 's'];

        // Get Element from summary
        var element;
        if (elements[uid]) {
            element = elements[uid];
        }
        else {  // not found
            console.warn("WARNING: trying to remove non-existing Element of type: ", elementTypeName, " and uid: ", uid);
            return;
        }

        // Update indexes and other member variables
        if (elementType == ElementType.object) {
            delete this.objectDataNames[uid];
        }

        // Update indexes and other member variables
        if (elementType == ElementType.action) {
            delete this.actionDataNames[uid];
        }

        // Remove from Frames{ let's read frameIntervals from summary
        for (var i = 0; i < element['frame_intervals'].length; i++) {
            var fi = element['frame_intervals'][i];
            for (var frameNum = fi['frame_start']; frameNum < fi['frame_end'] + 1; frameNum++) {
                var elementsInFrame = this.data['vcd']['frames'][frameNum][elementTypeName + 's'];
                if (elementsInFrame[uid]) {
                    delete elementsInFrame[uid];
                }
                if (Object.keys(elementsInFrame).length == 0) {  // objects might have end up empty TODO{ test this
                    elementsInFrame = null;
                }
            }
        }

        // Clean-up Frames
        this.clean();

        // Delete this element from summary
        delete elements[uid];
    }

    public rmObject(uid: number) {
        this.rmElement(ElementType.object, uid);
    }

    public rmAction(uid: number) {
        this.rmElement(ElementType.action, uid);
    }

    public rmEvent(uid: number) {
        this.rmElement(ElementType.event, uid);
    }

    public rmContext(uid: number) {
        this.rmElement(ElementType.context, uid);
    }

    public rmRelation(uid: number) {
        this.rmElement(ElementType.relation, uid);
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////
    // Modified by: Paola Cañas 09/06/2020
    ////////////////////////////////////////////////////////////////////////////////////////////////////
    /* Hay que crear una funciond e add o mirar como se optimiza para agragarlo en update. creo que se puede añdair el intervalo y luego se calculara solo lo demas*/
    /*
    Function to update or add one interval in "frame_intervals" list of specified object in specific element
    @elementType: element to be modified (ex:action,object)
    @uid: id of the object in element list
    @intervalId: position of the frameInterval to be modified in "frame_intervals" list of object
    @newItervalLimits: array=[start, end]
    */
    public updateOneFrameInterOfElement(elementType: ElementType, uid: number, intervalId: number, newIntervalLimits: Array<number>) {
        let elementTypeName = ElementType[elementType]
        if (this.data['vcd'][elementTypeName + 's'][uid]["frame_intervals"] == null) {
            console.warn("WARNING: trying to get frame intervals of " + uid + " but is not found.");
        } else if (!Array.isArray(newIntervalLimits)) {
            console.warn("WARNING: not a valid interval to include in vcd.");
        } else {
            //conver new interval to dict
            var newInterval = utils.asFrameIntervalDict(newIntervalLimits);
            var oldIntervals = this.data['vcd'][elementTypeName + 's'][uid]["frame_intervals"];
            if (intervalId != null) {
                if (this.data['vcd'][elementTypeName + 's'][uid]["frame_intervals"][intervalId] == null) {
                    console.warn("WARNING: trying to get frame interval of " + uid + " but is not found.");
                } else {
                    //interval exists and needs to be updated
                    this.data['vcd'][elementTypeName + 's'][uid]["frame_intervals"][intervalId] = newInterval;
                }

            } else {
                //add new interval to existing
                oldIntervals.push(newInterval);
                this.data['vcd'][elementTypeName + 's'][uid]["frame_intervals"] = oldIntervals;
            }
            //see if there is overlapping and unify
            oldIntervals = this.data['vcd'][elementTypeName + 's'][uid]["frame_intervals"];
            var newIntervals = utils.fuseFrameIntervals(oldIntervals);
            this.data['vcd'][elementTypeName + 's'][uid]["frame_intervals"] = newIntervals;
        }
    }
    /*
    Function to remove one interval in "frame_intervals" list of specified object in specific element
    @elementType: element to be modified (ex:action,object)
    @uid: id of the object in element list
    @interval: can be: 
    -position of the frameInterval to be modified in "frame_intervals" list of object
    -array with limits of interval
    -frame interval dict
    */
    public removeOneFrameInterOfElement(elementType: ElementType, uid: number, interval) {
        let elementTypeName = ElementType[elementType]
        //If interval is an Id
        var intervalToRemove;
        if (Number.isInteger(parseInt(interval))) {
            if (this.data['vcd'][elementTypeName + 's'][uid]["frame_intervals"][interval] == null) {
                console.warn("WARNING: trying to get frame interval of " + uid + " but is not found.");
            } else {
                intervalToRemove = this.data['vcd'][elementTypeName + 's'][uid]["frame_intervals"][interval];
            }
        }
        //interval is an array
        else if (Array.isArray(interval)) {
            if (interval.length != 2) {
                console.warn("WARNING: not a valid interval to include in vcd.");
            } else {
                intervalToRemove = utils.asFrameIntervalDict(interval);
            }
        }
        //interval is a dict 
        else if (interval.constructor == Object) {
            if (Object.keys(interval).length === 0) {
                console.warn("WARNING: not a valid interval to include in vcd.");
            } else {
                intervalToRemove = interval;
            }
        } else {
            console.warn("WARNING: not a valid interval to include in vcd.");
        }
        //remove
        this.removeElementFrameInterval(elementType, uid, intervalToRemove);
    }
}