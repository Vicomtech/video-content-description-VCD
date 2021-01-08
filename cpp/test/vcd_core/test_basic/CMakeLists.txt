#---------------------------------------------------#
#          CMake Project Configuration              #
#---------------------------------------------------#
# CMake will issue a warning if you don't set this
cmake_minimum_required(VERSION 2.6)

##############################
set(TEST_NAME test_basic)
PROJECT( ${TEST_NAME} )
##############################

if(COMMAND cmake_policy)
     cmake_policy(SET CMP0003 NEW)
endif(COMMAND cmake_policy)

#---------------------------------------------------#
#              Project Files                        #
#---------------------------------------------------#
# List source files in a variable so we can use it later more conveniently
set(SOURCE_FILES
	src/test_basic.cpp
)

link_directories( ${CMAKE_BINARY_DIR}/bin )
add_executable( ${TEST_NAME} ${SOURCE_FILES})

# Link libraries that are required for building this application
target_link_libraries( ${TEST_NAME} vcd_core )

set_target_properties(${TEST_NAME} PROPERTIES FOLDER "vcd_tests")

IF( BUILD_TESTS )
     message("Adding test: RUN_test_objects at " ${EXECUTABLE_OUTPUT_PATH}/test_basic)
     add_test( RUN_test_basic  ${EXECUTABLE_OUTPUT_PATH}/test_basic )
ENDIF( BUILD_TESTS )
