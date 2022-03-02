"""Download intersection masks for all intersections...

Need to keep intersection IDs... 
process intersections json file
"""

from itertools import count
import click
import json
import os
from tqdm import tqdm
from skimage.io import imsave
from dot.tiles import SlippyMap
from dot.tiles import draw_square_at_proportion, draw_square_at_pixel, get_cropped_centered_img
import stringcase
from dotenv import load_dotenv
load_dotenv()
MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")


#@click.command()
#@click.argument('intersection_file')
#@click.argument('place')
#@click.argument('limit')
def download_intersection_masks(intersection_file, place, limit):

    slippy_map = SlippyMap(zoom=18, token=MAPBOX_TOKEN, place=place)
    img_path = f'{os.getcwd()}/data/{stringcase.alphanumcase(place)}'

    if not os.path.isdir(f'{img_path}_masks'):
        os.mkdir(f'{img_path}_masks')
        
    if not os.path.isdir(f'{img_path}_satimgs'):
        os.mkdir(f'{img_path}_satimgs')

    with open(intersection_file, 'r') as f:
        data = json.load(f)

    print(len(data['features']))
    # with open(intersection_file, 'w') as f:
    #    data = json.load(f)

    counter = 0
    for feature in tqdm(data['features']):

        props = feature['properties']
        node_id = props['nodeid']
        longitude = props['longitude']
        latitude = props['latitude']

        # If the masks and images already exist, don't waste our 50k 
        if os.path.exists(f'{img_path}_masks/mask_{node_id}.png') &\
            os.path.exists(f'{img_path}_satimgs/satimg_{node_id}.png'):
            print(f"Files already exist for {node_id}, skipping...")
            continue
        
        box = slippy_map @ (longitude, latitude)
        print(node_id)
        imsave(f'{img_path}_masks/mask_{node_id}.png', box.figure_ground)
        imsave(f'{img_path}_satimgs/satimg_{node_id}.png', box.image)

        if int(limit) != -1 and counter > int(limit):
            break
        else:
            counter += 1


if __name__ == "__main__":
    download_intersection_masks("dc_intersections.json", "District of Columbia", "10")
    #download_intersection_masks()