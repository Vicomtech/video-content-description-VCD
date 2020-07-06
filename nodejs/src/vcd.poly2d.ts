/**
VCD (Video Content Description) library v4.2.1

Project website: http://vcd.vicomtech.org

Copyright (C) 2020, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a library to create and manage VCD content version 4.2.1.
VCD is distributed under MIT License. See LICENSE.

*/

import { Mat } from "./vcd.types"

const SRF6DCC_High_simplifier = 15
const SRF6DCC_Low_simplifier = 3
const SRF6DCC_High_symbol = 7
const SRF6DCC_Low_symbol = 6

const static_direction_kernel = [[5, 6, 7], [4, 9, 0], [3, 2, 1]]

const kernel_direction_data =  [[[5, 4, 2], [5, 9, 0], [5, 3, 1]],  // direction 0 updated kernel
                                [[5, 5, 4], [5, 9, 2], [3, 1, 0]],  // direction 1 updated kernel
                                [[5, 5, 5], [3, 9, 4], [1, 0, 2]],  // direction 2 updated kernel
                                [[3, 5, 5], [1, 9, 5], [0, 2, 4]],  // direction 3 updated kernel
                                [[1, 3, 5], [0, 9, 5], [2, 4, 5]],  // direction 4 updated kernel
                                [[0, 1, 3], [2, 9, 5], [4, 5, 5]],  // direction 5 updated kernel
                                [[2, 0, 1], [4, 9, 3], [5, 5, 5]],  // direction 6 updated kernel
                                [[4, 2, 0], [5, 9, 1], [5, 5, 3]]]  // direction 7 updated kernel

export interface CodeString {
    code: Array<number>,
    xinit: number,
    yinit: number
}

export interface Base64Encode {
    code: string,
    rest: number
}

export function extractRS6FCC2Points(_chaincode: Array<number>, _xinit: number, _yinit: number, _low: number, _high: number): Array<number> {
    let _coords = []
    _coords.push(Math.floor(_xinit))
    _coords.push(Math.floor(_yinit))
    let xinit = Math.floor(_xinit)
    let yinit = Math.floor(_yinit)
    if(_chaincode.length == 0) return _coords

    let previous_direction = 2
    let counter = 0
    for(let i=0; i<_chaincode.length; i++) {
        if(_chaincode[i] < 6 && _chaincode[i] > 0) {
            if(counter > 0) {
                let xy = checkPixelInMat(kernel_direction_data[previous_direction], 0)
                xinit += (xy[0]!=0) ? (xy[0] * counter) : (0)
                yinit += (xy[1]!=0) ? (xy[1] * counter) : (0)
                _coords.push(xinit)
                _coords.push(yinit)
                counter = 0
            }
            if (_chaincode[i] == 5) { // if code is 5 just go counter-direction
                previous_direction = (previous_direction+4) % 8
            }
            else {
                let xiyi = checkPixelInMat(kernel_direction_data[previous_direction], _chaincode[i])
                xinit += xiyi[0]
                yinit += xiyi[1]
                _coords.push(xinit)
                _coords.push(yinit)
                previous_direction = static_direction_kernel[xiyi[1] + 1][xiyi[0] + 1]
            }
        }
        else if(_chaincode[i] == 0) counter++
        else if(_chaincode[i] == SRF6DCC_Low_symbol) counter += SRF6DCC_Low_simplifier
        else if(_chaincode[i] == SRF6DCC_High_symbol) counter += SRF6DCC_High_simplifier

        if(i==_chaincode.length -1 && counter > 0) {  // only enters if its the last character
            let xy = checkPixelInMat(kernel_direction_data[previous_direction], 0)
            xinit += (xy[0] != 0) ? (xy[0]*counter):(0)
            yinit += (xy[1] != 0) ? (xy[1]*counter):(0)
            _coords.push(xinit)
            _coords.push(yinit)
        }
    }
    return _coords
}

export function computeSRF6DCC(_coords: Array<number>): CodeString {
    let _distances = []
    if(_coords.length == 0){
        return {code: [], xinit: 0, yinit: 0}
    }    
    let _xinit = Math.floor(_coords[0])
    let _yinit = Math.floor(_coords[1])
    let xinit = _xinit
    let yinit = _yinit

    // the polygon contouring starts always going down
    let previous_direction = 2
    for(let i=2; i<_coords.length; i+=2) {
        let x = Math.round(_coords[i])
        let y = Math.round(_coords[i + 1])
        let xi = x - xinit
        let yi = y - yinit
        let temp = []
        let fin = Math.max(Math.abs(xi), Math.abs(yi))

        let xii = 0
        if (xi != 0) xii = Math.floor(xi / Math.abs(xi))
        let yii = 0
        if (yi != 0) yii = Math.floor(yi / Math.abs(yi))

        for(let j=0; j<fin; j++) {
            let move = kernel_direction_data[previous_direction][yii + 1][xii + 1]
            if(move < 5) {
                temp.push(move)
                previous_direction = static_direction_kernel[yii + 1][xii + 1]
            }
            else if(move == 5) {
                temp.push(move)
                previous_direction = (previous_direction + 4) % 8
                move = kernel_direction_data[previous_direction][yii + 1][xii + 1]
                temp.push(move)
                previous_direction = static_direction_kernel[yii + 1][xii + 1]
            }
        }
        _distances = _distances.concat(temp)
        //for(let k=0; k<temp.length; k++) {
        //    _distances.push(temp[k])
        //}
        xinit = x
        yinit = y

        if(_distances.length != 0) {
            _distances = simplifyAllFrontSequenceMovements(_distances, SRF6DCC_Low_simplifier, SRF6DCC_High_simplifier, 
                SRF6DCC_Low_symbol, SRF6DCC_High_symbol)
        }
    }
    let codeString = {code: _distances, xinit: _xinit, yinit: _yinit}
    return codeString
}

export function extractSRF6DCC2Points(_chaincode, _xinit, _yinit) {
    return extractRS6FCC2Points(_chaincode, _xinit, _yinit, SRF6DCC_Low_simplifier, SRF6DCC_High_simplifier)
}

function checkPixelInMat(_kernel_direction_data, target){
    for(let row=0; row<3; row++) {
        for(let col=0; col<3; col++) {
            if(_kernel_direction_data[row][col] == target) {
                return [col-1, row-1]
            }
        }
    }
    return [0, 0]
}

function simplifyFrontSequenceMovements(_num, _low, _high, _low_symbol, _high_symbol, _next_steps) {
    let res1, res2, res3: number
    if(_high != -1){
        res1 = Math.floor(_num / _high)
        res2 = Math.floor(_num % _high / _low)
        res3 = Math.floor(_num % _high % _low)
    }
    else{
        res1 = 0
        res2 = Math.floor(_num / _low)
        res3 = Math.floor(_num % _low)
    }
    for(let i=0; i<res1; i++){
        _next_steps.push(_high_symbol) // _high_symbol: {SRF6DCC: 7} for high Roman numerals-like counting simplifications
    }
    for(let i=0; i<res2; i++){
        _next_steps.push(_low_symbol) // _low_symbol: {SRF6DCC: 6} for low Roman numerals-like counting simplifications
    }
    for(let i=0; i<res3; i++){
        _next_steps.push(0) 
    }
    return _next_steps
}

function simplifyAllFrontSequenceMovements(_chaincode, _low, _high, _low_symbol, _high_symbol) {
    let counter = 0
    let i = 0
    while(i<_chaincode.length) {
        if(_chaincode[i] == 0){
            counter += 1
        }
        else {
            if(counter >= _low) {
                // i -conuter // position of last 0 - counter
                // NOTE: migrating this code from C++
                /*
                //i - counter //position of last 0 - counter
                std::vector<int> next_steps;
                simplifyFrontSequenceMovements(counter, _low, _high, _low_symbol, _high_symbol, next_steps);
                 
                _chaincode.erase(_chaincode.begin() + i - counter, _chaincode.begin() + i);
                i -= counter;
                _chaincode.insert(_chaincode.begin() + i , next_steps.begin(), next_steps.end());
                i+= next_steps.size();
                */
                let next_steps = []
                next_steps = simplifyFrontSequenceMovements(counter, _low, _high, _low_symbol, _high_symbol, next_steps)
                _chaincode.splice(i-counter, counter)  // array.splice(index, howMany, [element1][, ..., elementN]);
                i -= counter
                for(let k=0; k<next_steps.length; k++) {
                    _chaincode.splice(i + k, 0, next_steps[k])  // I can't find a way to insert the entire array: _chaincode.splice(i, 0, next_steps)??
                }         
                i += next_steps.length      
            }
            counter = 0
        }
        if(i == _chaincode.length - 1) {
            if(counter >= _low) {
                /* Emulating the following C++ code
                //i - counter //position of last 0 - counter
                std::vector<int> next_steps;
                simplifyFrontSequenceMovements(counter, _low, _high, _low_symbol, _high_symbol, next_steps);
                 
                _chaincode.erase(_chaincode.end() - counter, _chaincode.end() );
                i -= counter;
                _chaincode.insert(_chaincode.

                */
                let next_steps = []
                next_steps = simplifyFrontSequenceMovements(counter, _low, _high, _low_symbol, _high_symbol, next_steps)
                _chaincode.splice(_chaincode.length-counter, counter) // remember, counter is howMany
                i -= counter                
                _chaincode = _chaincode.concat(next_steps)     // because in this case it is just concatenating next_steps at the end of _chaincode                  
                i += next_steps.length      
            }
            counter = 0
        }
        i += 1
    }
    return _chaincode
}

export function chainCodeBase64Decoder(_chaincodebits: string, _chaincode_bits: number, bitsvectorrest: number) {
    let chaincodevector: Array<number>
    let num_digits = 6 / _chaincode_bits
    let decoded_chaincode : Array<number>

    let getbits = Math.pow(2, _chaincode_bits) - 1  // number of bits that need to move to

    for(let i=0; i<_chaincodebits.length; i++) {
        let byte = base64Decoder(_chaincodebits[i])
        for(let j=0; j<num_digits; j++) {
            let number = byte & getbits
            chaincodevector.splice(i*num_digits, 0, number)
            byte -= number
            byte = byte >> _chaincode_bits
        }
    }
    for(let k=0; k<bitsvectorrest; k++) {
        delete chaincodevector[chaincodevector.length - 1]
    }

    return chaincodevector
}

export function chainCodeBase64Encoder(_chaincode, _chaincode_bits): Base64Encode {
    let num_digits = 6 / _chaincode_bits
    let rest = _chaincode.length % num_digits
    let vectrest = 0
    let outputstring = ''
    if(rest != 0) {
        vectrest = (num_digits - rest)
        for(let i=0; i<vectrest; i++) {
            _chaincode.push(0)
        }
    }
    for(let i=0; i<_chaincode.length; i+=num_digits) {
        let byte = 0
        for(let j=0; j<num_digits; j++) {
            byte += _chaincode[i + j] << (num_digits - 1 - j) * _chaincode_bits
        }
        outputstring += base64Encoder(byte)
    }
    const base64Encode = {code: outputstring, rest: vectrest} 
    return base64Encode
}

function base64Encoder(_num) {
    let alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    return alphabet[_num]
}

function base64Decoder(_value) {
    let alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    return alphabet.indexOf(_value)
}

export function testEncodingDecoding(num: Array<number>, num_bits: number) {
    let num2: Array<number>
    
    let result: Base64Encode = chainCodeBase64Encoder(num, num_bits)
    let codify = result['out']
    let rest = result['rest']

    num2 = chainCodeBase64Decoder(codify, num_bits, rest)
    
    // Compare num and num2
    if (num === num2) return true
    else return false
}