# Using the Python 3.9 bullseye base image
FROM python:3.9.10-bullseye

# Documenting this image's maintainer
MAINTAINER U.Group

WORKDIR /usr/src/app

RUN apt-get -q update && apt-get -qy install netcat

COPY ./devsecops/local/ug-satimages/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./devsecops/wait-for ./
COPY services/generate_satimages_masks/*.py ./satimages/
COPY services/generate_satimages_masks/dot/ ./satimages/dot/
