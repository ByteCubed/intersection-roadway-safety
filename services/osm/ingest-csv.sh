#!/usr/bin/env bash

INGEST_FILENAME=${1:-Crashes_in_DC.csv}

echo "Ingesting file: ${INGEST_FILENAME}"

curl --silent --output /dev/null "http://localhost:8080/dot-road-safety/ingest/crashes?filename=/app/data/crashes/${INGEST_FILENAME}"
