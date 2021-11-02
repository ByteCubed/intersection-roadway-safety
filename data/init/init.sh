psql -U $POSTGRES_USER -d $POSTGRES_DB -f /docker-entrypoint-initdb.d/sql/dc.sql
psql -U $POSTGRES_USER -d $POSTGRES_DB -f /docker-entrypoint-initdb.d/sql/mire.sql

mkfifo /tmp/omyfifo
zcat /tmp/dc/Crashes_in_DC.csv.zip > /tmp/omyfifo &
psql -U $POSTGRES_USER -d $POSTGRES_DB -c "COPY crashes.dc(x,y,objectid,crimeid,ccn,reportdate,routeid,measure,\"offset\",streetsegid,roadwaysegid,fromdate,todate,marid,address,latitude,longitude,xcoord,ycoord,ward,eventid,mar_address,mar_score,majorinjuries_bicyclist,minorinjuries_bicyclist,unknowninjuries_bicyclist,fatal_bicyclist,majorinjuries_driver,minorinjuries_driver,unknowninjuries_driver,fatal_driver,majorinjuries_pedestrian,minorinjuries_pedestrian,unknowninjuries_pedestrian,fatal_pedestrian,total_vehicles,total_bicycles,total_pedestrians,pedestriansimpaired,bicyclistsimpaired,driversimpaired,total_taxis,total_government,speeding_involved,nearestintrouteid,nearestintstreetname,offintersection,intapproachdirection,locationerror,lastupdatedate,mpdlatitude,mpdlongitude,mpdgeox,mpdgeoy,blockkey,subblockkey,fatalpassenger,majorinjuriespassenger,minorinjuriespassenger,unknowninjuriespassenger) from '/tmp/omyfifo' with csv header"
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
