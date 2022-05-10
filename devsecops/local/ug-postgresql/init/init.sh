#!/bin/bash

# Set max_wal_size
psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "ALTER SYSTEM SET max_wal_size TO 4096"

psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "CREATE EXTENSION hstore"

ogr2ogr -f "PostgreSQL" PG:"dbname=$POSTGRES_DB user=$POSTGRES_USER" "data/us-county-boundaries.geojson" -nln "public.county_lines_raw" -append
psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "create table public.county_lines as select ogc_fid, intptlat, countyfp_nozero::int, countyns, stusab, csafp, state_name, aland, geoid::int, namelsad, countyfp::int, awater, classfp, lsad::int, "name", funcstat, metdivfp, cbsafp, intptlon, statefp::int, mtfcc, geo_point_2d, wkb_geometry, st_transform(clr.wkb_geometry, 3857) as area3857 from public.county_lines_raw clr"
psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "create index area3857_index on public.county_lines using gist(area3857)"

sql_folder=/init/sql
for script in "$sql_folder"/*.sql
do
  psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f "$script"
done

psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "CREATE USER ${POSTGRES_USER_READ_ONLY} WITH PASSWORD '${POSTGRES_PASSWORD_READ_ONLY}'"
psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "CREATE USER ${POSTGRES_BUILDER_USER} WITH PASSWORD '${POSTGRES_BUILDER_PASSWORD}'"
psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "GRANT pg_read_server_files TO ${POSTGRES_BUILDER_USER}"
psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "GRANT USAGE ON SCHEMA public TO ${POSTGRES_BUILDER_USER}"
psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "GRANT USAGE ON SCHEMA mire TO ${POSTGRES_BUILDER_USER}"
psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "GRANT SELECT, REFERENCES ON ALL TABLES IN SCHEMA mire TO ${POSTGRES_BUILDER_USER}"
psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "GRANT SELECT, UPDATE, INSERT, DELETE ON table public.region_status TO ${POSTGRES_BUILDER_USER}"
psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "GRANT SELECT ON table public.county_lines TO ${POSTGRES_BUILDER_USER}"
psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "GRANT SELECT ON table public.county_lines_raw TO ${POSTGRES_BUILDER_USER}"
psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "GRANT CREATE ON database rws TO ${POSTGRES_BUILDER_USER}"


psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "GRANT USAGE ON SCHEMA mire TO ${POSTGRES_USER_READ_ONLY}"
psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "GRANT SELECT ON ALL TABLES IN SCHEMA mire TO ${POSTGRES_USER_READ_ONLY}"
psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA mire TO ${POSTGRES_USER_READ_ONLY}"
psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA mire GRANT SELECT ON TABLES TO ${POSTGRES_USER_READ_ONLY}"
psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA mire GRANT EXECUTE ON FUNCTIONS TO ${POSTGRES_USER_READ_ONLY}"
