
#-------------------------------------------------------------------------------------------------------------------------------
# VCD Core operations
#-------------------------------------------------------------------------------------------------------------------------------
# Include path to testing dependencies
set(TESTING_HEADERS ${CMAKE_SOURCE_DIR}/test/TestingFramework/)
MESSAGE("The path to testing framework is: ${TESTING_HEADERS}")
include_directories(${TESTING_HEADERS})

# Add all sources defined above to the program
include_directories( ${VCD_SOURCE_DIR}/modules/vcd_core/include)
include_directories ( ${CMAKE_BINARY_DIR})  # to include setup_strings
message("Searching setup_string.h at: " ${CMAKE_BINARY_DIR})

# Add demanded test cases
add_subdirectory( test_basic )
add_subdirectory( test_action_properties )
# add_subdirectory( test_converters )
# add_subdirectory( test_image )
# add_subdirectory( test_mesh )
# add_subdirectory( test_modify )
# add_subdirectory( test_sanity )
# add_subdirectory( test_semantics )
# add_subdirectory( test_serializer )
# add_subdirectory( test_stream_frame_properties )
add_subdirectory( test_uuid )


