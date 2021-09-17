"""
VCD (Video Content Description) library v5.0.0

Project website: http://vcd.vicomtech.org

Copyright (C) 2021, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 5.0.0.
VCD is distributed under MIT License. See LICENSE.

"""
import numpy as np
import math


def computeRS6FCC(coords):
    _distances = []
    high_symbol = 7
    low_symbol = 6

    if len(coords) == 0:
        return [], 0, 0, 0, 0

    _xinit = int(coords[0])
    _yinit = int(coords[1])
    xinit = _xinit
    yinit = _yinit

    static_direction_kernel = np.array([[5, 6, 7], [4, 9, 0], [3, 2, 1]])

    kernel_direction_data = np.array([[[5, 4, 2], [5, 9, 0], [5, 3, 1]],  # direction 0 updated kernel
                                      [[5, 5, 4], [5, 9, 2], [3, 1, 0]],  # direction 1 updated kernel
                                      [[5, 5, 5], [3, 9, 4], [1, 0, 2]],  # direction 2 updated kernel
                                      [[3, 5, 5], [1, 9, 5], [0, 2, 4]],  # direction 3 updated kernel
                                      [[1, 3, 5], [0, 9, 5], [2, 4, 5]],  # direction 4 updated kernel
                                      [[0, 1, 3], [2, 9, 5], [4, 5, 5]],  # direction 5 updated kernel
                                      [[2, 0, 1], [4, 9, 3], [5, 5, 5]],  # direction 6 updated kernel
                                      [[4, 2, 0], [5, 9, 1], [5, 5, 3]]]) # direction 7 updated kernel
    # the polygon contouring starts always going down.
    previous_direction = 2

    for i in range(2, len(coords), 2):
        x = round(coords[i])
        y = round(coords[i + 1])
        xi = x - xinit
        yi = y - yinit
        temp = []
        fin = max(abs(xi), abs(yi))

        xii = int(xi / abs(xi)) if xi != 0 else 0
        yii = int(yi / abs(yi)) if yi != 0 else 0

        for j in range(0, fin):
            move = kernel_direction_data[previous_direction][yii + 1][xii + 1]
            if move < 5:
                temp.append(move)
                previous_direction = static_direction_kernel[yii + 1][xii + 1]
            elif move == 5:
                temp.append(move)
                previous_direction = (previous_direction+4) % 8
                move = kernel_direction_data[previous_direction][yii+1][xii+1]
                temp.append(move)
                previous_direction = static_direction_kernel[yii+1][xii+1]

        for k in range(0, len(temp)):
            _distances.append(temp[k])

        xinit = x
        yinit = y

    if len(_distances) != 0:
        _distances, RS6FCC_Low_simplifier, RS6FCC_High_simplifier = simplifyCalculatedFrontSequenceMovements(_distances, low_symbol, high_symbol)
    else:
        RS6FCC_High_simplifier = 0
        RS6FCC_Low_simplifier = 0

    return _distances, RS6FCC_Low_simplifier, RS6FCC_High_simplifier, _xinit, _yinit


def extractRS6FCC2Points(_chaincode, _xinit, _yinit, _low, _high):
    RS6FCC_High_simplifier = _high
    RS6FCC_Low_simplifier = _low
    RS6FCC_High_symbol = 7
    RS6FCC_Low_symbol = 6
    _coords = []
    _coords.append(int(_xinit))
    _coords.append(int(_yinit))
    xinit = int(_xinit)
    yinit = int(_yinit)
    if len(_chaincode) == 0:
        return _coords

    static_direction_kernel = np.array([[5, 6, 7], [4, 9, 0], [3, 2, 1]])

    kernel_direction_data = np.array([[[5, 4, 2], [5, 9, 0], [5, 3, 1]],  # direction 0 updated kernel
                                      [[5, 5, 4], [5, 9, 2], [3, 1, 0]],  # direction 1 updated kernel
                                      [[5, 5, 5], [3, 9, 4], [1, 0, 2]],  # direction 2 updated kernel
                                      [[3, 5, 5], [1, 9, 5], [0, 2, 4]],  # direction 3 updated kernel
                                      [[1, 3, 5], [0, 9, 5], [2, 4, 5]],  # direction 4 updated kernel
                                      [[0, 1, 3], [2, 9, 5], [4, 5, 5]],  # direction 5 updated kernel
                                      [[2, 0, 1], [4, 9, 3], [5, 5, 5]],  # direction 6 updated kernel
                                      [[4, 2, 0], [5, 9, 1], [5, 5, 3]]]) # direction 7 updated kernel
    # the polygon contouring starts always going down.
    previous_direction = 2

    counter = 0
    for i in range(0, len(_chaincode)):
        if 6 > _chaincode[i] > 0:
            if counter > 0:
                x, y = checkPixelInMat(kernel_direction_data[previous_direction], 0)
                xinit += x * counter if x != 0 else 0
                yinit += y * counter if y != 0 else 0
                _coords.append(xinit)
                _coords.append(yinit)
                counter = 0

            if _chaincode[i] == 5:
                previous_direction = (previous_direction+4) % 8
            else:
                xi, yi = checkPixelInMat(kernel_direction_data[previous_direction], _chaincode[i])
                xinit += xi
                yinit += yi
                _coords.append(xinit)
                _coords.append(yinit)
                previous_direction = static_direction_kernel[yi+1][xi+1]

        elif _chaincode[i] == 0:
            counter += 1
        elif _chaincode[i] == RS6FCC_Low_symbol:
            counter += RS6FCC_Low_simplifier
        elif _chaincode[i] == RS6FCC_High_symbol:
            counter += RS6FCC_High_simplifier

        if i == len(_chaincode)-1 and counter >0:
            x, y = checkPixelInMat(kernel_direction_data[previous_direction], 0)
            xinit += x * counter if x != 0 else 0
            yinit += y * counter if y != 0 else 0
            _coords.append(xinit)
            _coords.append(yinit)

    return _coords

def computeSRF6DCC(_coords):
    _distances = []
    SRF6DCC_High_simplifier = 15
    SRF6DCC_Low_simplifier = 3
    SRF6DCC_High_symbol = 7
    SRF6DCC_Low_symbol = 6
    if len(_coords) == 0:
        return [], 0, 0
    _xinit = int(_coords[0])
    _yinit = int(_coords[1])
    xinit = _xinit
    yinit = _yinit

    static_direction_kernel = np.array([[5, 6, 7], [4, 9, 0], [3, 2, 1]])

    kernel_direction_data = np.array([[[5, 4, 2], [5, 9, 0], [5, 3, 1]],  # direction 0 updated kernel
                                      [[5, 5, 4], [5, 9, 2], [3, 1, 0]],  # direction 1 updated kernel
                                      [[5, 5, 5], [3, 9, 4], [1, 0, 2]],  # direction 2 updated kernel
                                      [[3, 5, 5], [1, 9, 5], [0, 2, 4]],  # direction 3 updated kernel
                                      [[1, 3, 5], [0, 9, 5], [2, 4, 5]],  # direction 4 updated kernel
                                      [[0, 1, 3], [2, 9, 5], [4, 5, 5]],  # direction 5 updated kernel
                                      [[2, 0, 1], [4, 9, 3], [5, 5, 5]],  # direction 6 updated kernel
                                      [[4, 2, 0], [5, 9, 1], [5, 5, 3]]]) # direction 7 updated kernel
    # the polygon contouring starts always going down.
    # the polygon contouring starts always going down.
    previous_direction = 2
    for i in range(2, len(_coords), 2):
        x = round(_coords[i])
        y = round(_coords[i + 1])
        xi = x - xinit
        yi = y - yinit
        temp = []
        fin = max(abs(xi), abs(yi))

        xii = int(xi / abs(xi)) if xi != 0 else 0
        yii = int(yi / abs(yi)) if yi != 0 else 0

        for j in range(0, fin):
            move = kernel_direction_data[previous_direction][yii+1][xii+1]
            if move < 5:
                temp.append(move)
                previous_direction = static_direction_kernel[yii+1][xii+1]
            elif move == 5:
                temp.append(move)
                previous_direction = (previous_direction + 4) % 8
                move = kernel_direction_data[previous_direction][yii+1][xii+1]
                temp.append(move)
                previous_direction = static_direction_kernel[yii+1][xii+1]

        for k in range(0, len(temp)):
            _distances.append(temp[k])

        xinit = x
        yinit = y

        if len(_distances) != 0:
            _distances = simplifyAllFrontSequenceMovements(_distances, SRF6DCC_Low_simplifier, SRF6DCC_High_simplifier, SRF6DCC_Low_symbol, SRF6DCC_High_symbol)
    return _distances, _xinit, _yinit

def extractSRF6DCC2Points(_chaincode, _xinit, _yinit ):
    SRF6DCC_High_simplifier = 15
    SRF6DCC_Low_simplifier = 3
    return extractRS6FCC2Points(_chaincode, _xinit, _yinit, SRF6DCC_Low_simplifier, SRF6DCC_High_simplifier)

def checkPixelInMat(_kernel_direction_data, target):
    for row in range(0, 3):
        for col in range(0, 3):
            if _kernel_direction_data[row][col] == target:
                return col - 1, row - 1
    return 0, 0


def checkValueInKernel(_kernel_direction_data, target):
    for row in range(0, 3):
        for col in range(0, 3):
            if _kernel_direction_data[row][col] == target:
                return col, row
    return 0, 0


def simplifyFrontSequenceMovements(_num, _low, _high, _low_symbol, _high_symbol, _next_steps):
    if _high != -1:
        res1 = int(math.floor(_num / _high))
        res2 = int(_num % _high / _low)
        res3 = int(_num % _high % _low)
    else:
        res1 = 0
        res2 = int(_num / _low)
        res3 = int(_num % _low)

    for i in range(0, res1):
        _next_steps.append(_high_symbol)  # _high_symbol: {SRF6DCC: 7} for high Roman numerals-like counting simplifications
    for i in range(0, res2):
        _next_steps.append(_low_symbol)  # _low_symbol: {SRF6DCC: 6} for low Roman numerals-like counting simplifications
    for i in range(0, res3):
        _next_steps.append(0)
    return _next_steps


def simplifyAllFrontSequenceMovements(_chaincode, _low, _high, _low_symbol, _high_symbol):
    counter = 0
    i = 0
    while i < len(_chaincode):
        if _chaincode[i] == 0:
            counter += 1
        elif _chaincode[i] != 0:
            if counter >= _low:
                # i - counter //position of last 0 - counter
                next_steps = []
                next_steps = simplifyFrontSequenceMovements(counter, _low, _high, _low_symbol, _high_symbol, next_steps)
                del _chaincode[i - counter: i]
                i -= counter
                _chaincode[i:i] = next_steps
                i += len(next_steps)
            counter = 0
        if i == len(_chaincode)-1:
            if counter >= _low:
                next_steps = []
                next_steps = simplifyFrontSequenceMovements(counter, _low, _high, _low_symbol, _high_symbol, next_steps)
                del _chaincode[len(_chaincode)-counter:len(_chaincode)]
                i -= counter
                _chaincode[len(_chaincode):len(_chaincode)] = next_steps
                i += len(next_steps)
            counter = 0
        i += 1
    return _chaincode


def base64Encoder(_num):
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    return alphabet[_num]


def base64Decoder(_value):
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    return alphabet.find(_value)


# Converts a vector of chaincode integers into a json printable characters string.
# By joining the digits to compose a 6 bits integer and the converting that integer in base64 character.
def chainCodeBase64Encoder(_chaincodevector, _chaincode_bits):
    # Add odd number in the vector for codification
    num_digits = int(6 / _chaincode_bits)
    _outputstring = ""
    rest = len(_chaincodevector) % num_digits
    if rest != 0:
        vectrest = int(num_digits - rest)
        for i in range(0, vectrest):
            _chaincodevector.append(0)
    else:
        vectrest = 0
    for i in range(0, len(_chaincodevector), num_digits):
        byte = 0
        for j in range(0, num_digits):
            byte += _chaincodevector[i + j] << (num_digits - 1 - j) * _chaincode_bits
        _outputstring += base64Encoder(byte)
    return _outputstring, vectrest


# Converts back the json printable characters string to a vector of chaincode integers.
# By converting from base64 to 6bits integer and then splitting in chain code vector.
def chainCodeBase64Decoder(_chaincodebits, _chaincode_bits, _bitsvectorrest):
    _chaincodevector = []
    num_digits = int(6 / _chaincode_bits)
    getbits = pow(2, _chaincode_bits) - 1 # number of bits that need to move to

    for i in range(0, len(_chaincodebits)):
        byte = base64Decoder(_chaincodebits[i])
        for j in range(0, num_digits):
            number = byte & getbits
            _chaincodevector.insert(i * num_digits, number)
            byte -= number
            byte = byte >> _chaincode_bits

    for k in range(0, _bitsvectorrest):
        _chaincodevector.pop(len(_chaincodevector) - 1)

    return _chaincodevector

def calculateMultiplier(val, x):
    return math.floor(val/x) + (val % x)

def calculateMultiplier2(val, x, y):
    return calculateMultiplier(math.floor(val/y) + (val % y), x)

def extractMultiplierMap(map):
    min_repetition = 0
    min_suma = math.inf
    for key_i in map:
        suma = 0
        for key_j in map:
            suma += map[key_j] * calculateMultiplier(key_j, key_i)
        if suma < min_suma:
            min_repetition = key_i
            min_suma = suma
    return min_repetition

def extractMultiplierMap2(map):
    min_suma = math.inf
    map_items = list(map.items())
    for val_i in map_items[:-1]:
        for val_j in map_items[1:]:
            suma = 0
            for val_k in map_items:
                suma += val_k[1] * calculateMultiplier2(val_k[0], val_i[0], val_j[0])
            if suma < min_suma:
                min_repetition_1 = val_i[0]
                min_repetition_2 = val_j[0]
                min_suma = suma
    return min_repetition_1, min_repetition_2

def simplifyCalculatedFrontSequenceMovements(_chaincode, _low_symbol, _high_symbol):
    repetitionCounterMap = {}
    i = 0
    while i < len(_chaincode)-1:
        if _chaincode[i] == 0:
            counter = 1
            j = i+1
            while j < len(_chaincode):
                if _chaincode[j] == 0:
                    counter += 1
                    if j == len(_chaincode)-1:
                        i = j-1
                else:
                    i = j-1
                    break
                j = j+1
            if counter > 1:
                if repetitionCounterMap.get(counter) == None:
                    repetitionCounterMap[counter] = 1
                else:
                    repetitionCounterMap[counter] += 1
        i += 1

    if len(repetitionCounterMap) <= 0:
        _low = -1
        _high = -1

    elif len(repetitionCounterMap) == 1:
        for key in repetitionCounterMap:
            _low = key
        _high = -1
        _chaincode = simplifyAllFrontSequenceMovements(_chaincode, _low, _high, 6, 7)
    elif len(repetitionCounterMap) == 2:
        count = 0
        for key in repetitionCounterMap:
            if count == 0:
                _low = key
            else:
                _high = key
            count += 1
        _chaincode = simplifyAllFrontSequenceMovements(_chaincode, _low, _high, 6, 7)
    else:
        _low, _high = extractMultiplierMap2(repetitionCounterMap)
        _chaincode = simplifyAllFrontSequenceMovements(_chaincode, _low, _high, 6, 7)

    return _chaincode, _low, _high

def getVecFromEncodedSRF6(x, y, rest, encoded_poly):
    decoded = chainCodeBase64Decoder(encoded_poly, 3, rest)
    vec = extractSRF6DCC2Points(decoded, x, y)
    return vec

def getVecFromEncodedRS6(x, y, low, high, rest, encoded_poly):
    decoded = chainCodeBase64Decoder(encoded_poly, 3, rest)
    vec = extractRS6FCC2Points(decoded, x, y, low, high)
    return vec