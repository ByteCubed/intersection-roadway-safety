# Using the Ubuntu base image
FROM ubuntu:21.10

# Documenting this image's maintainer
MAINTAINER U.Group

ENV DEBIAN_FRONTEND noninteractive

# Installing osm2pgsql
RUN apt-get update
RUN apt-get -y install osm2pgsql
RUN apt-get -y install osmctools
RUN apt-get -q update && apt-get -qy install netcat

COPY ./devsecops/local/ug-osm2pgsql/init/init.sh ./
COPY ./devsecops/wait-for ./
COPY services/postprocess/ /postprocess/
