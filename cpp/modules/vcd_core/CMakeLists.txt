set(MODULE_NAME vcd_core)
project(${MODULE_NAME})

# Set up sources
file(GLOB MODULE_SRCS "src/*.cpp" "src/*.h")
file(GLOB MODULE_HEADERS "include/*.h" "include/*.hpp")

# Options
option( ENABLE_GUID "Activate guid functionalities" ON )

# Include header files for json management
include_directories(${3RD_PARTY_PATH}/include/)

if (MAKE_LIB_STATIC)
    set(LIB_TYPE STATIC)
else()
    set(LIB_TYPE SHARED)
endif()

# Generate dependencies
if (ENABLE_GUID)
    add_definitions(-DENABLE_GUID)
    # Configure crossguid project
    set(XG_TESTS OFF)
    add_subdirectory(${3RD_PARTY_PATH}/crossguid ${CMAKE_BINARY_DIR}/crossguid)
    include_directories(${3RD_PARTY_PATH}/crossguid)
    # Set the building configuration depending on the platform
    if (UNIX)
        set(CROSSGUID_LIBS libxg.a uuid)
    endif()
    # In some cases, the 'xg' target does not compile with -fPIC flag, so force it
    set_property(TARGET xg PROPERTY POSITION_INDEPENDENT_CODE ON)
else()
    remove_definitions(-DENABLE_GUID)
endif(ENABLE_GUID)


# Create shared library
set( CMAKE_DEBUG_POSTFIX _d )
add_library(${MODULE_NAME} ${LIB_TYPE} ${MODULE_SRCS} ${MODULE_HEADERS})

set_target_properties( ${MODULE_NAME} PROPERTIES FOLDER "vcd_modules" )
# Change the output name from vcd_core to vcd
# set_target_properties( ${MODULE_NAME} PROPERTIES OUTPUT_NAME "vcd")

## Add a namespace alias.
# This is useful to abstract over use of the library as installed vs
#  subdirectory build
add_library(VCD::${MODULE_NAME} ALIAS ${MODULE_NAME})

target_include_directories(${MODULE_NAME}
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)

if (ENABLE_GUID)
    if(UNIX)
        message("CROSSGUID_LIBS=${CROSSGUID_LIBS}")
        add_dependencies(${MODULE_NAME} xg)
        target_link_directories(${MODULE_NAME} PRIVATE ${CMAKE_BINARY_DIR}/bin)
        target_link_libraries( ${MODULE_NAME} ${CROSSGUID_LIBS})
    else()
        add_dependencies(${MODULE_NAME} xg)
        target_link_libraries( ${MODULE_NAME} PRIVATE xg)
    endif()
endif()

# set c++14 as the used c++ standard for this library
DEFINE_CPP_STANDARD_AS_17(${MODULE_NAME})

# Include linter check to source files
SET(SRC_TO_CHECK_LINT ${MODULE_SRCS} ${MODULE_HEADERS})
ADD_LINT_CHECK_TO_TARGET(${MODULE_NAME} "${SRC_TO_CHECK_LINT}")

#---------------------------------------------------#
#                Module Installation                #
#---------------------------------------------------#
# Install library and headers (CMAKE_INSTALL_PREFIX is used prepended to these
# paths; in Linux, this is /usr/local)
# In Windows, this is C:\Program Files\<package-name>
message(MAIN_LIBRARY_NAME : ${MAIN_LIBRARY_NAME})
message(PROJECT_NAME : ${PROJECT_NAME})
message(MODULE_NAME : ${MODULE_NAME})
message(3RD_PARTY_PATH : ${3RD_PARTY_PATH})
#install(TARGETS ${MODULE_NAME} DESTINATION lib/${MAIN_LIBRARY_NAME})
#install(FILES ${MODULE_HEADERS} DESTINATION include/${MAIN_LIBRARY_NAME})

include(GNUInstallDirs)
set(INSTALL_CONFIGDIR ${CMAKE_INSTALL_LIBDIR}/cmake/vcd)

install(
    TARGETS
      ${MODULE_NAME}
    EXPORT
      ${MODULE_NAME}Targets
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)

install(EXPORT ${MODULE_NAME}Targets
    FILE ${MODULE_NAME}Targets.cmake
    NAMESPACE VCD::
    DESTINATION ${INSTALL_CONFIGDIR}
)

install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/include/
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/vcd
    FILES_MATCHING PATTERN "*.h*"
)

message(CMAKE_INSTALL_LIBDIR : ${CMAKE_INSTALL_LIBDIR})
message(INSTALL_CONFIGDIR : ${INSTALL_CONFIGDIR})

#---------------------------------------------------#
#            Module ConfigVersion file              #
#---------------------------------------------------#
include(CMakePackageConfigHelpers)
write_basic_package_version_file(
    ${CMAKE_CURRENT_BINARY_DIR}/${MODULE_NAME}ConfigVersion.cmake
    VERSION ${VCD_PROJECT_VERSION}
    COMPATIBILITY AnyNewerVersion
)

configure_package_config_file(
    ${CMAKE_CURRENT_LIST_DIR}/cmake/${MODULE_NAME}Config.cmake.in
    ${CMAKE_CURRENT_BINARY_DIR}/${MODULE_NAME}Config.cmake
    INSTALL_DESTINATION ${INSTALL_CONFIGDIR}
)

## Install all the helper files
install(
    FILES
      ${CMAKE_CURRENT_BINARY_DIR}/${MODULE_NAME}Config.cmake
      ${CMAKE_CURRENT_BINARY_DIR}/${MODULE_NAME}ConfigVersion.cmake
    DESTINATION ${INSTALL_CONFIGDIR}
)

message(PROJECT_VERSION : ${VCD_PROJECT_VERSION})
