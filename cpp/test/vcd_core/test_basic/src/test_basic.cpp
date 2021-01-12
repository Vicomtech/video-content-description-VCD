#define CATCH_CONFIG_MAIN // This definition generates a standard main function in compilation time, so no main function is needed.
#include "catch.hpp" // This is the testing framework. No other library or dependencies are needed.

// -- Project -- //
#include "vcd.h"
#include "vcd_types.h"
#include "setup_strings.h"

using namespace std;
using namespace vcd;

SCENARIO("Create some basic content, without time information, and do some basic search")
{
	GIVEN("Create and empty VCD")
	{
        THEN("Create an object")
        {
            VCD_ptr vcd = VCD::create();
            REQUIRE(vcd.get() != nullptr);
        }

        THEN("Add some data to the object")
        {
            VCD_ptr vcd = VCD::create();
            uint32_t uid_marcos = vcd->add_object("marcos", "person");
            REQUIRE(uid_marcos == 0);

            vcd::types::Bbox head_bbox = vcd::types::Bbox("head", {10, 10, 30, 30});
            types::Bbox body_bbox = types::Bbox("body", {0, 0, 60, 120});
            types::Vec speed_vec = types::Vec("speed", {0.0, 0.2});
            types::Num accel_num = types::Num("accel", 0.1);
            vcd->add_object_data(uid_marcos, head_bbox.get());
            vcd->add_object_data(uid_marcos, body_bbox.get());
            vcd->add_object_data(uid_marcos, speed_vec.get());
            vcd->add_object_data(uid_marcos, accel_num.get());




//            uint32_t uid_peter = vcd.add_object(name="peter", semantic_type="person");

//            vcd->add_object_data(uid=uid_peter, object_data=types.num("age", 38.0));
//            vcd->add_object_data(uid=uid_peter, object_data=types.vec("eyeL", {0, 0, 10, 10}));
//            vcd->add_object_data(uid=uid_peter, object_data=types.vec("eyeR", {0, 0, 10, 10}));
        }

        THEN("Write into string")
        {

        }

        THEN("We can ask VCD")
        {
            // PRELIMINAR TEST OF ATTRIBUTES, PLEASE REMOVE
            types::Bbox box1 = types::Bbox("head", {0, 0, 10, 10});
            box1.add_attribute(types::Boolean("visible", true).get());
        }
	}

	/*GIVEN("Read and write some VCD content")
	{
		std::string fileName = vcd::SetupStrings::testDataPath + "/vcd430_test_create_search_simple_nopretty.json";
		VCD vcd(fileName);

		std::string json_string = vcd.stringify(false);
		std::cout << json_string << std::endl;

		std::string fileNameOut = vcd::SetupStrings::testDataPath + "vcd430_test_create_search_simple_nopretty_out.json";
		vcd.save(fileNameOut, false);
	}
	*/	
}
