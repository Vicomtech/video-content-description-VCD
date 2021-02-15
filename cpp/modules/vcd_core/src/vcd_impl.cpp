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
#include <fstream>
#include <regex>
#include "vcd_impl.h"

#include <openssl/rand.h>
#include <iostream>

#include "vcd_types.h"

using std::string;

using vcd::types::ObjectDataTypeName;

namespace vcd {

/** @brief Generate a Version 4 UUID according to RFC-4122
 *
 * Uses the openssl RAND_bytes function to generate a
 * Version 4 UUID.
 *
 * @param buffer A buffer that is at least 38 bytes long.
 * @retval 1 on success, 0 otherwise.
 */
std::string
uuid_v4_gen() {
    union {
        struct {
            uint32_t time_low;
            uint16_t time_mid;
            uint16_t time_hi_and_version;
            uint8_t  clk_seq_hi_res;
            uint8_t  clk_seq_low;
            uint8_t  node[6];
        };
        uint8_t __rnd[16];
    } uuid;

//    int rc = RAND_bytes(uuid.__rnd, sizeof(uuid));

    // Refer Section 4.2 of RFC-4122
    // https://tools.ietf.org/html/rfc4122#section-4.2
    const auto cshr = (uuid.clk_seq_hi_res & 0x3F) | 0x80;
    uuid.clk_seq_hi_res = static_cast<uint8_t>(cshr);
    const auto thav = (uuid.time_hi_and_version & 0x0FFF) | 0x4000;
    uuid.time_hi_and_version = static_cast<uint16_t>(thav);

    char uuidv4[38];
    snprintf(uuidv4, 38, "%08x-%04x-%04x-%02x%02x-%02x%02x%02x%02x%02x%02x",
            uuid.time_low, uuid.time_mid, uuid.time_hi_and_version,
            uuid.clk_seq_hi_res, uuid.clk_seq_low,
            uuid.node[0], uuid.node[1], uuid.node[2],
            uuid.node[3], uuid.node[4], uuid.node[5]);

    return std::string(uuidv4);
}

///////////////////////////////////////////////
// VCD_Impl
///////////////////////////////////////////////
VCD_Impl::VCD_Impl(const std::string& fileName, const bool validation) :
    m_useUUID(false) {
    // Init last uid contanier
    m_lastUIDbyType.resize(ET_size, 0);

    // Init
    if (!fileName.empty()) {
        // Load from file
        std::ifstream file(fileName);
        file >> m_data;
        file.close();
    } else {
        reset();
    }
}

VCD_Impl::~VCD_Impl() {
}

void
VCD_Impl::reset() {
    m_data["vcd"] = json::object();  // = json::object();
    m_data["vcd"]["metadata"] = json::object();
    m_data["vcd"]["metadata"]["schema_version"] = "4.3.0";

    m_lastUIDbyType[ElementType::object] = -1;
    m_lastUIDbyType[ElementType::action] = -1;
    m_lastUIDbyType[ElementType::event] = -1;
    m_lastUIDbyType[ElementType::context] = -1;
    m_lastUIDbyType[ElementType::relation] = -1;

    // this->fis = FrameIntervals(0);  // works
    // this->fis = FrameIntervals({0, 10});  // works
    // this->fis = FrameIntervals({{0, 10}});  // works
    // data["vcd"]["frame_intervals"] = this->fis.get_dict();
}

std::string
VCD_Impl::stringify(const bool pretty) const {
    std::string str;
    if (pretty)
        str = m_data.dump(4);
    else
        str = m_data.dump();
    return str;
}

void
VCD_Impl::save(const std::string& fileName, const bool pretty,
               const bool validate) const {
    std::string json_string = this->stringify(pretty);
    std::ofstream f(fileName);
    f << json_string;
    f.close();
}

void
VCD_Impl::load(const std::string& fileName) {
    std::ifstream i(fileName);
    m_data.clear();
    i >> m_data;
    i.close();
}

std::string
VCD_Impl::add_object(const std::string& name,
                     const std::string& semantic_type) {
    //    m_data[name] = { {"currency", "USD"}, {"value", 42.99} };
    int frame_value = 0;
    std::string uid = "";
    std::string ont_uid = "";
    std::string coordinate_system;
    FrameIntervals fi(frame_value);
    SetMode set_mode = SetMode::union_t;
    return set_element(ElementType::object, name, semantic_type,
                       &fi, UID(uid), UID(ont_uid),
                       coordinate_system, set_mode).asStr();
}

void
VCD_Impl::add_object_data(const std::string &uid,
                          const types::ObjectData& object_data) {
    return set_element_data(ElementType::object, UID(uid), object_data,
                            nullptr, SetMode::union_t);
}

UID
VCD_Impl::get_uid_to_assign(const ElementType type, const UID &uid) {
    UID uid_to_assign;
    if (uid.isNone()) {
        if (m_useUUID) {
            uid_to_assign.withStr(uuid_v4_gen());
        } else {
            // Let's use integers
            ++m_lastUIDbyType[type];
            uid_to_assign.withInt(m_lastUIDbyType[type]);
        }
    } else {
        // uid is not None
        if (!uid.isUUID()) {
            // Ok, user provided a number, let's proceed
            if (uid.asInt() > m_lastUIDbyType[type]) {
                m_lastUIDbyType[type] = uid.asInt();
                uid_to_assign.withInt(m_lastUIDbyType[type]);
            } else {
                uid_to_assign = uid;
            }
        } else {
            // This is a UUID
            m_useUUID = true;
            uid_to_assign = uid;
        }
    }
    return uid_to_assign;
}

json*
VCD_Impl::get_element(const ElementType type, const UID &uid) {
    const std::string key = ElementTypeName[type] + "s";
    if (!m_data["vcd"].contains(key)) {
        std::cerr << "WARNING: trying to get a "
                  << ElementTypeName[type] << " but this VCD has none."
                  << std::endl;
        return nullptr;
    }
    const std::string uid_str = uid.asStr();
    if (m_data["vcd"][key].contains(uid_str)) {
        return &(m_data["vcd"][key][uid_str]);
    } else {
        std::cerr << "WARNING: trying to get non-existing "
                  << ElementTypeName[type]
                     << " with uid: " << uid_str << std::endl;
        return nullptr;
    }
}

json*
VCD_Impl::get_object(const UID &uid) {
        return get_element(ElementType::object, uid);
}

json*
VCD_Impl::get_action(const UID &uid) {
        return get_element(ElementType::action, uid);
}

json*
VCD_Impl::get_event(const UID &uid) {
        return get_element(ElementType::event, uid);
}

json*
VCD_Impl::get_context(const UID &uid) {
        return get_element(ElementType::context, uid);
}

json*
VCD_Impl::get_relation(const UID &uid) {
        return get_element(ElementType::relation, uid);
}

template <class T>
json&
VCD_Impl::setDefault(json &data, const std::string &key, T &&value) {
    if (!data.contains(key)) {
        data[key] = value;
    }
    // Return the element structure
    return data[key];
}

void
VCD_Impl::set_element_at_root_and_frames(const ElementType type,
                                         const std::string &name,
                                         const std::string &semantic_type,
                                   const FrameIntervals * const frame_intervals,
                                         const UID &uid, const UID &ont_uid,
                                         const std::string &coord_system) {
    // 1.- Copy from existing or create new entry (this copies everything,
    //     including element_data) element_data_pointers and frame intervals.
    auto uidstr = uid.asStr();
    // note: public functions use int or str for uids
//    auto element_existed = self.has(element_type, uidstr)
    const std::string elemKey = ElementTypeName[type] + "s";
    VCD_Impl::setDefault(m_data["vcd"], elemKey, json::object());
    auto& element = VCD_Impl::setDefault(m_data["vcd"][elemKey], uidstr,
                                         json::object());

//    fis_old = FrameIntervals()
//    if 'frame_intervals' in element:
//        fis_old = FrameIntervals(element['frame_intervals'])

    // 2.- Copy from arguments
    if (!name.empty()) {
        element["name"] = name;
    }
    if (!semantic_type.empty()) {
        element["type"] = semantic_type;
    }
//  if not frame_intervals.empty() or (element_existed and not fis_old.empty()):
//        # So, either the newFis has something, or the fisOld had something
//        # (in which case needs to be substituted)
//        # Under the previous control, no 'frame_intervals' field is added to
//        # newly created static elements
//        # -> should 'frame_intervals' be mandatory
//        element['frame_intervals'] = frame_intervals.get_dict()
    if (!ont_uid.isNone() && hasOntology(ont_uid.asStr())) {
        element["ontology_uid"] = ont_uid.asStr();
    }
//    if (coord_system != nullptr && hasCoordSys(coord_system)) {
//        element["coordinate_system"] = *coord_system;
//    }

    // 2.bis.- For Relations obligue to have rdf_objects and rdf_subjects
    //         entries (to be compliant with schema)
    if (type == ElementType::relation) {
        if (!element.contains("rdf_subjects")) {
            element["rdf_subjects"] = json::array();
        }
        if (!element.contains("rdf_objects")) {
            element["rdf_objects"] = json::array();
        }
    }

//    // 3.- Reshape element_data_pointers according to this new frame intervals
//    if element_type.name + '_data_pointers' in element:
//        edps = element[element_type.name + '_data_pointers']
//        for edp_name in edps:
//            # NOW, we have to UPDATE frame intervals of pointers because we
//            # have modified the frame_intervals
//            # of the element itself, adn
//            # If we compute the intersection frame_intervals, we can copy that
//            # into element_data_pointers frame intervals
//            fis_int = FrameIntervals()
//            if not frame_intervals.empty():
//                fis_int = frame_intervals.intersection(
//                            FrameIntervals(edps[edp_name]['frame_intervals']))

//            # Update the pointers
//            element.setdefault(element_type.name + '_data_pointers', {})
//            element[element_type.name + '_data_pointers'][edp_name] =
//                                                            edps[edp_name]
//            element[element_type.name + '_data_pointers'][edp_name]
//                                ['frame_intervals'] = fis_int.get_dict()

    // 4.- Now set at frames
//    if not frame_intervals.empty():
//        # 2.1.- There is frame_intervals specified
//        if not element_existed:
//            # 2.1.a) Just create the new element
//            self.__add_frames(frame_intervals, element_type, uid)
//            self.__update_vcd_frame_intervals(frame_intervals)
//        else:
//            # 2.1.b) This is a substitution: depending on the new
//            # frame_intervals, we may need to delete/add frames
//            # Add
//            fis_new = frame_intervals
//            for fi in fis_new.get():
//                for f in range(fi[0], fi[1] + 1):
//                    is_inside = fis_old.has_frame(f)
//                    if not is_inside:
//                        # New frame is not inside -> let's add this frame
//                        fi_ = FrameIntervals(f)
//                        self.__add_frames(fi_, element_type, uid)
//                        self.__update_vcd_frame_intervals(fi_)
//            # Remove
//            if element_existed and fis_old.empty():
//                # Ok, the element was originally static (thus with fisOld
//                # empty)
//                # so potentially there are pointers of the element in all
//                # frames (in case there are frames)
//                # Now the element is declared with a specific frame intervals.
//                # Then we first need to remove all
//                # element entries (pointers) in all OTHER frames
//                vcd_frame_intervals = self.get_frame_intervals()
//                if not vcd_frame_intervals.empty():
//                    for fi in vcd_frame_intervals.get():
//                        for f in range(fi[0], fi[1] + 1):
//                            # Only for those OTHER frames not those just added
//                            if not fis_new.has_frame(f):
//                                elements_in_frame =
//                       self.data['vcd']['frames'][f][element_type.name + 's']
//                                if uidstr in elements_in_frame:
//                                    del elements_in_frame[uidstr]
//                                    if len(elements_in_frame) == 0:
//       del self.data['vcd']['frames'][f][element_type.name + 's']
//                               if len(self.data['vcd']['frames'][f]) == 0:
//                                            self.__rm_frame(f)

//            # Next loop for is for the case fis_old wasn't empty, so we
//    just need to remove old content
//            for fi in fis_old.get():
//                for f in range(fi[0], fi[1] + 1):
//                    is_inside = fis_new.has_frame(f)
//                    if not is_inside:
//                        # Old frame not inside new ones -> let's remove this
//    frame
//                        elements_in_frame = self.data['vcd']['frames']
//    [f][element_type.name + 's']
//                        del elements_in_frame[uidstr]
//                        if len(elements_in_frame) == 0:
//                            del self.data['vcd']['frames'][f]
//    [element_type.name + 's']
//                            if len(self.data['vcd']['frames'][f]) == 0:
//                                self.__rm_frame(f)
//    else:
    // No frame interval is taken into account
    // 2.2.- The element is declared as static
//    if (type != ElementType::relation) {
        // frame-less relation must remain frame-less
//        vcd_frame_intervals = self.get_frame_intervals()
//        if not vcd_frame_intervals.empty():
//            // ... but VCD has already other elements or info that have
//            // established some frame intervals.
//            // The element is then assumed to exist in all frames: let's
//            // add a pointer into all frames.
//            self.__add_frames(vcd_frame_intervals, element_type, uid)

    // But, if the element existed previously, and it was dynamic, there is
    // already information inside frames.
    // If there is element_data at frames, they are removed
//    if not fis_old.empty():
//        self.rm_element_data_from_frames(element_type, uid, fis_old)

//        # Additionally, we need to remove element entries at frames, and
//        frames entirely to clean-up
//        for fi in fis_old.get():
//            for f in range(fi[0], fi[1] + 1):
//                elements_in_frame = self.data['vcd']['frames'][f]
//        [element_type.name + 's']
//                del elements_in_frame[uidstr]
//                # Clean-up
//                if len(elements_in_frame) == 0:
//                    del self.data['vcd']['frames'][f][element_type.name + 's']
//                    if len(self.data['vcd']['frames'][f]) == 0:
//                        self.__rm_frame(f)
}

UID
VCD_Impl::set_element(const ElementType type, const std::string &name,
                      const std::string &semantic_type,
                      const FrameIntervals * const frame_intervals,
                      const UID &uid, const UID &ont_uid,
                      const std::string &coordinate_system,
                      const SetMode set_mode) {
//        fis = frame_intervals
//        if set_mode == SetMode.union:
//            # Union means fusion, we are calling this function to "add"
//            # content, not to remove any
//            fis_existing = self.get_element_frame_intervals(element_type,
//                                                            uid.as_str())
//            fis = fis_existing.union(frame_intervals)

    // 0.- Get uid_to_assign
    // note: private functions use UID type for uids
    UID uid_to_assign = get_uid_to_assign(type, uid);

    // 1.- Set the root entries and frames entries
    set_element_at_root_and_frames(type, name, semantic_type, frame_intervals,
                                   uid_to_assign, ont_uid, coordinate_system);

    return uid_to_assign;
}

void
VCD_Impl::set_element_data(const ElementType type, const UID &uid,
                           const types::ObjectData &element_data,
                           const FrameIntervals * const frame_intervals,
                           const SetMode set_mode) {
    // 0.- Checks
    if (!has(type, uid)) {
        std::cerr << "WARNING: "
                     "Trying to set element_data for a non-existing element."
                  << std::endl;
        return;
    }
    auto* element_ptr = get_element(type, uid);
    if (element_ptr == nullptr) {
        std::cerr << "WARNING: "
                     "Error when trying to get element instance."
                  << std::endl;
        return;
    }
    auto& element = *element_ptr;

    // Read existing data about this element, so we can call __set_element
    const std::string& name = element["name"];
    const std::string& semantic_type = element["type"];
    UID ont_uid("");
    std::string cs;
    if (element.contains("ontology_uid")) {
        ont_uid = UID(element["ontology_uid"].get<std::string>());
    }
    if (element.contains("coordinate_system")) {
        cs = element["coordinate_system"];
    }

    const auto data = element_data.getData();
    if (data.contains("coordinate_system")) {
        if (!hasCoordSys(data["coordinate_system"])) {
            std::cerr << "WARNING: Trying to set element_data with a "
                         "non-declared coordinate system." << std::endl;
            return;
        }
    }

    // set_mode = SetMode.union
    // This is a static element_data. If it was declared dynamic before,
    // let's remove it.
    // self.__set_element(element_type, name, semantic_type, frame_intervals,
    //                    uid, ont_uid, cs, set_mode)
    // Add or replace (if already exists) element
    set_element_data_content(type, element, element_data);
    // Set the pointers
    set_element_data_pointers(type, uid, element_data, frame_intervals);
//    set_element(type, name, semantic_type, frame_intervals,
//                uid, ont_uid, cs, set_mode);
}

size_t
VCD_Impl::findElementByName(const json &elementList, const std::string &name) {
    size_t elem_pos = elementList.size();

    size_t cont = 0;
    bool has_elem = false;
    for (const auto& e : elementList) {
        has_elem = e["name"] == name;
        if (has_elem) {
            elem_pos = cont;
            break;
        }
        ++cont;
    }

    return elem_pos;
}

void
VCD_Impl::set_element_data_content(const ElementType type,
                                   json &element,
                                   const types::ObjectData &element_data) {
    // Adds the element_data to the corresponding container
    // If an element_data with same name exists, it is substituted
    const std::string data_key = ElementTypeName[type] + "_data";
    const std::string e_type_key = ObjectDataTypeName[element_data.getType()];
    VCD_Impl::setDefault(element, data_key, json::object());
    VCD_Impl::setDefault(element[data_key], e_type_key, json::array());
    // Find if element_data already there
    auto& list_aux = element[data_key][e_type_key];
    const size_t elem_pos = findElementByName(list_aux, element_data.getName());
    const bool has_elem = (elem_pos < list_aux.size());
    if (!has_elem) {
        // Not found, then just push this new element data
        element[data_key][e_type_key].emplace_back(element_data.getData());
    } else {
        // Found: let's replace
        element[data_key][e_type_key][elem_pos] = element_data.getData();
    }
}

void
VCD_Impl::set_element_data_pointers(const ElementType type, const UID &uid,
                                    const types::ObjectData &element_data,
                                    const FrameIntervals * const f_intervals) {
    const std::string type_key = ElementTypeName[type] + "s";
    const std::string data_point_key = ElementTypeName[type] + "_data_pointers";
    const std::string s_uid = uid.asStr();

    auto& element = m_data["vcd"][type_key][s_uid];
    auto& edp = VCD_Impl::setDefault(element, data_point_key, json::object());

    const std::string data_name = element_data.getName();
    edp[data_name] = json::object();
    edp[data_name]["type"] = ObjectDataTypeName[element_data.getType()];

    if (f_intervals == nullptr) {
        edp[data_name]["frame_intervals"] = json::array();
    } else {
        edp[data_name]["frame_intervals"] = f_intervals->get_dict();
    }

//    const auto& e_data_data = element_data.getData();
//    if (e_data_data.contains("attributes")) {
//        edp[element_data.getName()]["attributes"] = json::object();
//        // attr_type might be 'boolean', 'text', 'num', or 'vec'
//        for attr_type in element_data.data["attributes"]:
//            for attr in element_data.data['attributes'][attr_type]:
//       edp[element_data.data['name']]['attributes'][attr['name']] = attr_type
//    }
}

bool
VCD_Impl::has(const ElementType type, const UID &uid) const {
    const std::string key = ElementTypeName[type] + "s";
    if (!m_data["vcd"].contains(key)) {
        return false;
    } else {
        const std::string uid_str = uid.asStr();
        if (m_data["vcd"][key].contains(uid_str)) {
            return true;
        } else {
            return false;
        }
    }
}

bool
VCD_Impl::hasOntology(const std::string &ont_uid_str) const {
    if (m_data["vcd"].contains("ontologies")) {
        if (m_data["vcd"]["ontologies"].contains(ont_uid_str)) {
            return m_data["vcd"]["ontologies"][ont_uid_str].empty();
        }
    }
    return false;
}

bool
VCD_Impl::hasCoordSys(const std::string &coord_system) const {
    if (m_data["vcd"].contains("coordinate_systems")) {
        if (m_data["vcd"]["coordinate_systems"].contains(coord_system)) {
            return true;
        }
    }
    return false;
}

bool
VCD_Impl::has_element_data(const ElementType type, const UID &uid,
                           const types::ObjectData &element_data) const {
    if (!has(type, uid)) {
        return false;
    } else {
        const std::string uid_str = uid.asStr();
        const std::string key = ElementTypeName[type] + "s";
        const std::string data_key = ElementTypeName[type] + "_data_pointers";
        if (!m_data["vcd"][key][uid_str].contains(data_key)) {
            return false;
        }
        const std::string &name = element_data.getName();
        return m_data["vcd"][key][uid_str][data_key].contains(name);
    }
}


///////////////////////////////////////////////
// UID
///////////////////////////////////////////////
UID::UID(const int val) {
    withInt(val);
}

UID::UID(const std::string &val) {
    withStr(val);
}

void
UID::withInt(const int val) {
    set(std::to_string(val), val, false);
}

void
UID::withStr(const std::string &val) {
    const std::regex pattern(
                    "[0-9a-fA-F]{8}-"
                    "[0-9a-fA-F]{4}-"
                    "[0-9a-fA-F]{4}-"
                    "[0-9a-fA-F]{4}-"
                    "[0-9a-fA-F]{12}");
    if (val.empty()) {
        this->set("", -1, false);
    } else {
        const bool is_int = val.find_first_not_of("0123456789") == string::npos;
        if (is_int) {
            this->set(val, std::stoi(val), false);
        } else {
            // e.g. 3d4705a6-6a54-4c5c-9f33-bbb21cc5d576
            bool matches_regex = std::regex_match(val, pattern);
            if (matches_regex) {
                this->set(val, -1, true);
            } else {
                throw std::runtime_error(
                            "ERROR: UID string is not integer not UUID.");
            }
        }
    }
}

void UID::set(const std::string &uidStr, const int uidInt, const bool isUUID) {
    m_uidStr = uidStr;
    m_uidInt = uidInt;
    m_isUUID = isUUID;
}

///////////////////////////////////////////////
// FrameIntervals
///////////////////////////////////////////////
FrameIntervals::FrameIntervals(int frameValue) {
    if (frameValue == -1) {
        this->fisDict = nullptr;
    } else {
        this->fisDict = json::array();
        this->fisDict.push_back({
                                    {"frame_start", frameValue},
                                    {"frame_end", frameValue}
                                });
        this->fisNum = {{frameValue, frameValue}};
    }
}

FrameIntervals::FrameIntervals(const Tuple& frameValue) {
    this->fisDict = json::array();
    this->fisDict.push_back({
                                {"frame_start", frameValue[0]},
                                {"frame_end", frameValue[1]}
                            });
    this->fisNum = {frameValue};
}

FrameIntervals::FrameIntervals(const ArrayNx2& frameValue) {
    this->fisDict = json::array();
    for (auto it : frameValue)
        this->fisDict.push_back({{"frame_start", it[0]}, {"frame_end", it[1]}});
    this->fisNum = frameValue;
}

bool FrameIntervals::hasFrame(int frameNum) const {
    for (auto fi : this->fisNum) {
        if (fi[0] <= frameNum && frameNum <= fi[1])
            return true;
    }
    return false;
}

};  // namespace vcd
