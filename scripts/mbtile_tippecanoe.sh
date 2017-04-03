#!/bin/bash

set -e

INFILE=
MIN_ZOOM=0
MAX_ZOOM=22
FORCE=false
SKIPMODIFY=false

function usage {
  echo "Usage:"
  echo ""
  echo "-h --help"
  echo "--source=$INFILE"
  echo "--minzoom=$MIN_ZOOM"
  echo "--maxzoom=$MAX_ZOOM"
  echo "--config=$CONFIG"
  echo "-f --force"
  echo "-s --skipmodify"
  echo "Usage examples:"
  echo "./scripts/mbtile_tippecanoe.sh --source=~/data/swissnames/Labels.json --minzoom=6 --maxzoom=18 -f"
  echo "./scripts/mbtile_tippecanoe.sh --source=~/data/swissnames/Labels.json --config=configs/ch.swisstopo.swissnames3d_point.json --minzoom=6 --maxzoom=18 -f"
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
  if [ ! -f "${INFILE_NAME_MODIFIED}.json" ] || [ "$FORCE" = true ] && [ $SKIPMODIFY = false ]; then
    cd "${HOME}/vector-forge"
    rm -f "${INFILE_NAME_MODIFIED}.json"
    echo "Preparing geojson..."
    if [ -z "$CONFIG" ]; then
      MODIFYGEOJSON_CMD="node --harmony scripts/geojson-modifier.js --infile $INFILE \
                        --outfile "${INFILE_NAME_MODIFIED}.json" --tippecanoe_extensions '[{\"maxzoom\": \"maxzoom\", \"minzoom\": \"minzoom\"}]'"
      echo $MODIFYGEOJSON_CMD
      eval $MODIFYGEOJSON_CMD
    else
      MODIFYGEOJSON_CMD="node --harmony scripts/geojson-modifier.js --infile $INFILE \
                        --outfile "${INFILE_NAME_MODIFIED}.json" --config $CONFIG"
      echo $MODIFYGEOJSON_CMD
      eval $MODIFYGEOJSON_CMD
    fi
  else
    echo "Skipping geosjon preparation"
  fi
}

function process_tippecanoe {
  TIPPECANOE_CMD="./tippecanoe -o "${INFILE_NAME}.mbtiles" \
                 -rg --projection='EPSG:3857' --preserve-input-order -l swissnames -n ${INFILE_NAME} -x minzoom -x maxzoom \
                 "${INFILE_NAME_TIPPECANOE}.json" --minimum-zoom=$MIN_ZOOM --maximum-zoom=$MAX_ZOOM"
  if [ ! -f "${INFILE_NAME_TIPPECANOE}.mbtiles" ] || [ $FORCE = true ]; then
    cd "${HOME}/tippecanoe"
    rm -f "${INFILE_NAME}.mbtiles"
    echo "Preparing mbtiles..."
    echo $TIPPECANOE_CMD
    eval $TIPPECANOE_CMD
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
        -f | --force)
            FORCE=true
            ;;
        -s | --skipmodify)
            SKIPMODIFY=true
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
INFILE_NAME_MODIFIED="${INFILE_NAME}_modified"
if [ $SKIPMODIFY = true ]; then
  INFILE_NAME_TIPPECANOE=$INFILE_NAME
else
  INFILE_NAME_TIPPECANOE=$INFILE_NAME_MODIFIED
fi

echo $INFILE
echo $CONFIG
setup_tippecanoe
prepare_tippecanoe
process_tippecanoe
