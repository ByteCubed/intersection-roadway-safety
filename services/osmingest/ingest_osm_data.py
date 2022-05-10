"""Download intersection masks for all intersections...

Need to keep intersection IDs...
process intersections json file
"""

import psycopg2
import time
import os
from dotenv import load_dotenv
import subprocess
load_dotenv()

POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_PASSWORD = os.getenv('PGPASSWORD')
POSTGRES_USER = os.getenv('POSTGRES_BUILDER_USER')
HOST_NAME = os.getenv('HOSTNAME')
CURRENT_DIR = 'services/osmingest'

public_schema = "public"
county_lines_table = "county_lines"

BEGIN_WORKING_REGION_STATE = 5
OSM_STARTED_REGION_STATE = 6
OSM_COMPLETE_REGION_STATE = 7
OSM_POSTPROCESS_STARTED_REGION_STATE = 8
OSM_POSTPROCESS_COMPLETE_REGION_STATE = 9
SLEEP_DURATION = 60

conn = None
cur = None

large_states = ['texas', 'california', 'new_york', 'newyork', 'florida']

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
    """
    Connects to the database
    Returns
    -------

    """
    global conn
    global cur
    conn = psycopg2.connect(f"host={HOST_NAME} dbname={POSTGRES_DB} user={POSTGRES_USER} password={POSTGRES_PASSWORD} port=5432")
    conn.set_session(autocommit=True)
    cur = conn.cursor()


def update_region_state(region, status):
    """
    Upserts a region's work state.
    Prereq: Expects a database connection to already exist.
    Parameters
    ----------
    region - the region to upsert
    status - the state code for the region's work state

    Returns
    -------

    """
    cur.execute(f"""insert into region_status values ('{region}', {status}) on conflict (region_name) do update set region_state_id = {status};""")


def are_regions_to_work():
    """
    Connects to the database and checks for workable items.
    Returns
    -------
    A count of the workable items.
    """
    connect()
    cur.execute(f"""select count(1) from public.region_status rs where region_state_id in ({BEGIN_WORKING_REGION_STATE}, {OSM_COMPLETE_REGION_STATE})""")
    region_count = cur.fetchone()
    return region_count[0]


def get_region_state(region):
    """
    Returns the state of the given region
    Prereq: Expects a database connection to already exist.
    Parameters
    ----------
    region - the schema name to check

    Returns
    -------
    The schema's state (an int) if it exists, otherwise -1
    """
    cur.execute(f"""select region_state_id from public.region_status rs where region_name='{region}'""")
    region=cur.fetchone()
    if region is not None:
        region = int(region[0])
    else:
        region = -1
    return region


def get_list_from_file(filename):
    with open(filename) as f:
        lines = f.readlines()
    return lines


def set_search_path(region):
    """
    Sets a schema to default, with public as the secondary schema
    Prereq: Expects a database connection to already exist.
    Parameters
    ----------
    region - the schema name to set default.

    Returns
    -------

    """
    if region != '' and region is not None:
        #TODO remove of one of these and test
        cur.execute(f"""set search_path to {",".join([region, "public"])}""")
        cur.execute(f"""ALTER ROLE {POSTGRES_USER} set search_path = {",".join([region, "public"])}""")
        return 0
    else:
        return -1


def create_schema(schema_name):
    """
    Creates a schema.
    Prereq: Expects a database connection to already exist.
    Parameters
    ----------
    schema_name - the name of the schema to create

    Returns
    -------

    """
    cur.execute(f"""create schema if not exists {schema_name}""")
    cur.execute(f"""GRANT ALL PRIVILEGES ON SCHEMA {schema_name} TO {POSTGRES_USER}""")
    cur.execute(f"""ALTER DEFAULT PRIVILEGES IN SCHEMA {schema_name} GRANT ALL ON TABLES TO {POSTGRES_USER}""")
    cur.execute(f"""ALTER DEFAULT PRIVILEGES IN SCHEMA {schema_name} GRANT ALL ON FUNCTIONS TO {POSTGRES_USER}""")


def create_county_node_table(schema_name, state, county):
    """
    Copies the osm node table (planet_osm_ways) to the target schema.
    Prereq: Expects a database connection to already exist.
    Parameters
    ----------
    schema_name - the name of the target schema
    state - the name of the source schema
    county - the subregion name

    Returns
    -------

    """
    print(f"""Creating Nodes for {state}'s {county} county""")
    cur.execute(f"""create table if not exists {schema_name}.node as 
    select n.*
    from public.county_lines clr
    join {state}.node n on ST_INTERSECTS(clr.area3857, n.point3857)
    where lower(replace(state_name, ' ', '_')) = '{state}' and lower(replace(name, ' ', '_')) = '{county}'""")
    cur.execute(f"""CREATE INDEX IF NOT EXISTS {county}_node_index ON {schema_name}.node(node_id)""")
    cur.execute(f"""CREATE INDEX IF NOT EXISTS {county}_node_point_index ON {schema_name}.node USING gist(point3857)""")


def create_county_way_node_table(schema_name, state, county):
    """
    Copies the osm way_node table (planet_osm_ways) to the target schema.
    Prereq: Expects a database connection to already exist.
    Prereq: Expects the target schema to have a populated node table.
    Parameters
    ----------
    schema_name - the name of the target schema
    state - the name of the source schema
    county - the subregion name, only used for the printout

    Returns
    -------

    """
    print(f"""Creating way_node table for {state}'s {county} county""")
    cur.execute(f"""create table if not exists {schema_name}.way_node as select wn.* from {schema_name}.node n join {state}.way_node wn on n.node_id = wn.node_id""")
    cur.execute(f"""create index if not exists way_node_way on {schema_name}.way_node(way_id)""")
    cur.execute(f"""create index if not exists way_node_node on {schema_name}.way_node(node_id)""")


def create_county_osm_ways_table_from_state(schema_name, state, county):
    """
    Copies the osm ways table (planet_osm_ways) to the target schema.
    Prereq: Expects a database connection to already exist.
    Prereq: Expects the target schema to have a populated way_node table.
    Parameters
    ----------
    schema_name - the name of the target schema
    state - the name of the source schema
    county - the subregion name, only used for the printout

    Returns
    -------

    """
    print(f"""Copying osm way data into table for {state}'s {county} county""")
    cur.execute(f"""create table if not exists {schema_name}.planet_osm_ways as
                            select w.* from {schema_name}.way_node wn 
                                join {state}.planet_osm_ways w on wn.way_id  = w.id""")
    cur.execute(f"""create index if not exists way_raw_id on {schema_name}.planet_osm_ways(id)""")


def call_subprocess(args):
    subprocess.call(args, shell=True)


def run_sql_from_file(filename):
    """
    Currently unused shortcut for running a sql file using the current connection.
    Prereq: Expects a database connection to already exist.
    Parameters
    ----------
    filename - the sql file to be executed.

    Returns
    -------

    """
    cur.execute(open(filename, "r").read())


def create_regions_from_state(state):
    """
    Checks the county_lines references table for geometry on which to split the input region.
    For each subregion:
        Creates new schemas, copies the node, way, and way_node data over, and postprocesses the subregion.
    Prereq: Expects a database connection to already exist.
    Parameters
    ----------
    state - the name of the state or region to be split

    Returns
    -------

    """
    state = state.lower()
    cur.execute(f"""select lower(replace(name, ' ', '_')) as county from {public_schema}.{county_lines_table} where lower(replace(state_name, ' ', '_')) = '{state}'""")
    county_names = cur.fetchall()
    if county_names is not None:
        for county in county_names:
            county = county[0]
            schema_name = state + '_' + county
            create_schema(schema_name)
            create_county_node_table(schema_name, state, county)
            create_county_way_node_table(schema_name, state, county)
            create_county_osm_ways_table_from_state(schema_name, state, county)
            # Handles OSM postprocess and updates the region state. Needs the region name, not the filepath
            call_subprocess("./postprocess.sh %s" % schema_name)
    else:
        print(f"""No counties found for region {state}""")


def control_loop(data_dir):
    """
    Handles looping logic for ingesting and postprocessing osm data.
    Loops over the regions in the data_dir folder and:
        -ingests the data if the region is in an appropriate work state
        -calls a node and way_node creation script for all states, large and small
        -delegates large state handling to a helper method
        -calls the postprocessing script for small states
    Parameters
    ----------
    data_dir - the top-level directory in which the regions are stored.
               Its subdirectories are considered to be region names, containing region data.
               The subdirectories are expected to have a subfolder labeled "osm" containing a pbf file containing the roadway data for that region.
    Returns
    -------

    """
    region_paths = [os.path.join(data_dir, o) for o in os.listdir(data_dir)
                    if os.path.isdir(os.path.join(data_dir,o))]
    ignore_list = get_list_from_file(f"""{data_dir}ignore.txt""")
    while True:
        if are_regions_to_work():
            for region_path in region_paths:
                region = os.path.basename(region_path)
                if region in ignore_list:
                    continue
                region_state = get_region_state(region)
                if set_search_path(region) == 0:
                    # OSM ingestion, skip if it's complete
                    if region_state == BEGIN_WORKING_REGION_STATE:
                        # Handles OSM ingestion, updates the state, applies the appropriate permissions. Needs the filepath, not the region name.
                        call_subprocess("./osm_ingest.sh %s/" % region_path)
                    region_state = get_region_state(region)
                    # OSM Postprocessing
                    if region_state == OSM_COMPLETE_REGION_STATE:
                        # Handles Node and way_node creation.  Needs the region name, not the filepath
                        call_subprocess("./create_standard_node_and_way_node.sh %s" % region)
                        # large states require different processing
                        if region.lower() in large_states:
                            print(f"""{region} is a large state - splitting it into smaller parts""")
                            create_regions_from_state(region)
                        else:
                            print(f"""{region}: Running OSM Postprocess scripts""")
                            # Handles OSM postprocess and updates the region state. Needs the region name, not the filepath
                            call_subprocess("./postprocess.sh %s" % region)
                else:
                    print(f"""Skipping {region}, schema invalid""")
        else:
            print("No work yet, sleeping.")
            conn.close()
            time.sleep(SLEEP_DURATION)


def main():
    connect()
    data_dir='/data/'
    control_loop(data_dir)


if __name__ == "__main__":
    main()
