// Command-line tool to read Mapbox vector tiles (PBFs) using vector-tile-js.
// Output is written to stdout.
//
// How to run: 
//   node decode-vector-tile.js \
//     --input /data/tiles/14/8666/5765.pbf
// 

var commandLineArgs = require('command-line-args'),
    commandLineUsage = require('command-line-usage'),
    fs = require('fs'),
    Protobuf = require('pbf'),
    VectorTile = require('vector-tile').VectorTile,
    VectorTileLayer = require('vector-tile').VectorTileLayer,
    VectorTileFeature = require('vector-tile').VectorTileFeature,
    zlib = require('zlib');


const optionDefinitions = [
  { name: 'featureinfo', alias: 'f', type: Boolean },
  { name: 'geojson', alias: 'g', type: Boolean },
  { name: 'help', alias: 'h', type: Boolean },
  { name: 'input', type: String },
]
const options = commandLineArgs(optionDefinitions)

const sections = [
  {
    header: 'Vector Tile Printer',
    content: 'Prints [italic]{Mapbox Vector Tiles} encoded as (gzipped) ' +
             'Protocol buffers to stdout.'
  },
  {
    header: 'Options',
    optionList: [
      {
        name: 'featureinfo',
        description: 'Print information down to feature level.'
      },
      {
        name: 'geojson',
        description: 'Print feature as geojson.'
      },
      {
        name: 'help',
        description: 'Print this usage guide.'
      },
      {
        name: 'input',
        typeLabel: '[underline]{file}',
        description: 'The input to process (PBF).'
      }
    ]
  }
]
const usage = commandLineUsage(sections)

if (options.help == true || options.input == undefined) {
  console.log(usage);
  return;
} 

var printInfo = function(tile, compressed) {
  console.log('GZIP compressed: ' + compressed);
  console.log('Layer count: ' + Object.keys(tile.layers).length);
  console.log('Layer names: ' + Object.keys(tile.layers));
  for (var key in tile.layers) {
    if (tile.layers.hasOwnProperty(key)) {
      var layer = tile.layers[key];
      console.log('Layer ' + layer.name + ':');
      console.log('  Version: ' + layer.version);
      console.log('  Extent: ' + layer.extent);
      console.log('  Feature count: ' + layer.length);
      if (options.featureinfo || options.geojson) {
        console.log('  Features: ');
        for (i = 0; i < layer.length; i++) {
          var feature = layer.feature(i);
          if (options.geojson) {
            console.log(JSON.stringify(feature.toGeoJSON(), null, 2));
            continue;
          }
          console.log('  Feature ' + i + ':');
          console.log('    Type: ' + feature.type);
          console.log('    Keys: ' + Object.keys(feature.properties));
          var values = '';
          for (var key in feature.properties) {
            values = values + feature.properties[key] + ',';
          }
          console.log('    Values: ' + values);
          if (feature.id != undefined) {
            console.log('    Id: ' + feature.id);
          }
          console.log('    Extent: ' + feature.extent);
          console.log('    Bbox: ' + feature.bbox());
          console.log('    Geometry: ' +
              JSON.stringify(feature.loadGeometry()));
        }
      }
    }
  }
}

var data = fs.readFileSync(options.input);

zlib.gunzip(data, function(err, buffer) {
  var tile = new VectorTile(new Protobuf(buffer));
  if (!err) {
    printInfo(tile, true);
  } else {
    // Decompression failed. Maybe the file is not gzipped.
    console.log('Failed to gunzip ' + options.input);
    console.log('Try to decode raw PBF...');
    tile = new VectorTile(new Protobuf(data));
    printInfo(tile, false);
  }
});
