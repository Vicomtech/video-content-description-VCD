set(MODULE_NAME vcd_core)
project(${MODULE_NAME})

# Set up sources
file(GLOB MODULE_SRCS "src/*.cpp" "src/*.h")
file(GLOB MODULE_HEADERS "include/*.h" "include/*.hpp")

# Include header files
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

# Create shared library
set( CMAKE_DEBUG_POSTFIX _d )
add_library(${MODULE_NAME} SHARED ${MODULE_SRCS} ${MODULE_HEADERS})

#target_link_libraries(${MODULE_NAME} asls) # if any dependencies
set_target_properties( ${MODULE_NAME} PROPERTIES FOLDER "vcd_modules" )

# Install library and headers (CMAKE_INSTALL_PREFIX is used prepended to these paths; in Linux, this is /usr/local)
# In Windows, this is C:\Program Files\<package-name>
message(MAIN_LIBRARY_NAME : ${MAIN_LIBRARY_NAME})
message(PROJECT_NAME : ${PROJECT_NAME})
message(MODULE_NAME : ${MODULE_NAME})
install(TARGETS ${MODULE_NAME} DESTINATION lib/${MAIN_LIBRARY_NAME})
install(FILES ${MODULE_HEADERS} DESTINATION include/${MAIN_LIBRARY_NAME})
