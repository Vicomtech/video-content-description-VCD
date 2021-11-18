/*
* VCD (Video Content Description) library v4.3.0
*
* Project website: http://vcd.vicomtech.org
*
* Copyright (C) 2020, Vicomtech (http://www.vicomtech.es/),
* (Spain) all rights reserved.

* VCD is a C++ library to create and manage VCD content version 4.3.0.
* VCD is distributed under MIT License. See LICENSE.
* 
*/

#ifndef CORE_EXP_H_
#define CORE_EXP_H_

// =====================================================================================
// MACRO FOR IMPORTING AND EXPORTING FUNCTIONS AND CLASSES FROM DLL
// =====================================================================================
// When the symbol vcd_core_EXPORTS is defined in a project functions and
// classes are exported. In other cases they are imported from the DLL.
#if defined VCD_STATIC
    #define CORE_LIB
#else
    #ifdef vcd_core_EXPORTS  // this is the DLL
        #if defined _WIN32 || defined _WIN64
            #define CORE_LIB __declspec(dllexport)
        #else
            #define CORE_LIB
        #endif
    #else  // this is the client of the DLL
        #if defined _WIN32 || defined _WIN64
            #define CORE_LIB __declspec(dllimport)
        #else
            #define CORE_LIB
        #endif
    #endif
#endif

#endif  // CORE_EXP_H_
