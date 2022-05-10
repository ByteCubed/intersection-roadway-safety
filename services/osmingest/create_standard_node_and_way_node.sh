#!/bin/bash

region_name=$1

psql -h $HOSTNAME -p "$PORT" -U $POSTGRES_BUILDER_USER -d $POSTGRES_DB -c "ALTER ROLE $POSTGRES_BUILDER_USER SET search_path = $region_name,public;"
echo "Creating node table for $region_name"
psql -h $HOSTNAME -p "$PORT" -U $POSTGRES_BUILDER_USER -d $POSTGRES_DB -f ./postprocess/node_creation_query.sql
echo "Creating way_node table for $region_name"
psql -h $HOSTNAME -p "$PORT" -U $POSTGRES_BUILDER_USER -d $POSTGRES_DB -f ./postprocess/way_node_creation_query.sql