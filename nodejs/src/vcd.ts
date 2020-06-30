/**
* VCD (Video Content Description) 4.x.x
*
* This class is the main manager of VCD 4 content.
* It can be created void, and add content (e.g. Objects) using the API
* It can also be created by providing a JSON file.
* ```
* import { VCD4 } from 'vcd-ts'
* let vcd4 = new VCD4() // created void
* let vcd4 = new VCD4('myVCD.json') // loads myVCD.json file
* ```
*/

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
    
export class VCD4 {
	private data: any = {}
	private schema: any = {}
	
	private lastUID: any = {}
	private objectDataNames: any = {}
	private actionDataNames: any = {}
	
	private schema_file: "vcd_schema_json-v4.2.0.json";
	private version: "4.2.0";
	
	constructor(vcdFile = "") {
		this.init()		
	}
	
	printInfo() {
		console.log("This is a VCD4 content\n");
		console.log("\tversion: " + this.data['vcd']['version']);
	}
	
	private init(vcdFile = "") {
		if (vcdFile.length == 0) {			
			// Main VCD data
            this.data = { 'vcd': {} };
            this.data['vcd']['frames'] = {};
            this.data['vcd']['version'] = "4.2.0";
            this.data['vcd']['frame_intervals'] = [];

            // Schema information
            this.schema = {};

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
		else {
			// TODO: load from file, and validate with schema
		}
	}
	
	
	
	////////////////////////////////////////////////////////////////////////////////////////////////////
    // Core functions
    ////////////////////////////////////////////////////////////////////////////////////////////////////
	private computeLastUid() {
        this.lastUID = {};
        // Read all objects and fill lastUID
        this.lastUID['object'] = -1;
        if (this.data['vcd']['objects']) {
            for (const uid of Object.keys(this.data['vcd']['objects'])) {
                if (parseInt(uid) > this.lastUID['object']) {
                    this.lastUID['object'] = parseInt(uid);
                }
            }
        }

        this.lastUID['action'] = -1;
        if (this.data['vcd']['actions']) {
            for (const uid of Object.keys(this.data['vcd']['actions'])) {
                if (parseInt(uid) > this.lastUID['action']) {
                    this.lastUID['action'] = parseInt(uid);
                }
            }
        }

        this.lastUID['event'] = -1;
        if (this.data['vcd']['events']) {
            for (const uid of Object.keys(this.data['vcd']['events'])) {
                if (parseInt(uid) > this.lastUID['event']) {
                    this.lastUID['event'] = parseInt(uid);
                }
            }
        }

        this.lastUID['context'] = -1;
        if (this.data['vcd']['contexts']) {
            for (const uid of Object.keys(this.data['vcd']['contexts'])) {
                if (parseInt(uid) > this.lastUID['context']) {
                    this.lastUID['context'] = parseInt(uid);
                }
            }
        }

        this.lastUID['relation'] = -1;
        if (this.data['vcd']['relations']) {
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

    private getUidToAssign(elementType, uid) {
        var uidToAssign
        if (!this.assertElementType(elementType)) {
            return;
        }
        if (!uid) {
            this.lastUID[elementType] += 1;  // If null is provided, let's use the next one available
            uidToAssign = this.lastUID[elementType];
            return uidToAssign;
        }
        // uid is not null
        // There are already this type of elements in vcd
        if (uid > this.lastUID[elementType]) {
            this.lastUID[elementType] = uid;
            var uidToAssign = this.lastUID[elementType];
        }
        else {
            uidToAssign = uid;
        }
        return uidToAssign;
    }

    private updateFrameIntervalsOfVcd(frameIntervals) {

        if (!Array.isArray(frameIntervals)) {
            console.warn("frameIntervals not array");
            return;
        }
        if (frameIntervals.length == 0) {
            return;
        }

        // Fuse with existing
        var fit = JSON.parse(JSON.stringify(frameIntervals));
        var fis = this.data['vcd']['frame_intervals'] = this.data['vcd']['frame_intervals'] || [];
        fit += fis;

        // Now substitute
        var fitFused = this.fuseFrameIntervals(fit);
        this.data['vcd']['frame_intervals'] = fitFused;
    }

    private removeElementFrameInterval(elementType, uid, frameIntervalDict) {
        // This function removes a frameInterval from an element
        if (this.data['vcd'][elementType.name + 's'][uid]) {
            var fis = this.data['vcd'][elementType.name + 's'][uid]['frame_intervals'];

            var fiDictArrayToAdd = [];
            for (var i = 0; i < fis.length; i++) {
                // Three options{ 1) no intersection 2) one inside 3) intersection
                var maxStartVal = Math.max(frameIntervalDict['frameStart'], fis[i]['frameStart']);
                var minEndVal = Math.min(frameIntervalDict['frameEnd'], fis[i]['frameEnd']);

                if (frameIntervalDict['frameStart'] <= fis[i]['frameStart'] && frameIntervalDict['frameEnd'] >= fis[i]['frameEnd']) {
                    // Case c) equal tuples -> delete or Case f) interval to delete covers completely target interval
                    delete fis[i];
                }

                if (maxStartVal <= minEndVal) {
                    // There is some intersection{ cases a, b, d and e

                    if (maxStartVal == fis[i]['frameStart']) {  // cases a, b
                        var newFi1 = { 'frameStart': minEndVal + 1, 'frameEnd': fis[i]['frameEnd'] };
                        fis[i] = newFi1;
                    }
                    else if (minEndVal == fis[i]['frameEnd']) {  // case e
                        var newFi2 = { 'frameStart': fis[i]['frameStart'], 'frameEnd': maxStartVal - 1 };
                        fis[i] = newFi2;
                    }
                    else {  // case d maxStartVal > fiTuple[0] and minEndVal < fiTuple[1]
                        // Inside{ then we need to split into two frame intervals
                        var newFi3 = { 'frameStart': fis[i]['frameStart'], 'frameEnd': maxStartVal - 1 };
                        var newFi4 = { 'frameStart': minEndVal + 1, 'frameEnd': fis[i]['frameEnd'] };
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
                if (this.isInside(frameNum, fi)) {
                    found = true;
                }
            }
            if (!found) {
                // This frame is not included in the frameIntervals, let's modify them
                var idxToFuse = [];
                for (var i = 0; i < this.data['vcd']['frame_intervals'].length; i++) {
                    var fi = this.data['vcd']['frame_intervals'][i];
                    if (this.intersects(fi, this.asFrameIntervalDict(frameNum)) || this.consecutive(fi, this.asFrameIntervalDict(frameNum))) {
                        idxToFuse.push(i);
                    }
                }
                if (idxToFuse.length == 0) {
                    // New frameInterval, separated
                    this.data['vcd']['frame_intervals'].push({ 'frameStart': frameNum, 'frameEnd': frameNum });
                }
                else {
                    var newList = [];
                    var fusedFi = this.asFrameIntervalDict(frameNum);
                    for (var i = 0; i < this.data['vcd']['frame_intervals'].length; i++) {
                        var fi = this.data['vcd']['frame_intervals'][i];
                        if (idxToFuse.indexOf(i) > -1) {
                            fusedFi = { 'frame_start': Math.min(fusedFi['frame_start'], fi['frameStart']), 'frame_end': Math.max(fusedFi['frame_end'], fi['frame_end']) };
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

    private addFrame(frameNum) {
        // this.data['vcd']['frames'].setdefault(frameNum, {}) // 3.8 secs - 10.000 times
        if (!this.data['vcd']['frames'][frameNum]) {
            this.data['vcd']['frames'][frameNum] = {};
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

    private addFrames(frameValue, elementType, uidToAssign) {
        // This functions add frame structures to root vcd
        if (Number.isInteger(frameValue)) {
            this.addFrame(frameValue);
            this.data['vcd']['frames'][frameValue][elementType + 's'] = this.data['vcd']['frames'][frameValue][elementType + 's'] || {};
            this.data['vcd']['frames'][frameValue][elementType + 's'][uidToAssign] = this.data['vcd']['frames'][frameValue][elementType + 's'][uidToAssign] || {};
        }
        else if (Array.isArray(frameValue)) {
            for (var frameNum = frameValue[0]; frameNum < frameValue[1] + 1; frameNum++) {
                this.addFrame(frameNum);
                this.data['vcd']['frames'][frameNum][elementType + 's'] = this.data['vcd']['frames'][frameNum][elementType + 's'] || {};
                this.data['vcd']['frames'][frameNum][elementType + 's'][uidToAssign] = this.data['vcd']['frames'][frameNum][elementType + 's'][uidToAssign] || {};
            }
        }
        else if (frameValue.constructor == Object) {
            for (const key in frameValue) {
                var frameInterval = frameValue[key];
                for (var frameNum = frameInterval[0]; frameNum < frameInterval[1] + 1; frameNum++) {
                    // 1/3 Create the frame if it doesn't already exist
                    this.addFrame(frameNum);
                    // 2/3 Fill with entries for this element
                    this.data['vcd']['frames'][frameNum][elementType + 's'] = this.data['vcd']['frames'][frameNum][elementType + 's'] || {};
                    // 3/3 Create an empty entry (we only need the pointer at 'frames')
                    // If the entry already exists, it is overwritten to {}
                    this.data['vcd']['frames'][frameNum][elementType + 's'][uidToAssign] = this.data['vcd']['frames'][frameNum][elementType + 's'][uidToAssign] || {};
                }
            }
        }
        else {
            console.warn("WARNING: calling addFrames with " + typeof frameValue);
        }
    }

    private updateFrameIntervals(fisDictExisting, frameValue) {
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
            var fisDictNew = this.asFrameIntervalsArrayDict(frameValue);
            this.updateFrameIntervalsOfVcd(fisDictNew);
            return fisDictNew;
        }
        // Up to this point, fisExisting has something
        var lastFrameEnd = fisDictExisting[lastFrameEnd.length - 1]['frameEnd'];

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
                    if (fisDictFused[fisDictFused.length - 1]['frameEnd'] == lastFrameEnd) {

                        // Confirmed this element was updated last time
                        fisDictFused[fisDictFused.length - 1] = {
                            'frameStart': fisDictFused[-1]['frameStart'],
                            'frameEnd': fisDictFused[-1]['frameEnd'] + 1
                        }

                        // Now global frameIntervals at VCD (it is guaranteed that last entry was lastFrame)
                        var lastVcdFiDict = this.data['vcd']['frame_intervals'][-1];

                        // VCD frame intervals need to be updated as well
                        if (lastVcdFiDict["frameEnd"] == lastFrameEnd) {
                            // This is the first object updating this frame
                            this.data['vcd']['frame_intervals'][this.data['vcd']['frame_intervals'].length - 1] = {
                                'frameStart': lastVcdFiDict["frameStart"],
                                'frameEnd': lastVcdFiDict["frameEnd"] + 1
                            }
                        }
                        else if (lastVcdFiDict["frameEnd"] == frameValue) {
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
                    var fiDictNew = { 'frameStart': frameValue, 'frameEnd': frameValue }
                    fisDictFused = this.fuseFrameIntervalDict(fiDictNew, fisDictExisting);
                }
                else {
                    var fisDictNew = this.asFrameIntervalsArrayDict(frameValue)
                    fisDictExisting.extend(fisDictNew)
                    fisDictFused = this.fuseFrameIntervals(fisDictExisting)
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

    private addElement(elementType, name, semanticType = '', frameValue = null, uid = null, ontUid = null, stream = null) {
        if (frameValue != null) {
            if (!Number.isInteger(frameValue) && !Array.isArray(frameValue) && frameValue.constructor != Object) {
                console.warn("WARNING: frameValue has no valid format (int, array or object)");
            }
        }

        // 1/5 Get uid to assign
        // This function checks if the uid exists (keeps it), or if not, and if it is null
        var uidToAssign = this.getUidToAssign(elementType, uid);
        // Get existing frame intervals
        var fisDictsExisting = [];
        if (elementType + 's' in this.data['vcd']) {
            if (this.data['vcd'][elementType + 's'][uidToAssign]) {
                // This element already exists{ we need to fuse frameValue with the existing frameIntervals
                var element = this.data['vcd'][elementType + 's'][uidToAssign];
                fisDictsExisting['frame_intervals'] = fisDictsExisting['frame_intervals'] || [];
            }
        }

        var fisDictsUpdated;
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

    private updateElement(elementType, uid, frameValue) {
        if (!this.assertElementType(elementType)) {
            return;
        }

        if (!Number.isInteger(uid)) {
            console.warn("WARNING: uid is not integer");
            return;
        }

        // Check if this uid exists
        if (!this.data['vcd'][elementType.name + 's'][uid]) {
            console.warn("WARNING: trying to update a non-existing Element.")
            return;
        }

        // Read existing data about this element, so we can call addElement
        var name = this.data['vcd'][elementType.name + 's'][uid]['name'];
        var semanticType = this.data['vcd'][elementType.name + 's'][uid]['type'];
        var ontUid = null;
        var stream = null;
        if (this.data['vcd'][elementType.name + 's'][uid]['ontologyUid']) {
            ontUid = this.data['vcd'][elementType.name + 's'][uid]['ontologyUid'];
        }
        if (this.data['vcd'][elementType.name + 's'][uid]['stream']) {
            stream = this.data['vcd'][elementType.name + 's'][uid]['stream'];
        }

        // Call addElement (which internally creates OR updates)
        this.addElement(elementType, name, semanticType, frameValue, uid, ontUid, stream);
    }

    private createUpdateElement(elementType, name, semanticType, frameIntervalsDicts, uid, ontUid = null, stream = null) {
        // This function creates OR updates an element at the root of VCD using the given information
        var elementData = { 'name': name, 'type': semanticType, 'frame_intervals': frameIntervalsDicts };

        // Check existing data and push to elementData
        if (ontUid != null && this.getOntology(ontUid) != null) {
            elementData['ontologyUid'] = ontUid;
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
        if (elementType == 'object') {
            if (this.data['vcd']['objects']) {
                if (this.data['vcd']['objects'][uid]) {
                    if (this.data['vcd']['objects'][uid]['object_data']) {
                        elementData['object_data'] = this.data['vcd']['objects'][uid]['object_data'];
                    }
                }
            }
        }

        // Check data if action
        if (elementType == 'action') {
            if (this.data['vcd']['actions']) {
                if (this.data['vcd']['actions'][uid]) {
                    if (this.data['vcd']['actions'][uid]['action_data']) {
                        elementData['action_data'] = this.data['vcd']['actions'][uid]['action_data'];
                    }
                }
            }
        }

        // Check if relation
        else if (elementType == 'relation') {
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

        this.data['vcd'][elementType + 's'] = this.data['vcd'][elementType + 's'] || {};
        this.data['vcd'][elementType + 's'][uid] = elementData;  // This call creates or updates the element data
    }

    private updateObjectData(uid, objectData, frameIntervals) {
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
        if (!frameIntervals) {
            if (this.data['vcd']['objects'][uid]) {
                var object = this.data['vcd']['objects'][uid];
                // This is static content that goes into static part of Object
                object['object_data'] = object['object_data'] || {}; // Creates 'object_data' if it does not exist
                object['object_data'][objectData.type.name] = object['object_data'][objectData.type.name] || [];
                object['object_data'][objectData.type.name].push(objectData.data);
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
                for (var frameNum = fi['frameStart']; frameNum < fi['frameEnd'] + 1; frameNum++) {
                    this.data['vcd']['frames'][frameNum]['objects'] = this.data['vcd']['frames'][frameNum]['objects'] || {};
                    if (this.data['vcd']['frames'][frameNum]['objects'][uid]) {
                        object = this.data['vcd']['frames'][frameNum]['objects'][uid];
                        object['object_data'] = object['object_data'] || {};  // Creates 'object_data' if it does not exist
                        object['object_data'][objectData.type.name] = object['object_data'][objectData.type.name] || [];
                        object['object_data'][objectData.type.name].push(objectData.data);
                    }
                    else {  // need to create this entry, only with the pointer (uid) and the data
                        this.data['vcd']['frames'][frameNum]['objects'][uid] = {};
                        this.data['vcd']['frames'][frameNum]['objects'][uid]['object_data'] = {};
                        this.data['vcd']['frames'][frameNum]['objects'][uid]['object_data'][objectData.type.name] = [objectData.data];
                    }
                }
            }
        }
    }

    private updateActionData(uid, actionData, frameIntervals) {
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
                action['action_data'][actionData.type.name] = action['action_data'][actionData.type.name] || [];
                action['action_data'][actionData.type.name].push(actionData.data);
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
                for (var frameNum = fi['frameStart']; frameNum < fi['frameEnd'] + 1; frameNum++) {
                    this.data['vcd']['frames'][frameNum]['actions'] = this.data['vcd']['frames'][frameNum]['actions'] || {};
                    if (this.data['vcd']['frames'][frameNum]['actions'][uid]) {
                        action = this.data['vcd']['frames'][frameNum]['actions'][uid];
                        action['action_data'] = action['action_data'] || {};  // Creates 'action_data' if it does not exist
                        action['action_data'][actionData.type.name] = action['action_data'][actionData.type.name] || [];
                        action['action_data'][actionData.type.name].push(actionData.data);
                    }
                    else {  // need to create this entry, only with the pointer (uid) and the data
                        this.data['vcd']['frames'][frameNum]['actions'][uid] = {};
                        this.data['vcd']['frames'][frameNum]['actions'][uid]['action_data'] = {};
                        this.data['vcd']['frames'][frameNum]['actions'][uid]['action_data'][actionData.type.name] = [actionData.data];
                    }
                }
            }
        }
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////
    // Public API: add, update
    ////////////////////////////////////////////////////////////////////////////////////////////////////
    public addMetadataProperties(properties) {
        if (typeof properties != "object") {
            console.warn("properties not object");
            return;
        }
        var prop = this.data['vcd']['metadata']['properties'] || {};
        this.mergeObjects(prop, properties);
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

    public addOntology(ontologyName) {
        this.data['vcd']['ontologies'] = this.data['vcd']['ontologies'] || {};
        for (const ont_uid in this.data['vcd']['ontologies']) {
            if (this.data['vcd']['ontologies'][ont_uid] == ontologyName) {
                console.warn('WARNING: adding an already existing ontology');
                return null;
            }
        }
        var length = this.data['vcd']['ontologies'].length;
        this.data['vcd']['ontologies'][length] = ontologyName;
        return length;
    }

    public addStream(streamName: string, uri, description, sensorType) {
        if (typeof streamName != "string") {
            console.warn("streamName not string");
            return;
        }
        if (typeof uri != "string" && !(uri instanceof String)) {
            console.warn("uri not string");
            return;
        }
        if (typeof description != "string" && !(description instanceof String)) {
            console.warn("description not string");
            return;
        }

        this.data['vcd']['metadata'] = this.data['vcd']['metadata'] || {};
        this.data['vcd']['metadata']['streams'] = this.data['vcd']['metadata']['streams'] || {};
        this.data['vcd']['metadata']['streams'][streamName] = this.data['vcd']['metadata']['streams'][streamName] || {};

        if (this.assertSensorType(sensorType)) {
            this.data['vcd']['metadata']['streams'][streamName] = {
                'description': description, 'uri': uri, 'type': sensorType
            }
        }
    }

    public addFrameProperties(frameNum, properties) {
        if (properties.constructor != Object) {
            console.warn("properties not object");
            return;
        }
        this.addFrame(frameNum);  // this function internally checks if( the frame already exists
        this.data['vcd']['frames'][frameNum]['frame_properties'] = this.data['vcd']['frames'][frameNum]['frame_properties'] || {};
        this.data['vcd']['frames'][frameNum]['frame_properties']['properties'] = this.data['vcd']['frames'][frameNum]['frame_properties']['properties'] || {};
        this.mergeObjects(this.data['vcd']['frames'][frameNum]['frame_properties']['properties'], properties);
    }

    public addStreamProperties(streamName, properties, frameNum = null) {
        // This function can be used to add stream properties. if( frame_num is defined, the information is embedded
        // inside 'frame_properties' of the specified frame. Otherwise, the information is embedded into
        // 'stream_properties' inside 'metadata'.

        if (properties.constructor != Object) {
            console.warn("properties not object");
            return;
        }

        // Find if( this stream is declared
        if (this.data['vcd']['metadata']) {
            if (this.data['vcd']['metadata']['streams']) {
                if (this.data['vcd']['metadata']['streams'][streamName]) {
                    if (frameNum == null) {
                        // This information is static
                        this.data['vcd']['metadata']['streams'][streamName]['stream_properties'] = this.data['vcd']['metadata']['streams'][streamName]['stream_properties'] || {};
                        this.mergeObjects(this.data['vcd']['metadata']['streams'][streamName]['stream_properties'], properties);
                    }
                    else {
                        // This is information of the stream for( a specific frame
                        this.addFrame(frameNum); // to add the frame in case it does not exist
                        var frame = this.data['vcd']['frames'][frameNum];
                        frame['frame_properties'] = frame['frame_properties'] || {};
                        frame['frame_properties']['streams'] = frame['frame_properties']['streams'] || {};
                        frame['frame_properties']['streams'][streamName] = frame['frame_properties']['streams'][streamName] || {};
                        frame['frame_properties']['streams'][streamName]['stream_properties'] = frame['frame_properties']['streams'][streamName]['stream_properties'] || {};
                        this.mergeObjects(frame['frame_properties']['streams'][streamName]['stream_properties'], properties);
                    }
                }
                else {
                    console.warn('WARNING: Trying to add frame sync about non-existing stream');
                }
            }
        }
    }

    public updateObject(uid, frameValue) {
        // This function is only needed if( no add_object_data calls are used, but the object needs to be kept alive
        return this.updateElement('object', uid, frameValue);
    }

    public updateAction(uid, frameValue) {
        return this.updateElement('action', uid, frameValue);
    }

    public updateContext(uid, frameValue) {
        return this.updateElement('context', uid, frameValue);
    }

    public updateRelation(uid, frameValue) {
        return this.updateElement('relation', uid, frameValue);
    }

    public addObject(name, semanticType = '', frameValue = null, uid = null, ontUid = null, stream = null) {
        return this.addElement('object', name, semanticType, frameValue, uid, ontUid, stream);
    }

    public addAction(name, semanticType = '', frameValue = null, uid = null, ontUid = null, stream = null) {
        return this.addElement('action', name, semanticType, frameValue, uid, ontUid, stream);
    }

    public addEvent(name, semanticType = '', frameValue = null, uid = null, ontUid = null, stream = null) {
        return this.addElement('event', name, semanticType, frameValue, uid, ontUid, stream);
    }

    public addContext(name, semanticType = '', frameValue = null, uid = null, ontUid = null, stream = null) {
        return this.addElement('context', name, semanticType, frameValue, uid, ontUid, stream);
    }

    public addRelation(name, semanticType = '', frameValue = null, uid = null, ontUid = null) {
        return this.addElement(
            'relation', name, semanticType, frameValue, uid = uid, ontUid = ontUid
        );
    }

    public addRdf(relationUid, rdfType, elementUid, elementType) {
        if (!this.assertElementType(elementType)) {
            return;
        }
        if (!this.assertRDF(rdfType)) {
            return;
        }
        if (!this.data['vcd']['relations'][relationUid]) {
            console.warn("WARNING: trying to add RDF to non-existing Relation.")
            return;
        }
        else {
            if (!this.data['vcd'][elementType + 's'][elementUid]) {
                console.warn("WARNING: trying to add RDF using non-existing Element.")
                return;
            }
            else {
                if (rdfType == "subject") {
                    this.data['vcd']['relations'][relationUid]['rdf_subjects'] = this.data['vcd']['relations'][relationUid]['rdf_subjects'] || [];
                    this.data['vcd']['relations'][relationUid]['rdf_subjects'].push(
                        { 'uid': elementUid, 'type': elementType }
                    );
                }
                else {
                    this.data['vcd']['relations'][relationUid]['rdf_objects'] = this.data['vcd']['relations'][relationUid]['rdf_objects'] || [];
                    this.data['vcd']['relations'][relationUid]['rdf_objects'].push(
                        { 'uid': elementUid, 'type': elementType }
                    );
                }
            }
        }
    }

    public addObjectData(uid, objectData, frameValue = null) {
        if (!Number.isInteger(uid)) {
            console.warn("WARNING: uid is not integer");
        }

        // 1/3 Update element at vcd (internally, this fuses the frame intervals, etc.
        this.updateElement('object', uid, frameValue);

        // 2/3 Update object data
        var frameIntervals = this.asFrameIntervalsArrayDict(frameValue);
        this.updateObjectData(uid, objectData, frameIntervals);

        // 3/3 Update auxiliary array
        this.objectDataNames[uid] = this.objectDataNames[uid] || [];
        this.objectDataNames[uid].push(objectData.data['name']);
    }

    public addActionData(uid, actionData, frameValue = null) {
        if (!Number.isInteger(uid)) {
            console.warn("WARNING: uid is not integer");
        }

        // 1/3 Update element at vcd (internally, this fuses the frame intervals, etc.
        this.updateElement('action', uid, frameValue);

        // 2/3 Update action data
        var frameIntervals = this.asFrameIntervalsArrayDict(frameValue);
        this.updateActionData(uid, actionData, frameIntervals);

        // 3/3 Update auxiliary array
        this.actionDataNames[uid] = this.actionDataNames[uid] || [];
        this.actionDataNames[uid].push(actionData.data['name']);
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////
    // Get / Read
    ////////////////////////////////////////////////////////////////////////////////////////////////////
    public has(elementType, uid) {
        if (!this.data['vcd'][elementType + 's']) {
            return false;
        }
        else {
            if (this.data['vcd'][elementType + 's'][uid]) {
                return true;
            }
            else {
                return false;
            }
        }
    }

    public getAll(elementType) {
        //
        //Returns all elements of the specified ElementType.
        //e.g. all Object's or Context's
        //
        if (!this.assertElementType(elementType)) {
            return;
        }
        return this.data['vcd'][elementType + 's'];
    }

    public getAll2(elementType1, elementType2) {
        //
        //Returns all elements of the specified ElementType.
        //e.g. all Object's or Context's
        //
        if (!this.assertElementType(elementType1)) {
            return;
        }
        if (!this.assertElementType(elementType2)) {
            return;
        }

        var aux = {};
        aux[elementType1 + 's'] = this.data['vcd'][elementType1 + 's'];
        aux[elementType2 + 's'] = this.data['vcd'][elementType2 + 's'];

        return aux;
    }

    public getAll3(elementType1, elementType2, elementType3) {
        //
        //Returns all elements of the specified ElementType.
        //e.g. all Object's or Context's
        //
        if (!this.assertElementType(elementType1)) {
            return;
        }
        if (!this.assertElementType(elementType2)) {
            return;
        }
        if (!this.assertElementType(elementType3)) {
            return;
        }

        var aux = {};
        aux[elementType1 + 's'] = this.data['vcd'][elementType1 + 's'];
        aux[elementType2 + 's'] = this.data['vcd'][elementType2 + 's'];
        aux[elementType3 + 's'] = this.data['vcd'][elementType3 + 's'];

        return aux;
    }

    public getElement(elementType, uid) {
        if (!this.assertElementType(elementType)) {
            return;
        }
        if (this.data['vcd'][elementType + 's'] == null) {
            console.warn("WARNING: trying to get a " + elementType + " but this VCD has none.");
            return null;
        }
        if (this.data['vcd'][elementType + 's'][uid]) {
            return this.data['vcd'][elementType + 's'][uid];
        }
        else {
            console.warn("WARNING: trying to get non-existing " + elementType + " with uid: " + uid);
            return null;
        }
    }

    public getObject(uid) {
        return this.getElement('object', uid);
    }

    public getAction(uid) {
        return this.getElement('action', uid);
    }

    public getEvent(uid) {
        return this.getElement('event', uid);
    }

    public getContext(uid) {
        return this.getElement('context', uid);
    }

    public getRelation(uid) {
        return this.getElement('relation', uid);
    }

    public getFrame(frameNum) {
        if (this.data['vcd']['frames']) {
            return this.data['vcd']['frames'][frameNum];
        }
    }

    public getElementsOfType(elementType, type) {
        var uids = [];
        for (const uid in this.data['vcd'][elementType + 's']) {
            var element = this.data['vcd'][elementType + 's'][uid];
            if (element['type'] == type) {
                uids.push(uid);
            }
        }
        return uids;
    }

    public getObjectsWithObjectDataName(dataName) {
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

    public getObjectsWithActionDataName(dataName) {
        var uids = [];
        for (const uid in this.data['vcd']['actions']) {
            if (this.actionDataNames[uid]) {
                if (this.actionDataNames[uid][dataName]) {
                    uids.push(uid);
                }
            }
        }
        return uids;
    }

    public hasFrameObjectDataName(frameNum, dataName, uid_ = -1) {
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

    public hasFrameActionDataName(frameNum, dataName, uid_ = -1) {
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

    public getFramesWithObjectDataName(uid, dataName) {
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

    public getFramesWithActionDataName(uid, dataName) {
        var frames = [];
        if (this.data['vcd']['actions'][uid] && this.actionDataNames[uid]) {
            var object = this.data['vcd']['actions'][uid];
            if (this.actionDataNames[uid][dataName]) {
                // Now look into Frames
                var fis = object['frame_intervals'];
                for (var i = 0; i < fis.length; i++) {
                    var fi = fis[i];
                    var fi_tuple = [fi['frame_start'], fi['frame_end']];
                    for (var frameNum = fi_tuple[0]; frameNum < fi_tuple[1] + 1; frameNum++) {
                        if (this.hasFrameActionDataName(frameNum, dataName, uid)) {
                            frames.push(frameNum);
                        }
                    }
                }
            }
        }
        return frames;
    }

    public getObjectData(uid, dataName, frameNum = null) {
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

    public getActionData(uid, dataName, frameNum = null) {
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

    public getNumElements(elementType) {
        return this.data['vcd'][elementType + 's'].length;
    }

    public getNumObjects() {
        return this.getNumElements('object');
    }

    public getNumActions() {
        return this.getNumElements('action');
    }

    public getNumEvents() {
        return this.getNumElements('event');
    }

    public getNumContexts() {
        return this.getNumElements('context');
    }

    public getNumRelations() {
        return this.getNumElements('relation');
    }

    public getOntology(ontUid) {
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

    public getFrameIntervalsOfElement(elementType, uid) {
        if (!this.data['vcd'][elementType + 's']) {
            console.warn(elementType + 's' + " not in this.data['vcd']");
        }
        return this.data['vcd'][elementType + 's'][uid]['frame_intervals'];
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////
    // Remove
    ////////////////////////////////////////////////////////////////////////////////////////////////////
    public rmElementByType(elementType, semanticType) {
        var elements = this.data['vcd'][elementType + 's'];
        var index = null;

        // Get Element from summary
        var element = null;
        for (uid in elements) {
            element = element[uid];
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
        if (elementType == 'object') {
            delete this.objectDataNames[uid];
        }
        if (elementType == 'action') {
            delete this.actionDataNames[uid];
        }

        // Remove from Frames{ let's read frameIntervals from summary
        for (var i = 0; i < element['frame_intervals'].length; i++) {
            var fi = element['frame_intervals'][i];
            for (var frameNum = fi['frame_start']; frameNum < fi['frame_end'] + 1; frameNum++) {
                var elementsInFrame = this.data['vcd']['frames'][frameNum][elementType + 's'];
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

    public rmObjectByType(semanticType) {
        this.rmElementByType('object', semanticType);
    }

    public rmActionByType(semanticType) {
        this.rmElementByType('action', semanticType);
    }

    public rmEventByType(semanticType) {
        this.rmElementByType('event', semanticType);
    }

    public rmContextByType(semanticType) {
        this.rmElementByType('context', semanticType);
    }

    public rmRelationByType(semanticType) {
        this.rmElementByType('relation', semanticType);;
    }

    public rmElementByFrame(elementType, uid, frameIntervalTuple) {
        var frameIntervalDict = this.asFrameIntervalDict(frameIntervalTuple);
        var elements = this.data['vcd'][elementType + 's'];
        var element;

        if (elements[uid]) {
            element = elements[uid];
        }
        else {  // not found
            console.warn("WARNING: trying to remove non-existing Element of type: ", elementType, " and uid: ", uid);
            return;
        }
        // Remove from Frames{ let's read frameIntervals from summary
        for (var i = 0; i < element['frame_intervals'].length; i++) {
            var fi = element['frame_intervals'][i];
            for (var frameNum = fi['frame_start']; frameNum < fi['frame_end'] + 1; frameNum++) {
                if (frameIntervalDict['frame_start'] <= frameNum <= frameIntervalDict['frame_end']) {
                    var elementsInFrame = this.data['vcd']['frames'][frameNum][elementType + 's'];
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

        var outerInterval = this.getOuterFrameInterval(element['frame_intervals'])
        if (frameIntervalDict['frame_start'] <= outerInterval['frame_start'] && frameIntervalDict['frame_end'] >= outerInterval['frame_end']) {
            // The deleted frame interval covers the entire element, so let's delete it from the summary
            delete elements[uid];
        }
    }

    public rmObjectByFrame(uid, frameIntervalTuple) {
        return this.rmElementByFrame('object', uid, frameIntervalTuple);
    }

    public rmActionByFrame(uid, frameIntervalTuple) {
        return this.rmElementByFrame('action', uid, frameIntervalTuple);
    }

    public rmEventByFrame(uid, frameIntervalTuple) {
        return this.rmElementByFrame('event', uid, frameIntervalTuple);
    }

    public rmContextByFrame(uid, frameIntervalTuple) {
        return this.rmElementByFrame('context', uid, frameIntervalTuple);
    }

    public rmRelationByFrame(uid, frameIntervalTuple) {
        return this.rmElementByFrame('relation', uid, frameIntervalTuple);
    }

    public rmElement(elementType, uid) {
        var elements = this.data['vcd'][elementType + 's'];

        // Get Element from summary
        var element;
        if (elements[uid]) {
            element = elements[uid];
        }
        else {  // not found
            console.warn("WARNING: trying to remove non-existing Element of type: ", elementType, " and uid: ", uid);
            return;
        }

        // Update indexes and other member variables
        if (elementType == 'object') {
            delete this.objectDataNames[uid];
        }

        // Update indexes and other member variables
        if (elementType == 'action') {
            delete this.actionDataNames[uid];
        }

        // Remove from Frames{ let's read frameIntervals from summary
        for (var i = 0; i < element['frame_intervals'].length; i++) {
            var fi = element['frame_intervals'][i];
            for (var frameNum = fi['frame_start']; frameNum < fi['frame_end'] + 1; frameNum++) {
                var elementsInFrame = this.data['vcd']['frames'][frameNum][elementType + 's'];
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

    public rmObject(uid) {
        this.rmElement('object', uid);
    }

    public rmAction(uid) {
        this.rmElement('action', uid);
    }

    public rmEvent(uid) {
        this.rmElement('event', uid);
    }

    public rmContext(uid) {
        this.rmElement('context', uid);
    }

    public rmRelation(uid) {
        this.rmElement('relation', uid);
    }

    public setData(schema: any, data: any) {
        this.lastUID = {};
        this.schema = schema;
        this.data = data;
        this.init();
    }

    public getData(): any {
        return this.data;
    }

    public reset() {
        this.data = {};
        this.schema = {};
        this.lastUID = {};
        this.objectDataNames = {};
        this.actionDataNames = {};
    }


    ////////////////////////////////////////////////////////////////////////////////////////////////////
    // Modified by: Paola Cañas 09/06/2020
    ////////////////////////////////////////////////////////////////////////////////////////////////////

    /*
    @elementType: element to be modified (ex:action,object)
    @uid: id of the object in element list
    @intervalId: position of the frameInterval to be modified in "frame_intervals" list of object
    @newItervalLimits: array=[start, end]
    */
    public updateOneFrameInterOfElement(elementType, uid, intervalId, newIntervalLimits) {
        if (this.data['vcd'][elementType + 's'][uid]["frame_intervals"] == null || this.data['vcd'][elementType + 's'][uid]["frame_intervals"][intervalId] == null) {
            console.warn("WARNING: trying to get frame intervals of " + uid + " but is not found.");
        } else if (!Array.isArray(newIntervalLimits)) {
            console.warn("WARNING: not a valid interval to include in vcd.");
        } else {
            //modify interval
            var newInterval = this.asFrameIntervalDict(newIntervalLimits);
            this.data['vcd'][elementType + 's'][uid]["frame_intervals"][intervalId] = newInterval;
            //see if there is overlapping and unify
            var oldIntervals = this.data['vcd'][elementType + 's'][uid]["frame_intervals"];
            var newIntervals = this.fuseFrameIntervals(oldIntervals);
            this.data['vcd'][elementType + 's'][uid]["frame_intervals"] = newIntervals;
        }


    }
}