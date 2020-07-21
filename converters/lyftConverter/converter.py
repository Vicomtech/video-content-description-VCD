"""
VCD (Video Content Description) library v4.3.0

Project website: http://vcd.vicomtech.org

Copyright (C) 2020, Vicomtech (http://www.vicomtech.es/),
(Spain) all rights reserved.

VCD is a Python library to create and manage VCD content version 4.3.0.
VCD is distributed under MIT License. See LICENSE.

"""


import sys
sys.path.insert(0, "../..")
import vcd.core as core
import vcd.types as types
import os
from lyft_dataset_sdk.lyftdataset import LyftDataset

'''
Author: Mikel García Fonseca

Parser from Lyft Level 5 Dataset format to VCD (Video Content Descriptor)

Lyft Level 5 uses the same data format as nuScenes

The nuScenes format has 13 main building blocks:
    1. scene - 20 second snippet of a car's journey.
    2. sample - An annotated snapshot of a scene at a particular timestamp.
    3. sample_data - Data collected from a particular sensor.
    4. sample_annotation - An annotated instance of an object within our interest.
    5. instance - Enumeration of all object instance we observed.
    6. category - Taxonomy of object categories (e.g. vehicle, human).
    7. attribute - Property of an instance that can change while the category remains the same.
    8. visibility - Fraction of pixels visible in all the images collected from 6 different cameras..
    9. sensor - A specific sensor type.
    10. calibrated sensor - Definition of a particular sensor as calibrated on a particular vehicle.
    11. ego_pose - Ego vehicle poses at a particular timestamp.
    12. log - Log information from which the data was extracted.
    13. map - Map data that is stored as binary semantic masks from a top-down view. 

    More information of this format at: https://www.nuscenes.org/data-format

We parse all the data stored in this files into a single VCD file, one file for each Scene.

The folder with the Lyft data should have the following structure

+-- nuscenes
|   +-- maps (optional)
|   +-- lidar (optional)
|   +-- images (optional)
|   +-- v1.02-train
|   |    +-- attribute.json
|   |    +-- calibrated_sensor.json
|   |    +-- category.json
|   |    +-- ego_pose.json
|   |    +-- instance.json
|   |    +-- log.json
|   |    +-- map.json
|   |    +-- sample.json
|   |    +-- sample_annotation.json
|   |    +-- sample_data.json
|   |    +-- scene.json
|   |    +-- sensor.json
|   |    +-- visibility.json

The 13 json files from the v1.x-... folder is from where we retrieve the data to parse as VCD.
'''
dataset_path = '/home/VICOMTECH/mgarcia/Lyft_parser/data/v1.02-train'
lyft_folder = '/home/VICOMTECH/mgarcia/Lyft_parser/data/v1.02-train/v1.02-train'

# Read Lyft Level 5 data

level5data = LyftDataset(data_path=dataset_path, json_path=lyft_folder, verbose=True)

vcd = core.VCD()
scene_n = 1

for my_scene in level5data.scene:
    vcd = core.VCD()
    print("Parsing Scene nº: ", scene_n)

    # Add sensors to VCD
    for sensor in level5data.sensor:
        if sensor['modality'] == 'camera':
            vcd.add_stream(sensor['channel'], '', sensor['token'], core.StreamType.camera)
        elif sensor['modality'] == 'lidar':
            vcd.add_stream(sensor['channel'], '', sensor['token'], core.StreamType.lidar)
        else:
            vcd.add_stream(sensor['channel'], '', sensor['token'], core.StreamType.other)

    # Dictionary to map between frame nº and sample_token
    frame_token_map = {}
    token_sample = my_scene['first_sample_token']
    current_sample = level5data.get('sample', token_sample)
    # Add metadata to VCD
    vcd.data['vcd']['metadata'].setdefault('properties', dict())
    vcd.data['vcd']['metadata']['properties']['scene_token'] = my_scene['token']
    vcd.data['vcd']['metadata']['properties']['scene_name'] = my_scene['name']
    vcd.data['vcd']['metadata']['properties']['scene_description'] = my_scene['description']

    log = level5data.get('log', my_scene['log_token'])
    vcd.data['vcd']['metadata']['properties']['log_token'] = log['token']
    vcd.data['vcd']['metadata']['properties']['log_file'] = log['logfile']
    vcd.data['vcd']['metadata']['properties']['vehicle'] = log['vehicle']
    vcd.data['vcd']['metadata']['properties']['date'] = log['date_captured']
    vcd.data['vcd']['metadata']['properties']['location'] = log['location']

    map = level5data.get('map', log['map_token'])
    vcd.data['vcd']['metadata']['properties']['map_token'] = map['token']
    vcd.data['vcd']['metadata']['properties']['map_category'] = map['category']
    vcd.data['vcd']['metadata']['properties']['map_filename'] = map['filename']

    # Create dictionary to map between frame nº and sample_token
    for frame_num in range(0, my_scene['nbr_samples']):
        frame_token_map[current_sample['token']] = frame_num
        if current_sample['next'] != '':
            current_sample = level5data.get('sample', current_sample['next'])

    # Create dictionary to map between instance_token to VCD object uids
    objects_uids = {}
    for instance in level5data.instance:
        first_annotation = level5data.get('sample_annotation', instance['first_annotation_token'])
        last_annotation = level5data.get('sample_annotation', instance['last_annotation_token'])
        category_token = instance['category_token']
        category = level5data.get('category', category_token)
        sample = level5data.get('sample', first_annotation['sample_token'])
        scene = level5data.get('scene', sample['scene_token'])

        if scene['token'] == my_scene['token']:
            objects_uids[instance['token']] = vcd.add_object(instance['token'], category['name'])

    current_sample = level5data.get('sample', token_sample)

    # Add Sensors and some frame properties
    for frame_num in range(0, my_scene['nbr_samples']):
        vcd.add_frame_properties(frame_num, {"timestamp": str(current_sample['timestamp'])})
        vcd.add_frame_properties(frame_num, {"token": current_sample['token']})

        for sensor in current_sample['data']:
            data = level5data.get('sample_data', current_sample['data'][sensor])
            vcd.add_frame_properties(frame_num, {"token": current_sample['token']})

        if current_sample['next'] != '':
            current_sample = level5data.get('sample', current_sample['next'])

    current_sample = level5data.get('sample', token_sample)

    # Add annotation data and calibrated sensor data.
    for frame_num in range(0, my_scene['nbr_samples']):
        for annotation_token in current_sample['anns']:

            annotation = level5data.get('sample_annotation', annotation_token)
            instance_token = annotation['instance_token']
            instance = level5data.get('instance', instance_token)
            category_token = instance['category_token']
            category = level5data.get('category', category_token)
            attribute_token = annotation['attribute_tokens']

            if len(attribute_token) > 0:
                attribute = level5data.get('attribute', attribute_token[0])
                vcd.add_object_data(objects_uids[instance['token']],
                                    types.text('attribute', attribute['name']), (frame_num, frame_num))

            visibility_token = annotation['visibility_token']

            vcd.add_object_data(objects_uids[instance['token']],
                                types.point3d('translation', tuple(annotation['translation'])), (frame_num, frame_num ))
            vcd.add_object_data(objects_uids[instance['token']],
                                types.vec('size', tuple(annotation['size'])), (frame_num, frame_num))
            vcd.add_object_data(objects_uids[instance['token']],
                                types.vec('rotation', tuple(annotation['rotation'])), (frame_num, frame_num))

            vcd.add_object_data(objects_uids[instance['token']],
                                types.num('num_lidar_pts', annotation['num_lidar_pts']), (frame_num, frame_num))
            vcd.add_object_data(objects_uids[instance['token']],
                                types.num('num_radar_pts', annotation['num_radar_pts']), (frame_num, frame_num))

            vcd.add_object_data(objects_uids[instance['token']],
                                types.text('sample_annotation_token', annotation['token']), (frame_num, frame_num ))
            if visibility_token != '':
                visibility = level5data.get('visibility', visibility_token)
                vcd.add_object_data(objects_uids[instance['token']],
                                    types.text('visibility', visibility['level']),
                                    (frame_num, frame_num))

        for sensor in current_sample['data']:
            data = level5data.get('sample_data', current_sample['data'][sensor])
            ego_pose = level5data.get('ego_pose', data['ego_pose_token'])
            calibrated_sensor = level5data.get('calibrated_sensor', data['calibrated_sensor_token'])
            # Check if the data has width and
            if 'width' in data:
                vcd.add_stream_properties(data['channel'],
                                          {'camera_intrinsic': calibrated_sensor['camera_intrinsic'],
                                           'calibrated_sensor_token': calibrated_sensor['token'],
                                           'sensor_rotation': calibrated_sensor['rotation'],
                                           'sensor_translation': calibrated_sensor['translation'],
                                           'calibrated_sensor_token': calibrated_sensor['token'],
                                           'ego_translation': ego_pose['translation'],
                                           'ego_rotation': ego_pose['rotation'],
                                           'ego_pose_timestamp': ego_pose['timestamp'],
                                           'ego_pose_token': ego_pose['token'],
                                           'key_frame': data['is_key_frame'],
                                           'filename': data['filename'],
                                           'width': data['width'],
                                           'height': data['height'],
                                           'fileformat': data['fileformat'],
                                           'sample_data_token': data['token'],
                                           'timestamp': data['timestamp']}, frame_num)
            else:
                vcd.add_stream_properties(data['channel'],
                                          {'camera_intrinsic': calibrated_sensor['camera_intrinsic'],
                                           'calibrated_sensor_token': calibrated_sensor['token'],
                                           'sensor_rotation': calibrated_sensor['rotation'],
                                           'sensor_translation': calibrated_sensor['translation'],
                                           'calibrated_sensor_token': calibrated_sensor['token'],
                                           'ego_translation': ego_pose['translation'],
                                           'ego_rotation': ego_pose['rotation'],
                                           'ego_pose_timestamp': ego_pose['timestamp'],
                                           'ego_pose_token': ego_pose['token'],
                                           'key_frame': data['is_key_frame'],
                                           'filename': data['filename'],
                                           'fileformat': data['fileformat'],
                                           'sample_data_token': data['token'],
                                           'timestamp': data['timestamp']}, frame_num)

        if current_sample['next'] != '':
            current_sample = level5data.get('sample', current_sample['next'])

    # Write vcd files
    if not os.path.isfile('.vcd_files/vcd_lyft_'+my_scene['token']+'.json'):
        vcd.save('vcd_files/vcd_lyft_'+my_scene['token']+'.json', True)
    scene_n += 1

