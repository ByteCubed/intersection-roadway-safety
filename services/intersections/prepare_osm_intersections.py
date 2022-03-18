"""Extract MIRE attributes from OSM data
"""

import json
from collections import Counter

import osmnx as ox
import click
from tqdm import tqdm
import stringcase

from dot.geojson import make_point, make_point_collection
from dot.osm import (    
    extract_intersection_type,
    extract_intersection_roadway_names,
    extract_intersection_angles,
    extract_intersection_lanes,
    extract_intersection_oneway
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
def ingest_intersections(location: str):
    # Get simplified graph, keeping only endpoints and intersections:
    print("loading graph...")
    G = ox.io.load_graphml(f"{stringcase.alphanumcase(location)}.graphml")#, node_type=str)

    print("iterating over points...")
    # get GeoJSON Points...
    n_nodes = len(G)
    intersections = []
    print("Getting lanes...")
    lanes_dictionary = ox.stats.count_streets_per_node(G, [n for n in G.nodes])
    print("Done getting lanes...")
    for nid in tqdm(G.nodes, nrows=n_nodes):

        # street_names = extract_intersection_roadway_names(G, nid)
        # get intersection types, element 121
        intersection_type = extract_intersection_type(G, nid)

        # get names of roadways and paths meeting at intersection
        names = extract_intersection_roadway_names(G, nid)

        # get total number of lanes at intersection
        lanes = extract_intersection_lanes(G, nid)
        # lanes = ox.stats.count_streets_per_node(G, [nid])
        #The lanes is adictionary with single key, so cast this to an int
        # num_lanes = lanes[[x for x in lanes.keys()][0]]
        num_legs = lanes_dictionary[nid]


        # get number of roadway segments that are oneway at intersectin
        oneway = extract_intersection_oneway(G, nid)

        # intersecting angle
        angle = extract_intersection_angles(G, nid)

        if angle and int(angle) < 10:
            continue
        # angle = 10.2
        # print(oneway)
        # print(G.nodes[nid])
        if len(G.edges(nid)) <= 2:
            continue

        junction = OSMJunction(
                junction_type=intersection_type,
                num_legs=num_legs,
                angle=angle,
                oneway=oneway,
                lanes=lanes,
                longitude=G.nodes[nid]['x'],
                latitude=G.nodes[nid]['y'],
                names=names
            )

        intersections.append(
            make_point(junction.longitude, junction.latitude, **junction.dict(), tooltip=junction.json(indent=2))
        )

    print(f"Loaded {len(intersections)} intersections.")
    with open('dc_intersections.json', 'w') as outfile:
        json.dump(make_point_collection(intersections), outfile)


if __name__ == "__main__":
    ingest_intersections()
