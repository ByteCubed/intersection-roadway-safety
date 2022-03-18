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
    schema_name = "public"
    table_name = "planet_osm_intersections_alpha"
    # Connect to your postgres DB
    conn = psycopg2.connect(f"host={HOST_NAME} dbname={POSTGRES_DB} user={POSTGRES_USER} password={POSTGRES_PASSWORD} port=5432")

    # Open a cursor to perform database operations
    cur = conn.cursor()
    # cur.execute(f"""SELECT EXISTS (
    #                 SELECT FROM pg_tables
    #                 WHERE  schemaname = '{schema_name}'
    #                 AND    tablename  = '{table_name}'
    #             );""")
    # table_exists = cur.fetchone()[0]

    cur.execute(f"""CREATE TABLE IF NOT EXISTS rws.{schema_name}.{table_name}
    (
    nodehash TEXT
    ,longitude TEXT
    ,latitude TEXT
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
    ,node_id int8
    , primary key (nodehash)
    )""")

    cur.execute("""CREATE INDEX IF NOT EXISTS planet_osm_intersection_index ON
     rws.public.planet_osm_intersections_alpha USING gist(point);""")

    xsections = json.load(open(intersection_file, "r"))

    for xsect in xsections['features']:
        names = "|".join(xsect['properties']['names']).replace('"', "").replace("'", "")
        cur.execute(f"""INSERT INTO rws.public.planet_osm_intersections_alpha VALUES \
                    ('{xsect['properties']['nodeid']}',\
                    '{xsect['properties']['longitude']}',\
                    '{xsect['properties']['latitude']}',\
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
                ) on conflict do nothing;""")

    cur.execute(f"""update planet_osm_intersections_alpha poia2 
                        set node_id = subquery.node_id
                        from (
                            select poia.nodehash, n.node_id
                            from planet_osm_intersections_alpha poia 
                            join node n on ST_DWITHIN(poia.point, n.point3857, 5)
                                where ST_Distance(poia.point, n.point3857) = 
                                (select MIN(ST_Distance(poia.point, subnode.point3857)) 
                                from node subnode 
                                where ST_DWITHIN(poia.point, subnode.point3857, 5))
                        ) subquery 
                        where subquery.nodehash = poia2.nodehash and poia2.node_id is null;""")
    conn.commit()

    return 0


if __name__ == "__main__":
    load_intersections()
