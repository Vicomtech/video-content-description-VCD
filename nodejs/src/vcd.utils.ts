////////////////////////////////////////////////////////////////////////////////////////////////////
// Utils
////////////////////////////////////////////////////////////////////////////////////////////////////
/*export mergeObjects(obj1, obj2): any {
    let key;

    for (key in obj2) {
        if (obj2.hasOwnProperty(key)) {
            obj1[key] = obj2[key];
        }
    }
}*/



export function intersects(fiA: Object, fiB: Object): boolean {
    var maxStartVal = Math.max(fiA['frame_start'], fiB['frame_start']);
    var minEndVal = Math.min(fiA['frame_end'], fiB['frame_end']);
    return maxStartVal <= minEndVal;
}

export function consecutive(fiA: Object, fiB: Object): boolean {
    if (fiA['frame_end'] + 1 == fiB['frame_start'] || fiB['frame_end'] + 1 == fiA['frame_start']) {
        return true;
    }
    else {
        return false;
    }
}

export function isInside(frameNum: number, frameInterval: Object): boolean {
    return frameInterval['frame_start'] <= frameNum && frameNum <= frameInterval['frame_end'];
}

export function getOuterFrameInterval(frameIntervals: Array<Object>): any {
    var outer = null;
    for (var i = 0; i < frameIntervals.length; i++) {
        var fi = frameIntervals[i];
        if (outer == null) {
            outer = fi;
        }
        else {
            if (fi['frame_start'] < outer['frame_start']) {
                outer['frame_start'] = fi['frame_start'];
            }
            if (fi['frame_end'] > outer['frame_end']) {
                outer['frame_end'] = fi['frame_end'];
            }
        }
    }
    return outer;
}

export function asFrameIntervalDict(frameValue: any): Object {
    if (Number.isInteger(frameValue)) {
        return { 'frame_start': frameValue, 'frame_end': frameValue };
    }
    else if (Array.isArray(frameValue)) {
        return { 'frame_start': frameValue[0], 'frame_end': frameValue[1] };
    }
    else {
        console.warn("WARNING: trying to convert into frame interval a " + typeof frameValue);
    }
}

export function asFrameIntervalsArrayDict(frameValue: any) {
    // Allow for multiple type of frame_interval arguments (int, tuple, list(tuple))
    var frameIntervals;
    if (Number.isInteger(frameValue)) {  // The user has given as argument a "frame number"
        frameIntervals = [{ 'frame_start': frameValue, 'frame_end': frameValue }];
    }
    else if (Array.isArray(frameValue) && Number.isInteger(frameValue[0])) { // The user has given as argument a single "frame interval"
        frameIntervals = [{ 'frame_start': frameValue[0], 'frame_end': frameValue[1] }];
    }
    else if (frameValue == null) { // The user has provided nothing: this is a static element
        frameIntervals = [];
    }
    else {
        if (Array.isArray(frameValue) && Array.isArray(frameValue[0])) { // User provides a list of "frame intervals"
            frameIntervals = frameValue;
        }
        else {
            console.warn("WARNING trying to convert something not contemplated");
            return null;
        }
    }
    return frameIntervals;
}

export function asFrameIntervalsArrayTuples(frameIntervals: Array<Object>): Array<Array<Number> > {
    let fiTuples: number[][] = [[]];
    for (let fiDict in frameIntervals) {
        fiTuples.push([fiDict['frame_start'], fiDict['frame_end']]);
    }
    return fiTuples;
}

export function frameIntervalIsInside(frameIntervalsA: Array<Number>, frameIntervalsB: Array<Number>): boolean {
    let allInside: boolean = true;
    for (let fiA in frameIntervalsA) {
        let inside: boolean = false;
        for (let fiB in frameIntervalsB) {
            if(fiA[0] >= fiB[0] && fiA[1] <= fiB[1]) {
                inside = true;
                break;
            }
        }
        if(!inside){
            allInside = false;
            break;
        }
    }
}

export function fuseFrameIntervalDict(frameInterval: Object, frameIntervals: Array<Object>): Array<Object> {
    // This function inserts frameInterval into frameIntervals fusing intervals    
    if (frameIntervals.length == 0) {
        return [frameInterval];
    }

    var frameIntervalsToReturn = frameIntervals;
    var idxToFuse = [];  // idx of frameIntervals of the list
    for (var i = 0; i < frameIntervals.length; i++) {
        if (intersects(frameIntervals[i], frameInterval) || consecutive(frameIntervals[i], frameInterval)) {
            idxToFuse.push(i);
        }
    }
    if (idxToFuse.length == 0) {
        // New frame interval, separated, just append
        frameIntervalsToReturn.push(frameInterval);
    }
    else {
        // New frame interval has caused some fusion
        frameIntervalsToReturn = [];
        var fusedFi = frameInterval;
        for (var i = 0; i < frameIntervals.length; i++) {
            if (idxToFuse.indexOf(i) > -1) {
                fusedFi = {
                    'frame_start': Math.min(fusedFi['frame_start'], frameIntervals[i]['frame_start']),
                    'frame_end': Math.max(fusedFi['frame_end'], frameIntervals[i]['frame_end'])
                }
            }
            else {
                // also add those not affected by fusion
                frameIntervalsToReturn.push(frameIntervals[i]);
            }
        }
        frameIntervalsToReturn.push(fusedFi);
    }
    return frameIntervalsToReturn;
}

export function fuseFrameIntervals(frameIntervals: Array<Object>) {
    // This functions receives a list of frame_intervals and returns another one with
    // non-overlapping intervals
    // e.g. input: [(0, 5), (3, 6), (8, 10)]
    //      output:[(0, 6), (8, 10)]    

    var numFis = frameIntervals.length;

    if (numFis == 1) {
        return frameIntervals;
    }

    // Read first element
    var frameIntervalsFused = [frameIntervals[0]];
    var i = 1;
    while (i < numFis) {
        frameIntervalsFused = fuseFrameIntervalDict(frameIntervals[i], frameIntervalsFused);
        i += 1;
    }
    return frameIntervalsFused;
}

