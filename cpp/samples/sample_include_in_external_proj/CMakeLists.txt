CMAKE_MINIMUM_REQUIRED(VERSION 3.1)
# Set project name
PROJECT( sample_include_in_external_proj )

# Find core dependencies
FIND_PACKAGE( vcd_core REQUIRED )

# Set project source files
SET( PROJECT_SRCS
  main.cpp
  )

# Configure project output
ADD_EXECUTABLE( ${PROJECT_NAME} ${PROJECT_SRCS})

# Link project dependencies
target_link_libraries(${PROJECT_NAME} VCD::vcd_core)

set_target_properties(${PROJECT_NAME} PROPERTIES FOLDER "vcd_cpp_samples")
