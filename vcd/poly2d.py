"""
VCD (Video Content Description) library v4.1.0

Project website: http://vcd.vicomtech.org

Copyright (C) 2020, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.1.0.
VCD is distributed under MIT License. See LICENSE.

"""

import numpy as np
import math

def computeSRFSDCC(coords):
    _distances = []
    # Simplifiers
    high_simplifier = 15
    low_simplifier = 3
    high_symbol = 7
    low_symbol = 6

    # This method converts to integer position all (X,Y) coordinates. Then, uses the Bbox
    # to compute the relative positions computes a 1D array concatenating rows, and determines distances between points

    if len(coords) == 0:
        return []

    xinit = coords[0]
    yinit = coords[1]

    _distances.append(xinit)
    _distances.append(yinit)

    '''
     static Direction Kernel
     5(TopLeft)      6(Top)         7(TopRight)
     4(Left)         X              0(Right) 
     3(BottomLeft)   2(Bottom)      1(BottomRight)

    For a previous direction of going 2(Bottom), the kernel updates the "0" value to place of the movement and the rest of the values are set clockwise.
     New Kernel
     3 4 5 
     2 X 6 
     1 0 7
    '''
    static_direction_kernel = np.array([[5, 6, 7], [4, 9, 0], [3, 2, 1]])
    '''
    All SRF6DCC relative kernels
    Static direction 0  Static direction 1  Static direction 2  Static direction 3 
         54 4  2              5  52 4             53 5  54              3  51 5 
         5  X  0              51 x  2             3  x  4               1  x  52 
         53 3  1              3  1  0             1  0  2               0  2  4
    Static direction 4  Static direction 5  Static direction 6  Static direction 7 
         1  3  53              0  1  3            2  0  1               4  2  0 
         0  X  5               2  x  51           4  x  3               52 x  1
         2  4  54              4  52 5            54 5  53              5  51 3
    '''

    kernel_direction_data = np.array([[[54, 4, 2], [5, 9, 0], [53, 3, 1]],  # direction 0 updated kernel
                                      [[5, 52, 4], [51, 9, 2], [3, 1, 0]],  # direction 1 updated kernel
                                      [[53, 5, 54], [3, 9, 4], [1, 0, 2]],  # direction 2 updated kernel
                                      [[3, 51, 5], [1, 9, 52], [0, 2, 4]],  # direction 3 updated kernel
                                      [[1, 3, 53], [0, 9, 5], [2, 4, 54]],  # direction 4 updated kernel
                                      [[0, 1, 3], [2, 9, 51], [4, 52, 5]],  # direction 5 updated kernel
                                      [[2, 0, 1], [4, 9, 3], [54, 5, 53]],  # direction 6 updated kernel
                                      [[4, 2, 0], [52, 9, 1], [5, 51, 3]]]) # direction 7 updated kernel
    # the polygon contouring starts always going down.
    previous_direction = 2

    '''
    IMPORTANT NOTES: the kernel is always updated but not when backward movement is done.
    So when the kernel movement is 5, the backward step is saved in the chain code but the kernel is not updated.
    Similar happens when moving 51, 52, 53 or 54:
          In those cases there are two movements done. First it goes backwards, the step is saved but the kernel does not change
          and then the other movement [1,2,3 or 4] takes places, so the step is saved in the chaincode and the kernel must be updated through that direction.
    '''
    for i in range(0, len(coords), 2):
        x = round(coords[i])
        y = round(coords[i + 1])
        xi = x - xinit
        yi = y - yinit
        temp = []
        fin = max(abs(xi), abs(yi))
        xii = 0
        yii = 0

        if xi != 0:
            xii = int(xi / abs(xi))
        else:
            xii = 0
        if yi != 0:
            yii = int(yi / abs(yi))
        else:
            yii = 0

        for j in range(0, fin):
            move = kernel_direction_data[previous_direction][yii + 1][xii + 1]
            if move < 5:
                temp.append(move)
                previous_direction = static_direction_kernel[yii + 1][xii + 1]
            elif move == 51:
                # Equivalent to movement Back then Right
                temp.append(5)
                temp.append(1)
                xx, yy = checkPixelInMat(kernel_direction_data[previous_direction], 1)
                previous_direction = static_direction_kernel[yy][xx]

            elif move == 52:
                # Equivalent to movement Back then Left
                temp.append(5)
                temp.append(2)
                xx, yy = checkValueInKernel(kernel_direction_data[previous_direction], 2)
                previous_direction = static_direction_kernel[yy][xx]

            elif move == 53:
                # Equivalent to movement Back then Right
                temp.append(5)
                temp.append(3)
                xx, yy = checkValueInKernel(kernel_direction_data[previous_direction], 3)
                previous_direction = static_direction_kernel[yy][xx]

            elif move == 54:
                # Equivalent to movement Back then Left
                temp.append(5)
                temp.append(4)
                xx, yy = checkValueInKernel(kernel_direction_data[previous_direction], 4)
                previous_direction = static_direction_kernel[yy][xx]

            elif move == 5:
                temp.append(move)

        # usually there is a change of direction and then an accumulation of forward movements.  for example: 2 0 0 0 0 0 0 0
        # so we keep the fisrt movement and simplify the forward movements using romanic-like counting
        for k in range(0, len(temp)):
            if temp[k] == 0:
                break
            else:
                _distances.append(temp[k])

        num_of0 = temp.count(0)
        _distances = simplifyFrontSequenceMovements(num_of0, low_simplifier, high_simplifier, low_symbol,
                                                    high_symbol, _distances)
        xinit = x
        yinit = y

    return simplifyAllFrontSequenceMovements(_distances, low_simplifier, high_simplifier, low_symbol, high_symbol)


def extractSRF6DCC2Points(_chaincode, _xinit, _yinit):
    # Simplifiers
    high_simplifier = 15
    low_simplifier = 3
    high_symbol = 7
    low_symbol = 6
    _coords = []
    _coords.append(_xinit)
    _coords.append(_yinit)
    xinit = _xinit
    yinit = _yinit

    '''
    static Direction Kernel
    5(TopLeft)      6(Top)         7(TopRight)
    4(Left)         X              0(Right) 
    3(BottomLeft)   2(Bottom)      1(BottomRight)

    For a previous direction of going 2(Bottom), the kernel updates the "0" value to place of the movement and the rest of the values are set clockwise.
    New Kernel
    3 4 5 
    2 X 6 
    1 0 7
    '''
    static_direction_kernel = np.array([[5, 6, 7], [4, 9, 0], [3, 2, 1]])

    '''
    All SRF6DCC relative kernels
    Static direction 0  Static direction 1  Static direction 2  Static direction 3 
         54 4  2              5  52 4             53 5  54              3  51 5 
         5  X  0              51 x  2             3  x  4               1  x  52 
         53 3  1              3  1  0             1  0  2               0  2  4
    Static direction 4  Static direction 5  Static direction 6  Static direction 7 
         1  3  53              0  1  3            2  0  1               4  2  0 
         0  X  5               2  x  51           4  x  3               52 x  1
         2  4  54              4  52 5            54 5  53              5  51 3
    '''
    kernel_direction_data = np.array([[[54, 4, 2], [5, 9, 0], [53, 3, 1]],
                                      [[5, 52, 4], [51, 9, 2], [3, 1, 0]],
                                      [[53, 5, 54], [3, 9, 4], [1, 0, 2]],
                                      [[3, 51, 5], [1, 9, 52], [0, 2, 4]],
                                      [[1, 3, 53], [0, 9, 5], [2, 4, 54]],
                                      [[0, 1, 3], [2, 9, 51], [4, 52, 5]],
                                      [[2, 0, 1], [4, 9, 3], [54, 5, 53]],
                                      [[4, 2, 0], [52, 9, 1], [5, 51, 3]]])
    # the polygon contouring starts always going down.
    previous_direction = 2

    '''
    IMPORTANT NOTES: the kernel is always updated but not when backward movement is done.
    So when the kernel movement is 5, the backward step is saved in the chain code but the kernel is not updated.
    Similar happens when moving 51, 52, 53 or 54:
          In those cases there are two movements done. First it goes backwards,
          the step is saved but the kernel does not change and then the other movement [1,2,3 or 4] takes places,
          so the step is saved in the chaincode and the kernel must be updated through that direction.
    '''
    counter = 0
    for i in range(0, len(_chaincode)):
        if _chaincode[i] == low_symbol:
            counter += low_simplifier
            if i == len(_chaincode) - 1 and counter > 0:
                x, y = checkPixelInMat(kernel_direction_data[previous_direction], 0)
                xinit += x * counter if x != 0 else 0
                yinit += y * counter if y != 0 else 0
                _coords.append(xinit)
                _coords.append(yinit)
            continue

        elif _chaincode[i] == high_symbol:
            counter += high_simplifier
            if i == len(_chaincode) - 1 and counter > 0:
                x, y = checkPixelInMat(kernel_direction_data[previous_direction], 0)
                xinit += x * counter if x != 0 else 0
                yinit += y * counter if y != 0 else 0
                _coords.append(xinit)
                _coords.append(yinit)
            continue

        elif _chaincode[i] < 6:
            if counter > 0:
                x, y = checkPixelInMat(kernel_direction_data[previous_direction], 0)
                xinit += x * counter if x != 0 else 0
                yinit += y * counter if y != 0 else 0
                _coords.append(xinit)
                _coords.append(yinit)
            xi, yi = checkPixelInMat(kernel_direction_data[previous_direction], _chaincode[i])
            xinit += xi
            yinit += yi
            _coords.append(xinit)
            _coords.append(yinit)
            counter = 0
            if _chaincode[i] == 5:
                continue
            elif _chaincode[i] < 5:
                fin = max(abs(xi), abs(yi))
                xii = -400
                yii = -400
                xii = int(xi / abs(xi)) if xi != 0 else 0
                yii = int(yi / abs(yi)) if yi != 0 else 0
                previous_direction = static_direction_kernel[yii + 1][xii + 1]
    return _coords


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
    res1 = math.floor(_num / _high)
    res2 = math.floor(_num % _high / _low)
    res3 = math.floor(_num % _high % _low)
    for i in range(0, res1):
        _next_steps.append(_high_symbol)  # _high_symbol: {SRF6DCC: 7} for high Roman numerals-like counting simplifications
    for i in range(0, res2):
        _next_steps.append(_low_symbol)  # _low_symbol: {SRF6DCC: 6} for low Roman numerals-like counting simplifications
    for i in range(0, res3):
        _next_steps.append(0)
    return _next_steps


def simplifyAllFrontSequenceMovements(_chaincode, _low, _high, _low_symbol, _high_symbol):
    counter = 0
    for i in range(0, len(_chaincode)):
        if _chaincode[i] == 0:
            counter += 1
        else:
            if counter > 2:
                # i - counter //position of last 0 - counter
                next_steps = []
                next_steps = simplifyFrontSequenceMovements(counter, _low, _high, _low_symbol, _high_symbol, next_steps)
                del _chaincode[i - counter: i]
                i -= counter
                _chaincode[i:i] = next_steps
                i += len(next_steps)
            counter = 0
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


def getVecFromEncodedPoly(x, y, rest, encoded_poly):
    decoded = chainCodeBase64Decoder(encoded_poly, 3, rest)
    vec = extractSRF6DCC2Points(decoded, x, y)
    return vec
