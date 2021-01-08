#include <fstream>
#include <regex>
#include "vcd_impl.h"

namespace vcd
{

///////////////////////////////////////////////
// VCD_Impl
///////////////////////////////////////////////
VCD_Impl::VCD_Impl(const std::string& fileName, const bool validation) :
    m_useUUID(false)
{    
    if (!fileName.empty())
    {
        // Load from file
        std::ifstream file(fileName);                
        file >> m_data;
        file.close();
    }
    else
    {
        reset();
    }
    
}

VCD_Impl::~VCD_Impl()
{
}

void
VCD_Impl::reset()
{    
    m_data["vcd"] = json::object();  // = json::object();
    m_data["vcd"]["metadata"] = json::object();
    m_data["vcd"]["metadata"]["schema_version"] = "4.3.0";

    m_lastUIDbyType[ElementType::object] = -1;
    m_lastUIDbyType[ElementType::action] = -1;
    m_lastUIDbyType[ElementType::event] = -1;
    m_lastUIDbyType[ElementType::context] = -1;
    m_lastUIDbyType[ElementType::relation] = -1;

    //this->fis = FrameIntervals(0);  // works
    //this->fis = FrameIntervals({0, 10}); // works
    // this->fis = FrameIntervals({{0, 10}}); // works
    //data["vcd"]["frame_intervals"] = this->fis.get_dict();
}

std::string
VCD_Impl::stringify(const bool pretty) const
{
    std::string str;
    if(pretty)
        str = m_data.dump(4);
    else
        str = m_data.dump();
    return str;
}

void
VCD_Impl::save(const std::string& fileName, const bool pretty) const
{
    std::string json_string = this->stringify(pretty);
    std::ofstream f(fileName);
    f << json_string;
    f.close();
}

uint32_t
VCD_Impl::add_object(const std::string& name,
                     const std::string& semantic_type)
{
}

void
VCD_Impl::add_object_data(const uint32_t uid,
                          const types::TypeElement& object_data)
{
}

///////////////////////////////////////////////
// UID
///////////////////////////////////////////////
UID::UID(int val)
{
    this->set(std::to_string(val), val, false);
}
UID::UID(std::string val)
{
    if(val == "") { this->set("", -1, false); }
    else 
    {
        bool is_integer = !val.empty() && val.find_first_not_of("0123456789") == std::string::npos;
        if(is_integer)        
            this->set(val, std::stoi(val), false);        
        else
        {
            // e.g. 3d4705a6-6a54-4c5c-9f33-bbb21cc5d576
            std::regex pattern("[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}");
            bool matches_regex = std::regex_match(val, pattern);
            if(matches_regex)            
                this->set(val, -1, true);            
            else            
                throw std::runtime_error("ERROR: UID string is not integer not UUID.");
        }
    }
    
    
}
void UID::set(std::string uidStr, int uidInt, bool isUUID)
{
    this->uidStr = uidStr;
    this->uidInt = uidInt;
    this->is_UUID = isUUID;
}

///////////////////////////////////////////////
// FrameIntervals
///////////////////////////////////////////////
FrameIntervals::FrameIntervals(int frameValue)
{
    this->fisDict = json::array();
    this->fisDict.push_back({{"frame_start", frameValue}, {"frame_end", frameValue}});
    this->fisNum = {{frameValue, frameValue}};
}
FrameIntervals::FrameIntervals(const Tuple& frameValue)
{
    this->fisDict = json::array();
    this->fisDict.push_back({{"frame_start", frameValue[0]}, {"frame_end", frameValue[1]}});
    this->fisNum = {frameValue};
}
FrameIntervals::FrameIntervals(const ArrayNx2& frameValue)
{
    this->fisDict = json::array();
    for(auto it : frameValue)
        this->fisDict.push_back({{"frame_start", it[0]}, {"frame_end", it[1]}});
    this->fisNum = frameValue;
}
bool FrameIntervals::hasFrame(int frameNum) const
{
    for(auto fi : this->fisNum)
    {
        if( fi[0] <= frameNum && frameNum <= fi[1] )
            return true;
    }
    return false;
}

};  // namespace vcd
