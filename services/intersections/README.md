# Prototype data pipeline:
This folder contains all necessary resources that can be used to populate the postGIS 
database with MIRE features. Ultimately this code should be moved into its own microservice
in the devsecops folder. Furthermore, it might be useful to have this service split into a server
that accepts requests from a user, like ingest satellite images in DC and load them in the database.
This way a user can specify which what area they are most interested in dynamically.

To run, after activating a virtual environment:
* Populate your.env file with database credentials and mapbox token
	Specifically, "cp .env_blank .env", open .env and fill out MAPBOX token with your token obtained from the Mapbox website after creating an account.

* Execute the following commands:
```
    pip install -r requirements.txt
    python prepare_osm_graph.py "District of Columbia" # Using DC as an example location
    python prepare_osm_intersections.py "District of Columbia" # Depends on previous output
    python prepare_intersection_masks.py "dc_intersections.json" "District of Columbia" 100 # json from previous, # limit 100
    python load_intersections.py "dc_intersections.json" "District of Columbia" 
    python calculate_total_num_legs.py 
```

Windows Note - Installation may fail due to: 
* lacking a GDAL environment variable 
* because a package is lacking a proper wheel file
in either case download the appropriate wheel file, and run ```pip install <downloaded wheel file path>```

Afterwards, rerun ```pip install -r requirements.txt```
