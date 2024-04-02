"""

Registering two images based on corresponding landmarks using SpatialData


"""

import os
import sys

import numpy as np

from shapely.geometry import Polygon, Point, box
import tiffslide as ts
import large_image

import spatialdata as sd
import spatialdata_plot

import geopandas as gpd

from io import BytesIO
from PIL import Image
from math import floor
import json

import girder_client
from ctk_cli import CLIArgumentParser


def read_image_array(image_source):

    image_metadata = image_source.getMetadata()
    image_X, image_Y = image_metadata['sizeX'], image_metadata['sizeY']

    if 'frames' in image_metadata:
        image_array = np.zeros((len(image_metadata['frames']),image_Y,image_X),dtype = np.uint8)
        for i in range(len(image_metadata['frames'])):
            image_array[i,:,:] += image_source.getRegion(
                format = large_image.constants.TILE_FORMAT_NUMPY,
                region = {
                    'left': 0,
                    'top': 0,
                    'right': image_X,
                    'bottom': image_Y
                },
                frame = i
            )
    else:
        image_array = image_source.getRegion(
            format = large_image.constants.TILE_FORMAT_NUMPY,
            region = {
                'left': 0,
                'top': 0,
                'right': image_X,
                'bottom': image_Y
            }
        )
    
    return image_array

def shapely_from_json(json_annotations, scale_list):

    shape_list = []
    for el in json_annotations['annotation']['elements']:

        if el['type']=='point':
            shape_list.append(
                Point(el['center'][0]/scale_list[0],el['center'][1]/scale_list[0])
            )
    
    return shape_list

def postpone_transformation(
    sdata: sd.SpatialData,
    transformation: sd.transformations.BaseTransformation,
    source_coordinate_system: str,
    target_coordinate_system: str,
):
    for element_type, element_name, element in sdata._gen_elements():
        old_transformations = sd.transformations.get_transformation(element, get_all=True)
        if source_coordinate_system in old_transformations:
            old_transformation = old_transformations[source_coordinate_system]
            sequence = sd.transformations.Sequence([old_transformation, transformation])
            sd.transformations.set_transformation(element, sequence, target_coordinate_system)


def main(args):

    sys.stdout.flush()

    # Initialize girder client
    gc = girder_client.GirderClient(apiUrl = args.girderApiUrl)

    print('Input arguments:')
    for a in vars(args):
        print(f'{a}: {getattr(args,a)}')

    os.makedirs('/image_1/')
    os.makedirs('/image_2/')
    os.makedirs('/registered/')

    # Copying files over
    gc.downloadItem(
        itemId=args.input_image_1,
        dest = '/image_1/'
    )
    gc.downloadItem(
        itemId = args.input_image_2,
        dest = '/image_2/'
    )

    image_1_name = os.listdir('/image_1/')[0]
    image_2_name = os.listdir('/image_2/')[0]

    # Initializing large-image objects
    image_1 = large_image.open(f'/image_1/{image_1_name}')
    image_2 = large_image.open(f'/image_2/{image_2_name}')

    # Getting the image array for each (CYX format)
    image_1_array = read_image_array(image_1)
    image_2_array = read_image_array(image_2)

    # Reading landmarks
    image_1_landmarks = gc.get(f'/annotation/{args.input_landmarks_1}')
    image_2_landmarks = gc.get(f'/annotation/{args.input_landmarks_2}')

    image_1_shapes = shapely_from_json(image_1_landmarks)
    image_2_shapes = shapely_from_json(image_2_landmarks)

    image_1_sd = sd.SpatialData(
        images = {
            'image_1': sd.models.Image2DModel.parse(image_1_array)
        },
        shapes = {
            'image_1_landmarks': sd.models.ShapesModel.parse(
                np.squeeze(np.array([list(i.coords) for i in image_1_shapes])),
                geometry = 0,
                radius = 100
            )
        }
    )
    image_1_sd.rename_coordinate_systems({'global':'image_1_crs'})
    print(image_1_sd)

    image_2_sd = sd.SpatialData(
        images = {
            'image_2': sd.models.Image2DModel.parse(image_2_array)
        },
        shapes = {
            'image_2_landmarks': sd.models.ShapesModel.parse(
                np.squeeze(np.array([list(i.coords) for i in image_2_shapes])),
                geometry = 0,
                radius = 100
            )
        }
    )
    image_2_sd.rename_coordinate_systems({'global':'image_2_crs'})
    print(image_2_sd)

    # Concatenating spatialdata objects
    multi_sdata = sd.concatenate([image_1_sd, image_2_sd])
    print(multi_sdata)

    # Aligning based on landmarks
    print('Determining transform')
    transform = sd.transformations.align_elements_using_landmarks(
        references_coords = multi_sdata.shapes['image_1_landmarks'],
        moving_coords = multi_sdata.shapes['image_2_landmarks'],
        reference_element = multi_sdata.images['image_1'],
        moving_element = multi_sdata.images['image_2'],
        reference_coordinate_system='image_1_crs',
        moving_coordinate_system='image_2_crs',
        new_coordinate_system='aligned'
    )
    print('------------------------------')
    print(transform)
    print('--------------------------------')

    print('Postponing transformation')
    postpone_transformation(
        sdata = multi_sdata,
        transformation = transform,
        source_coordinate_system='image_2_crs',
        target_coordinate_system='aligned'
    )
    print('Done postponing')
    print(multi_sdata)

    # Writing aligned image 
    









if __name__=='__main__':

    main(CLIArgumentParser().parse_args())

