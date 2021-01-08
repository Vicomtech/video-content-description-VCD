#include <fstream>
#include <regex>
#include "vcd.h"

///////////////////////////////////////////////
// VCD
///////////////////////////////////////////////
vcd::VCD::VCD(std::string fileName, bool validation):
    useUUID(false) 
{    
        if(!fileName.empty())
    {
        // Load from file
        std::ifstream file(fileName);                
        file >> this->data;
        file.close();
    }
    else
    {
        this->reset();
    }
    
}
vcd::VCD::~VCD() 
{
}
void vcd::VCD::reset() 
{    
    data["vcd"] = json::object();  // = json::object();
    data["vcd"]["metadata"] = json::object();
    data["vcd"]["metadata"]["schema_version"] = "4.3.0";

    lastUID[ElementType::object] = -1;
    lastUID[ElementType::action] = -1;
    lastUID[ElementType::event] = -1;
    lastUID[ElementType::context] = -1;
    lastUID[ElementType::relation] = -1;

    //this->fis = FrameIntervals(0);  // works
    //this->fis = FrameIntervals({0, 10}); // works
    // this->fis = FrameIntervals({{0, 10}}); // works
    //data["vcd"]["frame_intervals"] = this->fis.get_dict();
}
std::string vcd::VCD::stringify(bool pretty) const
{
    if(pretty)
        return this->data.dump(4);
    else
        return this->data.dump();        
}
void vcd::VCD::save(std::string fileName, bool pretty) const 
{
    std::string json_string = this->stringify(pretty);
    std::ofstream f(fileName);
    f << json_string;
    f.close();
}

///////////////////////////////////////////////
// UID
///////////////////////////////////////////////
vcd::UID::UID(int val)
{
    this->set(std::to_string(val), val, false);
}
vcd::UID::UID(std::string val)
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
void vcd::UID::set(std::string uidStr, int uidInt, bool isUUID)
{
    this->uidStr = uidStr;
    this->uidInt = uidInt;
    this->is_UUID = isUUID;
}

///////////////////////////////////////////////
// FrameIntervals
///////////////////////////////////////////////
vcd::FrameIntervals::FrameIntervals(int frameValue) 
{
    this->fisDict = json::array();
    this->fisDict.push_back({{"frame_start", frameValue}, {"frame_end", frameValue}});
    this->fisNum = {{frameValue, frameValue}};
}
vcd::FrameIntervals::FrameIntervals(const Tuple& frameValue) 
{
    this->fisDict = json::array();
    this->fisDict.push_back({{"frame_start", frameValue[0]}, {"frame_end", frameValue[1]}});
    this->fisNum = {frameValue};
}
vcd::FrameIntervals::FrameIntervals(const ArrayNx2& frameValue) 
{
    this->fisDict = json::array();
    for(auto it : frameValue)
        this->fisDict.push_back({{"frame_start", it[0]}, {"frame_end", it[1]}});
    this->fisNum = frameValue;
}
bool vcd::FrameIntervals::hasFrame(int frameNum) const
{
    for(auto fi : this->fisNum)
    {
        if( fi[0] <= frameNum && frameNum <= fi[1] )
            return true;
    }
    return false;
}