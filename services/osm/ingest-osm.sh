#!/usr/bin/env bash

SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

INGEST_FILENAME=${1:-data.pbf}
STYLE_FILENAME=${2}

if [[ -z "${STYLE_FILENAME}" ]]; then
  echo "style is empty"
  curl -s https://raw.githubusercontent.com/openstreetmap/osm2pgsql/master/default.style --output "${SCRIPT_DIR}/data/osm/default.style"
  STYLE_FILENAME="default.style"
else
  echo "style is not empty"
fi

echo "Ingesting file: ${INGEST_FILENAME}"

mkdir "${SCRIPT_DIR}"/data/osm || true
docker run \
  -v "${SCRIPT_DIR}/data/osm:/data-osm" \
  -e PGPASSWORD=changeme \
  --network=osm2es \
  osm2pgsql \
  "/data-osm/${INGEST_FILENAME}" -r pbf -S "/data-osm/${STYLE_FILENAME}" --host db -U dot --database=dot
