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

folderblacklist=(`cat /data/ignore.txt`)
previous_process_complete_state=5
osm_start_work_state=6
osm_postprocess_started_state=7
osm_end_work_state=8
while true ; do
  workable_items_count $previous_process_complete_state $osm_postprocess_started_state
  workable_items=$?
  echo "Workable Items: $workable_items"
  if ((workable_items > 0)) ; then
    for region in `ls -d /data/*/`
    do
      size=${#folderblacklist[*]}
      counter=0
      while [ $counter -lt $size ]
      do
        if [ "${folderblacklist[$counter]}" = "$region" ] ; then
          #echo ""$region" matches"
          continue 2
        fi
        counter=$(( $counter + 1 ))
      done
      #echo ""$region" does not match"

      region_name=`echo $region | awk -F / '{ print $(NF-1) }'`
      initial_state=`psql -h "$HOSTNAME" -p "$PORT" -U "$POSTGRES_BUILDER_USER" -d "$POSTGRES_DB" -AXqtc "SELECT region_state_id FROM region_status WHERE region_name='$region_name'"`
      #psql -h $HOSTNAME -p "$PORT" -U $POSTGRES_BUILDER_USER -d $POSTGRES_DB -c "SET search_path=$region_name;"

      # if it's not at the start of our queue, forget about it
      if (( initial_state < previous_process_complete_state )) ; then
        continue 1
      fi
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
            update_region_status "$region_name" "$osm_postprocess_started_state"
          fi

          if (( initial_state <= osm_postprocess_started_state )) ; then
            psql -h $HOSTNAME -p "$PORT" -U $POSTGRES_BUILDER_USER -d $POSTGRES_DB -c "ALTER ROLE $POSTGRES_BUILDER_USER SET search_path = $region_name,public;"
            echo "Creating node table for $region_name"
            psql -h $HOSTNAME -p "$PORT" -U $POSTGRES_BUILDER_USER -d $POSTGRES_DB -f /postprocess/node_creation_query.sql
            echo "Creating way_node table for $region_name"
            psql -h $HOSTNAME -p "$PORT" -U $POSTGRES_BUILDER_USER -d $POSTGRES_DB -f /postprocess/way_node_creation_query.sql
            echo "Creating way_feature table for $region_name"
            psql -h $HOSTNAME -p "$PORT" -U $POSTGRES_BUILDER_USER -d $POSTGRES_DB -f /postprocess/way_feature_creation_query.sql
            echo "Creating way_feature view for $region_name"
            psql -h $HOSTNAME -p "$PORT" -U $POSTGRES_BUILDER_USER -d $POSTGRES_DB -f /postprocess/create_way_feature_view.sql
            echo "Creating way table for $region_name"
            psql -h $HOSTNAME -p "$PORT" -U $POSTGRES_BUILDER_USER -d $POSTGRES_DB -f /postprocess/way_creation_query.sql
            echo "Populating nodes' road status for $region_name"
            psql -h $HOSTNAME -p "$PORT" -U $POSTGRES_BUILDER_USER -d $POSTGRES_DB -f /postprocess/populate_node_road_status.sql
            echo "Creating waylet table for $region_name"
            psql -h $HOSTNAME -p "$PORT" -U $POSTGRES_BUILDER_USER -d $POSTGRES_DB -f /postprocess/waylet_creation_query.sql
            echo "Creating node_intersection table for $region_name"
            psql -h $HOSTNAME -p "$PORT" -U $POSTGRES_BUILDER_USER -d $POSTGRES_DB -f /postprocess/node_intersection_creation_query.sql
            echo "Creating curated way feature view for $region_name"
            psql -h $HOSTNAME -p "$PORT" -U $POSTGRES_BUILDER_USER -d $POSTGRES_DB -f /postprocess/create_curated_way_feature_view.sql
            echo "Creating angle table for $region_name"
            psql -h $HOSTNAME -p "$PORT" -U $POSTGRES_BUILDER_USER -d $POSTGRES_DB -f /postprocess/intersection_angle_creation_query.sql
            echo "Populating intersection features for $region_name"
            psql -h $HOSTNAME -p "$PORT" -U $POSTGRES_BUILDER_USER -d $POSTGRES_DB -f /postprocess/intersection_feature_creation_query.sql
            echo "Creating traffic_volume table for $region_name"
            psql -h $HOSTNAME -p "$PORT" -U $POSTGRES_BUILDER_USER -d $POSTGRES_DB -f /postprocess/traffic_volume_creation_query.sql
            echo "Linking crashes to intersections for $region_name"
            psql -h $HOSTNAME -p "$PORT" -U $POSTGRES_BUILDER_USER -d $POSTGRES_DB -f /postprocess/link_crashes_to_intersections.sql
            echo "Populating aadt intersection feature for $region_name"
            psql -h $HOSTNAME -p "$PORT" -U $POSTGRES_BUILDER_USER -d $POSTGRES_DB -f /postprocess/add_aadt_to_intersection_features.sql
            echo "Populating crash count intersection feature for $region_name"
            psql -h $HOSTNAME -p "$PORT" -U $POSTGRES_BUILDER_USER -d $POSTGRES_DB -f /postprocess/add_crash_data_to_intersection_features.sql

            update_region_status "$region_name" "$osm_end_work_state"
          fi
        fi
      fi
    done
  else
    echo "No work - sleeping $sleep_dur seconds."
    sleep "$sleep_dur"
  fi
done
