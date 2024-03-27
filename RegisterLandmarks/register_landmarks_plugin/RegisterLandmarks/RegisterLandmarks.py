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


def main(args):

    sys.stdout.flush()

    # Initialize girder client
    gc = girder_client.GirderClient(apiUrl = args.girderApiUrl)

    print('Input arguments:')
    for a in vars(args):
        print(f'{a}: {getattr(args,a)}')

    os.makedirs('/image_1/')
    os.makedirs('/image_2/')

    # Copying files over
    gc.downloadItem(
        itemId=args.input_image_1,
        dest = '/image_1/'
    )
    gc.downloadItem(
        itemId = args.input_image_2,
        dest = '/image_2/'
    )

    







if __name__=='__main__':

    main(CLIArgumentParser().parse_args())

