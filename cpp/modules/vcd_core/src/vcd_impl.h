#ifndef _VCD_Impl_H_
#define _VCD_Impl_H_

#include <nlohmann/json.hpp>
#include <string>

#include "vcd.h"

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

class VCD_Impl : public vcd::VCD
{
public:
    VCD_Impl(const std::string& fileName, const bool validation = false);
    ~VCD_Impl();

    void
    setUseUUID(const bool val) override { m_useUUID = val; }

    std::string
    stringify(const bool pretty = true) const override;

    void
    save(const std::string& fileName,
         const bool pretty = false) const override;

    uint32_t
    add_object(const std::string& name,
               const std::string& semantic_type) override;

    void
    add_object_data(const uint32_t uid,
                    const types::TypeElement& object_data) override;

private:
    void reset();

    bool m_useUUID;
    json m_data;

    FrameIntervals m_fis;

    std::map<ElementType, int> m_lastUIDbyType;
};

};  // namespace vcd

#endif  // _VCD_Impl_H_
