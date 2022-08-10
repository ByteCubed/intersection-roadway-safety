#!/bin/bash
# to run both Iowa and DC
#osmconvert ./data/osm/iowa-latest.osm.pbf --out-o5m | osmconvert - ./data/osm/district-of-columbia-latest.osm.pbf -o=./data/osm/dc_and_iowa.osm.pbf
#osm2pgsql -H $HOSTNAME -U $POSTGRES_BUILDER_USER -d $POSTGRES_DB -s -S ./data/osm/default.style ./data/osm/dc_and_iowa.osm.pbf

#accepts a region name and a status code, upserts the region_status table
function update_region_status() {
  psql -h "$HOSTNAME" -p "$PORT" -U "$POSTGRES_BUILDER_USER" -d "$POSTGRES_DB" -c "insert into public.region_status values ('$1', $2) on conflict (region_name) do update set region_state_id = $2;"
  echo "Updated $1's state to $2"
}
#accepts a region name and a status code, upserts the region_status table
function workable_items_count() {
  workable_items=`psql -h "$HOSTNAME" -p "$PORT" -U "$POSTGRES_BUILDER_USER" -d "$POSTGRES_DB" -AXqtc "select count(1) from public.region_status rs where region_state_id between $1 and $2"`
  return "$workable_items"
}

sleep_dur=60
sleep "$sleep_dur"

region=$1
previous_process_complete_state=5
osm_start_work_state=6
osm_end_work_state=7

region_name=`echo $region | awk -F / '{ print $(NF-1) }'`
initial_state=`psql -h "$HOSTNAME" -p "$PORT" -U "$POSTGRES_BUILDER_USER" -d "$POSTGRES_DB" -AXqtc "SELECT region_state_id FROM region_status WHERE region_name='$region_name'"`
psql -h "$HOSTNAME" -p "$PORT" -U "$POSTGRES_BUILDER_USER" -d "$POSTGRES_DB" -c "CREATE SCHEMA if not exists $region_name";

psql -h "$HOSTNAME" -p "$PORT" -U "$POSTGRES_BUILDER_USER" -d "$POSTGRES_DB" -c "GRANT USAGE ON SCHEMA ${region_name} TO ${POSTGRES_USER_READ_ONLY}"
psql -h "$HOSTNAME" -p "$PORT" -U "$POSTGRES_BUILDER_USER" -d "$POSTGRES_DB" -c "GRANT SELECT ON ALL TABLES IN SCHEMA ${region_name} TO ${POSTGRES_USER_READ_ONLY}"
psql -h "$HOSTNAME" -p "$PORT" -U "$POSTGRES_BUILDER_USER" -d "$POSTGRES_DB" -c "GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA ${region_name} TO ${POSTGRES_USER_READ_ONLY}"
psql -h "$HOSTNAME" -p "$PORT" -U "$POSTGRES_BUILDER_USER" -d "$POSTGRES_DB" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA ${region_name} GRANT SELECT ON TABLES TO ${POSTGRES_USER_READ_ONLY}"
psql -h "$HOSTNAME" -p "$PORT" -U "$POSTGRES_BUILDER_USER" -d "$POSTGRES_DB" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA ${region_name} GRANT EXECUTE ON FUNCTIONS TO ${POSTGRES_USER_READ_ONLY}"

psql -h "$HOSTNAME" -p "$PORT" -U "$POSTGRES_BUILDER_USER" -d "$POSTGRES_DB" -c "GRANT ALL PRIVILEGES ON SCHEMA ${region_name} TO ${POSTGRES_BUILDER_USER}"
psql -h "$HOSTNAME" -p "$PORT" -U "$POSTGRES_BUILDER_USER" -d "$POSTGRES_DB" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA ${region_name} GRANT ALL ON TABLES TO ${POSTGRES_BUILDER_USER}"
psql -h "$HOSTNAME" -p "$PORT" -U "$POSTGRES_BUILDER_USER" -d "$POSTGRES_DB" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA ${region_name} GRANT ALL ON FUNCTIONS TO ${POSTGRES_BUILDER_USER}"


# ingest osm data
if [ -f "${region}osm/override.sh" ] ; then
  if (( initial_state <= osm_end_work_state )) ; then
    echo "Overriding Normal Traffic Volume Ingestion Behavior for $region_name"
    bash "${region}osm/override.sh"
    update_region_status "$region_name" "$osm_end_work_state"
  fi
else
  files=(${region}osm/*.pbf)
  if [ -f "${files[0]}" ] ; then
    if (( initial_state <= osm_start_work_state )) ; then
      osm2pgsql -H $HOSTNAME -U $POSTGRES_BUILDER_USER -d $POSTGRES_DB -s -S ./data/default.style --middle-schema="$region_name" --output-pgsql-schema="$region_name" "${files[0]}"
      update_region_status "$region_name" "$osm_end_work_state"
    fi
  fi
fi