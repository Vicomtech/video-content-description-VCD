CMAKE_MINIMUM_REQUIRED(VERSION 3.1)
# Set project name
PROJECT( sample_include_source_code )

# Add vcd sources to the project
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/../..
                 ${CMAKE_BINARY_DIR}/vcd/
                 EXCLUDE_FROM_ALL)

# Set project source files
SET( PROJECT_SRCS
  main.cpp
  )

# Configure project output
ADD_EXECUTABLE( ${PROJECT_NAME} ${PROJECT_SRCS})

# Link project dependencies
target_link_libraries(${PROJECT_NAME} VCD::vcd_core)

set_target_properties(${PROJECT_NAME} PROPERTIES FOLDER "vcd_cpp_samples")
