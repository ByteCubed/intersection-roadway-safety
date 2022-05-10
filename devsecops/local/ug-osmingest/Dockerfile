# Using the Python 3.9 bullseye base image
FROM python:3.9.10-bullseye

# Documenting this image's maintainer
MAINTAINER U.Group

WORKDIR /usr/src/app

RUN apt-get -q update && apt-get -qy install netcat
RUN apt-get -y install osm2pgsql
RUN apt-get -y install osmctools

COPY ./devsecops/local/ug-osmingest/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./devsecops/wait-for ./

COPY data/default.style ./data/
COPY services/osmingest/*.py ./
COPY services/osmingest/*.sh ./
COPY services/postprocess/*.sql ./postprocess/


