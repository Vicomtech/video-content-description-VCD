cmake_minimum_required(VERSION 3.1)
project( VCD )
set(MAIN_LIBRARY_NAME ${PROJECT_NAME})

set_property(GLOBAL PROPERTY USE_FOLDERS ON) # to organize in folders

set(MAIN_PROJECT_BUILD_PATH ${PROJECT_BINARY_DIR})

# Version
#---------------------------------------------------#
#              Control version                	    #
#---------------------------------------------------#
set(VCD_MAJOR_VERSION 4)
set(VCD_MINOR_VERSION 3)  #Schema changes
set(VCD_VERSION_PATCH 0)  #c++ library changes
set(VCD_PROJECT_VERSION ${VCD_MAJOR_VERSION}.${VCD_MINOR_VERSION}.${VCD_VERSION_PATCH})
message(VCD_MAJOR_VERSION: ${VCD_MAJOR_VERSION})
message(VCD_MINOR_VERSION: ${VCD_MINOR_VERSION})
message(VCD_VERSION_PATCH: ${VCD_VERSION_PATCH})

#---------------------------------------------------#
#              CMake Modules                        #
#---------------------------------------------------#
SET(CMAKE_SCRIPT_PATH ${CMAKE_CURRENT_SOURCE_DIR}/cmake_modules)
SET(LINTER_PATH ${CMAKE_CURRENT_SOURCE_DIR}/3rdparty/lint)
SET(SRC_PATH ${CMAKE_CURRENT_SOURCE_DIR}/modules)
SET(3RD_PARTY_PATH ${CMAKE_CURRENT_SOURCE_DIR}/3rdparty)
INCLUDE(${CMAKE_CURRENT_SOURCE_DIR}/3rdparty/lint/CMake_lint_integration.cmake)
INCLUDE(${CMAKE_SCRIPT_PATH}/CMake_compilation_config.cmake)

# Options
option( ADD_VCD_CORE "Add VCD core" ON)
#option( BUILD_SAMPLES "Build samples" ON)
option( BUILD_TESTS "Build tests" OFF)
#option( BUILD_PERF "Build performance tests" OFF)
option( MAKE_LIB_STATIC "Generate the library as static" OFF)

# Add support C++14 definitions in Ubuntu
IF(UNIX AND NOT APPLE)
    SET(LINUX TRUE)
ENDIF()
#if(UNIX)
#    add_definitions ("-std=c++14")
#endif()

IF(WINDOWS)
    add_definitions(-D_HAS_AUTO_PTR_ETC=1)
ENDIF()

SET ( LIBRARY_OUTPUT_PATH ${PROJECT_BINARY_DIR}/bin CACHE PATH "Single output directory for building all libraries." FORCE )
SET ( EXECUTABLE_OUTPUT_PATH ${PROJECT_BINARY_DIR}/bin CACHE PATH "Single output directory for building all executables." FORCE )

# Add subdirectories
add_subdirectory(modules)

if (BUILD_SAMPLES)
    add_subdirectory(samples)
endif(BUILD_SAMPLES)

if (BUILD_TESTS)
ENABLE_TESTING() #This will generate the RUN_TESTS project in VS
    add_subdirectory(test)
endif(BUILD_TESTS)

if (BUILD_PERF)
    add_subdirectory(perf)
endif(BUILD_PERF)

# Configure template
message(CMAKE_INSTALL_PREFIX : ${CMAKE_INSTALL_PREFIX})
#configure_file("${CMAKE_CURRENT_SOURCE_DIR}/${MAIN_LIBRARY_NAME}.cmake.in" "${PROJECT_BINARY_DIR}/${MAIN_LIBRARY_NAME}Config.cmake" @ONLY)

#---------------------------------------------------#
#               Project Installation                #
#---------------------------------------------------#
# Install <package>Config.cmake, so this library can be found via find_package
# Prepending:
# Unix: /usr/local
# Windows 64b: C:\Program Files\${PROJECT_NAME}
# CONFIGURE_FILE("${PROJECT_SOURCE_DIR}/${MAIN_LIBRARY_NAME}.cmake.release.in" "${PROJECT_BINARY_DIR}/${MAIN_LIBRARY_NAME}Config.release.cmake" @ONLY )
# install(FILES ${PROJECT_BINARY_DIR}/${MAIN_LIBRARY_NAME}Config.release.cmake DESTINATION lib/cmake/${PROJECT_NAME} RENAME "${PROJECT_NAME}Config.cmake")


#---------------------------------------------------#
#               Project Documentation               #
#---------------------------------------------------#
OPTION( BUILD_VCD_DOC "Build VCD documentation" OFF )
IF( BUILD_VCD_DOC )

    FIND_PACKAGE( Doxygen )
    IF( NOT DOXYGEN_FOUND )
        message( FATAL_ERROR "Doxygen is needed to build the documentation. Please install it correctly" )
    ENDIF()

    #-- Configure the Template Doxyfile for our specific project

    #-- Add a custom target to run Doxygen when ever the project is built
    #ADD_CUSTOM_TARGET( Docs ALL
    ADD_CUSTOM_TARGET( Docs
        COMMAND ${DOXYGEN_EXECUTABLE} ${PROJECT_BINARY_DIR}/Doxyfile
        SOURCES ${PROJECT_BINARY_DIR}/Doxyfile )


    # NOTE: the following line has been moved to a script. Read below.
    # default init
    CONFIGURE_FILE( doc/Doxyfile.in ${PROJECT_BINARY_DIR}/Doxyfile @ONLY IMMEDIATE )
    MESSAGE("Generated doxigen file in '${PROJECT_BINARY_DIR}/Doxyfile'")

ENDIF()
