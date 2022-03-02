# Using the Ubuntu base image
FROM ubuntu:18.04

# Documenting this image's maintainer
MAINTAINER U.Group

ENV DEBIAN_FRONTEND noninteractive

# Installing osm2pgsql
RUN apt-get update
RUN apt-get -y install osm2pgsql

CMD sleep 10 && osm2pgsql --number-process=4 -H $HOSTNAME -U $POSTGRES_USER -d $POSTGRES_DB -s -S ./tmp/osm/default.style ./tmp/osm/district-of-columbia-latest.osm.pbf
