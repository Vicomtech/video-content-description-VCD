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

#include "vcd.h"
#include "vcd_types.h"
#include "setup_strings.h"

static char asset_path[] = TEST_ASSET_FOLDER;

using vcd::VCD;
using vcd::VCD_ptr;
using vcd::types::Bbox;
using vcd::types::Vec;
using vcd::types::Num;
using vcd::types::Boolean;

using std::string;

#include "vcd.h"
#include "vcd_types.h"
#include "setup_strings.h"

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
            std::string uid_marcos = vcd->add_object("marcos", "person");
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

            std::string uid_peter = vcd->add_object("peter", "person");
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

            auto vcd_file_nopretty_tst = getFileAsString(vcd_np_path);
            auto vcd_file_nopretty_out = getFileAsString(vcd_outnp_path);
            REQUIRE(vcd_file_nopretty_tst.compare(vcd_file_nopretty_out) == 0);
            //  - Pretty version
            char vcd_p[] = "vcd430_test_create_search_simple_pretty.json";
            fs::path vcd_p_path = fs::path(asset_path) / fs::path(vcd_p);
            REQUIRE(fs::exists(vcd_p_path));

            auto vcd_file_pretty_tst = getFileAsString(vcd_p_path);
            auto vcd_file_pretty_out = getFileAsString(vcd_outnp_path);
            REQUIRE(vcd_file_pretty_tst.compare(vcd_file_pretty_out) == 0);
        }

        THEN("Write into string") {
        }

        THEN("We can ask VCD") {
            // PRELIMINAR TEST OF ATTRIBUTES, PLEASE REMOVE
            Bbox box1 = Bbox("head", {0, 0, 10, 10});
            box1.add_attribute(Boolean("visible", true).get());
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
