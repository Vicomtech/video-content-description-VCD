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
#ifndef _VCD_H_
#define _VCD_H_

#include <string>
#include <memory>
#include <map>
#include <vector>

#include "core_exp.h"

namespace vcd {

class VCD_UID {
 public:
    ~VCD_UID();

    virtual bool
    isUUID() const = 0;

    virtual std::string
    asStr() const = 0;

    virtual int
    asInt() const = 0;

    virtual bool
    isNone() const = 0;
};

using ont_uid = std::string;
using obj_uid = std::string;
using act_uid = std::string;
using ctx_uid = std::string;
using coord_uid = std::string;
using meta_props = std::map<std::string, std::string>;

struct element_args {
    std::string semantic_type;
    ont_uid ontology_uid;
    obj_uid uid;
    coord_uid coord_system;
};

enum CoordinateSystemType {
    sensor_cs = 1,  // the coordinate system of a certain sensor
    local_cs = 2,   // e.g. vehicle-ISO8855 in OpenLABEL, or "base_link" in ROS
    scene_cs = 3,   // e.g. "odom" in ROS; starting as the first local-ls
    geo_utm = 4,    // In UTM coordinates
    geo_wgs84 = 5,  // In WGS84 elliptical Earth coordinates
    custom = 6      // Any other coordinate system
};

const std::string
CoordinateSystemTypeName[] {
    "sensor_cs",
    "local_cs",
    "scene_cs",
    "geo_utm",
    "geo_wgs84",
    "custom"
};

class VCD {
 public:
    virtual
    ~VCD();

    virtual void
    setUseUUID(const bool val) = 0;

    /**
     * @brief stringify Returns the information as a string and with a JSON
     * structure.
     * @param pretty If true, the return format includes a more readable
     * presentation, including returns and indentation.
     * @return The JSON content as a string
     */
    virtual std::string
    stringify(const bool pretty = true) const = 0;

    /**
     * @brief save Stores the loaded information in a JSON file in disk.
     * @param fileName Path and name of the output file.
     * @param prettyIf true, the return format includes a more readable
     * presentation, including returns and indentation.
     * @param validate ?
     */
    virtual void
    save(const std::string& fileName, const bool pretty = false,
         const bool validate = false) const = 0;

    /**
     * @brief load Loads stored information in a JSON file in disk.
     * @param fileName Path and name of the output file.
     */
    virtual void
    load(const std::string& fileName) = 0;

    // Add metadata and comments
    virtual void
    add_annotator(const std::string &annotator) = 0;

    virtual void
    add_comment(const std::string &comment) = 0;

    virtual void
    add_file_version(const std::string &file_version) = 0;

    virtual void
    add_name(const std::string &name) = 0;

    virtual void
    add_metadata_properties(const vcd::meta_props &properties) = 0;

    // Add object
    /**
     * @brief add_object Adds a new object to the scene definition.
     *
     * This call does not include a specific frame index, so it will not
     * belong to a specific frame. Instead, if no frame definition was
     * included yet, this object is interpreted as a general object, and it
     * is not included in any specific frame. Otherwise, if at least one frame
     * was defined before calling this function, this object will be included
     * in all new frames of the capture sequence.
     * @param name The name of the object
     * @param args The set of parameters for the object (see element_args)
     * @return The uuid of the object for its identification
     */
    virtual obj_uid
    add_object(const std::string& name, const element_args& args) = 0;

    /**
     * @brief add_object Adds a new object to the scene definition for the
     * specific frame index.
     *
     * This function includes the definition of the object in the structure,
     * and relates its uuid with the specified frame.
     * To relate a previously defined element with a new frame, you can add
     * the objects uuid as part of input parameters (see element_args).
     * @param name The name of the object
     * @param frame_index The index of the frame related with the defined
     * object. This index should be equal or bigger than the last defined frame.
     * @param args The set of parameters for the object (see element_args)
     * @return The uuid of the object for its identification
     */
    virtual obj_uid
    add_object(const std::string& name, const size_t frame_index,
               const element_args& args) = 0;

    // Add action
    /**
     * @brief add_action Adds a new action to the scene definition.
     *
     * This call does not include a specific frame index, so it will not
     * belong to a specific frame. Instead, if no frame definition was
     * included yet, this action is interpreted as a general action, and it
     * is not included in any specific frame. Otherwise, if at least one frame
     * was defined before calling this function, this action will be included
     * in all new frames of the capture sequence.
     * @param name The name of the action
     * @param args The set of parameters for the action (see element_args)
     * @return The uuid of the action for its identification
     */
    virtual act_uid
    add_action(const std::string& name, const element_args& args) = 0;

    /**
     * @brief add_action Adds a new action to the scene definition for the
     * specific frame index.
     *
     * This function includes the definition of the action in the structure,
     * and relates its uuid with the specified frame.
     * To relate a previously defined element with a new frame, you can add
     * the objects uuid as part of input parameters (see element_args).
     * @param name The name of the action
     * @param frame_index The index of the frame related with the defined
     * action. This index should be equal or bigger than the last defined frame.
     * @param args The set of parameters for the action (see element_args)
     * @return The uuid of the action for its identification
     */
    virtual act_uid
    add_action(const std::string& name, const size_t frame_index,
               const element_args& args) = 0;

    // Add context
    /**
     * @brief add_context Adds a new context to the scene definition.
     *
     * This call does not include a specific frame index, so it will not
     * belong to a specific frame. Instead, if no frame definition was
     * included yet, this context is interpreted as a general context, and it
     * is not included in any specific frame. Otherwise, if at least one frame
     * was defined before calling this function, this context will be included
     * in all new frames of the capture sequence.
     * @param name The name of the context
     * @param args The set of parameters for the context (see element_args)
     * @return The uuid of the context for its identification
     */
    virtual ctx_uid
    add_context(const std::string& name, const element_args& args) = 0;

    /**
     * @brief add_context Adds a new context to the scene definition for the
     * specific frame index.
     *
     * This function includes the definition of the context in the structure,
     * and relates its uuid with the specified frame.
     * To relate a previously defined element with a new frame, you can add
     * the objects uuid as part of input parameters (see element_args).
     * @param name The name of the context
     * @param frame_index The index of the frame related with the defined
     * context. This index should be equal or bigger than the last defined frame.
     * @param args The set of parameters for the context (see element_args)
     * @return The uuid of the context for its identification
     */
    virtual ctx_uid
    add_context(const std::string& name, const size_t frame_index,
                const element_args& args) = 0;

    // Ontologies
    virtual ont_uid
    add_ontology(const std::string &ontology) = 0;

    // Coordinate system
    virtual coord_uid
    add_coordinate_system(const std::string& name,
                          const CoordinateSystemType cs_type,
                          const std::string& parent_name = "",
                          const std::vector<float>& pose_wrt_parent = {}) = 0;

    // Getters
    virtual size_t
    get_num_objects() = 0;

    // Object data generators
    virtual void
    add_bbox_to_object(const obj_uid& uid,
                       const std::string& name,
                       const std::vector<int>& value,
                       const size_t frame_index = -1) = 0;

    virtual void
    add_vec_to_object(const obj_uid& uid,
                      const std::string& name,
                      const std::vector<float>& value,
                      const size_t frame_index = -1) = 0;

    virtual void
    add_num_to_object(const obj_uid& uid,
                      const std::string& name,
                      const double value,
                      const size_t frame_index = -1) = 0;

    virtual void
    add_bool_to_object(const obj_uid& uid,
                       const std::string& name,
                       const bool value,
                       const size_t frame_index = -1) = 0;

    virtual void
    add_text_to_object(const obj_uid& uid,
                       const std::string& name,
                       const std::string& text,
                       const size_t frame_index = -1) = 0;

    // Action data generators
    virtual void
    add_bbox_to_action(const obj_uid& uid,
                       const std::string& name,
                       const std::vector<int>& value,
                       const size_t frame_index = -1) = 0;

    virtual void
    add_vec_to_action(const obj_uid& uid,
                      const std::string& name,
                      const std::vector<float>& value,
                      const size_t frame_index = -1) = 0;

    virtual void
    add_num_to_action(const obj_uid& uid,
                      const std::string& name,
                      const double value,
                      const size_t frame_index = -1) = 0;

    virtual void
    add_bool_to_action(const obj_uid& uid,
                       const std::string& name,
                       const bool value,
                       const size_t frame_index = -1) = 0;

    virtual void
    add_text_to_action(const obj_uid& uid,
                       const std::string& name,
                       const std::string& text,
                       const size_t frame_index = -1) = 0;

    // Context data generators
    virtual void
    add_bbox_to_context(const obj_uid& uid,
                        const std::string& name,
                        const std::vector<int>& value,
                        const size_t frame_index = -1) = 0;

    virtual void
    add_vec_to_context(const obj_uid& uid,
                       const std::string& name,
                       const std::vector<float>& value,
                       const size_t frame_index = -1) = 0;

    virtual void
    add_num_to_context(const obj_uid& uid,
                       const std::string& name,
                       const double value,
                       const size_t frame_index = -1) = 0;

    virtual void
    add_bool_to_context(const obj_uid& uid,
                        const std::string& name,
                        const bool value,
                        const size_t frame_index = -1) = 0;

    virtual void
    add_text_to_context(const obj_uid& uid,
                        const std::string& name,
                        const std::string& text,
                        const size_t frame_index = -1) = 0;

    // Instance creation factories
    static CORE_LIB std::unique_ptr<VCD>
    create(const std::string& fileName, const bool validation = false);

    static CORE_LIB std::unique_ptr<VCD>
    create(const bool validation = false);
};
using VCD_ptr = std::unique_ptr<VCD>;

};  // namespace vcd

#endif  // _VCD_H_
