psql -U $POSTGRES_USER -d $POSTGRES_DB -c "CREATE EXTENSION hstore"

psql -U $POSTGRES_USER -d $POSTGRES_DB -f /docker-entrypoint-initdb.d/sql/dc.sql
psql -U $POSTGRES_USER -d $POSTGRES_DB -f /docker-entrypoint-initdb.d/sql/mire.sql
psql -U $POSTGRES_USER -d $POSTGRES_DB -f /docker-entrypoint-initdb.d/sql/intersect_angle.sql
ogr2ogr -f "PostgreSQL" PG:"dbname=$POSTGRES_DB user=$POSTGRES_USER" "/tmp/trafficvolume/2018_Traffic_Volume.geojson" -nln traffic_volume_raw -append

mkfifo /tmp/omyfifo
zcat /tmp/dc/Crashes_in_DC.csv.zip > /tmp/omyfifo &
psql -U $POSTGRES_USER -d $POSTGRES_DB -c "COPY crashes.dc(x,y,objectid,crimeid,ccn,reportdate,routeid,measure,\"offset\",streetsegid,roadwaysegid,fromdate,todate,marid,address,latitude,longitude,xcoord,ycoord,ward,eventid,mar_address,mar_score,majorinjuries_bicyclist,minorinjuries_bicyclist,unknowninjuries_bicyclist,fatal_bicyclist,majorinjuries_driver,minorinjuries_driver,unknowninjuries_driver,fatal_driver,majorinjuries_pedestrian,minorinjuries_pedestrian,unknowninjuries_pedestrian,fatal_pedestrian,total_vehicles,total_bicycles,total_pedestrians,pedestriansimpaired,bicyclistsimpaired,driversimpaired,total_taxis,total_government,speeding_involved,nearestintrouteid,nearestintstreetname,offintersection,intapproachdirection,locationerror,lastupdatedate,mpdlatitude,mpdlongitude,mpdgeox,mpdgeoy,blockkey,subblockkey,fatalpassenger,majorinjuriespassenger,minorinjuriespassenger,unknowninjuriespassenger) from '/tmp/omyfifo' WITH CSV HEADER"
rm /tmp/omyfifo

psql -U $POSTGRES_USER -d $POSTGRES_DB -c "CREATE USER ${POSTGRES_USER_READ_ONLY} WITH PASSWORD '${POSTGRES_PASSWORD_READ_ONLY}'"

psql -U $POSTGRES_USER -d $POSTGRES_DB -c "GRANT USAGE ON SCHEMA crashes TO ${POSTGRES_USER_READ_ONLY}"
psql -U $POSTGRES_USER -d $POSTGRES_DB -c "GRANT SELECT ON ALL TABLES IN SCHEMA crashes TO ${POSTGRES_USER_READ_ONLY}"
psql -U $POSTGRES_USER -d $POSTGRES_DB -c "GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA crashes TO ${POSTGRES_USER_READ_ONLY}"
psql -U $POSTGRES_USER -d $POSTGRES_DB -c "ALTER DEFAULT PRIVILEGES IN SCHEMA crashes GRANT SELECT ON TABLES TO ${POSTGRES_USER_READ_ONLY}"
psql -U $POSTGRES_USER -d $POSTGRES_DB -c "ALTER DEFAULT PRIVILEGES IN SCHEMA crashes GRANT EXECUTE ON FUNCTIONS TO ${POSTGRES_USER_READ_ONLY}"

psql -U $POSTGRES_USER -d $POSTGRES_DB -c "GRANT USAGE ON SCHEMA mire TO ${POSTGRES_USER_READ_ONLY}"
psql -U $POSTGRES_USER -d $POSTGRES_DB -c "GRANT SELECT ON ALL TABLES IN SCHEMA mire TO ${POSTGRES_USER_READ_ONLY}"
psql -U $POSTGRES_USER -d $POSTGRES_DB -c "GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA mire TO ${POSTGRES_USER_READ_ONLY}"
psql -U $POSTGRES_USER -d $POSTGRES_DB -c "ALTER DEFAULT PRIVILEGES IN SCHEMA mire GRANT SELECT ON TABLES TO ${POSTGRES_USER_READ_ONLY}"
psql -U $POSTGRES_USER -d $POSTGRES_DB -c "ALTER DEFAULT PRIVILEGES IN SCHEMA mire GRANT EXECUTE ON FUNCTIONS TO ${POSTGRES_USER_READ_ONLY}"

psql -U $POSTGRES_USER -d $POSTGRES_DB -c "select *,  ST_Transform(ST_SetSRID(ST_MakePoint(cast(longitude as float),cast(latitude as float)), 4326),3857) as point into crashes.dc_indexed from rws.crashes.dc"
psql -U $POSTGRES_USER -d $POSTGRES_DB -c "CREATE INDEX IF NOT EXISTS dc_indexed ON rws.crashes.dc_indexed USING gist(point)"
