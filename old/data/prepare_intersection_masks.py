"""Download intersection masks for all intersections...

Need to keep intersection IDs... 
process intersections json file
"""

import click
import json
import os
from tqdm import tqdm
from skimage.io import imsave
from dot.tiles import SlippyMap
from dotenv import load_dotenv
load_dotenv()


@click.command()
@click.argument('intersection_file')
@click.argument('place')
def download_intersection_masks(intersection_file, place):
    slippy_map = SlippyMap(zoom=18, token=os.getenv('MAPBOX_TOKEN'), place=place)
    os.mkdir('masks')

    with open(intersection_file, 'r') as f:
        data = json.load(f)

    #with open(intersection_file, 'w') as f:
    #    data = json.load(f)
    
    for feature in tqdm(data['features']):
        props = feature['properties']
        nodeid = props['nodeid']
        longitude = props['longitude']
        latitude = props['latitude']
        
        box = slippy_map @ (longitude, latitude)
        
        imsave(f'masks/{nodeid}.png', box.figure_ground)
        


if __name__ == "__main__":
    download_intersection_masks()
