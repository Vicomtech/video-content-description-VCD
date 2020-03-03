"""
VCD (Video Content Description) library v4.0.0

Project website: http://vcd.vicomtech.org

Copyright (C) 2020, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.0.0.
VCD is distributed under MIT License. See LICENSE.

"""


import warnings


def intersects(fi_a, fi_b):
    max_start_val = max(fi_a['frame_start'], fi_b['frame_start'])
    min_end_val = min(fi_a['frame_end'], fi_b['frame_end'])
    return max_start_val <= min_end_val


def consecutive(fi_a, fi_b):
    if fi_a['frame_end'] + 1 == fi_b['frame_start'] or fi_b['frame_end'] + 1 == fi_a['frame_start']:
        return True
    else:
        return False


def is_inside(frame_num, frame_interval):
    return frame_interval['frame_start'] <= frame_num <= frame_interval['frame_end']


def get_outer_frame_interval(frame_intervals):
    outer = None
    for fi in frame_intervals:
        if outer is None:
            outer = fi
        else:
            if fi['frame_start'] < outer['frame_start']:
                outer['frame_start'] = fi['frame_start']
            if fi['frame_end'] > outer['frame_end']:
                outer['frame_end'] = fi['frame_end']
    return outer


def as_frame_interval_dict(frame_value):
    if isinstance(frame_value, int):
        return {'frame_start': frame_value, 'frame_end': frame_value}
    elif isinstance(frame_value, tuple):
        return {'frame_start': frame_value[0], 'frame_end': frame_value[1]}
    else:
        warnings.warn("WARNING: trying to convert into frame interval dict a: " + type(frame_value))


def as_frame_intervals_array_dict(frame_value):
    # Allow for multiple type of frame_interval arguments (int, tuple, list(tuple))
    if isinstance(frame_value, int):  # The user has given as argument a "frame number"
        frame_intervals = [{'frame_start': frame_value, 'frame_end': frame_value}]
    elif isinstance(frame_value, tuple):  # The user has given as argument a single "frame interval"
        frame_intervals = [{'frame_start': frame_value[0], 'frame_end': frame_value[1]}]
    elif frame_value is None:  # The user has provided nothing: this is a static element
        frame_intervals = []
    else:
        assert isinstance(frame_value, list)  # User provides a list of "frame intervals"
        frame_intervals = frame_value
    return frame_intervals


def fuse_frame_interval_dict(frame_interval, frame_intervals):
    # This function inserts frame_interval into frame_intervals fusing intervals
    assert(isinstance(frame_interval, dict))
    assert (isinstance(frame_intervals, list))
    if len(frame_intervals) == 0:
        return [frame_interval]

    frame_intervals_to_return = frame_intervals
    idx_to_fuse = []  # idx of frame_intervals of the list
    for idx, fi in enumerate(frame_intervals):
        if intersects(fi, frame_interval) or consecutive(fi, frame_interval):
            idx_to_fuse.append(idx)
    if len(idx_to_fuse) == 0:
        # New frame interval, separated, just append
        frame_intervals_to_return.append(frame_interval)
    else:
        # New frame interval has caused some fusion
        frame_intervals_to_return = []
        fused_fi = frame_interval
        for idx, fi in enumerate(frame_intervals):
            if idx in idx_to_fuse:
                fused_fi = {
                    'frame_start': min(fused_fi['frame_start'], fi['frame_start']),
                    'frame_end': max(fused_fi['frame_end'], fi['frame_end'])
                }
            else:
                # also add those not affected by fusion
                frame_intervals_to_return.append(fi)
        frame_intervals_to_return.append(fused_fi)

    return frame_intervals_to_return


def fuse_frame_intervals(frame_intervals):
    # This functions receives a list of frame_intervals and returns another one with
    # non-overlapping intervals
    # e.g. input: [(0, 5), (3, 6), (8, 10)]
    #      output:[(0, 6), (8, 10)]
    assert(isinstance(frame_intervals, list))
    num_fis = len(frame_intervals)

    if num_fis == 1:
        return frame_intervals

    # Read first element
    frame_intervals_fused = [frame_intervals[0]]
    i = 1
    while i < num_fis:
        frame_intervals_fused = fuse_frame_interval_dict(frame_intervals[i], frame_intervals_fused)
        i += 1
    return frame_intervals_fused
