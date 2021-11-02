# dot-roadway-safety
Once the application is started the index will be located at
localhost:9200.
# Search API
The Search API is located at localhost:8080/dot-roadway-safety/ followed by the index and the query parameters shown below.
The index names are as follows:

Table  ------------------------  Index

Planet_osm_line --------- lines

Planet_osm_point ------- points

Planet_osm_polygon --- polygons

Planet_osm_roads ------ roads

Spatial_ref_sys ---------- spatialref

## Searching Each Index
Use the syntax below in the api to achieve your desired data results.

### Get All Entities
Returns all entities of the index

/[index]/all

**Example:** localhost:8080/dot-roadway-safety/lines/all

### Get Entities by Paging Data
Returns a number of entities determined by pageSize. PageNumber represents the iterations (pages) into total entities.

**WARNING:** *page 0 represents the first page*

/[index]/page={pageNumber}/size={pageSize}

**Example:** localhost:8080/dot-roadway-safety/spatialref/page=3/size=500

### Get Entity By OSM_ID
Returns a single entity with the requested OSM_ID

/[index]/{osmID}

**Example:** localhost:8080/dot-roadway-safety/roads/131462971

### Get Entity By Name
Returns a single entity by matching to the Name field

/[index]/by-name/{name}

**Example:** localhost:8080/dot-roadway-safety/roads/by-name/{roadName}

### Get Entity Like Name
Returns a number of entities that contain a match in the name field

/[index]/like-name/{name}

**Example:** localhost:8080/dot-roadway-safety/polygons/like-name/{name}

# Manage Data

## OSM

### Ingest OSM data to postgres

1. Download an OSM file and place it in `./data/osm`.
2. Ingest OSM file
   ```shell
   ./ingest-osm.sh <filename>
   ```

### Index OSM data from postgres to Elasticsearch

```shell
./index-osm.sh
```

## Crashes CSV

### Ingest Crashes CSV to postgres

1. Obtain a copy of crashes data in CSV and place in `./data/crashes`
2. Ingest CSV file
   ```shell
   ./ingest-csv.sh <filename>
   ```

### Index Crashes data from postgres to Elasticsearch

```shell
./index-csv.sh
```
