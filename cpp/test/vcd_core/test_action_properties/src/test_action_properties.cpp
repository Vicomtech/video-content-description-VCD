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
using vcd::types::Text;

using std::string;

using nlohmann::json;

SCENARIO("Add a set of actions to a VCD capture") {
    GIVEN("A set of actions") {
        THEN("Include the actions") {
            // 1.- Create a VCD instance
            VCD_ptr vcd = VCD::create();

            // 2.- Create all the elements
            //  2.1 - Actions
            // In frames from 0 to 10
            vcd::element_args running_args;
            running_args.semantic_type = "#Running";
            std::string uid_action1 = vcd->add_action("", running_args);
            running_args.uid = uid_action1;

            // In frames from 0 to 5
            vcd::element_args ctx2_args;
            ctx2_args.semantic_type = "#Highway";
            std::string uid_context2 = vcd->add_context("", ctx2_args);
            ctx2_args.uid = uid_context2;


            // Include running in the first frame to force holistic element
            // definitions.
            vcd->add_action("", 0, running_args);

            // Same can be done with events and event_data, and contexts
            // nd context_data.
            // And can be done as dynamic or static info
            //  2.2 - Objects
            // Holistic
            vcd::element_args marcos_args;
            marcos_args.semantic_type = "#Person";
            std::string uid_object1 = vcd->add_object("Marcos", marcos_args);
            marcos_args.uid = uid_object1;
            vcd->add_text_to_object(uid_object1, "Position", "#Researcher");

            //  2.3 - Contexts
            // Holistic
            vcd::element_args ctx1_args;
            ctx1_args.semantic_type = "#Sunny";
            std::string uid_context1 = vcd->add_context("", ctx1_args);
            ctx1_args.uid = uid_context1;
            vcd->add_text_to_context(uid_context1, "category", "#Weather");
            vcd->add_text_to_context(uid_context1, "annotation", "Manual");

            const size_t num_frames = 10;
            for (size_t frame_i = 0; frame_i <= num_frames; ++frame_i) {
                // Simulate action detection
                vcd->add_action("", frame_i, running_args);
                if (frame_i == 0) {
                    // Include the action data for the first frame
                    vcd->add_num_to_action(uid_action1,
                                           "confidence", 0.98, frame_i);
                    vcd->add_vec_to_action(uid_action1,
                                           "confidence_vec", {0.98, 0.97},
                                           frame_i);
                    vcd->add_text_to_action(uid_action1,
                                            "annotation", "Manual", frame_i);
                } else if (frame_i == 1) {
                    // Include the action data for the second frame
                    vcd->add_bool_to_action(uid_action1,
                                            "validated", true, frame_i);
                }
                // Simulate context detection
                if (frame_i <= 5) {
                    vcd->add_context("", frame_i, ctx2_args);
                }
                if (frame_i == 4) {
                    // Frame 4
                    vcd->add_num_to_context(ctx2_args.uid, "risk", 0.7,
                                          frame_i);
                    vcd->add_num_to_context(ctx2_args.uid, "weight", 0.5,
                                          frame_i);
                }
                // This is extra to fit with the output definition
//                vcd->add_object("Marcos", frame_i, marcos_args);
//                vcd->add_context("", frame_i, ctx1_args);
//                if (frame_i <= 5) {
//                    vcd->add_context("", frame_i, ctx2_args);
//                }
            }

            // 3. Compare results
            // Generate json data
            const bool pretty = true;
            const std::string vcd_out_pretty = vcd->stringify(pretty);

            // Save the json info into a file for comparisson
            string out_p = "vcd430_test_actions_with_action_data_OUT.json";
            fs::path vcd_outp_path = fs::path(asset_path) / fs::path(out_p);
            std::ofstream o_p(vcd_outp_path);
            o_p << vcd_out_pretty << std::endl;
            o_p.close();

            // Read reference JSON file
            string ref_p = "vcd430_test_actions_with_action_data.json";
            fs::path vcd_refp_path = fs::path(asset_path) / fs::path(ref_p);
            std::ifstream ref_file_data(vcd_refp_path);
            json ref_data;
            ref_file_data >> ref_data;
            ref_file_data.close();

            // Generate JSON structure for comparison
            json test_data = json::parse(vcd_out_pretty);

            REQUIRE(check_json_level_both_sides(test_data, ref_data));


//    if not os.path.isfile('./etc/vcd430_test_actions_with_action_data.json'):
//                vcd.save('./etc/vcd430_test_actions_with_action_data.json',
//                         True)
//      vcd_read = core.VCD('./etc/vcd430_test_actions_with_action_data.json',
//                                validation=True)
//            vcd_read_stringified = vcd_read.stringify()
//            vcd_stringified = vcd.stringify()
//            // print(vcd_stringified)
//            self.assertEqual(vcd_read_stringified, vcd_stringified)

//                    REQUIRE(vcd.get() != nullptr);
        }
    }
}
