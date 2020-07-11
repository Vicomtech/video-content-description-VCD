/**
VCD (Video Content Description) library v4.2.1

Project website: http://vcd.vicomtech.org

Copyright (C) 2020, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a library to create and manage VCD content version 4.2.1.
VCD is distributed under MIT License. See LICENSE.

*/

////////////////////////////////////////////////////////////////////////////////////////////////////
// Utils
////////////////////////////////////////////////////////////////////////////////////////////////////
export function intersectionBetweenFrameIntervalArrays(fisA: Array<Array<number>>, fisB: Array<Array<number>>): Array<Array<number>> {
    let fisInt = []
    for(let fiA of fisA) {
        for(let fiB of fisB) {
            let fiInt = intersectionBetweenFrameIntervals(fiA, fiB)
            if(fiInt != null) {
                fisInt.push(fiInt)
            }                
        }
    }
    return fisInt
}

export function intersectionBetweenFrameIntervals(fiA: Array<number>, fiB: Array<number>) {
    var maxStartVal = Math.max(fiA[0], fiB[0]);
    var minEndVal = Math.min(fiA[1], fiB[1]);

    if (maxStartVal <= minEndVal) {
        return [maxStartVal, minEndVal]
    }
    else {
        return null
    }
}

export function intersects(fiA: object, fiB: object): boolean {
    var maxStartVal = Math.max(fiA['frame_start'], fiB['frame_start']);
    var minEndVal = Math.min(fiA['frame_end'], fiB['frame_end']);
    return maxStartVal <= minEndVal;
}

export function consecutive(fiA: object, fiB: object): boolean {
    if (fiA['frame_end'] + 1 == fiB['frame_start'] || fiB['frame_end'] + 1 == fiA['frame_start']) {
        return true;
    }
    else {
        return false;
    }
}

export function isInsideFrameIntervals(frameNum: number, frameIntervals: Array<Array<number>>) {
    for(let fi of frameIntervals) {
        if(isInsideFrameInterval(frameNum, fi)) {
            return true
        }
    }
    return false
}

export function isInsideFrameInterval(frameNum: number, frameInterval: Array<number>) {
    return frameInterval[0] <= frameNum && frameNum <= frameInterval[1];
}

export function isInside(frameNum: number, frameInterval: object): boolean {
    return frameInterval['frame_start'] <= frameNum && frameNum <= frameInterval['frame_end'];
}

export function getOuterFrameInterval(frameIntervals: Array<object>): any {
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

export function asFrameIntervalDict(frameValue: number | Array<number>): object {
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

export function asFrameIntervalsArrayDict(frameValue: number | Array<number> | Array<Array<number>>): Array<object> {
    // Allow for multiple type of frame_interval arguments (int, tuple, list(tuple))
    var frameIntervals = [];
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
            for(let frameInterval of frameValue) {            
                // User provided Array<Array<number>>
                frameIntervals.push({'frame_start': frameInterval[0], 'frame_end': frameInterval[1]})
            }            
        }
        else {
            console.warn("WARNING trying to convert something not contemplated");
            return null;
        }
    }
    return frameIntervals;
}

export function asFrameIntervalsArrayTuples(frameIntervals: Array<object>): Array<Array<number> > {
    let fiTuples: number[][] = [];
    for (let fiDict of frameIntervals) {
        fiTuples.push([fiDict['frame_start'], fiDict['frame_end']]);
    }
    return fiTuples;
}

export function frameIntervalIsInside(frameIntervalsA: Array<Array<number>>, frameIntervalsB: Array<Array<number>>): boolean {
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
    return allInside;
}

export function fuseFrameIntervalDict(frameInterval: object, frameIntervals: Array<object>): Array<object> {
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

export function fuseFrameIntervals(frameIntervals: Array<object>) {
    // This functions receives a list of frame_intervals and returns another one with
    // non-overlapping intervals
    // e.g. input: [{'frame_start': 0, 'frame_end': 5}, {'frame_start': 3, 'frame_end': 6}, {'frame_start': 8, 'frame_end': 10}]
    //      output:[{'frame_start': 0, 'frame_end': 6}, {'frame_start': 8, 'frame_end': 10}]    

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

export function rmFrameFromFrameIntervals(frameIntervals: Array<object>, frameNum: number) {
    let fiDictNew = []
    for(let fi of frameIntervals) {
        if(frameNum < fi['frame_start']) {
            fiDictNew.push(fi)
            continue
        }
        if(frameNum == fi['frame_start']) {
            // Start frame, just remove it
            if(fi['frame_end'] > frameNum) {
                fiDictNew.push({'frame_start': frameNum + 1, 'frame_end': fi['frame_end']})
                continue
            }
        }
        else if(frameNum < fi['frame_end']) {
            // Inside! Need to split
            for(let f = fi['frame_start'] + 1; f<=fi['frame_end']; f++) {
                if (f==frameNum) {
                    fiDictNew.push({'frame_start': fi['frame_start'], 'frame_end': frameNum - 1})
                    fiDictNew.push({'frame_start': frameNum + 1, 'frame_end': fi['frame_end']})
                }
            }
        }
        else if(frameNum == fi['frame_end']) {
            // End frame, just remove it
            // no need to check if fi['frame_start'] > frameNum backwards as we are in the else if
            fiDictNew.push({'frame_start': fi['frame_start'], 'frame_end': frameNum - 1})
        }
        else{
            fiDictNew.push(fi)         
        }
    }
    return fiDictNew
}

