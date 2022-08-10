#Database Structure

##Data Sources

Data is ingested from three main sources and two supplementary sources: 
* OSM data, which provides standardized intersections, line segments, and the bulk of the features.
  * Drawn from [Open Street Map](https://www.openstreetmap.org/#map=8/32.708/-83.178); [download here](https://download.geofabrik.de/north-america/us.html).
  * Ingested from pbf files during the osm2pgsql step
* Crash Data, which provides details about crashes. Currently primarily used for total number of crashes; more features may be extracted later.
  * Drawn from Local DOT sites. [Open Data DC](https://opendata.dc.gov/datasets/crashes-in-dc/explore?location=38.906855%2C-77.068696%2C17.14), [Iowa](https://icat.iowadot.gov/), [Iowa (old)](https://mydata.iowa.gov/Crashes/Crash-Data/vagm-kc4w)

  * Ingested from csv during postgresql step
* Traffic Volume Data or AADT (Annual Average Daily Traffic). 
  * Drawn from Local DOT sites. [Open Data DC](https://opendata.dc.gov/datasets/DCGIS::2018-traffic-volume/about), [Iowa](https://public-iowadot.opendata.arcgis.com/datasets/IowaDOT::traffic-information/about)
  * Ingested from geojson during postgresql step
* Static ESRI data was not used in intersection generation but may be of interest to provide a ballpark check on intersection accuracy
  * Drawn from the csv download [available here](https://edg.epa.gov/metadata/catalog/search/resource/details.page?uuid=%7B33514B4C-54F2-464A-BCC7-35F441B7E21A%7D), with [documentation here.](https://www.epa.gov/sites/default/files/2021-06/documents/epa_sld_3.0_technicaldocumentationuserguide_may2021.pdf)
  * Intersection density is labeled D3b. Land area that is not protected from development is labeled Ac_Unpr.

* County Boundary Data was also used in the docker version of the application, and imported for consistency but otherwise unused in the Databricks version
  * County Boundary Data was pulled from [OpenDataSoft](https://public.opendatasoft.com/explore/dataset/us-county-boundaries/table/?disjunctive.statefp&disjunctive.countyfp&disjunctive.name&disjunctive.namelsad&disjunctive.stusab&disjunctive.state_name)


##Schema Structure
The schemas used include
* Public
  * This is where postgis functions are kept. Always use this as a secondary schema on your search path.
  * No DOT data is stored here.
  * Contains DOT metadata, such as the state of processing for each region
* MIRE
  * Stands for Model Inventory of Roadway Elements
  * Contains static reference tables for relevant features
* Regional Schemas
  * Regional Schemas don't have one name; instead, their name is assigned based on the region coved. E.g., "DC" or "Iowa"
  * These schemas contain the intersections and features for their corresponding region.

##Adding a New Region
Create a folder with the name of the region you'd like under the "data" folder at the top level of this project.
Underneath the folder, create 3 subfolders, named "aadt", "crashes", and "osm". Place your data sources in the corresponding folders.
Optionally, add a "preingest" or "postprocess" folder if you have sql you'd like to execute before or after the ingestion.

##Regional Raw Data Tables
####Crashes_Raw
Raw Traffic Data, should contain at minimum a crash, a row identifier, and a geometry object indicating the location the data corresponds to.
May also include data on crash severity; additional information about the crash may be used in the future.
Used to populate the non-raw crash table.
This table is populated from regional crash data sources, which are not necessarily standardized at the national level. Consequently, some custom processing may be necessary.
####Traffic_Volume_Raw
Raw Traffic Data, should contain at minimum the aadt (Annual Average Daily Traffic), a row identifier, and a geometry object indicating the location the data corresponds to.
Used to populate the non-raw traffic_volume table.
This table is populated from regional traffic volume sources, which are not necessarily standardized at the national level. Consequently, some custom processing may be necessary.
####Planet_OSM_Line
Contains a subset of Planet_OSM_Ways with interesting tags. Largely unused.
####Planet_OSM_Nodes
Contains points in space. Ways are formed from node sequences; each curve in a line must include at least one node. These are the basic building blocks underlying everything else.
####Planet_OSM_Point
Contains a subset of Planet_OSM_Nodes with interesting tags. Largely unused.
####Planet_OSM_Polygon
Contains ways which form an enclosed area, such as a reservoir. Largely unused.
####Planet_OSM_Rels
One of the three core data elements of osm (together with nodes and ways). Models logical relations between items (e.g., city boundaries, a road, or a shopping center). Currently unused.
####Planet_OSM_Roads
Contains a subset of Planet_OSM_Lines (itself a subset of Planet_OSM_Ways) suitable for rendering at low zoom levels. Largely unused.
####Planet_OSM_Ways
Contains a unique way ID, a list of nodes, and a list of features. In the feature list, every odd entry is a label and the following even entry is the data under that label.
(E.g., [highway, motorway] would mean that this way's highway type is a motorway.)

##Regional Tables

####Crashes
Contains crash data and a link to the closest node_id within 50 meters.

####Traffic_Volume
Contains aadt and a link to node_ids within 5 meters.

####Intersection_Angle
Contains the angles between "legs" of an intersection.

####Intersection_Features

Primary key is node_id. Tracks intersections and some rolled-up features from the way features view, crashes, traffic volume, and intersection_angle ables.

####Node

The basic OSM "point".
Some nodes are intersections; others are just bends in the road. Still others aren't on roads at all, but represent corners of buildings or the boundaries of state parks.

####Node_Intersections

The subset of nodes that are intersections. Contains some helpful aggregate features like the combined way_lines of its intersecting ways. Largely obsoleted by its derivative intersection_features.

####Way

A basic OSM feature. Ways are composed of line segments which are connected points. 

####Way_Feature

Contains a many-to-one mapping of way_id to feature name and feature description. Largely obsoleted by the way feature view.

####Way_Node

Contains a many-to-many mapping of way_id to node_id. Used as a link between things that care about ways (features) and things that care about nodes (intersections).

####Waylet

A waylet is a line segment between two connected points on a way. Used for building intersection features.

##Views

####Way_Feature_View

Summarizes the way_feature table, condensing all features into a flat, csv-like format. Associated with ways.

####Curated_Way_Feature_View

A subsection of the way_feature_view, focusing on features of particular interest. Unlike the underlying way_feature view, this view links directly to node_intersections as well. One intersection may have multiple entries in the curated way feature view.

##Reference Tables

###Public

The tables in the public schema are process aids as a rule. They include the following tables.

####County_Lines_Raw

Contains raw data denoting county boundaries. Used for breaking large states into smaller, more manageable regions for processing.

####County_Lines

Identical to the raw county line data with minor modifications for ease of processing. Notably, the area3857 field is added, which maps the polygons to geometry SRID 3857, the standard used in our other tables.

####Region_State

A static table listing states of processing (e.g., OSM ingest started, OSM Postprocess complete, Satellite image processing started)

####Region_Status

A table mapping regions to processing states defined in the region_state table.

###MIRE

Contains reference tables for MIRE features.

####Junction_Geometry_Type

Contains a list of geometry types (described in MIRE 116) for intersections, such as Y-intersections, T-Intersections, Roundabouts, etc.

####Junction_Type

Contains a list of types of intersections(described in MIRE 111), such as roadway/roadway (non-interchange), roadway/bikepath, etc.
