#ifndef _VCD_TYPES_H_
#define _VCD_TYPES_H_

#include <nlohmann/json.hpp>

namespace vcd
{

namespace types
{

class TypeElement
{
public:
    virtual
    ~TypeElement();

    virtual TypeElement&
    get() = 0;

    virtual nlohmann::json
    json() = 0;

protected:
    std::string m_name;
};

class Bbox : public TypeElement
{
public:
    Bbox(const std::string& name, const std::vector<int>& value);

    TypeElement&
    get() override;

    nlohmann::json
    json() override;

private:
    std::vector<int> m_value;
};

class Vec : public TypeElement
{
public:
    Vec(const std::string& name, const std::vector<float>& value);

    TypeElement&
    get() override;

    nlohmann::json
    json() override;


private:
    std::vector<float> m_value;
};

class Num : public TypeElement
{
public:
    Num(const std::string& name, const double value);

    TypeElement&
    get() override;

    nlohmann::json
    json() override;

private:
    double m_value = 0;
};

};  // namespace types

};  // namespace vcd

#endif  // _VCD_TYPES_H_
