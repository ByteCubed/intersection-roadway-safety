"""Download intersection masks for all intersections...

Need to keep intersection IDs...
process intersections json file
"""

import json
from os.path import exists

import boto3
import botocore

import psycopg2
import time
import os
from tqdm import tqdm
from skimage.io import imsave
from dot.tiles import SlippyMap
from PIL import Image
import io
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

intersection_table_name = "node_intersections"

BEGIN_WORKING_REGION_STATE = 9
SAT_IMAGE_PROCESSING_REGION_STATE = 10
SAT_IMAGE_COMPLETE_REGION_STATE = 11
SLEEP_DURATION = 60

DELETE_EMPTY_TILES = True
REGION_TILES_JSON = 'data/tile_offsets.json'
REGION_TILES = {}

# Names for tile properties
OFFSET_NAME = "offset"
TOTAL_WORK_NAME = "total_work_items"
BBOX_NAME = "bbox"

# Bounding Box index names
NORTH = 0
SOUTH = 1
EAST = 2
WEST = 3

# psycopg2 connection and cursor
conn = None
cur = None

# the size in lat/long degrees for tiles
x_step = 0.2
y_step = 0.5 * x_step


# AWS fields
access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
session = None
bucket_name = 'ib-dot-roadway-safety'
sat_data_prefix = 'satellite_data/'
sat_image_prefix = sat_data_prefix + 'sat_imgs/'
USE_CLOUD = False
CLIENT = boto3.client('s3', region_name='us-east-1', aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)

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


def upload_raw_to_s3(imdata, filename, folder):
    CLIENT.put_object(Body=imdata, Bucket=bucket_name, Key=folder + filename)


def upload_to_s3_from_local_file(filepath, filename, folder):
    CLIENT.upload_file(filepath + filename, bucket_name, folder + filename)

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


def get_nodes_and_intersections(region, limit):
    """
    Quick experimental comparison between OSM nodes and intersections
    Parameters
    ----------
    region - the target region
    limit - the total number of records returned. Half are ODDC, half OSM

    Returns
    -------
    The two jsons into which the data is loaded, corresponding to intersections and non-intersection nodes.
    """
    node_json = f'{region}_nodes.json'
    intersection_json = f'{region}_intersections.json'
    node_query = f"""select
                            n.node_id,
                            lat_int::float / 10000000 as lat,
                            long_int::float / 10000000 as long
                    from
                            {region}.node n
                    left join {region}.node_intersections ni on
                            n.node_id = ni.node_id
                    where
                        on_road
                        and ni.node_id is null
                    order by
                        random()
                    limit {limit};"""
    cur.execute(node_query)
    save_json(node_json, cur.fetchall())

    intersection_query = f"""select
                            n.node_id,
                            lat_int::float / 10000000 as lat,
                            long_int::float / 10000000 as long
                    from
                            {region}.node n
                    left join {region}.node_intersections ni on
                            n.node_id = ni.node_id
                    where
                        on_road
                        and ni.node_id is null
                    order by
                        random()
                    limit {limit};"""
    cur.execute(intersection_query)
    save_json(intersection_json, cur.fetchall())

    return node_json, intersection_json



def compare_with_open_data_dc(oddc_source, region, radius, limit):
    """
    Quick experimental comparison between Open Data DC ("ODDC") and OSM data
    Parameters
    ----------
    oddc_source - the schema + tablename for the ODDC data
    region - the target region
    radius - the maximum distance at which we consider two candidate intersections to be the same
    limit - the total number of records returned. Half are ODDC, half OSM

    Returns
    -------
    The two jsons into which the data is loaded.
    """
    oddc_out_json = f'oddc_vs_{region}.json'
    region_out_json = f'{region}_vs_oddc.json'
    query = f"""select
        min(ogc_fid) as ogc_fid,
        latitude, longitude, oddc_point3857
    from
        (select
            st_transform(st_setsrid(odi.wkb_geometry, 4326), 3857) as oddc_point3857,
            *
        from
            {oddc_source} odi) oddcsq
            left join {region}.{intersection_table_name} if2 on ST_DWITHIN(if2.point3857, oddcsq.oddc_point3857, {radius})
        where node_id is null
    group by latitude, longitude, oddc_point3857
    order by random()
    limit {limit};"""
    cur.execute(query)
    save_json(oddc_out_json, cur.fetchall())

    query = f"""select
        ni.node_id,
        lat, long
    from
        (select
            st_transform(st_setsrid(odi.wkb_geometry, 4326), 3857) as oddc_point3857, ogc_fid
        from
            {oddc_source} odi) oddcsq
            right join {region}.{intersection_table_name} ni on ST_DWITHIN(ni.point3857, oddcsq.oddc_point3857, {radius})
		    join {region}.intersection_features if2 on ni.node_id = if2.node_id
        where ogc_fid is null
		    and if2.nonramp_roads + if2.ramp_roads > 2
    order by random()
    limit {limit};"""
    cur.execute(query)
    save_json(region_out_json, cur.fetchall())

    return oddc_out_json, region_out_json




def load_intersections_from_db(out_file, schema_name, limit=0, offset=0):
    query = f"""select node_id, lat as latitude, 
                                long as longitude from {schema_name}.{intersection_table_name} order by node_id"""
    if limit is not None and limit > 0:
        query = query + f""" limit {limit} offset {offset};"""
    cur.execute(query)
    data = cur.fetchall()
    if out_file is not None:
        save_json(out_file, data, prefix=sat_data_prefix)
    return data



def load_intersections_from_db_for_tile(bbox, schema_name, limit=0, offset=0, out_file=None):
    query = (f"""select node_id, lat as latitude, 
                    long as longitude from {schema_name}.{intersection_table_name} 
                    where 
                    ST_CONTAINS(
                        st_transform(
                            st_setsrid(
                                st_makepolygon(
                                    st_geomfromtext('{format_line_string(bbox)}')
                                )
                            ,4236)
                        ,3857)
                    , point3857)
                    order by node_id""")
    if limit is not None and limit > 0:
        query = query + f""" limit {limit} offset {offset};"""
    cur.execute(query)
    data = cur.fetchall()
    if out_file is not None:
        save_json(out_file, data, prefix=sat_data_prefix)
    return data



def get_intersection_count_within_area(schema_name, bbox):
    """
    Parameters
    ----------
    schema_name - the target schema containing the intersection table
    bbox - the bounding box for the region under observation

    Returns
    -------
    The count of intersections in the given area
    """
    cur.execute(f"""select count(1) from {schema_name}.{intersection_table_name} 
                        where 
                        ST_CONTAINS(
                            st_transform(
                                st_setsrid(
                                    st_makepolygon(
                                        st_geomfromtext('{format_line_string(bbox)}')
                                    )
                                ,4236)
                            ,3857)
                        , point3857);""")
    intersection_count = cur.fetchone()
    return intersection_count[0]


def format_line_string(bbox):
    """
    Formats a linestring that postGIS can read into a geometry object, from an input bbox.
    Parameters
    ----------
    bbox - an array containing the northmost and southmost latitudes, followed by the eastmost and westmost longitudes

    Returns
    -------
    A string containing the formatted information
    """
    n, s, e, w = [str(bbox[i]) for i in (NORTH, SOUTH, EAST, WEST)]
    return 'LINESTRING(' +  e + ' ' + n + ', ' + \
                            w + ' ' + n + ',' + \
                            w + ' ' + s + ',' + \
                            e + ' ' + s + ',' + \
                            e + ' ' + n + ')'


def create_region_bbox(schema_name):
    """
    Creates a bounding box for a region by taking the northmost, southmost, etc. points
    Parameters
    ----------
    schema_name - the name of the schema to use

    Returns
    -------
    The bounding box for the region.
    """
    cur.execute(f"""select max(lat) as north, min(lat) as south, max(long) as east, min(long) as west 
                            from {schema_name}.{intersection_table_name}""")
    region_bbox = list(cur.fetchone())
    return region_bbox


def create_tiles(schema_name, region_bbox):
    """
    Creates tiles from a given region, using the global x_step and y_step to determine the number of boxes.
    Parameters
    ----------
    region_bbox - the bounding box for the region to be split
    schema_name - the name of the target schema

    Returns
    -------
    A list of tiles. Each tile is a dict containing:
        - bbox, an array of size 4, containing the N,S,E,W maximums for its area, in lat/long format.
        - offset, an integer indicating the amount worked (initially 0)
        - total_work_items, an integer corresponding to the amount of intersections within that schema and bbox
    """
    height = region_bbox[0] - region_bbox[1]
    length = region_bbox[2] - region_bbox[3]
    lat_steps = int(height / y_step) + 1
    long_steps = int(length / x_step) + 1
    tiles = []
    for x in range(0, long_steps):
        for y in range(0, lat_steps):
            tiles.append({
                            BBOX_NAME: [region_bbox[SOUTH] + (y + 1) * height / lat_steps, region_bbox[SOUTH] + y * height / lat_steps,
                                region_bbox[WEST] + (x + 1) * length / long_steps, region_bbox[WEST] + x * length / long_steps],
                            OFFSET_NAME: 0,
                            TOTAL_WORK_NAME: -1
                         })
    for tile in tiles:
        tile[TOTAL_WORK_NAME] = get_intersection_count_within_area(schema_name, tile[BBOX_NAME])
    if DELETE_EMPTY_TILES:
        tiles = [tile for tile in tiles if tile[TOTAL_WORK_NAME] > 0]
    return tiles


def get_unworked_tile(region_name):
    """
    Finds and returns the first unworked tile in the region. If none exists, creates tiles for the region and returns the first one.
    Parameters
    ----------
    region_name - the name of the region to be worked. Should correspond to the schema.

    Returns
    -------
    An int corresponding to the first tile where offset < work to do
    """
    if region_name not in REGION_TILES:
        REGION_TILES[region_name] = create_tiles(region_name, create_region_bbox(region_name))
    counter = 0
    for tile in REGION_TILES[region_name]:
        if tile[OFFSET_NAME] < tile[TOTAL_WORK_NAME]:
            return counter
        counter = counter + 1


def all_tiles_complete(region):
    """
    Checks if all tiles have been fully worked.
    Parameters
    ----------
    region - the region to check. Should match a key in REGION_TILES

    Returns
    -------
    True if all tiles are complete, false otherwise.
    """
    tiles = REGION_TILES[region]
    for tile in range(len(tiles)):
        if tiles[tile][OFFSET_NAME] < tiles[tile][TOTAL_WORK_NAME]:
            return False
    return True


def save_json(filepath, data, use_s3=USE_CLOUD, prefix='', indent=4):
    if use_s3:
        CLIENT.put_object(Body=json.dumps(data, indent=indent), Bucket=bucket_name, Key=prefix + filepath)
    else:
        with open(Path(filepath), 'w+') as f:
            f.write(json.dumps(data, indent=indent))


def load_json(filepath, use_s3=USE_CLOUD, prefix=''):
    if use_s3:
        response = CLIENT.get_object(Bucket=bucket_name, Key=prefix + filepath)
        data = json.loads(response['Body'].read())
    else:
        with open(Path(filepath), 'r') as f:
            data = json.loads(f.read())
    return data


def file_exists(file, prefix=''):
    """
    Checks that a file exists
    Parameters
    ----------
    file - the filename
    prefix - an optional prefix for use on s3

    Returns
    -------
    -------
    True if the file exists, False otherwise.
    """
    if USE_CLOUD:
        try:
            CLIENT.head_object(Bucket=bucket_name, Key=prefix + file)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                # The object does not exist.
                return False
            else:
                # Something else has gone wrong.
                raise
        else:
            return True
    else:
        return Path(file).is_file()


def download_intersection_images(slippy_map, img_path, data, limit=-1, offset=0, custom_data_label_mapping=[0,1,2], prefix='satimg'):
    """

    Parameters
    ----------
    slippy_map - a slippy map corresponding to the area. If the map and nodes mismatch, you won't get good data
    img_path - the folder to deposit the downloaded images
    intersection_file - the path to the file containing the data to find images for
    limit - the number of records to try to process
    offset - the number of initial data rows to skip
    custom_data_label_mapping - a 3-length array. The first value corresponds to the node_id index (or, if a dict is used, the key.
                                The second value corresponds to latitude, the third to longitude
    prefix - the output files' prefix


    Returns
    -------
    An integer indicating how many rows were processed, whether successful, skipped, or unsuccessful.
    """
    # if not os.path.isdir(f'{img_path}_masks'):
    #     os.mkdir(f'{img_path}_masks')

    if not os.path.isdir(f'{img_path}_satimgs'):
        os.mkdir(f'{img_path}_satimgs')

    error_nodes = []
    if file_exists(f'{img_path}_error.json', prefix=sat_image_prefix):
        error_nodes = load_json(f'{img_path}_error.json', prefix=sat_data_prefix)

    new_errors = 0
    skipped = 0
    counter = 1
    for index in tqdm(range(offset, len(data))):
        row = data[index]

        node_id = row[custom_data_label_mapping[0]]
        latitude = row[custom_data_label_mapping[1]]
        longitude = row[custom_data_label_mapping[2]]

        # If the masks and images already exist, don't waste our 50k
        if os.path.exists(f'{img_path}_satimgs/{prefix}_{node_id}.png'):

            print(f"Files already exist for {node_id}, skipping...")
            skipped += 1
            continue

        box = slippy_map @ (longitude, latitude)

        try:
            if USE_CLOUD:
                imdata = io.BytesIO() # prepare byte stream
                Image.fromarray(box.image).convert('RGB').save(imdata, format='png')
                imdata.seek(0)
                upload_raw_to_s3(imdata, f'satimg_{node_id}.png', sat_image_prefix + os.path.basename(img_path) + '/')
            else:
                # If not using cloud, save locally
                imsave(f'{img_path}_satimgs/satimg_{node_id}.png', box.image)
        except Exception as error:
            error_nodes.append(node_id)
            new_errors = new_errors + 1
            print(f'Failed to generate image for {node_id}, skipping')
            print(error)

            continue
        # try:
        #     imsave(f'{img_path}_masks/mask_{node_id}.png', box.figure_ground)
        #     print(f'Generated mask for {node_id}')
        # except:
        #     error_nodes.append(node_id)
        #     print(f'Failed to generate mask for {node_id}, skipping')
        #     continue

        if int(limit) != -1 and counter >= int(limit):
            break
        else:
            counter += 1

    if len(error_nodes) > 0:
        save_json(f'{img_path}_error.json', error_nodes, prefix=sat_data_prefix)

    return counter + new_errors + skipped - 1


def determine_region_name(candidate, delim):
    """
    Parameters
    ----------
    candidate - the candidate region string
    delim - the delimiter, typically an underscore

    Returns
    -------
    The region name matching the input string if a match can be made, or None if no match can be made.
    """
    # prioritize whole-word match
    if candidate in state_dict.keys():
        return state_dict[candidate]

    # if that's impossible, split the word on the delimiter
    # and try progressively longer subclauses (e.g., new, new_york, new_york_bronx, etc.)
    candidate_clauses = candidate.split(delim)
    substr = candidate_clauses[0]
    for i in range(1, len(candidate_clauses)-1):
        if substr in state_dict.keys():
            return state_dict[substr]
        substr = substr + delim + candidate_clauses[i]
    return None

    while are_regions_to_work() > 0:
        region = check_schema_ready()
        if len(region) > 0:
            #set names based on region name
            json_name = region + '.json'
            area_name = region.strip().upper()
            if region in state_dict.keys():
                area_name = state_dict[region]

def main(limit):
    global REGION_TILES
    
    # Create Session With Boto3.
    global session
    session = boto3.Session(
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key
    )

    if not file_exists(REGION_TILES_JSON, prefix=sat_data_prefix):
        if not USE_CLOUD:
            Path(REGION_TILES_JSON).touch(exist_ok=True)
        REGION_TILES = {}
        save_json(REGION_TILES_JSON, REGION_TILES, prefix=sat_data_prefix)
    else:
        REGION_TILES = load_json(REGION_TILES_JSON, prefix=sat_data_prefix)


    while True:
        if are_regions_to_work():
            region = check_schema_ready()
            if len(region) > 0:
                # set names based on region name
                json_name = region + '.json'
                area_name = determine_region_name(region.strip().upper(), '_')
                if area_name is not None:
                    tile_num = get_unworked_tile(region)
                    offset = REGION_TILES[region][tile_num][OFFSET_NAME]
                    tile_bounds = REGION_TILES[region][tile_num][BBOX_NAME]
                    slippy_map = SlippyMap(zoom=18, token=MAPBOX_TOKEN, bbox=tile_bounds)

                    update_region_state(region, SAT_IMAGE_PROCESSING_REGION_STATE)
                    data = load_intersections_from_db_for_tile(tile_bounds, region)

                    img_path = f'{os.getcwd()}/data/{stringcase.alphanumcase(region)}'
                    processed = download_intersection_images(slippy_map, img_path, data, limit=limit, offset=offset)

                    REGION_TILES[region][tile_num][OFFSET_NAME] = offset + processed
                    save_json(REGION_TILES_JSON, REGION_TILES, prefix=sat_data_prefix)

                # If the region is finished (all tiles fully processed), mark it finished.
                # Otherwise move it back to the end of the previous queue so it can be picked up again.
                if all_tiles_complete(region):
                    update_region_state(region, SAT_IMAGE_COMPLETE_REGION_STATE)
                else:
                    update_region_state(region, BEGIN_WORKING_REGION_STATE)


                conn.close()
        else:
            print("No work yet, sleeping.")
            conn.close()
            time.sleep(SLEEP_DURATION)


def run_on_static_file(region, filename, local_file=False):
    # Create Session With Boto3.
    global REGION_TILES
    global session
    session = boto3.Session(
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key
    )

    all_data = load_json(filename, use_s3=not local_file)

    connect()
    if len(region) > 0:
        # set names based on region name
        json_name = region + '.json'
        area_name = determine_region_name(region.strip().upper(), '_')
        if area_name is not None:

            if region not in REGION_TILES:
                REGION_TILES[region] = create_tiles(region, create_region_bbox(region))

            for tile in REGION_TILES[region]:
                tile_bounds = tile[BBOX_NAME]
                slippy_map = SlippyMap(zoom=18, token=MAPBOX_TOKEN, bbox=tile_bounds)

                # filters for lat between the N/S bounds and that long is between the E/W bounds
                data = [x for x in all_data if tile_bounds[1] <= x['latitude'] <= tile_bounds[0]
                                           and tile_bounds[3] <= x['longitude'] <= tile_bounds[2]]

                img_path = f'{os.getcwd()}/data/{stringcase.alphanumcase(region)}'
                download_intersection_images(slippy_map, img_path, data, custom_data_label_mapping=['node_id','latitude','longitude'])
                
                
def compare_intersection_data(compare_source_name, region, radius, limit):
    """
    Compares OSM data against another source.
    Parameters
    ----------
    compare_source_name - the schema + tablename for the ODDC data
    region - the target region
    radius - the maximum distance at which we consider two candidate intersections to be the same
    limit - the total number of records returned. Half are ODDC, half OSM

    Returns
    -------

    """
    dir_name = region + '_compare'
    connect()
    bbox = create_region_bbox(region)

    slippy_map = SlippyMap(zoom=18, token=MAPBOX_TOKEN, bbox=bbox)
    img_path = f'{os.getcwd()}/data/{dir_name}'
    present_in_comparison_source_but_not_region_db_json, present_in_region_db_but_not_comparison_source_json = compare_with_open_data_dc(compare_source_name, region, radius, limit)
    download_intersection_images(slippy_map, img_path, present_in_region_db_but_not_comparison_source_json, limit/2, prefix='osm')
    download_intersection_images(slippy_map, img_path, present_in_comparison_source_but_not_region_db_json, limit/2, prefix='oddc')

    node_json, intersection_json = get_nodes_and_intersections(region, limit)
    download_intersection_images(slippy_map, img_path + '_nodes', node_json, limit/2, prefix='dc_node')
    download_intersection_images(slippy_map, img_path + '_intersections', intersection_json, limit/2, prefix='dc_intersection')



if __name__ == "__main__":
    #compare_intersection_data('public.opendata_dc_intersections', 'dc', 10, 300)
    main("1000")
    # run_on_static_file('iowa', './data/intersection_features_iowa.json', local_file=True)
    #run_on_static_file('dc', './data/intersection_features_dc.json', local_file=True)

