"""
OpenStreetMap Tools
-------------------

This script is for interacting with OpenStreetMap data.
It allows you to download data for a region and create a NetworkX graph
from the roadways using the OSMnx library.
"""
import osmnx as ox
import networkx
import numpy as np
from numbers import Number
from typing import Tuple, List
from .mire_types.intersections import JunctionType, IntersectingAngle


def get_graph_from_place(
    place: str,
    intersections_only: bool = True):
    """Retrieve road network graph

    Parameters
    ----------
    place:
        A place name that can be searched in OpenStreetMap
    intersections_only:
        Whether the graph should include only intersections

    Returns
    -------
    MultiDiGraph:
        Graph where nodes represent points and edges are sections of roadway
    """
    G = ox.graph_from_place(place, clean_periphery=False, simplify=False)
    if intersections_only:
        G = ox.simplify_graph(G.copy(), strict=False)
    return G


def get_graph_from_point(location: Tuple[float, float], dist: int = 600):
    """

    Parameters
    ----------
    location: A lat/lon tuple for the center of the graph
    dist: Retain only those nodes within this many meters of the center of the graph

    Returns
    -------
    networkx.MultiDiGraph: Graph where nodes represent points and edges are sections of roadway
    """
    G = ox.graph_from_point(location, dist=dist, simplify=False)
    return G


def graph_to_nodes(G: networkx.MultiDiGraph):
    """
    Converts a graph to a list of nodes

    Parameters
    ----------
    G: The graph to convert

    Returns
    -------
    list: The nodes, represented as tuples.
            Tuple index 0 is the OSM node ID, index 1 is a dict
            The dict keys are 'y' (lat), 'x' (lon), 'osmid', and optionally 'highway'
    """
    return list(G.nodes(data=True))


def extract_intersection_type(G: networkx.MultiDiGraph, node):  # returns JunctionType
    """Get intersection type from adjacent edges to node
    """
    if len(G.edges(node)) < 2:
        return 0

    # keep track of which types of roadways are part of intersection
    roadtypes = set()
    for e in G.edges(node):
        # Look at every edge connected to this node        
        edge_data = G[e[0]][e[1]]

        highway_tags = [
            data['highway'] for data in edge_data.values() if 'highway' in data] + \
                [f"railway:{data['railway']}" for data in edge_data.values() if 'railway' in data]

        # some tags are a list, so extract each entry from those lists
        flattened_tags = []
        for tag in highway_tags:
            if isinstance(tag, str):
                flattened_tags.append(tag)
            else:
                flattened_tags.extend(tag)

        roadtypes.update(flattened_tags)


    junction_type = 0

    if 'path' in roadtypes and roadtypes & {'primary', 'secondary', 'tertiary', 'motorway', 'residential', 'service'}:
        junction_type |= JunctionType.PEDESTRIAN

    if 'cycleway' in roadtypes or 'trail' in roadtypes:
        junction_type |= JunctionType.BICYCLE_OR_TRAIL

    if any(['railway' in x for x in roadtypes]):
        junction_type |= JunctionType.RAILROAD

    if roadtypes & {'primary', 'secondary', 'tertiary', 'residential', 'service'}:
        junction_type |= JunctionType.ROADWAY

    if roadtypes & {'motorway', 'junction'}:
        junction_type |= JunctionType.INTERCHANGE_RAMP
    
    if not junction_type:
        junction_type = JunctionType.OTHER
    
    return junction_type


def extract_roadway_name(G: networkx.MultiDiGraph, edge: Tuple):
    """
    Get name from an edge, if defined
    """
    edge_data = G[edge[0]][edge[1]]
    for data in edge_data.values():
        if not 'name' in data:
            continue

        if isinstance(data['name'], str):
            return data['name']            

        else:
            # a list; return just the first entry for now. 
            # TODO: identify a better way to combine multiple names
            return data['name'][0]

    return None


def extract_intersection_oneway(G: networkx.MultiDiGraph, node):
    '''
    Get the proportion of roadway legs that are oneway for this intersection
    Parameters
    ----------
    G: Graph of roadway
    node: Intersection

    Returns
    -------
    Number of roadway legs that are oneway 0<=p<=1
    '''
    count = 0
    # IF there are no edges to a node return zero
    if len(G.edges(node)) == 0:
        return 0
    # In simplified graphs, there can be multiple edges per node pair
    total_num_edges = sum([len(e) for e in G.edges(node)])
    for n1, n2 in G.edges(node):
        edge_data = G.get_edge_data(n1, n2)
        for data in edge_data.values():
            if not 'oneway' in data:
                continue
            else:
                if np.isnan([data['oneway']]).any():
                    continue
                else:
                    if data['oneway']:
                        count += 1
                        
    #print("oneway : " + str(count / len(G.edges(node))))
    return count #/ len(G.edges(node)) #total_num_edges


def extract_intersection_lanes(G: networkx.MultiDiGraph, node):
    '''
    Extract the total number of roadway lanes at a given intersection
    (Sum of all lanes of all roadway legs)
    Parameters
    ----------
    G: Graph of roadway
    node: Intersection

    Returns
    -------
    Count of all roadway lanes, n>0
    '''
    count = 0
    if len(G.edges(node)) == 0:
        return 0
    for n1, n2 in G.edges(node):
        edge_data = G.get_edge_data(n1, n2)
        for data in edge_data.values():
            if not 'lanes' in data:
                continue
            else:
                try:
                    if isinstance(data['lanes'],list):
                        # Due to graph simplification, there can be subnodes
                        for subnode in data['lanes']:
                            count += int(subnode)
                    else:
                        count += int(data['lanes'])
                except ValueError:
                    continue

    return count


def extract_roadway_bearing(G: networkx.MultiDiGraph, edge):
    edge_data = G[edge[0]][edge[1]]
    for data in edge_data.values():
        if not 'bearing' in data:
            continue
        else:
            # print("BEARING:", data['bearing'])
            # import pdb
            # pdb.set_trace()
            if data['bearing'] and np.isnan([ data['bearing'] ]).any():
                return None 
            return data['bearing']
    
    return None


def extract_intersection_angles(G: networkx.MultiDiGraph, node):
    """
    Get element 129, intersecting angle
    """
    bearings = []
    for e in G.edges(node):
        bearing = extract_roadway_bearing(G, e)
        if bearing is not None:
            bearings.append(bearing)
    
    if len(bearings) > 1:
        # print("Bearings = " + str(bearings))
        bearing_cands = []
        for x in bearings:
            for y in bearings:
                # If the bearing is a list, it is a multi-point edge
                # We can take the first element as it is closest to the node
                if isinstance(x,list):
                    x = x[0]
                if isinstance(y,list):
                    y = y[0]
                val = float(abs(x-y))
                if val <= 90 and val >= 0 :
                    bearing_cands.append(val)
                elif val > 90 and val < 180:
                    bearing_cands.append(val-90)
                elif val >= 180 and val <= 270:
                    bearing_cands.append(val-180)
                elif val > 270 and val <= 360:
                    bearing_cands.append(360-val)
        # print("Final bearing : " + str(max(bearing_cands)))
        return IntersectingAngle(max(bearing_cands))
    
    return None

def extract_intersection_roadway_names(G: networkx.MultiDiGraph, node):  # List[str]
    """
    Get all the names of roads and trails in intersection
    """
    roadway_names = set()
    for e in G.edges(node):
        name = extract_roadway_name(G, e)
        if name is not None:
            roadway_names.update([name])
    
    return list(roadway_names)
