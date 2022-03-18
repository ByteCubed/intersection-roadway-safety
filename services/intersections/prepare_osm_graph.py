"""
Get OpenStreetMap graph and simplify
"""

import click
import osmnx as ox
import pyproj
from tqdm import tqdm
import stringcase

from dot.geojson import make_point, make_point_collection
from dot.osm import (    
    extract_intersection_type,
    extract_intersection_roadway_names,
    extract_intersection_angles
)
from dot.mire_types.osm import OSMNode
from dot.mire_types.intersections import OSMJunction


way_tags = [
    'bridge',
    'tunnel',
    'highway',
    'footway',
    'lanes',
    'maxspeed',
    'name',
    'tiger:name_base',
    'official_name',
    'alt_name',
    'oneway',
    'noexit',
    'abutters',
    'embedded_rails',
    'incline',
    'junction',
    'lit',
    'overtaking',
    'parking:condition',
    'parking:lane',
    'smoothness',
    'surface',
    'tactile_paving',
    'tracktype',
    'traffic_calming',
    'turn',
    'turn:lanes',
    'abutters',  # commercial / industrial / mixed / residential / retail etc. https://wiki.openstreetmap.org/wiki/Key:abutters
    'bicycle_road',
    'embedded_rails',
    'place',
    'railway',
    'bearing'
]
node_tags = [
    'ele',  # elevation
    'highway',  # turning circle, traffic signals, etc
    'ref',  # reference id?
    'barrier',
    'amenity',  # school, restaurant, parking, etc
    'emergency',  # firestation, hospital, etc
    'incline',
    'place',
    'name',
    'official_name',
    'alt_name',
]

ox.utils.config(
    use_cache=True,
    useful_tags_way=way_tags,
    useful_tags_node=node_tags
)


#@click.command()
#@click.argument('location', type=str)
def get_osm_graph(location: str):
    # Get simplified graph, keeping only endpoints and intersections:
    print("getting graph...")
    ox.utils.config(
        use_cache=True,
        useful_tags_way=way_tags,
        useful_tags_node=node_tags
    )
    G = ox.graph_from_place(
        location,
        simplify=False,
        network_type="drive_service"   # all_private
    )
    print("adding bearings...")
    G = ox.add_edge_bearings(G)
    # print("projecting graph...")
    # G = ox.simplification.simplify_graph(G)
    # crs = pyproj.crs.GeographicCRS(datum='WGS84')
    # G = ox.project_graph(G,to_crs=crs)
    # print("simplifying...")
    # G = ox.simplification.consolidate_intersections(G)
    # print("projecting back...")
    # crs = pyproj.crs.GeographicCRS(datum='WGS84')
    # G = ox.project_graph(G, to_crs=crs)
    # G = ox.add_edge_bearings(G)
    print("saving...")
    # import pdb
    # pdb.set_trace()

    ox.io.save_graphml(G, filepath=f"{stringcase.alphanumcase(location)}.graphml")


if __name__ == "__main__":
    get_osm_graph()
