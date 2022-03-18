"""Download intersection masks for all intersections...

Need to keep intersection IDs...
process intersections json file
"""

from itertools import count
import json
import click
import psycopg2
import os
from tqdm import tqdm
from skimage.io import imsave
from dot.tiles import SlippyMap
from dot.tiles import draw_square_at_proportion, draw_square_at_pixel, get_cropped_centered_img
import stringcase
from dotenv import load_dotenv

load_dotenv()
MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")

POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_USER = os.getenv('POSTGRES_USER')
HOST_NAME = os.getenv('HOSTNAME')
CURRENT_DIR = 'services/intersections'


def load_intersections_from_db(out_file, limit):
    schema_name = "public"
    table_name = "node_intersections"
    # Connect to your postgres DB
    conn = psycopg2.connect(f"host={HOST_NAME} dbname={POSTGRES_DB} user={POSTGRES_USER} password={POSTGRES_PASSWORD} port=5432")

    # Open a cursor to perform database operations
    cur = conn.cursor()

    cur.execute(f"""select node_id, lat as latitude, 
                    long as longitude from {schema_name}.{table_name} limit {limit};""")

    with open(out_file, 'w') as target:
        json.dump(cur.fetchall(), target)
    conn.close()


def download_intersection_masks(intersection_file, place, limit):
    slippy_map = SlippyMap(zoom=18, token=MAPBOX_TOKEN, place=place)
    img_path = f'{os.getcwd()}/data/{stringcase.alphanumcase(place)}'

    if not os.path.isdir(f'{img_path}_masks'):
        os.mkdir(f'{img_path}_masks')

    if not os.path.isdir(f'{img_path}_satimgs'):
        os.mkdir(f'{img_path}_satimgs')

    with open(intersection_file, 'r') as f:
        data = json.load(f)

    #print(data)

    error_nodes = []
    counter = 0
    for row in tqdm(data):

        node_id = row[0]
        latitude = row[1]
        longitude = row[2]

        # If the masks and images already exist, don't waste our 50k
        if os.path.exists(f'{img_path}_masks/mask_{node_id}.png') & \
                os.path.exists(f'{img_path}_satimgs/satimg_{node_id}.png'):
            print(f"Files already exist for {node_id}, skipping...")
            continue

        box = slippy_map @ (longitude, latitude)
        imsave(f'{img_path}_satimgs/satimg_{node_id}.png', box.image)
        try:
            imsave(f'{img_path}_masks/mask_{node_id}.png', box.figure_ground)
            print(f'Generated mask for {node_id}')
        except:
            error_nodes.append(node_id)
            print(f'Failed to generate mask for {node_id}, skipping')
            continue

        if int(limit) != -1 and counter > int(limit):
            break
        else:
            counter += 1

    if len(error_nodes) > 0:
        with open(f'{img_path}_error.json', 'w') as target:
            json.dump(error_nodes, target)


@click.command()
@click.argument('area_name')
@click.argument('json_name')
@click.argument('limit')
def main(area_name, json_name, limit):
    load_intersections_from_db(json_name, limit)
    download_intersection_masks(json_name, area_name, int(limit))


if __name__ == "__main__":
    main()
