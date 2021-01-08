#ifndef _VCD_H_
#define _VCD_H_

#include "core_exp.h"
#include <nlohmann/json.hpp>
#include <string>

using json = nlohmann::json;

namespace vcd
{
    typedef std::array<int, 2> Tuple;
    typedef std::vector<Tuple> ArrayNx2; 

    enum ElementType 
    {
        object = 1,
        action = 2,
        event = 3,
        context = 4,
        relation = 5
    };

    enum StreamType 
    {
        camera = 1,
        lidar = 2,
        radar = 3,
        gps_imu = 4,
        other = 5
    };

    enum RDF 
    {
        rdf_subject = 1,
        rdf_object = 2
    };

    /**
     * FrameIntervals
     * Can be initialized with int, Tuple and ArrayNx2
     * FrameIntervals fis = FrameIntervals(0);  // works
     * FrameIntervals fis = FrameIntervals({0, 10}); // works
     * FrameIntervals fis = FrameIntervals({{0, 10}}); // works
     */
    class FrameIntervals 
    {
        public:
            FrameIntervals() {}
            FrameIntervals(int frameValue);       
            FrameIntervals(const Tuple& frameValue);
            FrameIntervals(const ArrayNx2& frameValue);            

            bool empty() const { return this->fisNum.empty() || this->fisDict.empty(); }
            json get_dict() const { return fisDict; }
            ArrayNx2 get() const { return fisNum; }

            std::size_t getLength() const { return fisNum.size(); }
            bool hasFrame(int frameNum) const;

        private:
            json fisDict;
            ArrayNx2 fisNum;
    };

    class UID 
    {
        public:
            UID() { this->set("", -1, false); }
            UID(int val);
            UID(std::string val);

            bool isUUID() const { return is_UUID; }
            std::string asStr() const { return uidStr; }
            int asInt() const { return uidInt; }

            bool isNone() const { return (uidInt == -1 && uidStr == ""); }

        private:
            void set(std::string uidStr, int uidInt, bool isUUID);

            bool is_UUID;
            std::string uidStr;
            int uidInt;
    };

    class VCD 
    {
        public:            
            CORE_LIB VCD(std::string fileName=std::string(), bool validation=false);
            CORE_LIB ~VCD();

            void CORE_LIB setUseUUID(bool val) { useUUID = val; }

            std::string CORE_LIB stringify(bool pretty=true) const;
            void CORE_LIB save(std::string fileName, bool pretty=false) const;

        private:
            void reset();

            bool useUUID;
            json data;

            FrameIntervals fis;

            std::map<ElementType, int> lastUID;
    };
};

#endif // _VCD_H_