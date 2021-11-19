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
#include "vcd.h"

#include "vcd_impl.h"

#include <regex>

#ifdef ENABLE_GUID
    #include "Guid.hpp"
#endif

namespace vcd {

VCD::~VCD() {
}

std::unique_ptr<VCD>
VCD::create(const std::string& fileName, const bool validation) {
    return std::make_unique<VCD_Impl>(fileName, validation);
}

std::unique_ptr<VCD>
VCD::create(const bool validation) {
    return VCD::create("", validation);
}

/** @brief Generate a Version 4 UUID according to RFC-4122
 *
 * Uses the openssl RAND_bytes function to generate a
 * Version 4 UUID.
 *
 * @param buffer A buffer that is at least 38 bytes long.
 * @retval 1 on success, 0 otherwise.
 */
std::string
VCD_UID::generate_uuid4() {
#ifdef ENABLE_GUID
    std::string guid = xg::newGuid().str();
#else
    std::string guid("XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXXXX");
#endif

    return guid;
}

bool
VCD_UID::check_uuid4(const std::string &uuid) {
    const std::string reg_ex_uid =
            "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
            "[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$";
    return regex_match(uuid, std::regex(reg_ex_uid));
}

VCD_UID::~VCD_UID() {
}

};  // namespace vcd
