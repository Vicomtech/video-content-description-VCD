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
#include "vcd_types.h"

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

    static std::string
    generate_uuid4();

    static bool
    check_uuid4(const std::string &uuid);

 private:
    void set(const std::string &uidStr, const int uidInt, const bool isUUID);

    bool m_isUUID;
    std::string m_uidStr;
    int m_uidInt;
};

/**
 * @brief The HoliElems class
 * This class stores all the holistic element uids, to be included in all new
 * frames. The interface includes a set of constant references to the uid
 * lists, in order to directly access the data but not to modify the data.
 * To include new elements, use the proper accesor.
 */
class HoliElems {
 public:
    HoliElems() :
    uids(uids_store) {
        uids_store.resize(ElementType::ET_size);
    }

    bool
    empty() {
        return all_empty;
    }

    void
    addUid(const std::string& uid, const ElementType type) {
        uids_store[type].emplace_back(uid);
        if (all_empty) {
            all_empty = false;
        }
    }

    const std::vector<std::vector<std::string>> &uids;

 private:
    std::vector<std::vector<std::string>> uids_store;
    bool all_empty = true;
};


/**
 * @brief The VCD_Impl class
 * This class includes all the functionalities related to the data structure
 * management.
 */
class VCD_Impl : public vcd::VCD {
 public:
    explicit  VCD_Impl(const std::string& fileName,
                       const bool validation = false);
    ~VCD_Impl();

    // Declare or remove other constructors explicitely
//    VCD_Impl(const VCD_Impl&) = delete;
//    VCD_Impl(const VCD_Impl&&) = delete;

//    VCD_Impl&
//    operator=(VCD_Impl&) = delete;

//    VCD_Impl&
//    operator=(VCD_Impl&&) = delete;

    void
    setUseUUID(const bool val) override;

    std::string
    stringify(const bool pretty = true) const override;

    void
    save(const std::string& fileName,
         const bool pretty = false, const bool validate = false) const override;

    void
    load(const std::string& fileName) override;

    void
    update_vcd_frame_intervals(const size_t frame_index);

    // This version of the interval update adds only consecutive frame ids
    //  in blocks. If between the new frame index and the previous are one or
    // more frames, this function generates a new 'frame_start/frame_end' block.
    void
    update_element_frame_intervals(json &element, const size_t frame_index);

    // This version of the interval update function updates the last frame
    // index of the element to the new frame index parsed as parameter.
    void
    update_element_frame_intervals_no_gap(json &element,
                                          const size_t frame_index);

    json&
    add_frame(const size_t frame_index, const bool addMissedFrames = false);

    void
    includeElemUidToFrame(const ElementType type, const std::string &uid,
                          json& frame) const;

    void
    includeHoliElems(json& frame);

    void
    updateHoliFrameIntervals(const size_t frame_num);

    void
    add_missed_frames(const size_t frame_num);

    // Manage metadata
    void
    add_annotator(const std::string &annotator) override;

    void
    add_comment(const std::string &comment) override;

    void
    add_file_version(const std::string &file_version) override;

    void
    add_name(const std::string &name) override;

    void
    add_metadata_properties(const vcd::meta_props &properties) override;

    // Add object
    std::string
    add_object(const std::string& name,
               const element_args& args) override;

    std::string
    add_object(const std::string& name,
               const size_t frame_index,
               const element_args& args) override;

    // Object data generators
    void
    add_bbox_to_object(const obj_uid& uid,
                       const std::string& name,
                       const std::vector<int>& value,
                       const size_t frame_index = -1) override;

    void
    add_vec_to_object(const obj_uid& uid,
                      const std::string& name,
                      const std::vector<float>& value,
                      const size_t frame_index = -1) override;

    void
    add_num_to_object(const obj_uid& uid,
                      const std::string& name,
                      const double value,
                      const size_t frame_index = -1) override;

    void
    add_bool_to_object(const obj_uid& uid,
                       const std::string& name,
                       const bool value,
                       const size_t frame_index = -1) override;

    void
    add_text_to_object(const obj_uid& uid,
                       const std::string& name,
                       const std::string& text,
                       const size_t frame_index = -1) override;

    void
    add_point2d_to_object(const obj_uid& uid,
                          const std::string& name,
                          const std::vector<double>& point2d,
                          const size_t frame_index = -1) override;

    void
    add_point3d_to_object(const obj_uid& uid,
                          const std::string& name,
                          const std::vector<double>& point3d,
                          const size_t frame_index = -1) override;

    void
    add_poly2d_to_object(const obj_uid& uid,
                         const std::string& name,
                         const std::vector<std::vector<int>> &poly,
                         const Poly2DTypes mode,
                         const bool closed,
                         const size_t frame_index = -1) override;

    void
    add_mat_to_object(const obj_uid& uid,
                      const std::string& name,
                      const std::vector<float>& val,
                      const size_t channels,
                      const size_t width,
                      const size_t height,
                      const size_t frame_index = -1) override;

    // Add object_data
//    void
//    add_object_data(const std::string &uid_str,
//                    const types::ObjectData& object_data);

    void
    add_object_data(const std::string &uid_str,
                    const types::ObjectData& object_data,
                    const size_t frame_index);

    // Add action
    std::string
    add_action(const std::string& name,
               const element_args& args) override;

    std::string
    add_action(const std::string& name,
               const size_t frame_index,
               const element_args& args) override;

    // Action data generators
    void
    add_bbox_to_action(const obj_uid& uid,
                       const std::string& name,
                       const std::vector<int>& value,
                       const size_t frame_index = -1) override;

    void
    add_vec_to_action(const obj_uid& uid,
                      const std::string& name,
                      const std::vector<float>& value,
                      const size_t frame_index = -1) override;

    void
    add_num_to_action(const obj_uid& uid,
                      const std::string& name,
                      const double value,
                      const size_t frame_index = -1) override;

    void
    add_bool_to_action(const obj_uid& uid,
                       const std::string& name,
                       const bool value,
                       const size_t frame_index = -1) override;

    void
    add_text_to_action(const obj_uid& uid,
                       const std::string& name,
                       const std::string& text,
                       const size_t frame_index = -1) override;

    // Add action_data
//    void
//    add_action_data(const std::string &uid_str,
//                    const types::ObjectData& action_data);

    void
    add_action_data(const std::string &uid_str,
                    const types::ObjectData& action_data,
                    const size_t frame_index);

    // Add context
    std::string
    add_context(const std::string& name,
                const element_args& args) override;

    std::string
    add_context(const std::string& name,
                const size_t frame_index,
                const element_args& args) override;

    // Action data generators
    void
    add_bbox_to_context(const obj_uid& uid,
                        const std::string& name,
                        const std::vector<int>& value,
                        const size_t frame_index = -1) override;

    void
    add_vec_to_context(const obj_uid& uid,
                       const std::string& name,
                       const std::vector<float>& value,
                       const size_t frame_index = -1) override;

    void
    add_num_to_context(const obj_uid& uid,
                       const std::string& name,
                       const double value,
                       const size_t frame_index = -1) override;

    void
    add_bool_to_context(const obj_uid& uid,
                        const std::string& name,
                        const bool value,
                        const size_t frame_index = -1) override;

    void
    add_text_to_context(const obj_uid& uid,
                        const std::string& name,
                        const std::string& text,
                        const size_t frame_index = -1) override;

    // Add context_data
//    void
//    add_context_data(const std::string &uid_str,
//                     const types::ObjectData& context_data);

    void
    add_context_data(const std::string &uid_str,
                     const types::ObjectData& context_data,
                     const size_t frame_index);

    // Ontologies
    ont_uid
    add_ontology(const std::string &ontology) override;

    // Coordinate system
    coord_uid
    add_coordinate_system(const std::string& name,
                      const CoordinateSystemType cs_type,
                      const std::string& parent_name = "",
                      const std::vector<float>& pose_wrt_parent = {}) override;

    // Getters
    size_t
    get_num_objects() override;

    inline size_t
    getNoneFrameIndex() {
        return std::numeric_limits<size_t>::max();
    }

    inline bool
    isFrameIndexNone(const size_t frame_index) {
        return (frame_index == std::numeric_limits<size_t>::max());
    }

    inline void
    appendFrameIntervalToArray(json &element_array, const size_t frame_index) {
        element_array.emplace_back(json::object({
                                                   {"frame_start", frame_index},
                                                   {"frame_end", frame_index}
                                                }));
    }

 protected:
    json*
    get_metadata();

    json*
    get_frame(const int frame_num);

    json*
    get_element(const ElementType type, const std::string &uid_str);

    size_t
    get_num_elements(const ElementType type);

    json*
    get_object(const std::string &uid_str);

    json*
    get_action(const std::string &uid_str);

    json*
    get_event(const std::string &uid_str);

    json*
    get_context(const std::string &uid_str);

    json*
    get_relation(const std::string &uid_str);

    UID
    get_uid_to_assign(const ElementType type, const UID &uid);

    void
    set_element_at_root_and_frames(const ElementType type,
                                   const std::string &name,
                                   const std::string &semantic_type,
                                   const size_t frame_index,
                                   const std::string &uid_str,
                                   const ont_uid &ont_uid,
                                   const std::string &coord_system);

    std::string
    set_element(const ElementType type, const std::string &name,
                const std::string &semantic_type,
                const size_t frame_index,
                const UID &uid, const ont_uid &ont_uid,
                const std::string &coordinate_system = nullptr,
                const SetMode set_mode = union_t);

    void
    set_element_data(const ElementType type, const std::string &uid_str,
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
    has(const ElementType type, const std::string &uid_str) const;

    bool
    hasOntology(const std::string &ont_uid_str) const;

    bool
    hasCoordSys(const std::string &coord_system) const;

    bool
    has_element_data(const ElementType type, const std::string &uid_str,
                     const types::ObjectData &element_data) const;

    inline bool
    isFrameWithIndex(const size_t frame_index) {
        const std::string frame_index_str = std::to_string(frame_index);
        return m_data["openlabel"]["frames"].contains(frame_index_str);
    }

    static size_t
    findElementByName(const json &elementList, const std::string &name);

 private:
    // Rest of private functions
    void reset();

    bool m_useUUID;
    json m_data;

    size_t m_curFrameIndex = 0;

    // Check the used uid numbers for each type
    std::vector<int> m_lastUIDbyType;

    // Objects to be considered in every frame
    HoliElems m_holiElemes;
};

};  // namespace vcd

#endif  // _VCD_Impl_H_
