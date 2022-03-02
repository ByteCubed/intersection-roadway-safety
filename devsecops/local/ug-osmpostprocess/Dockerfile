# Using the postgres base image
FROM postgis/postgis:13-master

# Documenting this image's maintainer
MAINTAINER U.Group

WORKDIR /postprocess/

COPY services/osm/postprocess/ /postprocess/

CMD sleep 1 && /postprocess/postprocess.sh
