# Using the Python 3.9 bullseye base image
FROM python:3.9.10-bullseye

# Documenting this image's maintainer
MAINTAINER U.Group

WORKDIR /usr/src/app

COPY ./devsecops/local/ug-satimages/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY services/generate_satimages_masks/*.py ./satimages/
COPY services/generate_satimages_masks/.env ./satimages/
COPY services/generate_satimages_masks/dot/ ./satimages/dot/

CMD python ./satimages/generate_intersection_masks.py "District of Columbia", "dc_intersections.json", "100"
