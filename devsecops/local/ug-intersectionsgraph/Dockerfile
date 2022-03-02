# Using the Python 3.9 bullseye base image
FROM python:3.9.10-bullseye

# Documenting this image's maintainer
MAINTAINER U.Group

WORKDIR /usr/src/app

COPY ./devsecops/local/ug-intersectionsgraph/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY services/intersections/*.py ./intersectionsgraph/
COPY services/intersections/.env ./intersectionsgraph/
COPY services/intersections/dot/ ./intersectionsgraph/dot/

CMD python ./intersectionsgraph/intersections_init.py "District of Columbia" "dc_intersections.json" "100"
