import json
import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()
import click
import stringcase

POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_USER = os.getenv('POSTGRES_USER')
HOST_NAME = os.getenv('HOSTNAME')
# CURRENT_DIR = os.getcwd()
CURRENT_DIR = 'services/intersections'


#@click.command()
#@click.argument('intersection_file')
#@click.argument('place')
def load_intersections(intersection_file, place):
    # Connect to your postgres DB
    conn = psycopg2.connect(f"host={HOST_NAME} dbname={POSTGRES_DB} user={POSTGRES_USER} password={POSTGRES_PASSWORD} port=5432")

    # Open a cursor to perform database operations
    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS rws.public.planet_osm_intersections_alpha
    (
    longitude TEXT
    ,latitude TEXT
    ,nodeid TEXT
    ,num_legs TEXT
    ,geometry_type TEXT
    ,geometry TEXT
    ,angle TEXT
    ,lanes TEXT
    ,oneway TEXT
    ,names TEXT
    ,junction_type TEXT
    ,point geometry(point,3857)
    ,maskimage TEXT
    ,satimage TEXT
    )""")

    cur.execute("""CREATE INDEX IF NOT EXISTS planet_osm_intersection_index ON
     rws.public.planet_osm_intersections_alpha USING gist(point);""")

    xsections = json.load(open(intersection_file, "r"))

    for xsect in xsections['features']:
        names = "|".join(xsect['properties']['names']).replace('"', "").replace("'", "")
        cur.execute(f"""INSERT INTO rws.public.planet_osm_intersections_alpha VALUES \
                    ('{xsect['properties']['longitude']}',\
                    '{xsect['properties']['latitude']}',\
                    '{xsect['properties']['nodeid']}',\
                    '{xsect['properties']['num_legs']}',\
                    '{xsect['properties']['geometry_type']}',\
                    '{xsect['properties']['geometry']}',\
                    '{xsect['properties']['angle']}',\
                    '{xsect['properties']['lanes']}',\
                    '{xsect['properties']['oneway']}',\
                    '{names}',\
                    {xsect['properties']['junction_type']},\
                    ST_Transform(ST_SetSRID(ST_MakePoint({xsect['properties']['longitude']},\
                         {xsect['properties']['latitude']}), 4326),3857),\
                    '{CURRENT_DIR}/data/{stringcase.alphanumcase(place)}_masks/mask_{xsect['properties']['nodeid']}.png',\
                    '{CURRENT_DIR}/data/{stringcase.alphanumcase(place)}_satimgs/satimg_{xsect['properties']['nodeid']}.png'\
                );""")

    conn.commit()

    return 0


if __name__ == "__main__":
    load_intersections()
