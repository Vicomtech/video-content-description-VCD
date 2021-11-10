
#-------------------------------------------------------------------------------------------------------------------------------
# VCD Core operations
#-------------------------------------------------------------------------------------------------------------------------------
# Add all sources defined above to the program
include_directories( ${VCD_SOURCE_DIR}/modules/vcd_core/include)
include_directories ( ${CMAKE_BINARY_DIR})  # to include setup_strings

# Add demanded test cases
add_subdirectory( test_basic )
add_subdirectory( test_action_properties )
add_subdirectory( test_uuid )

# add_subdirectory( test_converters )
# add_subdirectory( test_image )
# add_subdirectory( test_mesh )
# add_subdirectory( test_modify )
# add_subdirectory( test_sanity )
# add_subdirectory( test_semantics )
# add_subdirectory( test_serializer )
# add_subdirectory( test_stream_frame_properties )



