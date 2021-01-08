#include "vcd.h"

#include "vcd_impl.h"

namespace vcd
{

VCD::~VCD()
{
}

std::unique_ptr<VCD>
VCD::create(const std::string& fileName, const bool validation)
{
    return std::make_unique<VCD_Impl>(fileName, validation);
}

std::unique_ptr<VCD>
VCD::create(const bool validation)
{
    return VCD::create("", validation);
}

};  // namespace vcd
