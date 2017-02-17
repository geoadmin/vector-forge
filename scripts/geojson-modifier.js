// Command-line tool to modify features in a GeoJSON file.
// Output is written to stdout.
//
// How to run: 
//   node geojson_modifier.js \
//     --infile /data/inputfile.geojson \
//     --patterns '["key:value"]' \
//     --tippecanoe_extensions '[{ "maxzoom": 14, "minzoom": 12 }]' \
//     --outfile /data/outfile.geojson
// 

var commandLineArgs = require('command-line-args'),
    commandLineUsage = require('command-line-usage'),
    es = require('event-stream'),
    JSONStream = require('JSONStream'),
    fs = require('fs');


const optionDefinitions = [
  { name: 'patterns', alias: 'p', type: String },
  { name: 'tippecanoe_extensions', alias: 't', type: String },
  { name: 'help', alias: 'h', type: Boolean },
  { name: 'infile', type: String },
  { name: 'outfile', type: String, defaultValue: 'modified.geojson' },
]
const options = commandLineArgs(optionDefinitions);

const sections = [
  {
    header: 'Modifies GeoJSON features.',
    content: 'Modifies selected [italic]{GeoJSON} features ' +
             'and writes them to a new file.'
  },
  {
    header: 'Options',
    optionList: [
      {
        name: 'help',
        description: 'Print this usage guide.'
      },
      {
        name: 'patterns',
        description: 'Array with \'Key:value\' pairs to select features ' +
                     'to modify. Key must match a feature\'s property. The ' +
                     'number of pairs have to match the size of the ' +
                     'tippecanoe_extensions array.' +
                     '\nExample: \'["KATEGORIE:20"]\''
      },
      {
        name: 'tippecanoe_extensions',
        description: 'Array with tippecanoe extensions to add to features. ' +
                     '\nExample 1: \'[{ "maxzoom": 9, "minzoom": 4 }]\'' +
                     '\nExample 2: \'[{ "maxzoom": "MaxZoom", "minzoom": ' +
                     '"MinZoom" }]\'. The actual value is taken from an ' +
                     'attribute of the feature, e.g. MaxZoom and MinZoom.'
      },
      {
        name: 'infile',
        typeLabel: '[underline]{file}',
        description: 'The input file with GeoJSON features.'
      },
      {
        name: 'outfile',
        typeLabel: '[underline]{file}',
        description: 'The output file with modified GeoJSON features.'
      }
    ]
  }
]
const usage = commandLineUsage(sections);

if (options.help == true || options.infile == undefined ||
    options.tippecanoe_extensions == undefined) {
  console.log(usage);
  return;
} 
console.log('\nInput:  \t' + options.infile);

// For now we take only the first pattern and extension.
// TODO: Add logic to handle multiple patterns.
if (options.patterns) {
  var patternKey = options.patterns === '' ? '' :
      JSON.parse(options.patterns)[0].split(':')[0];
  var patternValue = options.patterns === '' ? '' :
      JSON.parse(options.patterns)[0].split(':')[1];
  console.log('Pattern:\t"' + patternKey + ':' + patternValue + '"');
}
var extension = JSON.parse(options.tippecanoe_extensions)[0];
console.log('Extension:\t' + JSON.stringify(extension));

// Parse GeoJSON with JSONPath features.*.geometry
var numFeatures = 0, numModifiedFeatures = 0;
var readStream = fs.createReadStream(options.infile, {enicoding: 'utf8'});
var readJSONStream = JSONStream.parse('features.*');


// Modifies the GeoJSON feature.
var modifyGeoJSON = function(data) {
  if (!extension) {
    // Nothing to change.
    return data;
  }
  if (patternKey && patternValue) {
    // Does the feature match the pattern?
    if (data.properties === undefined ||
        data.properties[patternKey] != patternValue) {
      return data;
    }
  }
  ++numModifiedFeatures;
  // Adds a tippecanoe extension.
  var featureExtension = {};
  for (key in extension) {
    switch(key) {
      case 'minzoom':
      case 'maxzoom':
        if (parseInt(data.properties[extension[key]]) > 0) {
          featureExtension[key] = parseInt(data.properties[extension[key]]);
        } else if (parseInt(extension[key]) > 0) {
          featureExtension[key] = parseInt(extension[key]);
        }
        break;
      case 'layer':
        if (data.properties.hasOwnProperty(extension[key])) {
          featureExtension[key] = data.properties[extension[key]];
        } else {
          featureExtension[key] = extension[key];
        }
        break;
      default:
    }
  }
  data.tippecanoe = featureExtension;
  
  return data;
}

// Emits anything from _before_ the first match
readJSONStream.on('header', function (data) {
  if (data != undefined) {
    data.features = [];
    console.log('\nHeader:\n' + JSON.stringify(data));
    this.write(data);
  }
})

// Emits the (potentially modified) feature.
readJSONStream.on('data', function(data) {
  if (++numFeatures % 1000 == 0) {
      process.stdout.write('Modified ' + numModifiedFeatures / 1000 + 'k of '
          + numFeatures / 1000 + 'k features\r');
  }
  this.write(modifyGeoJSON(data));
});

// Emits anything from _after_ the last match
readJSONStream.on('end', function(data) {
  if (data != undefined) {
    this.write(data);
    console.log('Footer:\n' + JSON.stringify(data));
  }

  console.log('\nResults written to \'' + options.outfile + '\'.');
});

var writeStream = fs.createWriteStream(options.outfile);
// The writeStream expects strings and not JSON objects.
var jsonToStrings = JSONStream.stringify(
    open='[\n', sep=',\n', close='\n]\n');

readStream
  .pipe(readJSONStream)
  .pipe(jsonToStrings)
  .pipe(writeStream);
