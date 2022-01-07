"""
Take intersection data from OpenStreetMap and integrate crash data from
the US Accidents dataset into it.

For initial exploration this script is bound on DC. This makes things
easy because it is classified as a state but it's fairly small.
"""

from dot import osm
import geopandas as gpd
from geopy.distance import distance
import numpy as np
import osmnx as ox
import pandas as pd
from scipy.special import softmax
import stringcase
from tqdm import tqdm

from warnings import simplefilter


# Ignore all future warnings because of GeoPandas dependencies complaining
simplefilter(action='ignore', category=FutureWarning)


def ingest_intersections(location: str):
    # Taken from data/prepare_osm_intersections.py
    # Get simplified graph, keeping only endpoints and intersections:
    print("loading graph...")
    G = ox.io.load_graphml(f"{stringcase.alphanumcase(location)}.graphml", node_type=str)

    print("iterating over points...")
    # get GeoJSON Points...
    n_nodes = len(G)
    intersections = []
    for nid in tqdm(G.nodes, nrows=n_nodes):

        # street_names = extract_intersection_roadway_names(G, nid)
        # get intersection types, element 121
        intersection_type = osm.extract_intersection_type(G, nid)

        # get names of roadways and paths meeting at intersection
        names = osm.extract_intersection_roadway_names(G, nid)

        # get total number of lanes at intersection
        lanes = osm.extract_intersection_lanes(G, nid)

        # get proportion of roadway segments that are oneway at intersection
        oneway = osm.extract_intersection_oneway(G, nid)

        # intersecting angle
        angle = osm.extract_intersection_angles(G, nid)

        if len(G.edges(nid)) <= 2:
            continue
        intersections.append({
            'junction_type': intersection_type,
            'num_legs': len(G.edges(nid)),
            'angle': angle,
            'oneway': oneway,
            'lanes': lanes,
            'longitude': G.nodes[nid]['x'],
            'latitude': G.nodes[nid]['y'],
        })

    return intersections


def integrate(acc_df: pd.DataFrame, intrs_df: pd.DataFrame, radius: int):
    '''

    Parameters
    ----------
    acc_df: DataFrame containing accidents from the US_Accidents dataset for the chosen locale
    intrs_df: DataFrame containing intersections loaded from OpenStreetMap for the chosen locale
    radius: The radius within which to associate crashes to nearby intersections (in meters)

    Returns
    -------
    DataFrame of intersections with `accidents` column containing lists of accidents
    '''
    # Create GeoPandas DataFrame
    # Resource: https://gis.stackexchange.com/questions/349637/given-list-of-points-lat-long-how-to-find-all-points-within-radius-of-a-give
    # crs argument is to set the Coordinate Reference System
    # EPSG:4326 is the WGS84 latitude-longitude projection, units in degrees
    intrs_gdf = gpd.GeoDataFrame(dc_intrs_df,
                                    geometry=gpd.points_from_xy(dc_intrs_df.longitude,
                                                                dc_intrs_df.latitude),
                                    crs={"init": "EPSG:4326"})
    acc_gdf = gpd.GeoDataFrame(dc_acc_df, geometry=gpd.points_from_xy(dc_acc_df.Start_Lng,
                                                                      dc_acc_df.Start_Lat),
                                  crs={"init": "EPSG:4326"})

    # Create projection to measure distances in meters
    # EPSG:3857 is WGS 84 / Pseudo-Mercator -- Spherical Mercator, Google Maps, OpenStreetMap, Bing, ArcGIS, ESRI
    # Ellipsoidal distance model! Units in meters
    intrs_gdf_proj = intrs_gdf.to_crs({"init": "EPSG:3857"})
    acc_gdf_proj = acc_gdf.to_crs({"init": "EPSG:3857"})

    # Put it all together to create a list of:
    # [{'accident': id, 'weight': softmin} , ...] for each intersection¶
    print("Match crashes to intersections")
    new_intrs_list = []
    for idx, intr_row in tqdm(intrs_gdf_proj.iterrows(), total=intrs_gdf.shape[0]):
        # make row into GPD df
        df = intr_row.to_frame().T
        gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude),
                               crs={"init": "EPSG:4326"})
        gdf_proj = gdf.to_crs({"init": "EPSG:3857"})
        # Expand the boundaries 200m beyond the boundaries of the intersection point
        x = gdf_proj.buffer(radius).unary_union

        # Find all the accident entries within this 200m radius
        neighbors = acc_gdf_proj["geometry"].intersection(x)

        # Get the distance from each accident to the intersection
        accidents = []
        for idx, acc_row in acc_gdf_proj[~neighbors.is_empty].iterrows():
            crash_dist = distance((intr_row.latitude, intr_row.longitude),
                                  (acc_row.Start_Lat, acc_row.Start_Lng))
            accidents.append({'acc_id': idx,
                              'latitude': acc_row.Start_Lat,
                              'longitude': acc_row.Start_Lng,
                              'dist': crash_dist.m,
                              'severity': acc_row['Severity'],
                              'time': acc_row['Start_Time'],
                              'temp': acc_row['Temperature(F)'],
                              'crossing': acc_row['Crossing'],
                              'roundabout': acc_row['Roundabout'],
                              'stop': acc_row['Stop'],
                              'traffic_signal': acc_row['Traffic_Signal'],
                              'night': True if acc_row['Civil_Twilight']=="Night" else False,
                              'precipitation': True if np.isnan(acc_row['Precipitation(in)']) else False
                              })

        # Extract intersection features from accidents
        if len(accidents) > 0:
            count = 0
            crossing = 0
            roundabout = 0
            stop = 0
            traffic_signal = 0
            for accident in accidents:
                if accident['crossing'] is True:
                    crossing += 1
                if accident['roundabout'] is True:
                    roundabout += 1
                if accident['stop'] is True:
                    stop += 1
                if accident['traffic_signal'] is True:
                    traffic_signal += 1
                count += 1

            is_crossing = True if crossing/count >= 0.5 else False
            is_roundabout = True if roundabout/count >= 0.5 else False
            is_stop = True if stop/count >= 0.5 else False
            is_signal = True if traffic_signal/count >= 0.5 else False
        else:
            is_crossing = np.NaN
            is_roundabout = np.NaN
            is_stop = np.NaN
            is_signal = np.NaN

        # Convert the distances to weights with SoftMin(x) which is SoftMax(-x)
        if len(accidents) > 0:
            weights = softmax([-i['dist'] for i in accidents])
            for accident, weight in zip(accidents, weights):
                accident['weight'] = weight

        # Create new intersection entry for new final DF
        new_intr_row = {
            'lat': intr_row['latitude'],
            'lon': intr_row['longitude'],
            'accidents': accidents,
            'type': intr_row['junction_type'],
            'num_legs': intr_row['num_legs'],
            'lanes': intr_row['lanes'],
            'angle': intr_row['angle'],
            'oneway': intr_row['oneway'],
            'crossing': is_crossing,
            'roundabout': is_roundabout,
            'stop': is_stop,
            'traffic_signal': is_signal,
        }
        new_intrs_list.append(new_intr_row)

    return pd.DataFrame(new_intrs_list)


if __name__=="__main__":
    # Load US Accidents
    print("Loading accidents from data/US_Accidents_June20.tar")
    us_acc_df = pd.read_csv('US_Accidents_June20.tar', low_memory=False)
    dc_acc_df = us_acc_df[us_acc_df['State'] == 'DC']

    # Load intersections
    dc_intrs_list = ingest_intersections('District of Columbia')
    dc_intrs_df = pd.DataFrame(dc_intrs_list)

    # Debug:
    # dc_intrs_df = dc_intrs_df.head(2000)

    new_intrs_df = integrate(dc_acc_df, dc_intrs_df, 50)

    print(f"Processed all intersections. Saving intersection_accidents.json to disk.")
    new_intrs_df.to_json("intersection_accidents.json")
    new_intrs_df.to_pickle("intersection_accidents.pkl")