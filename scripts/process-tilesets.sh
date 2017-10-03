#!/bin/bash
#
# Merges GeoJSON files and produces a composite MBTile.


let MAXZOOM=15
let MINZOOM=6
INPUT_LIST=""
OUTPUT_PATH='.'
FILEPATTERN='composite'

function usage {
  echo "Usage:"
  echo
  echo "-h --help"
  echo -e "--maxzoom \t Maximum zoom level to generate tiles [default:15]"
  echo -e "--minzoom \t Minimum zoom level to generate tiles [default:6]"
  echo -e "--inputs \t List of input files [default:\"${INPUT_LIST}\"]"
  echo -e "--outputpath \t Directory for output files [default: ${OUTPUT_PATH}]"
  echo -e "--filepattern \t File pattern for output files [default: ${FILEPATTERN}]"
  echo
  echo "Usage example:"
  echo "./process-tilesets.sh \
--inputs=\"data/tiles/base.json data/tiles/adds.json\" \
--outputpath=data/tiles \
--filepattern=composite"
}


while [ "${1}" != "" ]; do
    PARAM=`echo ${1} | awk -F= '{print $1}'`
    VALUE=`echo ${1} | awk -F= '{print $2}'`
    case ${PARAM} in
        --help)
            usage
            exit
            ;;
        --maxzoom)
            let MAXZOOM=${VALUE}
            ;;
        --minzoom)
            let MINZOOM=${VALUE}
            ;;
        --inputs)
            INPUT_LIST="${VALUE}"
            ;;
        --outputpath)
            OUTPUT_PATH=${VALUE}
            ;;
        --filepattern)
            eval FILEPATTERN=${VALUE}
            ;;
        *)
            echo "ERROR: unknown parameter \"${PARAM}\""
            usage
            exit 1
            ;;
    esac
    shift
done

# Reset timer.
SECONDS=0

if [[ -z "${INPUT_LIST}" ]]
then
  usage
  exit
else
  echo
  echo Inputs: ${INPUT_LIST}
  for geojson in ${INPUT_LIST}
  do
    if [ ! -f ${geojson} ]; then
      echo "ERROR: File not found: ${geojson}"
      exit
    fi
  done
fi

OUTPUT=${OUTPUT_PATH}/${FILEPATTERN}
OUTPUT_JSON=${OUTPUT}.geojson
OUTPUT_MODIFIED=${OUTPUT}_modified.geojson
OUTPUT_MBTILE=${OUTPUT}.mbtiles

echo
echo Outputs:
echo Composite JSON: ${OUTPUT_JSON}
echo Modified JSON: ${OUTPUT_MODIFIED}
echo Composite MBTile: ${OUTPUT_MBTILE}

# Write header of GeoJSON
echo "{\"name\":\"${FILEPATTERN}\",\"type\":\"FeatureCollection\"" > ${OUTPUT_JSON}
echo ',"crs":{"type":"name","properties":{"name":"EPSG:3857"}}' >> ${OUTPUT_JSON}
echo ',"features":[' >> ${OUTPUT_JSON}

# Create composite of all input jsons
echo
echo Merge input files...
let i=0
for geojson in ${INPUT_LIST}
do
  if ((i > 0))
  then
    echo -n ',' >> ${OUTPUT_JSON}
  fi
  let n=$(< ${geojson} wc -l)-4
  echo Number of features in ${geojson}: ${n}
  grep coordinates ${geojson} >> ${OUTPUT_JSON}
  let i=${i}+1
done
echo "]}" >> ${OUTPUT_JSON}
let n=$(< ${OUTPUT_JSON} wc -l)-4
echo Number of features in composite: ${n}

echo Adding tippecanoe extension...
set -o xtrace
node ${HOME}/vector-forge/scripts/geojson-modifier.js \
    --infile ${OUTPUT_JSON} \
    --tippecanoe_extensions '[{ "maxzoom": "maxzoom", "minzoom": "minzoom"}]' \
    --maxzoom_limit ${MINZOOM} \
    --minzoom_limit ${MAXZOOM} \
    --outfile ${OUTPUT_MODIFIED}

${HOME}/tippecanoe/tippecanoe -f \
    --output ${OUTPUT_MBTILE} \
    --exclude=minzoom --exclude=maxzoom --exclude=labelgeometry \
    --attribute-type=stufe:int \
    --preserve-input-order \
    --maximum-zoom=${MAXZOOM} \
    --minimum-zoom=${MINZOOM} \
    --projection EPSG:3857 \
    -n ${FILEPATTERN} -l ${FILEPATTERN}-layer \
    --description='Composite Tileset' \
    ${OUTPUT_MODIFIED}
set +o xtrace

duration=$SECONDS
echo
echo "Elapsed time: $(($duration / 60)) minutes and $(($duration % 60)) seconds."
