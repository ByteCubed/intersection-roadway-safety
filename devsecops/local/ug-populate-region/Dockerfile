# Using the Postgres 14 base image
FROM postgis/postgis:13-master

# Documenting this image's maintainer
MAINTAINER U.Group

RUN apt-get update &&\
    apt-get install -y binutils libproj-dev gdal-bin &&\
    apt-get -qy install netcat

COPY ./devsecops/wait-for ./
COPY devsecops/local/ug-populate-region/init/init.sh ./
