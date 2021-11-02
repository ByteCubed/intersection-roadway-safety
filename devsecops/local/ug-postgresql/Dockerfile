# Using the Postgres 14 base image
FROM postgres:14

# Documenting this image's maintainer
MAINTAINER U.Group

# Copying the initialization script into the initialization directory
# NOTE: ".sh" and ".sql" files do not execute if a database already exists.
COPY data/init/  /docker-entrypoint-initdb.d/
