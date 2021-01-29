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
#ifndef _VCD_Impl_H_
#define _VCD_Impl_H_

#include <nlohmann/json.hpp>
#include <string>

#include "vcd.h"

using json = nlohmann::json;

namespace vcd {

typedef std::array<int, 2> Tuple;
typedef std::vector<Tuple> ArrayNx2;

enum ElementType {
    object = 0,
    action = 1,
    event = 2,
    context = 3,
    relation = 4,
    ET_size
};

enum StreamType {
    camera = 1,
    lidar = 2,
    radar = 3,
    gps_imu = 4,
    other = 5
};

enum SetMode {
    union_t = 1,
    replace_t = 2
};

enum RDF {
    rdf_subject = 1,
    rdf_object = 2
};

class CoordSys;

/**
 * FrameIntervals
 * Can be initialized with int, Tuple and ArrayNx2
 * FrameIntervals fis = FrameIntervals(0);  // works
 * FrameIntervals fis = FrameIntervals({0, 10}); // works
 * FrameIntervals fis = FrameIntervals({{0, 10}}); // works
 */
class FrameIntervals {
 public:
    FrameIntervals() {}
    explicit FrameIntervals(int frameValue);
    explicit FrameIntervals(const Tuple& frameValue);
    explicit FrameIntervals(const ArrayNx2& frameValue);

    bool empty() const { return this->fisNum.empty() || this->fisDict.empty(); }
    json get_dict() const { return fisDict; }
    ArrayNx2 get() const { return fisNum; }

    std::size_t getLength() const { return fisNum.size(); }
    bool hasFrame(int frameNum) const;

 private:
    json fisDict;
    ArrayNx2 fisNum;
};

class UID : public VCD_UID {
 public:
    UID() { this->set("", -1, false); }
    explicit UID(const int val);
    explicit UID(const std::string &val);

    bool
    isUUID() const override { return m_isUUID; }

    std::string
    asStr() const override { return m_uidStr; }

    int
    asInt() const override { return m_uidInt; }

    bool
    isNone() const override { return (m_uidInt == -1 && m_uidStr == ""); }

    void
    withInt(const int val);

    void
    withStr(const std::string &val);

 private:
    void set(const std::string &uidStr, const int uidInt, const bool isUUID);

    bool m_isUUID;
    std::string m_uidStr;
    int m_uidInt;
};

class VCD_Impl : public vcd::VCD {
 public:
    explicit  VCD_Impl(const std::string& fileName,
                       const bool validation = false);
    ~VCD_Impl();

    void
    setUseUUID(const bool val) override { m_useUUID = val; }

    std::string
    stringify(const bool pretty = true) const override;

    void
    save(const std::string& fileName,
         const bool pretty = false) const override;

    VCD_UID
    add_object(const std::string& name,
               const std::string& semantic_type) override;

    void
    add_object_data(const uint32_t uid,
                    const types::ObjectData& object_data) override;

 protected:
    UID
    get_uid_to_assign(const ElementType type, const UID &uid);

    void
    set_element_at_root_and_frames(const ElementType type,
                                   const std::string &name,
                                   const std::string &semantic_type,
                                   const FrameIntervals &frame_intervals,
                                   const UID &uid, const UID &ont_uid,
                                   const CoordSys * const coord_system);

    UID
    set_element(const ElementType type, const std::string &name,
                const std::string &semantic_type,
                const FrameIntervals &frame_intervals,
                const UID &uid, const UID &ont_uid,
                const CoordSys * const coordinate_system = nullptr,
                const SetMode set_mode = union_t);

 private:
    void reset();

    bool m_useUUID;
    json m_data;

    FrameIntervals m_fis;

    std::vector<int> m_lastUIDbyType;
};

};  // namespace vcd

#endif  // _VCD_Impl_H_
