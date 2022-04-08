#Database Structure
##Data Sources
Data is ingested from three sources: 
* OSM data, which provides standardized intersections, line segments, and the bulk of the features. 
  * Drawn from Open Street Map
  * Ingested from pbf files during the osm2pgsql step
* Crash Data, which provides details about crashes. Currently primarily used for total number of crashes; more features may be extracted later.
  * Drawn from Local DOT sites
  * Ingested from csv during postgresql step
* Traffic Volume Data or AADT (Annual Average Daily Traffic). 
  * Drawn from Local DOT sites
  * Ingested from geojson during postgresql step

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
####Traffic_Volume_Raw
####Planet_OSM_Line
####Planet_OSM_Nodes
####Planet_OSM_Point
####Planet_OSM_Polygon
####Planet_OSM_Rels
####Planet_OSM_Roads
####Planet_OSM_Ways

##Regional Tables
####Crashes
Contains crash data and a link to the closest node_id within 50 meters.
####Traffic_Volume
####Intersection_Angle
Contains the angles between "legs" of an intersection.
####Intersection_Features
Primary key is node_id. Tracks intersections and some rolled-up features from the way features view, crashes, traffic volume, and intersection_angle ables.
####Node
The basic OSM "point".
Some nodes are intersections; others are just bends in the road.
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
