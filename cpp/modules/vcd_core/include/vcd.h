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
#ifndef _VCD_H_
#define _VCD_H_

#include <string>
#include <memory>

#include "core_exp.h"
#include "vcd_types.h"

namespace vcd {

class VCD {
 public:
    virtual
    ~VCD();

    virtual void
    setUseUUID(const bool val) = 0;

    virtual std::string
    stringify(const bool pretty = true) const = 0;

    virtual void
    save(const std::string& fileName, bool pretty = false) const = 0;

    virtual uint32_t
    add_object(const std::string& name, const std::string& semantic_type) = 0;

    virtual void
    add_object_data(const uint32_t uid,
                    const types::ObjectData& object_data) = 0;

    // Instance creation factories
    static CORE_LIB std::unique_ptr<VCD>
    create(const std::string& fileName, const bool validation = false);

    static CORE_LIB std::unique_ptr<VCD>
    create(const bool validation = false);
};
using VCD_ptr = std::unique_ptr<VCD>;

};  // namespace vcd

#endif  // _VCD_H_
