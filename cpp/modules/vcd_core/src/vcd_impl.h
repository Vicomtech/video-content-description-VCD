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

const std::string
ElementTypeName[] {
    "object",
    "action",
    "event",
    "context",
    "relation"
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
    explicit FrameIntervals(const json& frame_dict);

    bool empty() const { return this->fisNum.empty() || this->fisDict.empty(); }
    json get_dict() const { return fisDict; }
    ArrayNx2 get() const { return fisNum; }

    std::size_t getLength() const { return fisNum.size(); }
    bool hasFrame(int frameNum) const;

    static std::unique_ptr<FrameIntervals>
    create(const FrameValue * const frameValue);

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
         const bool pretty = false, const bool validate = false) const override;

    void
    load(const std::string& fileName) override;

    void
    update_vcd_frame_intervals(const size_t frame_index);

    void
    update_element_frame_intervals(json &element, const size_t frame_index);

    json&
    add_frame(const size_t frame_index, const bool addMissedFrames = false);

    std::string
    add_object(const std::string& name,
               const std::string& semantic_type) override;

    std::string
    add_object(const std::string& name,
               const std::string& semantic_type,
               const size_t frame_index) override;

    void
    add_object_data(const std::string &uid,
                    const types::ObjectData& object_data) override;

    void
    add_object_data(const std::string &uid,
                    const types::ObjectData& object_data,
                    const size_t frame_index) override;

    inline size_t
    getNoneFrameIndex() {
        return std::numeric_limits<size_t>::max();
    }

    inline bool
    isFrameIndexNone(const size_t frame_index) {
        return (frame_index != std::numeric_limits<size_t>::max());
    }

    inline void
    appendFrameIntervalToArray(json element_array, const size_t frame_index) {
        element_array.emplace_back(json::object({
                                                   {"frame_start", frame_index},
                                                   {"frame_end", frame_index}
                                                }));
    }

 protected:
    json*
    get_frame(const int frame_num);

    json*
    get_element(const ElementType type, const UID &uid);

    json*
    get_object(const UID &uid);

    json*
    get_action(const UID &uid);

    json*
    get_event(const UID &uid);

    json*
    get_context(const UID &uid);

    json*
    get_relation(const UID &uid);

    UID
    get_uid_to_assign(const ElementType type, const UID &uid);

    void
    set_element_at_root_and_frames(const ElementType type,
                                   const std::string &name,
                                   const std::string &semantic_type,
                                   const size_t frame_index,
                                   const UID &uid, const UID &ont_uid,
                                   const std::string &coord_system);

    UID
    set_element(const ElementType type, const std::string &name,
                const std::string &semantic_type,
                const size_t frame_index,
                const UID &uid, const UID &ont_uid,
                const std::string &coordinate_system = nullptr,
                const SetMode set_mode = union_t);

    void
    set_element_data(const ElementType type, const UID &uid,
                     const types::ObjectData &element_data,
                     const size_t frame_index,
                     const SetMode set_mode = union_t);

    void
    set_element_data_content(const ElementType type, json &element,
                             const types::ObjectData &element_data);

    void
    set_element_data_pointers(const ElementType type, json &element,
                            const types::ObjectData &element_data,
                            const size_t frame_index);
    /**
     * @brief setdefault Simulates the behaviour of setdefault funcion in
     * python. In python, the setdefault() method returns the value of the
     * item with the specified key. If the key does not exist, inserts the key,
     * with the specified value.
     * @param data The json data structure to manipulate.
     * @param key The key to evaluate.
     * @param value The value to store in the case the key does not exists.
     * @return The reference to the key element.
     */
    template <class T>
    static json&
    setDefault(json &data, const std::string &key, T &&value);

    bool
    has(const ElementType type, const UID &uid) const;

    bool
    hasOntology(const std::string &ont_uid_str) const;

    bool
    hasCoordSys(const std::string &coord_system) const;

    bool
    has_element_data(const ElementType type, const UID &uid,
                     const types::ObjectData &element_data) const;

    inline bool
    isFrameWithIndex(const size_t frame_index) {
        const std::string frame_index_str = std::to_string(frame_index);
        return m_data["vcd"]["frames"].contains(frame_index_str);
    }

    static size_t
    findElementByName(const json &elementList, const std::string &name);

 private:
    void reset();

    bool m_useUUID;
    json m_data;

    FrameIntervals m_fis;

    std::vector<int> m_lastUIDbyType;
};

};  // namespace vcd

#endif  // _VCD_Impl_H_
