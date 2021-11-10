#include<iostream>

#include "vcd.h"

int main() {
    // Load VCD library and generate a sequence of N bboxes
    const size_t N = 10000;

    // Create vcd instance
    vcd::VCD_ptr vcd = vcd::VCD::create();

    // Define an object to be tracked during the sequence (a static bbox)
    vcd::element_args obj_args;
    obj_args.semantic_type = "static_object";

    // Add the object to the current vcd definition
    std::string uid_obj = vcd->add_object("the_obj", obj_args);

    // Generate a loop and include a set of bboxes as frames
    const int& rect_w = 50;
    const int& rect_h = 50;
    const int center_x = 400;
    const int center_y = 300;
    for (size_t frame_cont = 0; frame_cont < N; ++frame_cont) {
        vcd->add_bbox_to_object(uid_obj, "obj_bbox",
                                {center_x, center_y, rect_w, rect_h},
                                frame_cont);
    }

    // Export the generated definition to an external file
    const bool pretty = true;
    vcd->save("sample_include_int_external_proj.vcd", pretty);
}
