#!/usr/bin/env bash

set -e

SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

DEMO_DATA_FILENAME="district-of-columbia-latest.osm.pbf"
DEMO_DATA_PATH="${SCRIPT_DIR}/data/osm/${DEMO_DATA_FILENAME}"

mkdir -p "${SCRIPT_DIR}/data/osm"

if [[ ! -f "${DEMO_DATA_PATH}" ]]; then
  echo "Downloading ${DEMO_DATA_FILENAME}"
  curl -s "https://download.geofabrik.de/north-america/us/${DEMO_DATA_FILENAME}" --output "${DEMO_DATA_PATH}"
fi

echo "Bringing up environment..."
docker-compose up -d db elasticsearch kibana

until docker run --rm -e "PGPASSWORD=changeme" --network=osm2es postgres psql -h "db" -U "dot" -c '\q' > /dev/null 2>&1; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

echo "Running osm2pgsql..."
"${SCRIPT_DIR}"/ingest-osm.sh "${DEMO_DATA_FILENAME}"

docker-compose up -d app

until curl --output /dev/null --silent --head --fail "http://localhost:8080"; do
  >&2 echo "App is unavailable - sleeping"
  sleep 1
done

echo "Indexing OSM data to elasticsearch"
"${SCRIPT_DIR}"/index-osm.sh
