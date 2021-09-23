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
#define CATCH_CONFIG_MAIN
#include "catch.hpp"

// -- Project -- //
#include <fstream>
#if defined(__linux__)
    #include <experimental/filesystem>
    namespace fs = std::experimental::filesystem;
#else
    #include <filesystem>
    #ifdef _MSC_VER == 1900
    namespace fs = std::experimental::filesystem;
    #else
    namespace fs = std::filesystem;
    #endif
#endif

#include <nlohmann/json.hpp>

#include "vcd.h"
#include "vcd_types.h"
#include "test_utils.h"

#include "vcd_impl.h"

static char asset_path[] = TEST_ASSET_FOLDER;

using vcd::VCD;
using vcd::VCD_ptr;
using vcd::types::Bbox;
using vcd::types::Vec;
using vcd::types::Num;
using vcd::types::Boolean;

using std::string;

using nlohmann::json;

using vcd::obj_uid;

// Indirection class to get inner elements of vcd instance
namespace vcd {
class VCD_Inner : public vcd::VCD_Impl {
 public:
    VCD_Inner() : vcd::VCD_Impl("") {
    }

    json*
    get_inner_element(const vcd::ElementType type, const std::string &uid_str) {
        return get_element(type, uid_str);
    }

    json*
    get_object(const std::string &uid_str) {
        return vcd::VCD_Impl::get_object(uid_str);
    }
};
}  // namespace vcd

// ----- //

std::string
getStreamAsString(const std::istream& in) {
    std::stringstream out;
    out << in.rdbuf();
    return out.str();
}

std::string
getFileAsString(const std::string& filePath) {
    std::ifstream stream;
    try {
        // Set to throw on failure
        stream.exceptions(std::fstream::failbit | std::fstream::badbit);
        stream.open(filePath);
    } catch (std::system_error& error) {
        std::cerr << "Failed to open '" << filePath
                  << "'\n" << error.code().message() << std::endl;
        return "Open fail";
    }

    return getStreamAsString(stream);
}

SCENARIO("Create some basic content, without time information") {
    GIVEN("A VCD structure") {
        THEN("Test number based uid") {
            // 1.- Create a VCD instance
            vcd::VCD_Inner vcd_impl;
//            VCD_ptr vcd = VCD::create();

            // We can add elements and get UIDs as strings
            vcd::element_args mike_args;
            mike_args.semantic_type = "Person";
            const auto uid0 = vcd_impl.add_object("Mike", mike_args);
            REQUIRE(uid0 == "0");

            // We can also specify which UID we will like our elements to have
            // We can only use strings
            // Response is always string
            vcd::element_args susan_args;
            susan_args.semantic_type = "Person";
            susan_args.uid = "2";
            const obj_uid uid2 = vcd_impl.add_object("Susan", susan_args);
            REQUIRE(uid2 == "2");

            // The user must use uuids in string format for all public functions
            vcd_impl.add_bool_to_object(uid2, "checked", true);
            vcd_impl.add_bool_to_object("2", "double-checked", true);

            // Same happens with ontology uids
            const vcd::ont_uid ont_uid_0 = vcd_impl.add_ontology(
                                    "http://www.vicomtech.org/viulib/ontology");
            REQUIRE(!ont_uid_0.empty());

            // Test ontology uid
            vcd::element_args mark_args;
            mark_args.semantic_type = "#Pedestrian";
            mark_args.ontology_uid = ont_uid_0;
            const obj_uid uid3 = vcd_impl.add_object("Mark", mark_args);
            const json* data = vcd_impl.get_inner_element(vcd::object, uid3);
            REQUIRE(data != nullptr);
            REQUIRE((*data)["ontology_uid"] == "0");

            // Generate json data
            const bool pretty = true;
            const std::string vcd_out_pretty = vcd_impl.stringify(pretty);

            // All returned UIDs are strings, and when written into JSON as well
            // print(vcd.stringify(False))
            const std::string ref_json =
                    "{"
                    "\"openlabel\":{"
                    "   \"metadata\":{"
                    "       \"schema_version\":\"1.0.0\""
                    "   },"
                    "   \"objects\":{"
                    "       \"0\":{"
                    "           \"name\":\"Mike\","
                    "           \"type\":\"Person\""
                    "       },"
                    "       \"2\":{"
                    "           \"name\":\"Susan\","
                    "           \"type\":\"Person\","
                    "           \"object_data\":{"
                    "               \"boolean\":[{"
                    "                   \"name\":\"checked\","
                    "                   \"val\":true"
                    "                },{"
                    "                   \"name\":\"double-checked\","
                    "                   \"val\":true"
                    "                }]"
                    "           },"
                    "           \"object_data_pointers\":{"
                    "               \"checked\":{"
                    "                   \"type\":\"boolean\","
                    "                   \"frame_intervals\":[]"
                    "               },"
                    "               \"double-checked\":{"
                    "                   \"type\":\"boolean\","
                    "                   \"frame_intervals\":[]"
                    "               }"
                    "           }"
                    "       },"
                    "       \"3\":{"
                    "           \"name\":\"Mark\","
                    "           \"type\":\"#Pedestrian\","
                    "           \"ontology_uid\":\"0\""
                    "       }"
                    "   },"
                    "   \"ontologies\":{"
                    "       \"0\":\"http://www.vicomtech.org/viulib/ontology\""
                    "   }"
                    "   }"
                    "}";
            const json ref_data = json::parse(ref_json);
            const json test_data = json::parse(vcd_out_pretty);
            REQUIRE(check_json_level(test_data, ref_data));
        }

        THEN("Test guid based uid") {
            // 0.- Check if UUID generator is active
            const std::string test_uuid = vcd::UID::generate_uuid4();
            REQUIRE(test_uuid != "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXXXX");

            // 1.- Create a VCD instance
            vcd::VCD_Inner vcd_impl;
//            VCD_ptr vcd = VCD::create();
            vcd_impl.setUseUUID(true);

            // We can add elements and get UIDs as strings
            vcd::element_args mike_args;
            mike_args.semantic_type = "Person";
            const auto uid0 = vcd_impl.add_object("Mike", mike_args);
            CHECK(uid0 != "0");
            REQUIRE(uid0.size() == 36);

            // We can also specify which UID we will like our elements to have
            // We can only use strings
            // Response is always string
            vcd::element_args susan_args;
            susan_args.semantic_type = "Person";
            const std::string uuid2 = vcd::UID::generate_uuid4();
            REQUIRE(uuid2.size() == 36);
            susan_args.uid = uuid2;
            const obj_uid uid2 = vcd_impl.add_object("Susan", susan_args);
            CHECK(uid2 == uuid2);
            REQUIRE(uid2.size() == 36);

            // The user must use uuids in string format for all public functions
            vcd_impl.add_bool_to_object(uid2, "checked", true);
            vcd_impl.add_bool_to_object("2", "double-checked", true);

            // Same happens with ontology uids
            const vcd::ont_uid ont_uid_0 = vcd_impl.add_ontology(
                                    "http://www.vicomtech.org/viulib/ontology");
            REQUIRE(!ont_uid_0.empty());

            // Test ontology uid
            vcd::element_args mark_args;
            mark_args.semantic_type = "#Pedestrian";
            mark_args.ontology_uid = ont_uid_0;
            const obj_uid uid3 = vcd_impl.add_object("Mark", mark_args);
            const json* data = vcd_impl.get_inner_element(vcd::object, uid3);
            REQUIRE(data != nullptr);
            REQUIRE((*data)["ontology_uid"] == "0");
        }

        THEN("Use explicit uuid v4 values as input") {
            // 1.- Create a VCD instance
            vcd::VCD_Inner vcd_impl;
            const std::string uuid1 = vcd::UID::generate_uuid4();
            // Adding an object and specifying its uid to be a previously
            // defined UUID, from this call on VCD uses UUID
            vcd::element_args marcos_args;
            marcos_args.semantic_type = "person";
            marcos_args.uid = uuid1;
            std::string uid1 = vcd_impl.add_object("marcos", marcos_args);
            const auto *object = vcd_impl.get_object(uid1);
            REQUIRE(object != nullptr);
            REQUIRE((*object)["name"] == "marcos");

            vcd::element_args orti_args;
            orti_args.semantic_type = "person";
            const auto uid2 = vcd_impl.add_object("orti", orti_args);

            const bool match_regex = vcd::UID::check_uuid4(uid2);
            REQUIRE(match_regex);
        }
    }
}
