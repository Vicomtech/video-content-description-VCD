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
#ifndef _VCD_TYPES_H_
#define _VCD_TYPES_H_

#include <nlohmann/json.hpp>

namespace vcd {

namespace types {

enum ObjectDataType {
    none = 0,
    bbox = 1,
    rbbox = 2,
    num = 3,
    text = 4,
    boolean = 5,
    poly2d = 6,
    poly3d = 7,
    cuboid = 8,
    image = 9,
    mat = 10,
    binary = 11,
    point2d = 12,
    point3d = 13,
    vec = 14,
    line_reference = 15,
    area_reference = 16,
    mesh = 17,
    ODT_size = 18
};

const std::string
ObjectDataTypeName[] {
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

class ObjectData {
 public:
    virtual
    ~ObjectData();

    virtual ObjectData&
    get() = 0;

    ObjectDataType
    getType() const { return m_type; }

    std::string
    getName() const { return m_name; }

    nlohmann::json
    getData() const { return m_data; }

 protected:
    ObjectDataType m_type;
    std::string m_name;
    nlohmann::json m_data;
};

class ObjectDataGeometry : public ObjectData {
 public:
    virtual
    ~ObjectDataGeometry();

    void
    add_attribute(const ObjectData &object_data);
};


class Bbox : public ObjectDataGeometry {
 public:
    Bbox(const std::string& name, const std::vector<int>& value);

    ObjectData&
    get() override;
};

class Vec : public ObjectData {
 public:
    Vec(const std::string& name, const std::vector<float>& value);

    ObjectData&
    get() override;
};

class Num : public ObjectData {
 public:
    Num(const std::string& name, const double value);

    ObjectData&
    get() override;
};

class Boolean : public ObjectData {
 public:
    Boolean(const std::string& name, const bool value);

    ObjectData&
    get() override;
};

class Text : public ObjectData {
 public:
    Text(const std::string& name, const std::string& text);

    ObjectData&
    get() override;
};

class Point2d : public ObjectData {
 public:
    Point2d(const std::string& name, const double x, const double y);

    ObjectData&
    get() override;
};

class Point3d : public ObjectData {
 public:
    Point3d(const std::string& name,
            const double x, const double y, const double z);

    ObjectData&
    get() override;
};

};  // namespace types

};  // namespace vcd

#endif  // _VCD_TYPES_H_
