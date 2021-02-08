"""
VCD (Video Content Description) library v4.3.1

Project website: http://vcd.vicomtech.org

Copyright (C) 2021, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.3.1.
VCD is distributed under MIT License. See LICENSE.

"""

import vcd.core as core
import vcd.utils as utils


# NOTE: This module is under development. It does not exhaustively analyze the content for coherency.

def check_frame_intervals(vcd):
    # This function analyzes a given vcd content and evaluates its internal coherence
    assert(isinstance(vcd, core.VCD))

    fis_vcd = vcd.get_frame_intervals().get_dict()

    objects = vcd.get_all(core.ElementType.object)
    actions = vcd.get_all(core.ElementType.action)
    events = vcd.get_all(core.ElementType.event)
    contexts = vcd.get_all(core.ElementType.context)
    relations = vcd.get_all(core.ElementType.relation)

    fis_objects = []
    fis_actions = []
    fis_events = []
    fis_contexts = []
    fis_relations = []
    if objects is not None:
        for object in objects.values():
            fis_objects += object.get('frame_intervals')
    if actions is not None:
        for action in actions.values():
            fis_actions += action.get('frame_intervals')
    if events is not None:
        for event in events.values():
            fis_events += event.get('frame_intervals')
    if contexts is not None:
        for context in contexts.values():
            fis_contexts += context.get('frame_intervals')
    if relations is not None:
        for relation in relations.values():
            fis_relations += relation.get('frame_intervals')

    fis_elements = utils.fuse_frame_intervals(
        fis_objects + fis_actions + fis_events + fis_contexts + fis_relations
    )

    valid = True
    if not len(fis_vcd) == len(fis_elements):
        valid = False
    else:
        equals = list(map(lambda t1, t2: t1 == t2, fis_vcd, fis_elements))
        if False in equals:
            valid = False

    return valid


def check_frames_elements(vcd):
    # This function analyzes a given vcd content and evaluates its internal coherence
    assert (isinstance(vcd, core.VCD))

    objects = vcd.get_all(core.ElementType.object)
    actions = vcd.get_all(core.ElementType.action)
    events = vcd.get_all(core.ElementType.event)
    contexts = vcd.get_all(core.ElementType.context)
    relations = vcd.get_all(core.ElementType.relation)

    elements_array = [objects, actions, events, contexts, relations]
    names = ['objects', 'actions', 'events', 'contexts', 'relations']

    for counter, elements in enumerate(elements_array):
        if elements is not None:
            for element_key, element_value in elements.items():
                fis_elements_dicts = element_value.get('frame_intervals')
                for fis_element_dict in fis_elements_dicts:
                    frame_start = fis_element_dict['frame_start']
                    frame_end = fis_element_dict['frame_end']

                    for frame_num in range(frame_start, frame_end):
                        # Check if this frame_num has an entry with the element
                        frame = vcd.get_frame(frame_num)
                        if frame is None:
                            return False

                        if element_key not in frame[names[counter]]:
                            return False

    return True
