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
#ifndef _TEST_UTILS_H_
#define _TEST_UTILS_H_

#include <string>
#include <fstream>

#include <nlohmann/json.hpp>

using nlohmann::json;

// Define a comparison function for recursivity
bool
check_json_level(const json &data_a, const json &data_b) {
    // Check the element type and do the proper analysis
    if (data_a.is_object()) {
        if (!data_b.is_object()) return false;
        for (auto& el_a : data_a.items()) {
            // Check if the element exists
            if (!data_b.contains(el_a.key())) {
                printf("Missed element with key '%s'\n", el_a.key().c_str());
                return false;
            } else {
                // If exists, check the value of the element
                const json& newElem_a = el_a.value();
                const auto& key = el_a.key();
                const json& newElem_b = data_b[key];
                bool isEqual = check_json_level(newElem_a, newElem_b);
                if (!isEqual) {
                    printf("Error in element with key '%s'\n", key.c_str());
                    return false;
                }
            }
        }
    } else if (data_a.is_array()) {
        if (!data_b.is_array()) return false;
        size_t n_a = data_a.size();
        size_t n_b = data_b.size();
        if (n_a != n_b) return false;
        for (size_t i = 0; i < n_a; ++i) {
            const bool isEqual = check_json_level(data_a[i], data_b[i]);
            if (!isEqual) {
                printf("Error in element with index '%zi'\n", i);
                return false;
            }
        }
    } else if (data_a.is_boolean()) {
        if (!data_b.is_boolean()) return false;
        return data_a == data_b;
    } else if (data_a.is_number()) {
        if (!data_b.is_number()) return false;
        // Check similarity insteada of equality to avoid errors with similar
        // but not equal float values.
        const float a = data_a.get<float>();
        const float b = data_b.get<float>();
        const float sim = abs(a - b);
        const float threshold = 0.001;
        return sim < threshold;
    } else if (data_a.is_null()) {
        return data_b.is_null();

    } else if (data_a.is_string()) {
        const auto& str_a = data_a.get<std::string>();
        const auto& str_b = data_b.get<std::string>();
        const bool are_equal = str_a.compare(str_b) == 0;
        return are_equal;
    }

    return true;
}

bool
check_json_level_both_sides(const json &data_a, const json &data_b) {
    const bool atob = check_json_level(data_a, data_b);
    if (!atob) {
        return false;
    }
    const bool btoa = check_json_level(data_b, data_a);
    return btoa;
}

bool
compare_json_files(const std::string& file_a, const std::string& file_b) {
    // Read json file A
    std::ifstream file_a_i(file_a);
    json data_a;
    file_a_i >> data_a;
    file_a_i.close();

    // Read json file B
    std::ifstream file_b_i(file_b);
    json data_b;
    file_b_i >> data_b;
    file_b_i.close();

    // Make a loop to compare both json structures
    return check_json_level(data_a, data_b);
}

#endif  // _TEST_UTILS_H_
