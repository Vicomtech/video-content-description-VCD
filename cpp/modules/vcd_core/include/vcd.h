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

class VCD_UID {
 public:
    ~VCD_UID();

    virtual bool
    isUUID() const = 0;

    virtual std::string
    asStr() const = 0;

    virtual int
    asInt() const = 0;

    virtual bool
    isNone() const = 0;
};

using ont_uid = std::string;
using obj_uid = std::string;

struct obj_args {
    std::string semantic_type;
    ont_uid ontology_uid;
    obj_uid uid;
};

class VCD {
 public:
    virtual
    ~VCD();

    virtual void
    setUseUUID(const bool val) = 0;

    /**
     * @brief stringify Returns the information as a string and with a JSON
     * structure.
     * @param pretty If true, the return format includes a more readable
     * presentation, including returns and indentation.
     * @return The JSON content as a string
     */
    virtual std::string
    stringify(const bool pretty = true) const = 0;

    /**
     * @brief save Stores the loaded information in a JSON file in disk.
     * @param fileName Path and name of the output file.
     * @param prettyIf true, the return format includes a more readable
     * presentation, including returns and indentation.
     * @param validate ?
     */
    virtual void
    save(const std::string& fileName, const bool pretty = false,
         const bool validate = false) const = 0;

    /**
     * @brief load Loads stored information in a JSON file in disk.
     * @param fileName Path and name of the output file.
     */
    virtual void
    load(const std::string& fileName) = 0;

    // Add object
    virtual obj_uid
    add_object(const std::string& name, const obj_args& args) = 0;

    virtual obj_uid
    add_object(const std::string& name, const size_t frame_index,
               const obj_args& args) = 0;

    // Add object_data
    virtual void
    add_object_data(const std::string &uid,
                    const types::ObjectData& object_data) = 0;

    virtual void
    add_object_data(const std::string &uid,
                    const types::ObjectData& object_data,
                    const size_t frame_index) = 0;

    virtual ont_uid
    add_ontology(const std::string &ontology) = 0;

    // Instance creation factories
    static CORE_LIB std::unique_ptr<VCD>
    create(const std::string& fileName, const bool validation = false);

    static CORE_LIB std::unique_ptr<VCD>
    create(const bool validation = false);
};
using VCD_ptr = std::unique_ptr<VCD>;

};  // namespace vcd

#endif  // _VCD_H_
