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

static const bool S_ADD_MISSIED_FRAMES = false;

namespace vcd {

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

    m_lastUIDbyType[ElementType::object]   = -1;
    m_lastUIDbyType[ElementType::action]   = -1;
    m_lastUIDbyType[ElementType::event]    = -1;
    m_lastUIDbyType[ElementType::context]  = -1;
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
    if (f.is_open()) {
        f << json_string;
        f.close();
    } else {
        std::cerr << "Error opening file '" << fileName << "'\n";
        std::cerr << "      Is the path reachablet?\n";
    }
}

void
VCD_Impl::load(const std::string& fileName) {
    std::ifstream i(fileName);
    if (i.is_open()) {
        m_data.clear();
        i >> m_data;
        i.close();
    } else {
        std::cerr << "Error opening file '" << fileName << "'\n";
        std::cerr << "      Does the file exist?\n";
    }
}

void
VCD_Impl::update_vcd_frame_intervals(const size_t frame_index) {
    // NOTE: This function has an simplified implementation if compared with
    //       the python version of the library. In this version, a single big
    //       interval is defined from the first to the final interval value.
    // This function creates the union of existing VCD with the input
    // frameIntervals
    if (!m_data["vcd"].contains("frame_intervals")) {
        m_data["vcd"]["frame_intervals"] = json::array();
//        m_data["vcd"]["frame_intervals"].push_back({
//                        {"frame_start", frame_index},
//                        {"frame_end", frame_index}
//                    });
        appendFrameIntervalToArray(m_data["vcd"]["frame_intervals"],
                                   frame_index);
    }
    const int cur_value = m_data["vcd"]["frame_intervals"][0]["frame_end"];
    const int max_value = std::max(cur_value, static_cast<int>(frame_index));
    m_data["vcd"]["frame_intervals"][0]["frame_end"] = max_value;
}

void
VCD_Impl::update_element_frame_intervals(json &element,
                                         const size_t frame_index) {
    const bool has_fi = element.contains("frame_intervals");
    const bool is_good_fi = !isFrameIndexNone(frame_index);
    if (!is_good_fi) return;
    if (has_fi) {
        const size_t lst_value = element["frame_intervals"].back()["frame_end"];
        if (lst_value == (frame_index - 1)) {
            // If the end value of the last interval is the prevous frame
            // increment this value in the element, because we are in the same
            // interval.
            element["frame_intervals"].back()["frame_end"] = frame_index;
        } else {
            // If the current value does not follow the last interval, generate
            // a new one.
            appendFrameIntervalToArray(element["frame_intervals"],
                                       frame_index);
        }
    } else {
        // If the element has not any frame_interval values, include the list
        element["frame_intervals"] = json::array();
        appendFrameIntervalToArray(element["frame_intervals"], frame_index);
    }
}

json&
VCD_Impl::add_frame(const size_t frame_num, const bool addMissedFrames) {
    if (!m_data["vcd"].contains("frames")) {
        m_data["vcd"]["frames"] = json::object({});
    }
    const std::string frm_num_str = std::to_string(frame_num);
    if (!m_data["vcd"]["frames"].contains(frm_num_str)) {
        m_data["vcd"]["frames"][frm_num_str] = json::object({});

        bool is_first_frame = (frame_num == 0);
        if (addMissedFrames && !is_first_frame) {
            // Include all the frames between the last defined frame and the
            // current frame index.
            json &frame_list = m_data["vcd"]["frames"];
            size_t cur_frame_num = frame_num - 1;
            bool frm_found = frame_list.contains(std::to_string(cur_frame_num));
            is_first_frame = (cur_frame_num <= 0);
            while (!frm_found && !is_first_frame) {
                const std::string std_key = std::to_string(cur_frame_num);
                frame_list[std_key] = json::object({});
                --cur_frame_num;
                frm_found = frame_list.contains(std::to_string(cur_frame_num));
                is_first_frame = (cur_frame_num <= 0);
            }
        }
    }
    return m_data["vcd"]["frames"][frm_num_str];
}

// Manage metadata
void
VCD_Impl::add_annotator(const std::string &annotator) {
    auto &meta = setDefault(m_data["vcd"], "metadata", json::object());
    meta["annotator"] = annotator;
}

void
VCD_Impl::add_comment(const std::string &comment) {
    auto &meta = setDefault(m_data["vcd"], "metadata", json::object());
    meta["comment"] = comment;
}

void
VCD_Impl::add_file_version(const std::string &version) {
    auto &meta = setDefault(m_data["vcd"], "metadata", json::object());
    meta["file_version"] = version;
}

void
VCD_Impl::add_name(const std::string &name) {
    auto &meta = setDefault(m_data["vcd"], "metadata", json::object());
    meta["name"] = name;
}

void
VCD_Impl::add_metadata_properties(const vcd::meta_props &properties) {
    auto &meta = setDefault(m_data["vcd"], "metadata", json::object());
    for (const auto &elem : properties) {
        const std::string &key = elem.first;
        const std::string &value = elem.second;
        meta[key] = value;
    }
}

std::string
VCD_Impl::add_object(const std::string& name,
                     const obj_args& args) {
    const size_t null_frame_index = getNoneFrameIndex();
    return add_object(name, null_frame_index, args);
}

std::string
VCD_Impl::add_object(const std::string& name,
                     const size_t frame_index,
                     const obj_args& args) {
    //    m_data[name] = { {"currency", "USD"}, {"value", 42.99} };
//    int frame_value = 0;
    std::string coordinate_system;
    SetMode set_mode = SetMode::union_t;
    return set_element(ElementType::object, name, args.semantic_type,
                       frame_index, UID(args.uid), args.ontology_uid,
                       coordinate_system, set_mode).asStr();
}

void
VCD_Impl::add_object_data(const std::string &uid,
                          const types::ObjectData& object_data) {
    const size_t null_frame_index = getNoneFrameIndex();
    return set_element_data(ElementType::object, UID(uid), object_data,
                            null_frame_index, SetMode::union_t);
}

void
VCD_Impl::add_object_data(const std::string &uid,
                          const types::ObjectData& object_data,
                          const size_t frame_index) {
    return set_element_data(ElementType::object, UID(uid), object_data,
                            frame_index, SetMode::union_t);
}

ont_uid
VCD_Impl::add_ontology(const std::string &ontology) {
    json& ontologies = setDefault(m_data["vcd"], "ontologies", json::object());
    // Check if ontology already exists
    for (const auto &ont : ontologies.items()) {
        if (ont.value() == ontology) {
            std::cout << "WARNING: adding an already existing ontology\n";
            return ont.key();
        }
    }
    const std::string new_key = std::to_string(ontologies.size());
    ontologies[new_key] = ontology;
    return new_key;
}

// Getters
size_t
VCD_Impl::get_num_objects() {
    return get_num_elements(ElementType::object);
}

UID
VCD_Impl::get_uid_to_assign(const ElementType type, const UID &uid) {
    UID uid_to_assign;
    if (uid.isNone()) {
        if (m_useUUID) {
            uid_to_assign.withStr(UID::generate_uuid4());
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
VCD_Impl::get_metadata() {
    if (!m_data["vcd"].contains("metadata")) {
        return nullptr;
    } else {
        return &m_data["vcd"]["metadata"];
    }
}

json*
VCD_Impl::get_frame(const int frame_num) {
    if (!m_data["vcd"].contains("frames")) {
        return nullptr;
    } else {
        const json &frames = m_data["vcd"]["frames"];
        const std::string frame_key = std::to_string(frame_num);
        // First check if the current frame exists in the list
        const bool frame_exists = frames.contains(frame_key);
        if (frame_exists) {
            // Then get the frame if it exists
            return &m_data["vcd"]["frames"][std::to_string(frame_num)];
        } else {
            return nullptr;
        }
    }
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

size_t
VCD_Impl::get_num_elements(const ElementType type) {
    const std::string key = ElementTypeName[type] + "s";
    if (m_data["vcd"].contains(key)) {
        return m_data["vcd"][key].size();
    } else {
        return 0;
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
                                         const size_t frame_index,
                                         const UID &uid, const ont_uid &ont_uid,
                                         const std::string &coord_system) {
    // 1.- Copy from existing or create new entry (this copies everything,
    //     including element_data) element_data_pointers and frame intervals.
    const std::string uidstr = uid.asStr();
    // note: public functions use int or str for uids
    const bool element_existed = has(type, uid);
    const bool fi_is_good = !isFrameIndexNone(frame_index);
    const std::string typeKey = ElementTypeName[type] + "s";
    auto& typeLst = setDefault(m_data["vcd"], typeKey, json::object());
    auto& element = setDefault(typeLst, uidstr, json::object());

    // 2.- Copy from arguments
    if (!element_existed) {
        if (!name.empty()) {
            element["name"] = name;
        }
        if (!semantic_type.empty()) {
            element["type"] = semantic_type;
        }
        if (!ont_uid.empty()) {
            element["ontology_uid"] = ont_uid;
        }
    }
    update_element_frame_intervals(element, frame_index);
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

    // 3.- Reshape element_data_pointers according to this new frame intervals
    const std::string dpoint_key = ElementTypeName[type] + "_data_pointers";
    if (element.contains(dpoint_key) && fi_is_good) {
        json &edps = element[dpoint_key];
        for (auto &edp : edps) {
            // NOW, we have to UPDATE frame intervals of pointers because we
            // have modified the frame_intervals of the element itself, and
            // If we compute the intersection frame_intervals, we can copy that
            // into element_data_pointers frame intervals
            update_element_frame_intervals(edp, frame_index);
        }
    }

    // 4.- Now set at frames
    if (fi_is_good) {
        // 2.1.- There is frame_intervals specified so it is a dynamic element
        const bool frame_exists = isFrameWithIndex(frame_index);
        if (!frame_exists) {
            // 2.1.a) Just create the new element
            add_frame(frame_index, S_ADD_MISSIED_FRAMES);
            // And update the main
            update_vcd_frame_intervals(frame_index);
        }
        // 2.1.b) Add new data to existing frame
        json* frame = get_frame(frame_index);
        if (frame == nullptr) {
            // ERROR: the frame does not exist!
            return;
        }
        // Add the referenced empty elements inside the frame info list
        json& type_element = setDefault(*frame, typeKey, json::object());
        setDefault(type_element, uid.asStr(), json::object());
    }
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
                      const size_t frame_index,
                      const UID &uid, const ont_uid &ont_uid,
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
    set_element_at_root_and_frames(type, name, semantic_type, frame_index,
                                   uid_to_assign, ont_uid, coordinate_system);

    return uid_to_assign;
}

void
VCD_Impl::set_element_data(const ElementType type, const UID &uid,
                           const types::ObjectData &element_data,
                           const size_t frame_index,
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
    const bool fi_is_good = !isFrameIndexNone(frame_index);
    // Check if the new frame index is posterior to last frame index
    if (fi_is_good) {
        if (frame_index < m_curFrameIndex) {
            std::cerr << "Warning: Detected an old frame index! "
                         "Call ignored.\n";
            return;
        } else {
            m_curFrameIndex = frame_index;
        }
    }

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

    // Store element data values
    if (!fi_is_good) {
        // There is not a frame index defined, so this information should be
        // static. This means that the information is stored in the objects
        // definition and not in the frame definition.
        set_element_data_content(type, element, element_data);
    } else {
        // As there is a usable frame index defined, we have to include the
        // values in the specified frame.
        json *frme_elem = get_frame(frame_index);
        if (frme_elem == nullptr) {
            frme_elem = &add_frame(frame_index, S_ADD_MISSIED_FRAMES);
        }
        const std::string elem_key = ElementTypeName[type] + "s";
        json &type_elem_in_fr = (*frme_elem)[elem_key][uid.asStr()];
        set_element_data_content(type, type_elem_in_fr, element_data);
        // Also update the frame interval values in the object
        update_element_frame_intervals(element, frame_index);
    }
    // And create/update data pointers with empty information
    set_element_data_pointers(type, element, element_data, frame_index);
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
    auto& list_aux = VCD_Impl::setDefault(element[data_key], e_type_key,
                                          json::array());
    // Find if element_data already there
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
VCD_Impl::set_element_data_pointers(const ElementType type, json &element,
                                    const types::ObjectData &element_data,
                                    const size_t frame_index) {
    const std::string type_key = ElementTypeName[type] + "s";
    const std::string data_point_key = ElementTypeName[type] + "_data_pointers";

    auto& dp = VCD_Impl::setDefault(element, data_point_key, json::object());

    const std::string data_name = element_data.getName();
    auto& edp = VCD_Impl::setDefault(dp, data_name, json::object());
    edp["type"] = ObjectDataTypeName[element_data.getType()];

    // Update objects frame interval inside the data pointer data
    const bool fi_is_good = !isFrameIndexNone(frame_index);
    if (fi_is_good) {
        update_element_frame_intervals(edp, frame_index);
    } else {
        VCD_Impl::setDefault(edp, "frame_intervals", json::array());
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

/** @brief Generate a Version 4 UUID according to RFC-4122
 *
 * Uses the openssl RAND_bytes function to generate a
 * Version 4 UUID.
 *
 * @param buffer A buffer that is at least 38 bytes long.
 * @retval 1 on success, 0 otherwise.
 */
std::string
UID::generate_uuid4() {
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

bool
UID::check_uuid4(const std::string &uuid) {
    const std::string reg_ex_uid =
            "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
            "[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$";
    return regex_match(uuid, std::regex(reg_ex_uid));
}

void UID::set(const std::string &uidStr, const int uidInt, const bool isUUID) {
    m_uidStr = uidStr;
    m_uidInt = uidInt;
    m_isUUID = isUUID;
}

};  // namespace vcd
