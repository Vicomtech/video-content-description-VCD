# Define the test asset folder path to be accessed from the test modules
set(TEST_ASSET_FOLDER ${CMAKE_CURRENT_SOURCE_DIR}/../../tests/etc)
add_definitions(-DTEST_ASSET_FOLDER="${TEST_ASSET_FOLDER}")

if (ADD_VCD_CORE)
    add_subdirectory( vcd_core )
endif(ADD_VCD_CORE)
