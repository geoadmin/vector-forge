#!/bin/bash
# Usage example:
# ./scripts/mbtile_tippecanoe.sh ~/data/swissnames/Labels.json 7 22

INFILE=$1
MIN_ZOOM=$2
MAX_ZOOM=$3

INFILE_NAME=${INFILE::(-5)}

function setup_tippecanoe {
  if [ ! -d "${HOME}/tippecanoe" ]; then
    echo 'Setting up tippecanoe'
    cd ~
    git clone https://github.com/mapbox/tippecanoe
    cd ~/tippecanoe && make
  else
    echo 'Skipping tippecanoe installation'
  fi
}

function prepare_tippecanoe {
  if [ ! -f "${INFILE_NAME}_modified.json" ]; then
    cd "${HOME}/vector-forge"
    echo "Preparing geojson..."
    echo "node --harmony scripts/geojson-modifier.js --infile $INFILE --outfile "${INFILE_NAME}_modified.json" --tippecanoe_extensions '[{ "maxzoom": "'${MAX_ZOOM}'", "minzoom": "'${MIN_ZOOM}'"}]'"
    node --harmony scripts/geojson-modifier.js --infile $INFILE --outfile "${INFILE_NAME}_modified.json" --tippecanoe_extensions '[{ "maxzoom": "'${MAX_ZOOM}'", "minzoom": "'${MIN_ZOOM}'"}]'
    # node --harmony scripts/geojson-modifier.js --infile ~/data/swissnames/Labels.json --outfile ~/data/swissnames/test.json --config configs/ch.swisstopo.swissnames3d_point.json
  else
    echo "Skipping geosjon preparation, ${INFILE_NAME}_modified.json already exists"
  fi
}

function process_tippecanoe {
  if [ ! -f "${INFILE_NAME}.mbtiles" ]; then
    cd "${HOME}/tippecanoe"
    echo "Preparing mbtiles..."
    echo "./tippecanoe -o "${INFILE_NAME}.mbtiles" --force -rg --projection 'EPSG:3857' "${INFILE_NAME}_modified.json""
    ./tippecanoe -o "${INFILE_NAME}.mbtiles" --force -rg --projection 'EPSG:3857' "${INFILE_NAME}_modified.json"
  else
    echo "Skipping tile creations file ${INFILE_NAME}.mbtiles already exists"
  fi
}

setup_tippecanoe
prepare_tippecanoe
process_tippecanoe
