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
#include "vcd_types.h"

using json = nlohmann::json;

namespace vcd {

namespace types {

const char* ObjectDataTypeNames[] = {
    "none",
    "bbox",
    "rbbox",
    "num",
    "text",
    "boolean",
    "poly2d",
    "poly3d",
    "cuboid",
    "image",
    "mat",
    "binary",
    "point2d",
    "point3d",
    "vec",
    "line_reference",
    "area_reference",
    "mesh"
};

// Abstract class implementations
ObjectData::~ObjectData() {
}

ObjectDataGeometry::~ObjectDataGeometry() {
}

void
ObjectDataGeometry::add_attribute(const ObjectData &object_data) {
    // Creates 'attributes' if it does not exist
    if (m_data["attributes"].is_null()) {
        m_data["attributes"] = nlohmann::json({});
    }

    const ObjectDataType attrType = object_data.getType();
    const auto& attrTypeName = ObjectDataTypeNames[attrType];
    const auto& attrName = object_data.getName();
    const bool attrNotEmpty = !m_data["attributes"][attrTypeName].is_null();
    if (attrNotEmpty) {
        // There are attributes of this type, find inside if an attribute with
        // the same name appears.
        auto& attrList = m_data["attributes"][attrTypeName];
        std::vector<size_t> posList;
        size_t i = 0;
        for (const auto& e : attrList) {
            if (e["name"] == attrName) {
                posList.push_back(i);
            }
            ++i;
        }
        if (posList.size() == 0) {
            // Specific attribute was not found
            m_data["attributes"][attrTypeName].push_back(object_data.getData());
        } else {
            // Ok, exists, so let's substitute
            const size_t pos = posList[0];
            m_data["attributes"][attrTypeName][pos] = object_data.getData();
        }
    } else {
        m_data["attributes"][attrTypeName] = {object_data.getData()};  // list
    }
}

// Bbox class
Bbox::Bbox(const std::string& name, const std::vector<int>& value) {
        m_name = name;
        m_data = {{"name", name}, {"val", value}};
        m_type = bbox;
}

ObjectData&
Bbox::get() {
    return static_cast<ObjectData&>(*this);
}

// Vec class
Vec::Vec(const std::string& name, const std::vector<float>& value) {
        m_name = name;
        m_data = {{"name", name}, {"val", value}};
        m_type = vec;
}

ObjectData&
Vec::get() {
    return static_cast<ObjectData&>(*this);
}

// Num class
Num::Num(const std::string& name, const double value) {
    m_name = name;
    m_data = {{"name", name}, {"val", value}};
    m_type = num;
}

ObjectData&
Num::get() {
    return static_cast<ObjectData&>(*this);
}

// Boolean class
Boolean::Boolean(const std::string& name, const bool value) {
    m_name = name;
    m_data = {{"name", name}, {"val", value}};
    m_type = boolean;
}

ObjectData&
Boolean::get() {
    return static_cast<ObjectData&>(*this);
}

};  // namespace types

};  // namespace vcd
