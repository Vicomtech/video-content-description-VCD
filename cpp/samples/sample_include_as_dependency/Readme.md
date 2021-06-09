# How to include VCD to external C/C++ project
Using CMake, you only need to add VCD as package and include the module as library.

To add VCD to your project, you need to have a version of VCD installed in the system or in a directory of your choice.

In your CMake project, include the package configuration:

```
[...]

# Find core dependencies
FIND_PACKAGE( vcd_core REQUIRED )

[...]
```

Then, and after the binary definition (i.e. ADD_EXECUTABLE or ADD_LIBRARY call), set vcd as needed library for the linker:

```
[...]

# Link project dependencies
target_link_libraries(${PROJECT_NAME} VCD::vcd_core)

[...]
```

At this point, you can include the VCD header files in your code, and use the VCD features directly.