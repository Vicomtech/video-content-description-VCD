![VCD Video Content Description](../doc/logo/VCD_logo_2020.png)
# Video Content Description (VCD) for C++

This version of the VCD library is a C++ implementation of a subset of features in the original VCD implementation focused on constrained data acquisition environments like embedded circuits or onboard systems.

The compilation structure is based on CMake.

## Install

To build and install the VCD-C++ library, first, generate the project using CMake commands, and then build it with the selected compilation system. In this document, we expose the steps to build and install the library on Linux machines (tested on Ubuntu 18.04).

First, open a terminal, and clone the repository content to your machine on the desired folder:

```
$ git clone git@github.com:Vicomtech/video-content-description-VCD.git
```

Then go to the C++ version folder:

```
$ cd video-content-description-VCD/cpp
```

Create a folder to store the generated binaries, and go inside:

```
$ mkdir build
$ cd build
```

Then, create the CMake project and build the library:

```
$ cmake ..
$ make -j8
```

At this point, you should have all the binaries generated in the folder structure inside _build_. To install the library in your system, just call the install option of the make command:

```
$ sudo make install
```

## Install in a specific folder

In some cases, you could not have root permissions to install the library in the main system folders, and you could need to install it in an arbitrary folder. For those cases, you can define the desired target folder in the CMake generation call and have all the final binary and configuration elements in that target folder.

To define a specific installation folder, go to the build folder, and specify the target location to CMake like this:

```
$ cmake -DCMAKE_INSTALL_PREFIX=<abs path to the target folder> ..
```

And then follow the same process to generate the final binaries:

```
$ make -j8
$ make install
```

Note that in this case, the _sudo_ invocation is not needed.

## How to include in your CMake project

There are two options to include VCD-C++ in your CMake project. You can include the installed binaries as dependency or include the VCD source code as part of your project.

### Include VCD as dependency

Once you have the library installed, you can include those binaries using the _find_package_ function of CMake in the CMakeLists.txt file of your project:

```
[...]

# Find core dependencies
FIND_PACKAGE( vcd_core REQUIRED )

[...]
```

Once you have the final binary defined (i.e. ADD_EXECUTABLE or ADD_LIBRARY call), you have to include the VCD binaries for linking:

```
[...]

# Configure project output
ADD_EXECUTABLE( ${PROJECT_NAME} ${PROJECT_SRCS})

[...]

# Link project dependencies
target_link_libraries(${PROJECT_NAME} VCD::vcd_core)

[...]
```

Then, you can build your project.

In the case that the files are not in the finding paths of CMake, the project could not be able to find the VCD installation directory. In that case, CMake will suggest defining the VCD configuration path ('vcd_core_DIR' parameter) to fix this error.

You can define this parameter in the CMake call to generate YOUR project, just like this:

```
$ cmake -Dvcd_core_DIR=<abs path to the vcd install folder>/lib/cmake/vcd ..
```

### Include VCD source code

Once you have the library code downloaded, you can include those source files as part of your project. During the building of your project, the VCD library should be generated inside the binary folder of your project, and then it could be included in the linkage of the final files.

To include the source code as part of your project, add the directory where the main CMakeLists.txt file of VCD is located:

```
[...]

# Add vcd sources to the project
add_subdirectory(<Abs path to the vcd source directory>
                 ${CMAKE_BINARY_DIR}/vcd/
                 EXCLUDE_FROM_ALL)

[...]
```

In this call, you have to define manually the path to VCD source code. The other two parameters define the path in the binary folder where the VCD library will be stored (_${CMAKE_BINARY_DIR}/vcd/_) and exclude the VCD source to be loaded in the IDE (_EXCLUDE_FROM_ALL_), in the case of using one.

Once you have the source code included, and after define the project binary (i.e. ADD_EXECUTABLE or ADD_LIBRARY call), you have to include the VCD module for linking:

```
[...]

# Configure project output
ADD_EXECUTABLE( ${PROJECT_NAME} ${PROJECT_SRCS})

[...]

# Link project dependencies
target_link_libraries(${PROJECT_NAME} VCD::vcd_core)

[...]
```

Then, you can build your project.
