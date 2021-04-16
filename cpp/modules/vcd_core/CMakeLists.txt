set(MODULE_NAME vcd_core)
project(${MODULE_NAME})

# Set up sources
file(GLOB MODULE_SRCS "src/*.cpp" "src/*.h")
file(GLOB MODULE_HEADERS "include/*.h" "include/*.hpp")

# Include header files for json management
include_directories(${3RD_PARTY_PATH}/include/)

if (MAKE_LIB_STATIC)
    set(LIB_TYPE STATIC)
else()
    set(LIB_TYPE SHARED)
endif()

# Create shared library
set( CMAKE_DEBUG_POSTFIX _d )
add_library(${MODULE_NAME} ${LIB_TYPE} ${MODULE_SRCS} ${MODULE_HEADERS})

set_target_properties( ${MODULE_NAME} PROPERTIES FOLDER "vcd_modules" )

# set c++14 as the used c++ standard for this library
DEFINE_CPP_STANDARD_AS_14(${MODULE_NAME})

# Include linter check to source files
SET(SRC_TO_CHECK_LINT ${MODULE_SRCS} ${MODULE_HEADERS})
ADD_LINT_CHECK_TO_TARGET(${MODULE_NAME} "${SRC_TO_CHECK_LINT}")

# Install library and headers (CMAKE_INSTALL_PREFIX is used prepended to these paths; in Linux, this is /usr/local)
# In Windows, this is C:\Program Files\<package-name>
message(MAIN_LIBRARY_NAME : ${MAIN_LIBRARY_NAME})
message(PROJECT_NAME : ${PROJECT_NAME})
message(MODULE_NAME : ${MODULE_NAME})
install(TARGETS ${MODULE_NAME} DESTINATION lib/${MAIN_LIBRARY_NAME})
install(FILES ${MODULE_HEADERS} DESTINATION include/${MAIN_LIBRARY_NAME})
