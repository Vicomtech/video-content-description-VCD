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
#include "vcd_poly2d.h"

#ifdef __include_poly2d__

#include <cmath>
#include <algorithm>

Poly2DDefinition
computeSRF6DCC(const std::vector<int> &coords) {
//    std::vector<int> distances;
    const size_t SRF6DCC_High_simplifier = 15;
    const size_t SRF6DCC_Low_simplifier = 3;
    const size_t SRF6DCC_High_symbol = 7;
    const size_t SRF6DCC_Low_symbol = 6;

    Poly2DDefinition polyDef;
    if (coords.size() == 0) {
        return polyDef;
    }
    polyDef.xinit = static_cast<int>(coords[0]);
    polyDef.yinit = static_cast<int>(coords[1]);
    int xinit = polyDef.xinit;
    int yinit = polyDef.yinit;

    const std::vector<std::vector<int>> st_dir_kernel {
                                                        {5, 6, 7},
                                                        {4, 9, 0},
                                                        {3, 2, 1}
                                                      };

    const std::vector<std::vector<std::vector<int>>> kernel_dir_data = {
        {{5, 4, 2}, {5, 9, 0}, {5, 3, 1}},  // direction 0 updated kernel
        {{5, 5, 4}, {5, 9, 2}, {3, 1, 0}},  // direction 1 updated kernel
        {{5, 5, 5}, {3, 9, 4}, {1, 0, 2}},  // direction 2 updated kernel
        {{3, 5, 5}, {1, 9, 5}, {0, 2, 4}},  // direction 3 updated kernel
        {{1, 3, 5}, {0, 9, 5}, {2, 4, 5}},  // direction 4 updated kernel
        {{0, 1, 3}, {2, 9, 5}, {4, 5, 5}},  // direction 5 updated kernel
        {{2, 0, 1}, {4, 9, 3}, {5, 5, 5}},  // direction 6 updated kernel
        {{4, 2, 0}, {5, 9, 1}, {5, 5, 3}}   // direction 7 updated kernel
      };

    // the polygon contouring starts always going down.
    int prev_dir = 2;
    int x, y;
    int xi, yi;
    int xii, yii;
    int fin;
    std::vector<int> temp;
    const size_t n = coords.size();
    for (size_t i = 2; i < n; i += 2) {
        x = static_cast<int>(round(coords[i]));
        y = static_cast<int>(round(coords[i + 1]));
        xi = x - xinit;
        yi = y - yinit;
        temp.clear();
        fin = std::max(abs(xi), abs(yi));

        xii = xi != 0? static_cast<int>(xi / abs(xi)) : 0;
        yii = yi != 0? static_cast<int>(yi / abs(yi)) : 0;

        for (int j = 0; j < fin; ++j) {
            const auto& move = kernel_dir_data[prev_dir][yii+1][xii+1];
            if (move < 5) {
                temp.push_back(move);
                prev_dir = st_dir_kernel[yii+1][xii+1];
            } else if (move == 5) {
                temp.push_back(move);
                prev_dir = (prev_dir + 4) % 8;
                const auto & new_move = kernel_dir_data[prev_dir][yii+1][xii+1];
                temp.push_back(new_move);
                prev_dir = st_dir_kernel[yii+1][xii+1];
            }
        }

        const size_t m = temp.size();
        for (size_t k = 0; k < m; ++k) {
            polyDef.distances.push_back(temp[k]);
        }

        xinit = x;
        yinit = y;

        if (polyDef.distances.size() != 0) {
            simplifyAllFrontSequenceMovements(&(polyDef.distances),
                                              SRF6DCC_Low_simplifier,
                                              SRF6DCC_High_simplifier,
                                              SRF6DCC_Low_symbol,
                                              SRF6DCC_High_symbol);
        }
    }
    return polyDef;
}

std::vector<int>
simplifyFrontSequenceMovements(const int num,
                               const int low, const int high,
                               const int low_symbol, const int high_symbol) {
    std::vector<int> next_steps;
    int res1 = 0;
    int res2 = 0;
    int res3 = 0;
    if (high != -1) {
        res1 = static_cast<int>(std::floor(num / high));
        res2 = static_cast<int>(num % high / low);
        res3 = static_cast<int>(num % high % low);
    } else {
        res1 = 0;
        res2 = static_cast<int>(num / low);
        res3 = static_cast<int>(num % low);
    }

    for (int i = 0; i < res1; ++i) {
        // high_symbol: {SRF6DCC: 7} for high Roman numerals-like
        //              counting simplifications
        next_steps.push_back(high_symbol);
    }
    for (int i = 0; i < res2; ++i) {
        // low_symbol: {SRF6DCC: 6} for low Roman numerals-like
        //             counting simplifications
        next_steps.push_back(low_symbol);
    }
    for (int i = 0; i < res3; ++i) {
        next_steps.push_back(0);
    }

    return next_steps;
}

void
simplifyAllFrontSequenceMovements(std::vector<int>* chaincode_ptr,
                                  const int low, const int high,
                                  const int low_symbol, const int high_symbol) {
    std::vector<int>& chaincode = *chaincode_ptr;
    int counter = 0;
    size_t i = 0;
    while (i < chaincode.size()) {
        if (chaincode[i] == 0) {
            counter += 1;
        } else if (chaincode[i] != 0) {
            if (counter >= low) {
                // i - counter // position of last 0 - counter
                const auto next_steps = simplifyFrontSequenceMovements(counter,
                                                                   low, high,
                                                                   low_symbol,
                                                                   high_symbol);
                // del _chaincode[i - counter: i]
                chaincode.erase(std::next(chaincode.begin(), i - counter),
                                std::next(chaincode.begin(), i));
                i -= counter;
//                chaincode[i] = next_steps;
                chaincode.insert(std::begin(chaincode) + i,
                                 std::begin(next_steps), std::end(next_steps));
                i += next_steps.size();
            }
            counter = 0;
        }
        if (i == chaincode.size() - 1) {
            if (counter >= low) {
                const auto next_steps = simplifyFrontSequenceMovements(counter,
                                                                   low, high,
                                                                   low_symbol,
                                                                   high_symbol);
                // del chaincode[len(chaincode)-counter:len(chaincode)]
                const auto s = chaincode.size();
                chaincode.erase(std::next(chaincode.begin(), s - counter),
                                std::next(chaincode.begin(), s));
                i -= counter;
                // chaincode[len(_chaincode):len(_chaincode)] = next_steps
                chaincode.insert(std::begin(chaincode) + s,
                                 std::begin(next_steps), std::end(next_steps));
                i += next_steps.size();
            }
            counter = 0;
        }
        i += 1;
    }
}

#endif  // __include_poly2d__
