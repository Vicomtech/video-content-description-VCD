#include "vcd_types.h"

namespace vcd
{

namespace types
{
// Abstract class implementations
TypeElement::~TypeElement()
{
}

// Bbox class
Bbox::Bbox(const std::string& name, const std::vector<int>& value) :
        m_value(value) {
        m_name = name;
    };

TypeElement&
Bbox::get()
{
    return static_cast<TypeElement&>(*this);
}

nlohmann::json
Bbox::json()
{
}

// Vec class
Vec::Vec(const std::string& name, const std::vector<float>& value) :
        m_value(value) {
        m_name = name;
    };

TypeElement&
Vec::get()
{
    return static_cast<TypeElement&>(*this);
}

nlohmann::json
Vec::json()
{
}

// Num class
Num::Num(const std::string& name, const double value) :
    m_value(value) {
    m_name = name;
};

TypeElement&
Num::get()
{
    return static_cast<TypeElement&>(*this);
}

nlohmann::json
Num::json()
{
}

};  // namespace types

};  // namespace vcd
