#!/bin/bash

set -e

INFILE=
MIN_ZOOM=0
MAX_ZOOM=22
CONFIG=

function usage {
  echo "Usage:"
  echo ""
  echo "\t-h --help"
  echo "\t--source=$INFILE"
  echo "\t--minzoom=$MIN_ZOOM"
  echo "\t--maxzoom=$MAX_ZOOM"
  echo "\t--config=$CONFIG"
  echo "\tUsage examples:"
  echo "\t./scripts/mbtile_tippecanoe.sh --source=~/data/swissnames/Labels.json --minzoom=7 --maxzoom=22"
  echo "\t./scripts/mbtile_tippecanoe.sh --source=~/data/swissnames/Labels.json --config=configs/ch.swisstopo.swissnames3d_point.json --minzoom=7 --maxzoom=22"
}

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
    if [ -z "$CONFIG" ]; then
      echo "node --harmony scripts/geojson-modifier.js --infile $INFILE --outfile "${INFILE_NAME}_modified.json" --tippecanoe_extensions '[{ "maxzoom": "\'${MAX_ZOOM}\'", "minzoom": "\'${MIN_ZOOM}\'"}]'"
      node --harmony scripts/geojson-modifier.js --infile $INFILE --outfile "${INFILE_NAME}_modified.json" --tippecanoe_extensions '[{ "maxzoom": "'${MAX_ZOOM}'", "minzoom": "'${MIN_ZOOM}'"}]'
    else
      echo "node --harmony scripts/geojson-modifier.js --infile $INFILE --outfile "${INFILE_NAME}_modified.json" --config $CONFIG"
      node --harmony scripts/geojson-modifier.js --infile $INFILE --outfile "${INFILE_NAME}_modified.json" --config $CONFIG
    fi
  else
    echo "Skipping geosjon preparation, ${INFILE_NAME}_modified.json already exists"
  fi
}

function process_tippecanoe {
  if [ ! -f "${INFILE_NAME}.mbtiles" ]; then
    cd "${HOME}/tippecanoe"
    echo "Preparing mbtiles..."
    echo "./tippecanoe -o "${INFILE_NAME}.mbtiles" --force -rg --projection 'EPSG:3857' "${INFILE_NAME}_modified.json""
    ./tippecanoe -o "${INFILE_NAME}.mbtiles" --force -rg --projection 'EPSG:3857' "${INFILE_NAME}_modified.json" --minimum-zoom $MIN_ZOOM --maximum-zoom $MAX_ZOOM
  else
    echo "Skipping tile creations file ${INFILE_NAME}.mbtiles already exists"
  fi
}

while [ "$1" != "" ]; do
  PARAM=`echo $1 | awk -F= '{print $1}'`
  VALUE=`echo $1 | awk -F= '{print $2}'`
    case $PARAM in
        -h | --help)
            usage
            exit
            ;;
        --source)
            INFILE=$VALUE
            eval INFILE=$INFILE
            ;;
        --minzoom)
            MIN_ZOOM=$VALUE
            ;;
        --maxzoom)
            MAX_ZOOM=$VALUE
            ;;
        --config)
            CONFIG=$VALUE
            eval CONFIG=$CONFIG
            ;;
        *)
            echo "ERROR: unknown parameter \"$PARAM\""
            usage
            exit 1
            ;;
    esac
    shift
done

INFILE_NAME=${INFILE::(-5)}

echo $INFILE
echo $CONFIG
setup_tippecanoe
prepare_tippecanoe
process_tippecanoe
