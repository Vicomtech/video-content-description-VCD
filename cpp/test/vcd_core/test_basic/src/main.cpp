#define CATCH_CONFIG_MAIN // This definition generates a standard main function in compilation time, so no main function is needed.
#include "catch.hpp" // This is the testing framework. No other library or dependencies are needed.

// -- Project -- //
#include "vcd.h"
#include "setup_strings.h"

using namespace std;
using namespace vcd;

SCENARIO("Video Content Description - Objects")
{
	GIVEN("Create and empty VCD")
	{
		VCD vcd;
		string json_string = vcd.stringify(false);
		cout << json_string << endl;

		//vcd::FrameIntervals fi_int = vcd::FrameIntervals(2);
		//FrameIntervals fi_tuple = FrameIntervals({0, 10});
		//FrameIntervals fi_list_tuples = FrameIntervals(ArrayNx2({{0, 10}}));	
		

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
