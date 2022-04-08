"""Download intersection masks for all intersections...

Need to keep intersection IDs...
process intersections json file
"""

from itertools import count
import json
import click
import psycopg2
import time
import os
from tqdm import tqdm
from skimage.io import imsave
from dot.tiles import SlippyMap
from dot.tiles import draw_square_at_proportion, draw_square_at_pixel, get_cropped_centered_img
import stringcase
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")

POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_PASSWORD = os.getenv('PGPASSWORD')
POSTGRES_USER = os.getenv('POSTGRES_BUILDER_USER')
HOST_NAME = os.getenv('HOSTNAME')
CURRENT_DIR = 'services/intersections'

BEGIN_WORKING_REGION_STATE = 8
SAT_IMAGE_PROCESSING_REGION_STATE = 9
SAT_IMAGE_COMPLETE_REGION_STATE = 10
SLEEP_DURATION = 60

REGION_OFFSET_JSON = 'data/sat_img_offsets.json'
REGION_OFFSETS = {}

conn = None
cur = None

state_dict = {
    'AL': 'Alabama, United States',
    'AK': 'Alaska, United States',
    'AZ': 'Arizona, United States',
    'AR': 'Arkansas, United States',
    'CA': 'California, United States',
    'CZ': 'Canal Zone, United States',
    'CO': 'Colorado, United States',
    'CT': 'Connecticut, United States',
    'DE': 'Delaware, United States',
    'DC': 'District of Columbia, United States',
    'FL': 'Florida, United States',
    'GA': 'Georgia, United States',
    'GU': 'Guam, United States',
    'HI': 'Hawaii, United States',
    'ID': 'Idaho, United States',
    'IL': 'Illinois, United States',
    'IN': 'Indiana, United States',
    'IA': 'Iowa, United States',
    'KS': 'Kansas, United States',
    'KY': 'Kentucky, United States',
    'LA': 'Louisiana, United States',
    'ME': 'Maine, United States',
    'MD': 'Maryland, United States',
    'MA': 'Massachusetts, United States',
    'MI': 'Michigan, United States',
    'MN': 'Minnesota, United States',
    'MS': 'Mississippi, United States',
    'MO': 'Missouri, United States',
    'MT': 'Montana, United States',
    'NE': 'Nebraska, United States',
    'NV': 'Nevada, United States',
    'NH': 'New Hampshire, United States',
    'NJ': 'New Jersey, United States',
    'NM': 'New Mexico, United States',
    'NY': 'New York, United States',
    'NC': 'North Carolina, United States',
    'ND': 'North Dakota, United States',
    'OH': 'Ohio, United States',
    'OK': 'Oklahoma, United States',
    'OR': 'Oregon, United States',
    'PA': 'Pennsylvania, United States',
    'PR': 'Puerto Rico, United States',
    'RI': 'Rhode Island, United States',
    'SC': 'South Carolina, United States',
    'SD': 'South Dakota, United States',
    'TN': 'Tennessee, United States',
    'TX': 'Texas, United States',
    'UT': 'Utah, United States',
    'VT': 'Vermont, United States',
    'VI': 'Virgin Islands, United States',
    'VA': 'Virginia, United States',
    'WA': 'Washington, United States',
    'WV': 'West Virginia, United States',
    'WI': 'Wisconsin, United States',
    'WY': 'Wyoming, United States',
    'ALABAMA': 'Alabama, United States',
    'ALASKA': 'Alaska, United States',
    'ARIZONA': 'Arizona, United States',
    'ARKANSAS': 'Arkansas, United States',
    'CALIFORNIA': 'California, United States',
    'CANALZONE': 'Canal Zone, United States',
    'COLORADO': 'Colorado, United States',
    'CONNECTICUT': 'Connecticut, United States',
    'DELAWARE': 'Delaware, United States',
    'DISTRICTOFCOLUMBIA': 'District of Columbia, United States',
    'FLORIDA': 'Florida, United States',
    'GEORGIA': 'Georgia, United States',
    'GUAM': 'Guam, United States',
    'HAWAII': 'Hawaii, United States',
    'IDAHO': 'Idaho, United States',
    'ILLINOIS': 'Illinois, United States',
    'INDIANA': 'Indiana, United States',
    'IOWA': 'Iowa, United States',
    'KANSAS': 'Kansas, United States',
    'KENTUCKY': 'Kentucky, United States',
    'LOUISIANA': 'Louisiana, United States',
    'MAINE': 'Maine, United States',
    'MARYLAND': 'Maryland, United States',
    'MASSACHUSETTS': 'Massachusetts, United States',
    'MICHIGAN': 'Michigan, United States',
    'MINNESOTA': 'Minnesota, United States',
    'MISSISSIPPI': 'Mississippi, United States',
    'MISSOURI': 'Missouri, United States',
    'MONTANA': 'Montana, United States',
    'NEBRASKA': 'Nebraska, United States',
    'NEVADA': 'Nevada, United States',
    'NEWHAMPSHIRE': 'New Hampshire, United States',
    'NEWJERSEY': 'New Jersey, United States',
    'NEWMEXICO': 'New Mexico, United States',
    'NEWYORK': 'New York, United States',
    'NORTHCAROLINA': 'North Carolina, United States',
    'NORTHDAKOTA': 'North Dakota, United States',
    'OHIO': 'Ohio, United States',
    'OKLAHOMA': 'Oklahoma, United States',
    'OREGON': 'Oregon, United States',
    'PENNSYLVANIA': 'Pennsylvania, United States',
    'PUERTORICO': 'Puerto Rico, United States',
    'RHODEISLAND': 'Rhode Island, United States',
    'SOUTHCAROLINA': 'South Carolina, United States',
    'SOUTHDAKOTA': 'South Dakota, United States',
    'TENNESSEE': 'Tennessee, United States',
    'TEXAS': 'Texas, United States',
    'UTAH': 'Utah, United States',
    'VERMONT': 'Vermont, United States',
    'VIRGINISLANDS': 'Virgin Islands, United States',
    'VIRGINIA': 'Virginia, United States',
    'WASHINGTON': 'Washington, United States',
    'WESTVIRGINIA': 'West Virginia, United States',
    'WISCONSIN': 'Wisconsin, United States',
    'WYOMING': 'Wyoming, United States'
}

def connect():
    global conn
    global cur
    conn = psycopg2.connect(f"host={HOST_NAME} dbname={POSTGRES_DB} user={POSTGRES_USER} password={POSTGRES_PASSWORD} port=5432")
    cur = conn.cursor()


def update_region_state(region, status):
    cur.execute(f"""insert into region_status values ('{region}', {status}) on conflict (region_name) do update set region_state_id = {status};""")
    conn.commit()


def are_regions_to_work():
    connect()
    cur.execute(f"""select count(1) from public.region_status rs where region_state_id <= {BEGIN_WORKING_REGION_STATE}""")
    region_count = cur.fetchone()
    return region_count[0]


def check_schema_ready():
    cur.execute(f"""select * from public.region_status rs where region_state_id = {BEGIN_WORKING_REGION_STATE}""")
    region = cur.fetchone()
    if region is not None:
        region = region[0]
    else:
        region = ''
    return region


def load_intersections_from_db(out_file, schema_name, limit, offset=0):
    table_name = "node_intersections"
    cur.execute(f"""select node_id, lat as latitude, 
                    long as longitude from {schema_name}.{table_name} order by node_id limit {limit} offset {offset};""")

    save_json(out_file, cur.fetchall())


def save_json(filename, data):
    with open(filename, 'w+') as f:
        f.write(json.dumps(data))


def load_json(filename):
    with open(filename, 'r') as f:
        data = json.loads(f.read())
    return data


def download_intersection_masks(intersection_file, place, limit):
    slippy_map = SlippyMap(zoom=18, token=MAPBOX_TOKEN, place=place)
    img_path = f'{os.getcwd()}/data/{stringcase.alphanumcase(place)}'

    if not os.path.isdir(f'{img_path}_masks'):
        os.mkdir(f'{img_path}_masks')

    if not os.path.isdir(f'{img_path}_satimgs'):
        os.mkdir(f'{img_path}_satimgs')

    data = load_json(intersection_file)

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
        save_json(f'{img_path}_error.json', error_nodes)


# @click.command()
# @click.argument('area_name')
# @click.argument('json_name')
# @click.argument('limit')
def main(limit):
    global REGION_OFFSETS
    region_offset_file = Path(REGION_OFFSET_JSON)
    if not region_offset_file.is_file():
        region_offset_file.touch(exist_ok=True)
    else:
        REGION_OFFSETS = load_json(REGION_OFFSET_JSON)

    while are_regions_to_work() > 0:
        region = check_schema_ready()
        if len(region) > 0:
            #set names based on region name
            json_name = region + '.json'
            area_name = region.strip().upper()
            if region in state_dict.keys():
                area_name = state_dict[region]

            # set offset based on region offset, if available
            offset = 0
            if region in REGION_OFFSETS.keys():
                offset = int(REGION_OFFSETS[region])

            update_region_state(region, SAT_IMAGE_PROCESSING_REGION_STATE)
            load_intersections_from_db(json_name, region, limit, offset)
            download_intersection_masks(json_name, area_name, int(limit))
            update_region_state(region, SAT_IMAGE_COMPLETE_REGION_STATE)
            conn.close()
            REGION_OFFSETS[region] = offset + int(limit)
            save_json(REGION_OFFSET_JSON, REGION_OFFSETS)
        else:
            print("No work yet, sleeping.")
            conn.close()
            time.sleep(SLEEP_DURATION)


if __name__ == "__main__":
    main("100")
