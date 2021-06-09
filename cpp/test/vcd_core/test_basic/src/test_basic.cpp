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

    json*
    get_metadata() {
        return vcd::VCD_Impl::get_metadata();
    }
};
}  // namespace vcd

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
    GIVEN("A set of object data") {
        THEN("Create an object") {
            VCD_ptr vcd = VCD::create();
            REQUIRE(vcd.get() != nullptr);
        }

        THEN("Add some data to the object") {
            // 1.- Create a VCD instance
            VCD_ptr vcd = VCD::create();

            // 2.- Create the Object
            vcd::element_args marcos_args;
            marcos_args.semantic_type = "person";
            std::string uid_marcos = vcd->add_object("marcos", marcos_args);
            CHECK(uid_marcos == "0");

            // 3.- Add some data to the object
            {
                // Define the internal objects for marcos
                vcd->add_bbox_to_object(uid_marcos, "head", {10, 10, 30, 30});
                vcd->add_bbox_to_object(uid_marcos, "body", {0, 0, 60, 120});
                vcd->add_vec_to_object(uid_marcos, "speed", {0.0, 0.2});
                vcd->add_num_to_object(uid_marcos, "accel", 0.1);
            }

            vcd::element_args peter_args;
            peter_args.semantic_type = "person";
            std::string uid_peter = vcd->add_object("peter", peter_args);
            {
                // Define the internal objects for peter
                vcd->add_num_to_object(uid_peter, "age", 38.0);
                vcd->add_vec_to_object(uid_peter, "eyeL", {0, 0, 10, 10});
                vcd->add_vec_to_object(uid_peter, "eyeR", {0, 0, 10, 10});
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
            CHECK(compare_json_files(vcd_outnp_path, vcd_np_path));

            //  - Pretty version
            char vcd_p[] = "vcd430_test_create_search_simple_pretty.json";
            fs::path vcd_p_path = fs::path(asset_path) / fs::path(vcd_p);
            REQUIRE(fs::exists(vcd_p_path));
            // Compare both json definition
            CHECK(compare_json_files(vcd_outp_path, vcd_p_path));
        }

        THEN("Write into string") {
        }

        THEN("Add some objects and frames") {
            // 1.- Create a VCD instance
            VCD_ptr vcd = VCD::create();

            // 2.- Create some Objects
            vcd::element_args marcos_args;
            marcos_args.semantic_type = "person";
            std::string uid_marcos = vcd->add_object("marcos", marcos_args);
            CHECK(uid_marcos == "0");
            vcd::element_args peter_args;
            peter_args.semantic_type = "person";
            std::string uid_peter = vcd->add_object("peter", peter_args);
            CHECK(uid_peter == "1");

            // 3.- Add some data to the objects
            //   - Marcos
            vcd->add_bbox_to_object(uid_marcos, "body", {0, 0, 60, 120}, 0);
            vcd->add_bbox_to_object(uid_marcos, "body", {0, 0, 62, 124}, 1);
            vcd->add_bbox_to_object(uid_marcos, "body", {0, 0, 70, 128}, 2);
            vcd->add_bbox_to_object(uid_marcos, "body", {0, 0, 100, 160}, 5);
            //   - Peter
            vcd->add_bbox_to_object(uid_peter, "body", {0, 0, 200, 190}, 7);
            vcd->add_bbox_to_object(uid_peter, "body", {0, 0, 180, 185}, 8);
            vcd->add_bbox_to_object(uid_peter, "body", {0, 0, 160, 179}, 9);
            //       !Should be ignored, because the frame index is < the
            //        last frame index.
            vcd->add_bbox_to_object(uid_peter, "body", {0, 0, 99, 99}, 5);

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

        THEN("Activate UUID generator and add some objects and frames") {
            // 1.- Create a VCD instance
            VCD_ptr vcd = VCD::create();

            // Configure vcd to use complete uuid values
            vcd->setUseUUID(true);

            // 2.- Create some Objects
            vcd::element_args marcos_args;
            marcos_args.semantic_type = "person";
            std::string uid_marcos = vcd->add_object("marcos", marcos_args);
            CHECK(uid_marcos.size() == 36);
            vcd::element_args peter_args;
            peter_args.semantic_type = "person";
            std::string uid_peter = vcd->add_object("peter", peter_args);
            CHECK(uid_peter.size() == 36);

            CHECK(uid_peter != uid_marcos);

            // 3.- Add some data to the objects
            //   - Marcos
            vcd->add_bbox_to_object(uid_marcos, "body", {0, 0, 60, 120}, 0);
            vcd->add_bbox_to_object(uid_marcos, "body", {0, 0, 62, 124}, 1);
            vcd->add_bbox_to_object(uid_marcos, "body", {0, 0, 70, 128}, 2);
            vcd->add_bbox_to_object(uid_marcos, "body", {0, 0, 100, 160}, 5);
            //   - Peter
            vcd->add_bbox_to_object(uid_peter, "body", {0, 0, 200, 190}, 7);
            vcd->add_bbox_to_object(uid_peter, "body", {0, 0, 180, 185}, 8);
            vcd->add_bbox_to_object(uid_peter, "body", {0, 0, 160, 179}, 9);
            //       !Should be ignored, because the frame index is < the
            //        last frame index.
            vcd->add_bbox_to_object(uid_peter, "body", {0, 0, 99, 99}, 5);

            // 4.- Save the json info into a file for comparisson
            string out_p = "vcd430_test_create_frames_uuid_pretty_OUT.json";
            fs::path vcd_outp_path = fs::path(asset_path) / fs::path(out_p);
            std::ofstream o_p(vcd_outp_path);
            const std::string json_string = vcd->stringify();
            o_p << json_string << std::endl;
            o_p.close();

            // 5.- Check if the uuid values are stored in the file
            const std::string json_string_ugly = vcd->stringify(false);
            json data = json::parse(json_string_ugly);

            REQUIRE(data.contains("vcd"));
            REQUIRE(data["vcd"].contains("objects"));

            // Check the size of uuid values
            size_t cont = 0;
            for (auto& el : data["vcd"]["objects"].items()) {
                CHECK(el.key().size() == 36);
                ++cont;
            }

            REQUIRE(cont == 2);
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
            vcd::element_args marcos_args;
            marcos_args.semantic_type = "person";
            marcos_args.ontology_uid = ont_uid_1;
            const std::string uid_marcos = vcd->add_object("marcos",
                                                           marcos_args);
            CHECK(uid_marcos == "0");

            // 4.- Add some data to the object
            // Define the internal objects for marcos
            vcd->add_bbox_to_object(uid_marcos, "head", {10, 10, 30, 30});
            vcd->add_bbox_to_object(uid_marcos, "body", {0, 0, 60, 120});
            vcd->add_vec_to_object(uid_marcos, "speed", {0.0, 0.2});
            vcd->add_num_to_object(uid_marcos, "accel", 0.1);

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

        THEN("Create objects without data") {
            VCD_ptr vcd = VCD::create();

            vcd::element_args pedestrian_args;
            pedestrian_args.semantic_type = "#Pedestrian";
            std::string pedestrian_uid = vcd->add_object("", pedestrian_args);
            pedestrian_args.uid = pedestrian_uid;

            vcd::element_args car_args;
            car_args.semantic_type = "#Car";
            std::string car_uid = vcd->add_object("", car_args);
            car_args.uid = car_uid;

            // Pedestrian frames (0, 30), Car frames (20, 30)
            const size_t num_frames = 31;
            for (size_t i = 0; i < num_frames; ++i) {
                // Include pedestrian in the entire interval
                vcd->add_object("", i, pedestrian_args);
                if (i >= 20) {
                    // Include car only above the frame #20
                    vcd->add_object("", i, car_args);
                }
            }

            // Generate json data
            const bool pretty = true;
            const std::string vcd_out_pretty = vcd->stringify(pretty);

            // Save the json info into a file for comparisson
            string out_p = "vcd430_test_objects_without_data_OUT.json";
            fs::path vcd_outp_path = fs::path(asset_path) / fs::path(out_p);
            std::ofstream o_p(vcd_outp_path);
            o_p << vcd_out_pretty << std::endl;
            o_p.close();

            // Read reference JSON file
            string ref_p = "vcd430_test_objects_without_data.json";
            fs::path vcd_refp_path = fs::path(asset_path) / fs::path(ref_p);
            std::ifstream ref_file_data(vcd_refp_path);
            json ref_data;
            ref_file_data >> ref_data;
            ref_file_data.close();

            // Generate JSON structure for comparison
            json test_data = json::parse(vcd_out_pretty);

            REQUIRE(check_json_level(ref_data, test_data));
        }
    }

    GIVEN("A reference json file") {
        THEN("VCD loads and saves properly") {
            // 1.- Create VCD from file
            VCD_ptr vcd = VCD::create();
            const string ref_file = "vcd430_test_create_search_mid.json";
            fs::path vcd_r_path = fs::path(asset_path) / fs::path(ref_file);
            vcd->load(vcd_r_path);
            const string gen_file = "vcd430_test_create_search_mid_TEST.json";
            fs::path vcd_g_path = fs::path(asset_path) / fs::path(gen_file);
            vcd->save(vcd_g_path);
            // 2.- Re-load generated file
            VCD_ptr vcd2 = VCD::create();
            vcd2->load(vcd_g_path);
            // 3.- Compare
            const bool both_equal = check_json_level(
                                        json::parse(vcd->stringify(false)),
                                        json::parse(vcd2->stringify(false)));
            REQUIRE(both_equal);
        }
    }

    GIVEN("Extra metadata values") {
        THEN("The metadata can be updated") {
            // 1.- Create VCD from file
            vcd::VCD_Inner vcd;

            const std::string annotator = "Algorithm001";
            const std::string comment =
                            "Annotations produced automatically - SW v0.1";
            // This is a versioning for the annotation file itself
            const std::string file_version = "2.0";
            // A friendly name
            const std::string name = "vcd_" + file_version + "-" + annotator;
            vcd.add_annotator(annotator);
            vcd.add_comment(comment);
            vcd.add_file_version(file_version);
            vcd.add_name(name);

            // Other customized metadata can be added as well
            vcd::meta_props props = {
                {"target", "Test track"},
                {"origin", "synthetic"}};
            vcd.add_metadata_properties(props);

            json *meta = vcd.get_metadata();
            REQUIRE((*meta)["annotator"] == annotator);
            REQUIRE((*meta)["comment"] == comment);
        }
    }

    GIVEN("A simulated event set") {
        THEN("Simulate an online operation during 1000 frames") {
            // And cut-off every 100 frames into a new VCD
            std::vector<vcd::VCD_Inner> vcds;
            vcds.reserve(10);
            vcd::obj_uid uid = "-1";
            vcd::VCD *vcd_cur = nullptr;
            // Define carlota arguments
            vcd::element_args carlota_args;
            carlota_args.semantic_type = "Car";
            // Simulate
            for (size_t frame_num = 0; frame_num < 1000; ++frame_num) {
                int frame_num_i = static_cast<int>(frame_num);
                if (frame_num % 100 == 0) {
                    // Create new VCD
                    vcds.emplace_back();
                    vcd_cur = &vcds.back();
                    // Optionally we could here dump into JSON file
                    if (frame_num == 0) {
                        // leave VCD to assign uid = 0
                        uid = vcd_cur->add_object("CARLOTA", carlota_args);
                        carlota_args.uid = uid;
                        vcd_cur->add_bbox_to_object(uid, "",
                                                    {0, frame_num_i, 0, 0},
                                                    frame_num);
                    } else {
                        // tell VCD to use last_uid
                        uid = vcd_cur->add_object("CARLOTA", carlota_args);
                        vcd_cur->add_bbox_to_object(uid, "",
                                                    {0, frame_num_i, 0, 0},
                                                    frame_num);
                    }
                } else {
                    // Continue with current VCD
                    vcd_cur->add_bbox_to_object(uid, "",
                                                {0, frame_num_i, 0, 0},
                                                frame_num);
                }
            }
            json* obj = nullptr;
            for (auto& vcd_this : vcds) {
                REQUIRE(vcd_this.get_num_objects() == 1);
                obj = vcd_this.get_object(uid);
                REQUIRE(obj != nullptr);
                REQUIRE((*obj)["name"] == "CARLOTA");
                REQUIRE((*obj)["type"] == "Car");
            }
        }
    }

    GIVEN("A scene definition") {
        THEN("Load all the scene elements") {
            using vcd::CoordinateSystemType;
            VCD_ptr vcd = VCD::create();

            // Generate coordinate system element
            // The main coordinate system (the parent)
            const std::string main_coord_sys_name = "MainOdometry";
            vcd::coord_uid cs1 = vcd->add_coordinate_system(main_coord_sys_name,
                                               CoordinateSystemType::local_cs,
                                               "", {});
            // A child coordinate system with no odometry data
            const std::string ch_coord_sys_name = "ChildOdometry";
            vcd::coord_uid cs2 = vcd->add_coordinate_system(ch_coord_sys_name,
                                               CoordinateSystemType::local_cs,
                                               cs1, {});
            // A child coordinate system with odometry data
            const std::string ch2_coord_sys_name = "ChildOdometry2";
            vcd::coord_uid cs3 = vcd->add_coordinate_system(ch2_coord_sys_name,
                                               CoordinateSystemType::local_cs,
                                               cs1, {1.0, 0.0, 0.0, 0.76,
                                                     0.0, 1.0, 0.0, 0.0,
                                                     0.0, 0.0, 1.0, 1.73,
                                                     0.0, 0.0, 0.0, 1.0});
            // Repeat the same name to check if it is ignored
            vcd::coord_uid cs4 = vcd->add_coordinate_system(main_coord_sys_name,
                                               CoordinateSystemType::local_cs,
                                               "", {});

            // Define some objects
            vcd::element_args pedestrian_args;
            pedestrian_args.semantic_type = "#Pedestrian";
            pedestrian_args.coord_system = cs3;
            std::string pedestrian_uid = vcd->add_object("", pedestrian_args);
            pedestrian_args.uid = pedestrian_uid;

            vcd::element_args car_args;
            car_args.semantic_type = "#Car";
            car_args.coord_system = cs1;
            std::string car_uid = vcd->add_object("", car_args);
            car_args.uid = car_uid;

            // Pedestrian frames (0, 30), Car frames (20, 30)
            const size_t num_frames = 31;
            for (size_t i = 0; i < num_frames; ++i) {
                // Include pedestrian in the entire interval
                vcd->add_object("", i, pedestrian_args);
                if (i >= 20) {
                    // Include car only above the frame #20
                    vcd->add_object("", i, car_args);
                }
            }

            // Generate json data
            const bool pretty = true;
            const std::string vcd_out_pretty = vcd->stringify(pretty);

            // Save the json info into a file for comparisson
            string out_p = "vcd430_test_general_scene_definition_OUT.json";
            fs::path vcd_outp_path = fs::path(asset_path) / fs::path(out_p);
            std::ofstream o_p(vcd_outp_path);
            o_p << vcd_out_pretty << std::endl;
            o_p.close();

            // Read reference JSON file
            string ref_p = "vcd430_test_general_scene_definition.json";
            fs::path vcd_refp_path = fs::path(asset_path) / fs::path(ref_p);
            std::ifstream ref_file_data(vcd_refp_path);
            json ref_data;
            ref_file_data >> ref_data;
            ref_file_data.close();

            // Generate JSON structure for comparison
            json test_data = json::parse(vcd_out_pretty);

            REQUIRE(check_json_level(ref_data, test_data));
        }
    }

    GIVEN("A set of matrix elements") {
        THEN("Save matrix data in the structure") {
            using vcd::CoordinateSystemType;
            VCD_ptr vcd = VCD::create();

            // reate the Object
            vcd::element_args marcos_args;
            marcos_args.semantic_type = "person";
            std::string uid_marcos = vcd->add_object("marcos", marcos_args);
            CHECK(uid_marcos == "0");

            // Add some matrix data to the object
            size_t channels = 1;
            size_t width = 3;
            size_t height = 3;
            vcd->add_mat_to_object(uid_marcos, "3x3",
                                   {1, 2, 3, 4, 5, 6, 7, 8, 9},
                                   channels, width, height);


            channels = 3;
            width = 3;
            height = 3;
            vcd->add_mat_to_object(uid_marcos, "3x3x3",
                                   {1, 2, 3, 4, 5, 6, 7, 8, 9,
                                    1, 2, 3, 4, 5, 6, 7, 8, 9,
                                    1, 2, 3, 4, 5, 6, 7, 8, 9},
                                   channels, width, height);


            // Generate json data
            const bool pretty = true;
            const std::string vcd_out_pretty = vcd->stringify(pretty);

            // Save the json info into a file for comparisson
            string out_p = "vcd430_test_matrix_definition_OUT.json";
            fs::path vcd_outp_path = fs::path(asset_path) / fs::path(out_p);
            std::ofstream o_p(vcd_outp_path);
            o_p << vcd_out_pretty << std::endl;
            o_p.close();

            // Read reference JSON file
            string ref_p = "vcd430_test_matrix_definition.json";
            fs::path vcd_refp_path = fs::path(asset_path) / fs::path(ref_p);
            std::ifstream ref_file_data(vcd_refp_path);
            json ref_data;
            ref_file_data >> ref_data;
            ref_file_data.close();

            // Generate JSON structure for comparison
            json test_data = json::parse(vcd_out_pretty);

            REQUIRE(check_json_level(ref_data, test_data));
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
