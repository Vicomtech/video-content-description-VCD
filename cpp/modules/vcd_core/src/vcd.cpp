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
#include "vcd.h"

#include "vcd_impl.h"

namespace vcd {

VCD::~VCD() {
}

std::unique_ptr<VCD>
VCD::create(const std::string& fileName, const bool validation) {
    return std::make_unique<VCD_Impl>(fileName, validation);
}

std::unique_ptr<VCD>
VCD::create(const bool validation) {
    return VCD::create("", validation);
}

VCD_UID::~VCD_UID() {
}

FrameValue::FrameValue(const int frameIndex_) {
    frameIndex = frameIndex_;
    frameStart = -1;
    frameEnd = -1;
}

FrameValue::FrameValue(const int frameStart_, const int frameEnd_) {
    frameIndex = -1;
    frameStart = frameStart_;
    frameEnd = frameEnd_;
}

};  // namespace vcd
