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
#include "setup_strings.h"
#include "test_utils.h"

static char asset_path[] = TEST_ASSET_FOLDER;

using vcd::VCD;
using vcd::VCD_ptr;
using vcd::types::Bbox;
using vcd::types::Vec;
using vcd::types::Num;
using vcd::types::Boolean;

using std::string;

using nlohmann::json;

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

SCENARIO("Create some basic content, without time information, and do some "
         "basic search") {
    GIVEN("Create and empty VCD") {
        THEN("Create an object") {
            VCD_ptr vcd = VCD::create();
            REQUIRE(vcd.get() != nullptr);
        }

        THEN("Add some data to the object") {
            // 1.- Create a VCD instance
            VCD_ptr vcd = VCD::create();

            // 2.- Create the Object
            vcd::obj_args marcos_args;
            marcos_args.semantic_type = "person";
            std::string uid_marcos = vcd->add_object("marcos", marcos_args);
            CHECK(uid_marcos == "0");

            // 3.- Add some data to the object
            {
                // Define the internal objects for marcos
                Bbox head_bbox("head", {10, 10, 30, 30});
                Bbox body_bbox("body", {0, 0, 60, 120});
                Vec speed_vec("speed", {0.0, 0.2});
                Num accel_num("accel", 0.1);
                vcd->add_object_data(uid_marcos, head_bbox.get());
                vcd->add_object_data(uid_marcos, body_bbox.get());
                vcd->add_object_data(uid_marcos, speed_vec.get());
                vcd->add_object_data(uid_marcos, accel_num.get());
            }

            vcd::obj_args peter_args;
            peter_args.semantic_type = "person";
            std::string uid_peter = vcd->add_object("peter", peter_args);
            {
                // Define the internal objects for peter
                Num age("age", 38.0);
                Vec eyeL("eyeL", {0, 0, 10, 10});
                Vec eyeR("eyeR", {0, 0, 10, 10});
                vcd->add_object_data(uid_peter, age.get());
                vcd->add_object_data(uid_peter, eyeL);
                vcd->add_object_data(uid_peter, eyeR);
            }
            // 4.- Write into string
            VCD_ptr vcd_tst = VCD::create();
            const std::string vcd_string_pretty = vcd->stringify();
            const bool indent = false;
            const std::string vcd_string_nopretty = vcd->stringify(indent);

            // (AVOID RIGHT NOW) 5.- We can ask VCD

            // Save the json info into a file for comparisson
            string out_p = "vcd430_test_create_search_simple_pretty_OUT.json";
            fs::path vcd_outp_path = fs::path(asset_path) / fs::path(out_p);
            std::ofstream o_p(vcd_outp_path);
            o_p << vcd_string_pretty << std::endl;
            o_p.close();

           string out_np = "vcd430_test_create_search_simple_nopretty_OUT.json";
            fs::path vcd_outnp_path = fs::path(asset_path) / fs::path(out_np);
            std::ofstream o_np(vcd_outnp_path);
            o_np << vcd_string_nopretty << std::endl;
            o_np.close();

            // Get the reference JSON text
            //  - No pretty version
            char vcd_np[] = "vcd430_test_create_search_simple_nopretty.json";
            fs::path vcd_np_path = fs::path(asset_path) / fs::path(vcd_np);
//            std::cout << vcd_np_path.c_str() << std::endl;
            REQUIRE(fs::exists(vcd_np_path));
            // Compare both json definition
            REQUIRE(compare_json_files(vcd_outnp_path, vcd_np_path));

            //  - Pretty version
            char vcd_p[] = "vcd430_test_create_search_simple_pretty.json";
            fs::path vcd_p_path = fs::path(asset_path) / fs::path(vcd_p);
            REQUIRE(fs::exists(vcd_p_path));
            // Compare both json definition
            REQUIRE(compare_json_files(vcd_outp_path, vcd_p_path));
        }

        THEN("Write into string") {
        }

        THEN("Add some objects and frames") {
            // 1.- Create a VCD instance
            VCD_ptr vcd = VCD::create();

            // 2.- Create some Objects
            vcd::obj_args marcos_args;
            marcos_args.semantic_type = "person";
            std::string uid_marcos = vcd->add_object("marcos", marcos_args);
            CHECK(uid_marcos == "0");
            vcd::obj_args peter_args;
            peter_args.semantic_type = "person";
            std::string uid_peter = vcd->add_object("peter", peter_args);
            CHECK(uid_peter == "1");

            // 3.- Add some data to the objects
            //   - Marcos
            Bbox body_bbox_m0("body", {0, 0, 60, 120});
            vcd->add_object_data(uid_marcos, body_bbox_m0.get(), 0);
            Bbox body_bbox_m1("body", {0, 0, 62, 124});
            vcd->add_object_data(uid_marcos, body_bbox_m1.get(), 1);
            Bbox body_bbox_m2("body", {0, 0, 70, 128});
            vcd->add_object_data(uid_marcos, body_bbox_m2.get(), 2);
            Bbox body_bbox_m5("body", {0, 0, 100, 160});
            vcd->add_object_data(uid_marcos, body_bbox_m5.get(), 5);
            //   - Peter
            Bbox body_bbox_p7("body", {0, 0, 200, 190});
            vcd->add_object_data(uid_peter, body_bbox_p7.get(), 7);
            Bbox body_bbox_p8("body", {0, 0, 180, 185});
            vcd->add_object_data(uid_peter, body_bbox_p8.get(), 8);
            Bbox body_bbox_p9("body", {0, 0, 160, 179});
            vcd->add_object_data(uid_peter, body_bbox_p9.get(), 9);
            Bbox body_bbox_p5("body", {0, 0, 99, 99});
            vcd->add_object_data(uid_peter, body_bbox_p5.get(), 5);

            // 4.- Save the json info into a file for comparisson
            string out_p = "vcd430_test_create_frames_simple_pretty_OUT.json";
            fs::path vcd_outp_path = fs::path(asset_path) / fs::path(out_p);
            std::ofstream o_p(vcd_outp_path);
            const std::string vcd_string_pretty = vcd->stringify();
            o_p << vcd_string_pretty << std::endl;
            o_p.close();

            // 5.- Compare with reference json files
            //  - Pretty version
            char vcd_p[] = "vcd430_test_create_frames_simple_pretty.json";
            fs::path vcd_p_path = fs::path(asset_path) / fs::path(vcd_p);
            REQUIRE(fs::exists(vcd_p_path));
            // Compare both json definition
            REQUIRE(compare_json_files(vcd_outp_path, vcd_p_path));
        }

//        THEN("We can include attributes") {
//            // PRELIMINAR TEST OF ATTRIBUTES, PLEASE REMOVE
//            Bbox box1 = Bbox("head", {0, 0, 10, 10});
//            box1.add_attribute(Boolean("visible", true).get());
//        }

        THEN("We can include ontologies") {
            // 1.- Create a VCD instance
            VCD_ptr vcd = VCD::create();

            // 2.- Create some ontologies
            const vcd::ont_uid ont_uid_1 = vcd->add_ontology(
                                "http://www.vicomtech.org/viulib/ontology");
            const vcd::ont_uid ont_uid_2 = vcd->add_ontology(
                                "http://www.alternativeURL.org/ontology");
            const vcd::ont_uid ont_uid_1_bis = vcd->add_ontology(
                                "http://www.vicomtech.org/viulib/ontology");

            REQUIRE(ont_uid_1 == ont_uid_1_bis);
            REQUIRE(ont_uid_1 != ont_uid_2);

            // 3.- Create the Object
            vcd::obj_args marcos_args;
            marcos_args.semantic_type = "person";
            marcos_args.ontology_uid = ont_uid_1;
            const std::string uid_marcos = vcd->add_object("marcos",
                                                           marcos_args);
            CHECK(uid_marcos == "0");

            // 4.- Add some data to the object
            // Define the internal objects for marcos
            Bbox head_bbox("head", {10, 10, 30, 30});
            Bbox body_bbox("body", {0, 0, 60, 120});
            Vec speed_vec("speed", {0.0, 0.2});
            Num accel_num("accel", 0.1);
            vcd->add_object_data(uid_marcos, head_bbox.get());
            vcd->add_object_data(uid_marcos, body_bbox.get());
            vcd->add_object_data(uid_marcos, speed_vec.get());
            vcd->add_object_data(uid_marcos, accel_num.get());

            // Generate json data
            const bool pretty = true;
            const std::string vcd_out_pretty = vcd->stringify(pretty);

            // Save the json info into a file for comparisson
            string out_p = "vcd430_test_ontology_OUT.json";
            fs::path vcd_outp_path = fs::path(asset_path) / fs::path(out_p);
            std::ofstream o_p(vcd_outp_path);
            o_p << vcd_out_pretty << std::endl;
            o_p.close();

            // Read reference JSON file
            string ref_p = "vcd430_test_ontology.json";
            fs::path vcd_refp_path = fs::path(asset_path) / fs::path(ref_p);
            std::ifstream ref_file_data(vcd_refp_path);
            json ref_data;
            ref_file_data >> ref_data;
            ref_file_data.close();

            // Generate JSON structure for comparison
            json test_data = json::parse(vcd_out_pretty);

            REQUIRE(check_json_level(test_data, ref_data));
        }
    }

    /*GIVEN("Read and write some VCD content") {
        std::string fileName = vcd::SetupStrings::testDataPath +
                            "/vcd430_test_create_search_simple_nopretty.json";
        VCD vcd(fileName);

        std::string json_string = vcd.stringify(false);
        std::cout << json_string << std::endl;

        std::string fileNameOut = vcd::SetupStrings::testDataPath +
                           "vcd430_test_create_search_simple_nopretty_out.json";
        vcd.save(fileNameOut, false);
    }
    */
}
