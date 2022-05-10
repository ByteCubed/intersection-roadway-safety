"""
Mapbox Satellite Tiles
----------------------

This script is a set of tools for getting satellite imagery from MapBox.


TODO: tree search, https://automating-gis-processes.github.io/site/notebooks/L3/spatial_index.html
>>> node_sindex = nodes.sindex
>>> node_sindex.intersection.__doc__
'Find tree geometries that intersect the input coordinates.\n\n            Parameters\n            ----------\n            coordinates : sequence or array\n                Sequence of the form (min_x, min_y, max_x, max_y)\n                to query a rectangle or (x, y) to query a point.\n            objects : boolean, default False\n                If True, return the label based indexes. If False, integer indexes\n                are returned.\n            '
>>> N = 38.97729759796989
>>> S = 38.97516238593476
>>> E = -76.99307670898439
>>> W = -76.99582329101564
>>> node_sindex.intersection(W, S, E, N)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: intersection() takes from 2 to 3 positional arguments but 5 were given
>>> node_sindex.intersection((W, S, E, N))
<generator object Index._get_ids at 0x132dc2c10>
>>> node_idx = list(node_sindex.intersection((W, S, E, N)))
>>> nodes[node_idx]
Empty DataFrame
Columns: []
Index: [281072, 281074, 29918140, 29918141, 29918142, 29918143, 29918144, 29918145, 30066940, 30066941, 30066942, 30100500, 49167037, 49174193, 49182343, 49184747, 49188193, 49190879, 49190880, 49198976, 49243106, 49261234, 49262666, 49265638, 49283681, 49294805, 49321719, 49333578, 49368511, 49715918, 49715932, 49715936, 49715946, 49715951, 49715966, 49715970, 49715974, 49715981, 49715998, 49715999, 49716007, 49716018, 49716020, 49716021, 49716023, 49716024, 49716025, 49716026, 49716027, 49716030, 49716033, 49716039, 49716054, 49716056, 49716057, 49716059, 49716060, 49716061, 49716063, 49716064, 49716065, 49716066, 49716068, 49716069, 49716071, 49716074, 49716075, 49716078, 49716080, 49716082, 49716083, 49716084, 49716085, 49716086, 49716088, 49716089, 49716090, 49716091, 49716093, 49716094, 49716095, 49716097, 49716098, 49716100, 49716102, 49716126, 49716129, 49716131, 49716133, 49716134, 49716135, 49716137, 49716138, 49716152, 49716156, 49716157, 49716159, 49716160, 49716165, 49716175, ...]

[162603 rows x 0 columns]
>>> 
"""
import sys
sys.path.insert(0,'/Users/dylan.frizzell/dot/roadway-safety/old/src/')

import itertools
import numbers
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from io import BytesIO
import tempfile

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from skimage import io
from skimage.util import img_as_ubyte
from typing import Union, Tuple
import math
import os
import time
import pathlib
import requests
import requests_cache
from skimage.transform import resize

import osmnx as ox

from dot.mire_types.osm import GeoPoint

requests_cache.install_cache('satellite_cache')
MAPBOX_TOKEN = os.getenv('MAPBOX_TOKEN', None)
ZOOM_LEVEL = 18
TILE_WIDTH = {
    # Zoom level: Tile width in degrees of longitude
    18: 0.001,
    17: 0.003,
    16: 0.005,
    15: 0.011,
    14: 0.022,
    13: 0.044,
    12: 0.088,
    11: 0.176,
    10: 0.352,
    9: 0.703,
}

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


def get_feature_sizes(G):
    """
    Get node and edge sizes for graph rendering
    """
    default_width = 4
    street_widths = {
        "footway": 1.5,
        "steps": 1.5,
        "pedestrian": 1.5,
        "service": 1.5,
        "path": 1.5,
        "track": 1.5,
        "motorway": 6,
    }
    # for each edge, get a linewidth according to street type
    edge_linewidths = []
    for _, _, d in G.edges(keys=False, data=True):
        street_type = d["highway"][0] if isinstance(d["highway"], list) else d["highway"]
        if street_type in street_widths:
            edge_linewidths.append(street_widths[street_type])
        else:
            edge_linewidths.append(default_width)
    
    # for each node, get a nodesize according to the narrowest incident edge
    node_widths = dict()
    for node in G.nodes:
        # first, identify all the highway types of this node's incident edges
        ie_data = [G.get_edge_data(node, nbr) for nbr in G.neighbors(node)]
        edge_types = [d[min(d)]["highway"] for d in ie_data]
        if not edge_types:
            # if node has no incident edges, make size zero
            node_widths[node] = 0
        else:
            # flatten the list of edge types
            et_flat = []
            for et in edge_types:
                if isinstance(et, list):
                    et_flat.extend(et)
                else:
                    et_flat.append(et)

            # lookup corresponding width for each edge type in flat list
            edge_widths = [
                street_widths[et] if et in street_widths else default_width for et in et_flat
            ]

            # node diameter should equal largest edge width to make joints
            # perfectly smooth. alternatively use min(?) to prevent
            # anything larger from extending past smallest street's line.
            # circle marker sizes are in area, so use diameter squared.
            circle_diameter = max(edge_widths)
            circle_area = circle_diameter ** 2
            node_widths[node] = circle_area
    
    # assign the node size to each node in the graph
    node_sizes = [node_widths[node] for node in G.nodes]
    return node_sizes, edge_linewidths


class SlippyBox:
    """Collection of slippy tiles and bounding boxes to make images
    """
    url = f"https://api.mapbox.com/v4/mapbox.satellite"

    def __init__(
        self,
        zoom: int,
        center: GeoPoint,
        token = None,
        xy: Tuple[int, int] = None,
        nodes=None,
        edges=None,
        node_sindex=None,
        edge_sindex=None
        ):
        """
        Parameters
        ----------
        zoom:
            slippy tile zoom level
        center:
            lon/lat of center of time
        graph:
            pre-loaded graph, optional
        """
        self._image = None
        self._mask = None
        self._graph = None
                
        # TRUE if we use the tile, FALSE otherwise. Center [1,1] is always used
        self._tile_mask = np.array(
            [[0, 0, 0],
            [0, 1, 0],
            [0, 0, 0]],
            dtype=np.bool
        )

        self.zoom = int(zoom)
        if not token:
            self.token = MAPBOX_TOKEN
        else:
            self.token = str(token)

        # GeoPoints
        self.center_point = center
        self.upper_left_point = None
        self.lower_right_point = None

        # tiles        
        self.center_tile = None  # type: Tuple[int, int]

        if xy is not None:
            # tile name specified, use exactly that tile

            self.center_tile = xy
            self.center_proportion = (0.5, 0.5)  # center of the center tile
            # get UL of tile
            self.upper_left_point = SlippyMap.tile_to_point(self.center_tile[0], self.center_tile[1], self.zoom)

            # get LR of tile
            self.lower_right_point = SlippyMap.tile_to_point(self.center_tile[0]+1, self.center_tile[1]+1, self.zoom)
  
        else:
            # tile name not specified; get exactly one tile size, but combined from multiple tiles

            # tile in which center point exists
            self.center_tile = SlippyMap.point_to_tile(self.center_point.longitude, self.center_point.latitude, self.zoom)
            self.center_proportion = SlippyMap.point_to_proportion(self.center_point.longitude, self.center_point.latitude, self.zoom)

            px, py = self.center_proportion
            x, y = self.center_tile            

            if px <= 0.5 and py <= 0.5:
                                
                self.upper_left_point = SlippyMap.pixel_to_point(x-1, y-1, np.remainder(px-0.5, 1.0), np.remainder(py-0.5, 1.0), self.zoom)
                self.lower_right_point = SlippyMap.pixel_to_point(x, y, px+0.5, py+0.5, self.zoom)

                self._tile_mask[0, 0] = 1
                self._tile_mask[0, 1] = 1
                self._tile_mask[1, 0] = 1
                
            elif px <= 0.5 and py > 0.5:
                
                #ul_host_tile = (x-1 + np.remainder(px - 0.5, 1.0), y + py)
                #lr_host_tile = (x + px, y+1 + np.remainder(py + 0.5, 1.0))

                self.upper_left_point = SlippyMap.pixel_to_point(x-1, y, np.remainder(px - 0.5, 1.0), py-0.5, self.zoom)
                self.lower_right_point = SlippyMap.pixel_to_point(x, y+1, px+0.5, np.remainder(py+0.5,1.0), self.zoom)                

                self._tile_mask[1, 0] = 1
                self._tile_mask[2, 0] = 1
                self._tile_mask[2, 1] = 1
            
            elif px > 0.5 and py <= 0.5:
                
                #ul_host_tile = (x + px, y-1 + np.remainder(py - 0.5, 1.0))
                #lr_host_tile = (x+1 + np.remainder(px + 0.5, 1.0), y+py)

                self.upper_left_point = SlippyMap.pixel_to_point(x, y-1, px-0.5, np.remainder(py-0.5, 1.0), self.zoom)
                self.lower_right_point = SlippyMap.pixel_to_point(x+1, y, np.remainder(px+0.5,1.0), py + 0.5, self.zoom)

                self._tile_mask[0, 1] = 1
                self._tile_mask[0, 2] = 1
                self._tile_mask[1, 2] = 1
            
            elif px > 0.5 and py > 0.5:
                
                #ul_host_tile = (x + px, y + py)
                #lr_host_tile = (x + 1 + np.remainder(px + 0.5, 1.0), y+1+np.remainder(py+0.5, 1.0))

                self.upper_left_point = SlippyMap.pixel_to_point(x, y, px-0.5, py-0.5, self.zoom)
                self.lower_right_point = SlippyMap.pixel_to_point(
                    x+1, y+1, np.remainder(px+0.5, 1.0), np.remainder(py+0.5, 1.0), self.zoom
                )

                self._tile_mask[2, 1] = 1
                self._tile_mask[2, 2] = 1
                self._tile_mask[1, 2] = 1
        
        if nodes is not None:
            # todo: get bounding box
            N, S, E, W = self.upper_left_point.latitude, \
                     self.lower_right_point.latitude, \
                     self.lower_right_point.longitude, \
                     self.upper_left_point.longitude
                        
            nodes_idx = list(node_sindex.intersection((W, S, E, N)))
            edges_idx = list(edge_sindex.intersection((W, S, E, N)))

            new_nodes = nodes.iloc[nodes_idx]
            new_edges = edges.iloc[edges_idx]

            self._graph = ox.utils_graph.graph_from_gdfs(new_nodes, new_edges)
            
            

    @property
    def image(self):
        if self._image is None:
            full_image = None
            # use tile mask to request images. Use bounding box to stitch together.
            for i, j in itertools.product(range(-1, 2), repeat=2):
                if not self._tile_mask[j + 1, i + 1]:                    
                    continue

                # request image
                r = requests.get(f"{SlippyBox.url}/{self.zoom}/{self.center_tile[0] + i}/{self.center_tile[1] + j}.jpg70?access_token={self.token}")
                if r.status_code == 200:
                    f = BytesIO(r.content)
                    img = io.imread(f)

                    if full_image is None:
                        shape = (img.shape[0] * 3, img.shape[1] * 3, img.shape[2])
                        full_image = np.zeros(shape, dtype=img.dtype)
                    full_image[(j+1)*256:(j+2)*256,(i+1)*256:(i+2)*256,:] = img[:]
                else:
                    print(f"FAILURE {r.status_code} for {r.url}")

            # get center of target image relative to full image
            xloc = 256 + round(self.center_proportion[0] * 256)
            yloc = 256 + round(self.center_proportion[1] * 256)

            self._image = full_image[yloc-128:yloc+128, xloc-128:xloc+128, :]

        return self._image

    @property
    def osm_graph(self):
        """graph in bounding box
        """     
        if self._gdf is None:
            N, S, E, W = self.upper_left_point.latitude, self.lower_right_point.latitude, self.lower_right_point.longitude, self.upper_left_point.longitude
            G = ox.graph_from_bbox(
                N+0.001,
                S-0.001,
                E+0.001,
                W-0.001,
                simplify=False,
                retain_all=True,
                truncate_by_edge=True,                
                # clean_periphery=False,
                clean_periphery=True,
                network_type="all_private"
            )
            self._graph = ox.utils_graph.get_undirected(G)
                    
        return self._graph

    @property
    def figure_ground(self):
        """figure ground, adapted from osmnx
        """

        #if any([x is None for x in [self._node_sizes, self._edge_linewidths]]):
        self._node_sizes, self._edge_linewidths = get_feature_sizes(self._graph)
        # bounding box
        N, S, E, W = self.upper_left_point.latitude, \
                     self.lower_right_point.latitude, \
                     self.lower_right_point.longitude, \
                     self.upper_left_point.longitude
        # print('truncating..')        

        #tg = ox.truncate.truncate_graph_bbox(
        #    self._graph, N+0.001, S-0.001, E+0.001, W-0.001, retain_all=True,
        #)
        # print('done')
        
        f = tempfile.NamedTemporaryFile(suffix='.png')
        # print('plot graph')
        ox.plot_graph(
            self._graph,
            figsize=(2,2),
            show=False,
            bbox=(N,S,E,W),
            edge_linewidth=self._edge_linewidths,
            node_size=self._node_sizes,
            node_color='w',
            edge_color='w',
            save=True,
            filepath=f.name,
            dpi=300
        )
        # print('done!')
        # read the temp file image       
        img = io.imread(f.name)
    
        # rescale      
        img = resize(img_as_ubyte(img), (256, 256))
        # save the scaled image for testing
        #io.imsave('scaled.png', img)
        # return the image
        return img


    @property
    def osm_mask(self):
        """Get OSM data within bounding box
        """
        if self._mask is None:
            N, S, E, W = self.upper_left_point.latitude, self.lower_right_point.latitude, self.lower_right_point.longitude, self.upper_left_point.longitude
            G = ox.graph_from_bbox(
                N+0.0001,
                S-0.0001,
                E+0.0001,
                W-0.0001,
                simplify=False,
                retain_all=True,
                truncate_by_edge=True,                
                # clean_periphery=False,
                clean_periphery=True,
                network_type="all_private"
            )            
            
            fig = plt.figure(figsize=(3, 3), dpi=256, frameon=False, facecolor="#111111", tight_layout=True)
            ax = plt.axes()
            # ax.figure = fig
            ax.set_facecolor("#111111")
            # fig, ax = ox.plot_figure_ground(G, ax=ax, show=False, bbox=(N, S, E, W))
            
            #fig, ax = ox.plot_graph(G, show=True, node_size=6, edge_linewidth=3, bbox=(N,S,E,W), node_color='w', edge_color='w')
            
            # extent = ax.bbox.transformed(fig.dpi_scale_trans.inverted())
            fig, ax = ox.plot_graph(G, ax=ax, show=True, node_size=6, edge_linewidth=3, bbox=(N,S,E,W), node_color='w', edge_color='w')
            
            # print(fig.dpi)
            canvas = FigureCanvas(fig)
            canvas.draw()
            width, height = canvas.figure.get_size_inches() * canvas.figure.get_dpi()
            
            self._mask = np.fromstring(canvas.tostring_rgb(), dtype='uint8').reshape(int(width),int(height),3)
        
        return self._mask
            

class SlippyMap:
    """Encapsulate functionality for slippy map tile names and lat/lon mappings

    Note that this also encapsulates OSM functionality, which should probably be another
    class inheriting from SlippyMap.
    """
    def __init__(self, zoom, place=None, bbox=[], token=None):
        self.zoom = int(zoom)
        #ox.config(log_console=True)
        if place is not None:
            print(f"Place: {place}")
            # query to get initial map
            self._graph = ox.graph_from_place(
                place,
                simplify=False,
                retain_all=True,
                truncate_by_edge=True,
                # clean_periphery=False,
                clean_periphery=True,
                network_type="drive_service"
            )

            # get nodes, edges, and spatial index
            self._gdf_nodes, self._gdf_edges = ox.utils_graph.graph_to_gdfs(self._graph)
            self._node_sindex = self._gdf_nodes.sindex
            self._edge_sindex = self._gdf_edges.sindex
        elif len(bbox) >= 4:
            height = (bbox[0]-bbox[1])/2
            length = (bbox[2]-bbox[3])/2
            print(f"Center Point: {bbox[1] + height}, {bbox[3] + length} and height/length: {height}, {length}")
            # query to get initial map
            self._graph = ox.graph_from_bbox(
                north=bbox[0],
                south=bbox[1],
                east=bbox[2],
                west=bbox[3],
                simplify=False,
                retain_all=True,
                truncate_by_edge=True,
                # clean_periphery=False,
                clean_periphery=True,
                network_type="drive_service"
            )

            # get nodes, edges, and spatial index
            self._gdf_nodes, self._gdf_edges = ox.utils_graph.graph_to_gdfs(self._graph)
            self._node_sindex = self._gdf_nodes.sindex
            self._edge_sindex = self._gdf_edges.sindex
        else:
            self._graph = None
            self._gdf_nodes, self._gdf_edges = None, None
            self._node_sindex = None
            self._edge_sindex = None

        if not token:
            self.token = MAPBOX_TOKEN
        else:
            self.token = str(token)
    
    @staticmethod
    def point_to_tile(longitude, latitude, zoom):
        """
        Point in degrees to x/y tile name
        """
        lat_rad = math.radians(latitude)
        n = 2.0 ** zoom
        xtile = int((longitude + 180.0) / 360.0 * n)
        ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        
        return (xtile, ytile)
    
    @staticmethod
    def point_to_proportion(longitude, latitude, zoom):
        """
        Where does point land within tile, proportionally?
        """
        lat_rad = math.radians(latitude)
        n = 2.0 ** zoom
        xpct = math.modf((longitude + 180.0) / 360.0 * n)[0]
        ypct = math.modf((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)[0]
        return xpct, ypct

    @staticmethod
    def tile_to_center_point(x, y, zoom):
        """
        Get center point of a tile in lat/lon
        """    
        n = 2 ** (zoom + 1)  # center in coordinates of next zoom level

        center_lon = (2*x + 1) / n * 360.0 - 180.0
        center_lat = np.arctan(math.sinh(math.pi * (1 - 2 * (2*y + 1) / n))) * 180.0 / math.pi

        return GeoPoint(longitude=center_lon, latitude=center_lat)

    @staticmethod
    def tile_to_point(x, y, zoom):
        """
        Get lat/lon of upper-left of tile
        """
        n = 2 ** zoom

        lon = x / n * 360.0 - 180.0
        lat = np.arctan(math.sinh(math.pi * (1 - 2 * y / n))) * 180.0 / math.pi

        return GeoPoint(longitude=lon, latitude=lat)

    @staticmethod
    def pixel_to_point(x, y, px, py, zoom):
        """
        Transform pixel (given by px, py) within tile x, y, zoom
        into longitude/latitude geopoint
        """
        # full floating-point values... then invert to get lon/lat
        x = x + px
        y = y + py

        lon = x/(2**zoom)*360.0 - 180
        lat = math.atan(math.sinh(math.pi * (1 - 2*y/(2**zoom))))*180.0/math.pi

        return GeoPoint(longitude=lon, latitude=lat)

    def __getitem__(self, idx: Union[Tuple, GeoPoint]):
        # idx is lon/lat or tile index x, y
        # if lon/lat, find tile that contains point
        x = None
        y = None
        lon = None
        lat = None
        try:
            lon = idx.longitude
            lat = idx.latitude
        except AttributeError:
            if all(isinstance(x, numbers.Integral) for x in idx):
                # represents a tile name
                x, y = idx
            else:
                # lon/lat
                lon, lat = idx

        if not lon or not lat:
            center_point = self.tile_to_center_point(x, y, self.zoom)

        elif not x or not y:
            x, y = self.point_to_tile(lon, lat, self.zoom)
            center_point = GeoPoint(lon, lat)

        return SlippyBox(
            self.zoom,
            center=center_point,
            xy=(x, y),
            token=self.token
        )

    def __matmul__(self, center: Union[GeoPoint, Tuple]):
        """
        custom tile with center at geo coordinates

        * Get tile containing center
        * Get %x, %y in pixels, of point within that tile
        * Get neighboring tiles
        * crop

        """


        try:
            # what is the bounding box? Need to get that to trim the graph... or pass
            # spatial index along with nodes and edges
            return SlippyBox(
                self.zoom,
                center=GeoPoint(longitude=center[0], latitude=center[1]),
                token=self.token,
                nodes=self._gdf_nodes,
                edges=self._gdf_edges,
                node_sindex=self._node_sindex,
                edge_sindex=self._edge_sindex
                #gdf_nodes=self._gdf_nodes,
                #gdf_edges=self._gdf_edges
            )
        except TypeError:
            return SlippyBox(
                self.zoom,
                center=center,
                token=self.token,
                nodes=self._gdf_nodes,
                edges=self._gdf_edges,
                node_sindex=self._node_sindex,
                edge_sindex=self._edge_sindex
                #gdf_nodes=self._gdf_nodes,
                #gdf_edges=self._gdf_edges
            )




def lat_lon_to_tile(lat_deg: float, lon_deg: float, zoom: int = ZOOM_LEVEL):
    """
    Takes a point lat/lon and Mapbox zoom level and calculates the
    corresponding Mapbox tile image's X and Y coordinates

    Parameters
    ----------
    lat_deg: Latitude in degrees
    lon_deg: Longitude in degrees
    zoom: Mapbox zoom level (18 is closest, 1 is farthest)

    Returns
    -------
    tuple: Mapbox tile number coordinates for looking up images
    """
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (xtile, ytile)


def get_tile_url(x: int, y: int, zoom: int, token: str = MAPBOX_TOKEN):
    """
    Takes Mapbox tile information and parses into valid Mapbox image URL

    Parameters
    ----------
    x: Mapbox tile number x coordinate
    y: Mapbox tile number y coordinate
    zoom: Mapbox zoom level (18 is closest, 1 is farthest)
    token: Mapbox API token (from your Mapbox account)

    Returns
    -------
    str: The URL to the specified tile image
    """
    url = f"https://api.mapbox.com/v4/mapbox.satellite/{zoom}/{x}/{y}.jpg70?access_token={token}"
    return url


def get_tile_img(url: str):
    """
    Downloads Mapbox tile image from URL

    Parameters
    ----------
    url: Valid Mapbox URL

    Returns
    -------
    Mapbox tile image (JPG)
    """
    r = requests.get(url)
    if r.status_code == 200:
        return r.data()
    else:
        print(f"FAILURE {r.status_code}")


def lat_lon_to_proportion(lat_deg: float, lon_deg: float, zoom: int = ZOOM_LEVEL):
    """
    Calculates the X/Y location within an image of a given lat/lon at
    a given zoom level as a proportion.
    Top left = 0, 0
    Bottom right = 1, 1

    Parameters
    ----------
    lat_deg: Latitude of point in degrees
    lon_deg: Longitude of point in degrees
    zoom: Mapbox zoom level

    Returns
    -------
    tuple: X proportion and Y proportion
    """
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    x_proportion = math.modf((lon_deg + 180.0) / 360.0 * n)[0]
    y_proportion = math.modf((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)[0]
    return (x_proportion, y_proportion)


def draw_square_at_proportion(img: np.ndarray, x_prop: float, y_prop: float, radius: int = 5):
    """
    Draws a red square on img at the given x/y proportions.
    (Matplotlib stores images as numpy ndarrays)

    Parameters
    ----------
    img: The image upon which to draw the square
    x_prop: The X location of the point as a proportion (0=left, 1=right)
    y_prop: The Y location of the point as a proportion (0=top, 1=bottom)
    radius: Radius of the square to draw

    Returns
    -------
    np.ndarray: The new image
    """
    red = [255, 0, 0]
    img = img.copy()
    height, width, bands = img.shape

    # Update red pixel value for RGBA image
    if bands == 4:
        red = [1, 0, 0, 1]

    # Turn percentiles into pixels:
    x_pixel = round(x_prop * width)
    y_pixel = round(y_prop * height)

    # Draw a 10x10 red square at pixel location
    for i in range(y_pixel - radius, y_pixel + radius):
        for j in range(x_pixel - radius, x_pixel + radius):
            try:
                img[i][j] = red
            except IndexError:
                # Box hits edge of image
                continue

    return img


def draw_square_at_pixel(img, x_pixel: int, y_pixel: int, radius: int = 5):
    """
    Draws a red square on img at the pixel location given
    https://stackoverflow.com/questions/55545400/how-to-draw-a-point-in-an-image-using-given-coordinate

    Parameters
    ----------
    img: The image upon which to draw the square
    x_pct: The X location of the point as a pixel/index
    y_pct: The Y location of the point as a pixel/index
    radius: Radius of the square to draw

    Returns
    -------
    np.ndarray: The new image
    """
    red = [255, 0, 0]
    img = img.copy()
    height, width, bands = img.shape

    # Update red pixel value for RGBA image
    if bands == 4:
        red = [1, 0, 0, 1]

    # Draw a red square at pixel location
    for i in range(y_pixel - radius, y_pixel + radius):
        for j in range(x_pixel - radius, x_pixel + radius):
            try:
                img[i][j] = red
            except IndexError:
                # Box hits edge of image
                continue

    return img


def get_cropped_centered_img(lat: float, lon: float, mapbox_token: str = MAPBOX_TOKEN,
                             zoom: int = ZOOM_LEVEL, mark_point=True):
    """
    Takes a lat/lon for a point, gets the corresponding Mapbox tile image,
    and the neighboring images necessary to put the point in the center of the image.
    Composites the tiles into a single 256x256 image and then centers it at the point.
    Draws a red square at the given point.

    Parameters
    ----------
    lat: Latitude of point
    lon: Longitude of point
    mapbox_token: Mapbox API token
    zoom: Mapbox zoom level

    Returns
    -------
    np.ndarray: The final composited image with red square at point
    """
    # Get the image containing the lat-lon point first
    x, y = lat_lon_to_tile(lat, lon, zoom=zoom)
    center_img = get_tile_url(x, y, zoom=zoom, token=mapbox_token)
    # Locate the point in the image
    x_loc, y_loc = lat_lon_to_proportion(lat, lon, zoom=zoom)
    x_pixel, y_pixel = None, None

    # The 4 if blocks get the main image url and the other 3 needed for the composite image
    if (x_loc >= 0.5) and (y_loc >= 0.5):
        top_left_tile = center_img
        # Get tiles to the right, below, and below-right
        top_right_tile = get_tile_url(x + 1, y, zoom=zoom, token=mapbox_token)
        bottom_left_tile = get_tile_url(x, y + 1, zoom=zoom, token=mapbox_token)
        bottom_right_tile = get_tile_url(x + 1, y + 1, zoom=zoom, token=mapbox_token)
        # Change location of point from percentiles into pixels
        x_pixel = round(x_loc * 256)
        y_pixel = round(y_loc * 256)

    if (x_loc < 0.5) and (y_loc >= 0.5):
        top_right_tile = center_img
        # Get tiles to the left, below, and below-left
        top_left_tile = get_tile_url(x - 1, y, zoom=zoom, token=mapbox_token)
        bottom_right_tile = get_tile_url(x, y + 1, zoom=zoom, token=mapbox_token)
        bottom_left_tile = get_tile_url(x - 1, y + 1, zoom=zoom, token=mapbox_token)
        # Change location of point from percentiles into pixels
        x_pixel = round(x_loc * 256) + 256
        y_pixel = round(y_loc * 256)

    if (x_loc >= 0.5) and (y_loc < 0.5):
        bottom_left_tile = center_img
        # Get tiles to the right, above, and above-right
        bottom_right_tile = get_tile_url(x + 1, y, zoom=zoom, token=mapbox_token)
        top_left_tile = get_tile_url(x, y - 1, zoom=zoom, token=mapbox_token)
        top_right_tile = get_tile_url(x + 1, y - 1, zoom=zoom, token=mapbox_token)
        # Change location of point from percentiles into pixels
        x_pixel = round(x_loc * 256)
        y_pixel = round(y_loc * 256) + 256

    if (x_loc < 0.5) and (y_loc < 0.5):
        bottom_right_tile = center_img
        # Get tiles to the left, above, and above-left
        bottom_left_tile = get_tile_url(x - 1, y, zoom=zoom, token=mapbox_token)
        top_right_tile = get_tile_url(x, y - 1, zoom=zoom, token=mapbox_token)
        top_left_tile = get_tile_url(x - 1, y - 1, zoom=zoom, token=mapbox_token)
        # Change location of point from percentiles into pixels
        x_pixel = round(x_loc * 256) + 256
        y_pixel = round(y_loc * 256) + 256

    # Download all 4 images
    top_left_img = io.imread(top_left_tile)
    top_right_img = io.imread(top_right_tile)
    bottom_left_img = io.imread(bottom_left_tile)
    bottom_right_img = io.imread(bottom_right_tile)

    # Composite image
    top_img = np.concatenate((top_left_img, top_right_img), axis=1)
    bottom_img = np.concatenate((bottom_left_img, bottom_right_img), axis=1)
    full_img = np.concatenate((top_img, bottom_img), axis=0)

    # Add red square at point
    if mark_point:
        full_img = draw_square_at_pixel(full_img, x_pixel, y_pixel)

    # Resize to 256, centered at point, and return final img
    x_min = x_pixel - 128
    x_max = x_pixel + 128
    y_min = y_pixel - 128
    y_max = y_pixel + 128

    return full_img[y_min:y_max, x_min:x_max]


def draw_dc_intersection_crash_img(lat: float, lon: float, mapbox_token: str = MAPBOX_TOKEN,
                                   zoom: int = ZOOM_LEVEL, **kwargs):
    """
    Using MatPlotLib display a satellite image centered at the given lat/lon
    and draw a circle at the point of each crash in the DC crash dataset.

    Parameters
    ----------
    lat: Latitude of point
    lon: Longitude of point
    mapbox_token: Mapbox API token
    zoom: Mapbox zoom level
    **kwargs: Arguments to set MatPlotLib options, e.g. radius=2, alpha=0.5

    Returns
    -------
    None: this function displays an image using MatPlotLib
    """

    # Load DC crash data file
    cwd = pathlib.Path(__file__).absolute()
    dot_dir = cwd.parent.parent.parent
    dc_crash_filepath = dot_dir / 'data' / 'Crashes_in_DC.csv'
    crashes = pd.read_csv(str(dc_crash_filepath), low_memory=False,
                          usecols=['LATITUDE', 'LONGITUDE'])
    crashes.columns = ['lat', 'lon']

    # Get lat/lon bounds for image at given zoom level
    lat_min = lat - TILE_WIDTH[zoom] * (127 / 256)
    lat_max = lat + TILE_WIDTH[zoom] * (127 / 256)
    lon_min = lon - TILE_WIDTH[zoom] * (127 / 256)
    lon_max = lon + TILE_WIDTH[zoom] * (127 / 256)

    # Select just the crashes that will be on the image
    visible_crashes = crashes[(crashes['lat'] > lat_min) & (crashes['lat'] < lat_max) &
                              (crashes['lon'] > lon_min) & (crashes['lon'] < lon_max)]

    # Draw the intersection satellite image
    plt.imshow(get_cropped_centered_img(lat, lon, mapbox_token, zoom=zoom, mark_point=False))
    # For each crash, add a circle to the image
    for idx, (crash_lat, crash_lon) in visible_crashes.iterrows():
        x_prop, y_prop = lat_lon_to_proportion(crash_lat, crash_lon, zoom)
        x_px = x_prop * 256
        y_px = y_prop * 256
        circle = plt.Circle((x_px, y_px), **kwargs)
        plt.gca().add_patch(circle)
    # Display the final image
    plt.axis('off')
    plt.show()


def tile_latitude_range(y, z, dim=256):
    """
    Longitude of each pixel in an image. Default 256 pixels in image.
    """
    pix_range = np.linspace(y, y+1, dim)
    n = 2**z
    lat = np.degrees(np.arctan(np.sinh(np.pi * (1-2*pix_range/n))))

    return pix_range, lat

def tile_resolution_range(y, z, dim=256):
    """
    Get distance in meters per pixel
    """
    pix_range, lat = tile_latitude_range(y, z, dim=dim)
    n = 2**z
    res = 156543.03 * np.cos(lat) / n  # 156543.03 is distance of equator in meters
    return res


if __name__ == "__main__":
    # NY Ave NW & 1st St NW, Washington DC
    dc_latitude, dc_longitude = 38.906296, -77.012163
    draw_dc_intersection_crash_img(dc_latitude, dc_longitude,
                                   mapbox_token=MAPBOX_TOKEN, zoom=18,
                                   radius=2, facecolor='red',
                                   edgecolor='red', linewidth='1', alpha=0.5
                                   )
