#!/bin/bash

#accepts a region name and a status code, upserts the region_status table
function update_region_status() {
  psql -h "$HOSTNAME" -p "$PORT" -U "$POSTGRES_BUILDER_USER" -d "$POSTGRES_DB" -c "insert into public.region_status values ('$1', $2) on conflict (region_name) do update set region_state_id = $2;"
  echo "Updated $1's state to $2"
}

function ingest_file() {
  files=(${1}/*.geojson)
  if [ -f "${files[0]}" ] ; then
    ogr2ogr -f "PostgreSQL" PG:"host=$HOSTNAME port="$PORT" dbname=$POSTGRES_DB user=$POSTGRES_BUILDER_USER" "${files[0]}" -nln "${2}".${3}_raw -append
  else
    files=(${1}/*.csv)
    if [ -f "${files[0]}" ] ; then
      psql -h "$HOSTNAME" -p "$PORT" -U "$POSTGRES_BUILDER_USER" -d "$POSTGRES_DB" -c "\copy ${2}.${3}_raw from '${files[0]}' csv delimiter ',' quote '\"' header;"
    fi
  fi
}

# Dynamic Content Below
folderblacklist=(`cat /data/ignore.txt`)
for region in `ls -d /data/*/`
do
  size=${#folderblacklist[*]}
  counter=0
  state=1
  while [ $counter -lt $size ]
  do
    if [ "${folderblacklist[$counter]}" = "$region" ] ; then
      #echo ""$region" matches"
      continue 2
    fi
    counter=$(( counter + 1 ))
  done
  #echo ""$region" does not match"

  #create schema and set default
  region_name=`echo $region | awk -F / '{ print $(NF-1) }'`
  initial_state=`psql -h "$HOSTNAME" -p "$PORT" -U "$POSTGRES_BUILDER_USER" -d "$POSTGRES_DB" -AXqtc "SELECT region_state_id FROM region_status WHERE region_name='$region_name'"`

  if (( initial_state <= state )) ; then
    psql -h "$HOSTNAME" -p "$PORT" -U "$POSTGRES_BUILDER_USER" -d "$POSTGRES_DB" -c "CREATE SCHEMA if not exists $region_name";

    psql -h "$HOSTNAME" -p "$PORT" -U "$POSTGRES_BUILDER_USER" -d "$POSTGRES_DB" -c "GRANT USAGE ON SCHEMA ${region_name} TO ${POSTGRES_USER_READ_ONLY}"
    psql -h "$HOSTNAME" -p "$PORT" -U "$POSTGRES_BUILDER_USER" -d "$POSTGRES_DB" -c "GRANT SELECT ON ALL TABLES IN SCHEMA ${region_name} TO ${POSTGRES_USER_READ_ONLY}"
    psql -h "$HOSTNAME" -p "$PORT" -U "$POSTGRES_BUILDER_USER" -d "$POSTGRES_DB" -c "GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA ${region_name} TO ${POSTGRES_USER_READ_ONLY}"
    psql -h "$HOSTNAME" -p "$PORT" -U "$POSTGRES_BUILDER_USER" -d "$POSTGRES_DB" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA ${region_name} GRANT SELECT ON TABLES TO ${POSTGRES_USER_READ_ONLY}"
    psql -h "$HOSTNAME" -p "$PORT" -U "$POSTGRES_BUILDER_USER" -d "$POSTGRES_DB" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA ${region_name} GRANT EXECUTE ON FUNCTIONS TO ${POSTGRES_USER_READ_ONLY}"

    psql -h "$HOSTNAME" -p "$PORT" -U "$POSTGRES_BUILDER_USER" -d "$POSTGRES_DB" -c "GRANT ALL PRIVILEGES ON SCHEMA ${region_name} TO ${POSTGRES_BUILDER_USER}"
    psql -h "$HOSTNAME" -p "$PORT" -U "$POSTGRES_BUILDER_USER" -d "$POSTGRES_DB" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA ${region_name} GRANT ALL ON TABLES TO ${POSTGRES_BUILDER_USER}"
    psql -h "$HOSTNAME" -p "$PORT" -U "$POSTGRES_BUILDER_USER" -d "$POSTGRES_DB" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA ${region_name} GRANT ALL ON FUNCTIONS TO ${POSTGRES_BUILDER_USER}"
    update_region_status "$region_name" "$state"
  fi
  state=$((state+1))

  psql -h "$HOSTNAME" -p "$PORT" -U "$POSTGRES_BUILDER_USER" -d "$POSTGRES_DB" -c "SET search_path TO $region_name,public";

  # preingest
  if (( initial_state <= state )) ; then
    for script in `ls -d ${region}preingest/*.sql`
    do
      echo "Running $script"
      psql -h "$HOSTNAME" -p "$PORT" -U "$POSTGRES_BUILDER_USER" -d "$POSTGRES_DB" -f "$script"
    done
    update_region_status "$region_name" "$state"
  fi
  state=$((state+1))

  # ingest crash data
  if (( initial_state <= state )) ; then
    if [ -f "${region}crashes/override.sh" ] ; then
      echo "Overriding Normal Crash Ingestion Behavior for $region_name"
      bash "${region}crashes/override.sh"
    else
      ingest_file "${region}crashes" "$region_name" "crashes"
    fi
    update_region_status "$region_name" "$state"
  fi
  state=$((state+1))

  # ingest aadt
  if (( initial_state <= state )) ; then
    if [ -f "${region}aadt/override.sh" ] ; then
      echo "Overriding Normal Traffic Volume Ingestion Behavior for $region_name"
      bash "${region}aadt/override.sh"
    else
      ingest_file "${region}aadt" "$region_name" "traffic_volume"
    fi
    update_region_status "$region_name" "$state"
  fi
  state=$((state+1))

  # postprocess
  if (( initial_state <= state )) ; then
    for script in `ls -d ${region}postprocess/*.sql`
    do
      echo "Running $script"
      psql -h "$HOSTNAME" -p "$PORT" -U "$POSTGRES_BUILDER_USER" -d "$POSTGRES_DB" -f "$script"
    done
    update_region_status "$region_name" "$state"
  fi
  state=$((state+1))
done

