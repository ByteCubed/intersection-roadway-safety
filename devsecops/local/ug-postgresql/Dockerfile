# Using the Postgres 14 base image
FROM postgis/postgis:13-master

# Documenting this image's maintainer
MAINTAINER U.Group

RUN apt-get update &&\
    apt-get install -y binutils libproj-dev gdal-bin

# Copying the initialization script into the initialization directory
# NOTE: ".sh" and ".sql" files do not execute if a database already exists.
COPY devsecops/local/ug-postgresql/init/init.sh  /docker-entrypoint-initdb.d/
COPY data/us-county-boundaries.geojson  /data/
COPY data/OpenDataDC_Intersection_Points_for_accuracy_metric.geojson  /data/

