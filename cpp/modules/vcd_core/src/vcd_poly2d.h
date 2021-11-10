/*
* VCD (Video Content Description) library v4.3.0
*
* Project website: http://vcd.vicomtech.org
*
* Copyright (C) 2020, Vicomtech (http://www.vicomtech.es/),
* (Spain) all rights reserved.

* VCD is a C++ library to create and manage VCD content version 4.3.0.
* VCD is distributed under MIT License. See LICENSE.
*
*/
#ifndef _VCD_poly2d_H_
#define _VCD_poly2d_H_

#define __include_poly2d__
#ifdef __include_poly2d__

#include<vector>
#include<string>

// enum Poly2DTypes {
//    MODE_POLY2D_ABSOLUTE = 0,
//    // MODE_POLY2D_BBOX = 1,
//    // MODE_POLY2D_BBOX_DIST = 2,
//    // MODE_POLY2D_F8DCC = 3,
//    // MODE_POLY2D_RF8DCC = 4,
//    MODE_POLY2D_SRF6DCC = 5,
//    // MODE_POLY2D_RS6FCC = 6
// };

const std::string
Poly2DTypeName[] {
    "MODE_POLY2D_ABSOLUTE",
    "MODE_POLY2D_BBOX",
    "MODE_POLY2D_BBOX_DIST",
    "MODE_POLY2D_F8DCC",
    "MODE_POLY2D_RF8DCC",
    "MODE_POLY2D_SRF6DCC",
    "MODE_POLY2D_RS6FCC"
};

struct Poly2DDefinition {
    std::vector<int> distances;
    int xinit = 0;
    int yinit = 0;
};

Poly2DDefinition
computeSRF6DCC(const std::vector<int> &coords);

std::vector<int>
simplifyFrontSequenceMovements(const int num,
                               const int low, const int high,
                               const int low_symbol, const int high_symbol);

void
simplifyAllFrontSequenceMovements(std::vector<int>* chaincode_ptr,
                                  const int low, const int high,
                                  const int low_symbol, const int high_symbol);

#endif  // __include_poly2d__

#endif  // _VCD_poly2d_H_
