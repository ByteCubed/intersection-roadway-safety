# Using the postgres base image
FROM postgis/postgis:13-master

# Documenting this image's maintainer
MAINTAINER U.Group

WORKDIR /intersections/

COPY services/intersections/create-intersections-xsect/ /intersections/

CMD sleep 15 && /intersections/create-intersections-xsect.sh
