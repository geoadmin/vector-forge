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
    exec = require('child_process').exec,
    JSONStream = require('JSONStream'),
    userHome = require('user-home'),
    fs = require('fs');


const optionDefinitions = [
  { name: 'patterns', alias: 'p', type: String },
  { name: 'tippecanoe_extensions', alias: 't', type: String },
  { name: 'config', alias: 'c', type: String },
  { name: 'maxzoom_limit', type: Number, defaultValue: 6 },
  { name: 'minzoom_limit', type: Number, defaultValue: 16 },
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
        name: 'config',
        description: 'A json configuration file describing how ' +
                     'and which features to modify'
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
        name: 'maxzoom_limit',
        description: 'Force maxzoom values to be bigger or equal this limit.'
      },
      {
        name: 'minzoom_limit',
        description: 'Force minzoom values to be smaller or equal this limit.'
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

var tildePath = function(path) {
  return path.replace(/^~($|\/)/, userHome + '/');
};

if (options.help == true || options.infile == undefined ||
    (options.tippecanoe_extensions == undefined && options.config === undefined)) {
  console.log(usage);
  return;
}
console.log('\nInput:  \t' + options.infile);
// For now we take only the first pattern and extension.
if (options.patterns) {
  var patternKey = options.patterns === '' ? '' :
      JSON.parse(options.patterns)[0].split(':')[0];
  var patternValue = options.patterns === '' ? '' :
      JSON.parse(options.patterns)[0].split(':')[1];
  console.log('Pattern:\t"' + patternKey + ':' + patternValue + '"');
} else if (options.config) {
  var readStreamConfig = fs.createReadStream(tildePath(options.config), {encoding: 'utf8'});
  var readJSONStreamConfig = JSONStream.parse();
  console.log('Config:\t' + options.config);
}
var extension;
if (options.tippecanoe_extensions) {
  extension = JSON.parse(options.tippecanoe_extensions)[0];
  console.log('Extension:\t' + JSON.stringify(extension));
}
if (options.minzoom_limit < options.maxzoom_limit) {
  console.log('Error: Value of --minzoom_limit smaller than --maxzoom_limit.');
  return;
}

// Parse GeoJSON with JSONPath features.*.geometry
var numTotalFeatures = 0, numProcessedFeatures = 0, numModifiedFeatures = 0;
var readStream = fs.createReadStream(tildePath(options.infile), {encoding: 'utf8'});
var readJSONStream = JSONStream.parse('features.*');

var createTippecanoeExtensionFromGlobals = function(data) {
  var featureExtension = {};
  var zoom = 0;
  for (key in extension) {
    switch(key) {
      case 'minzoom':
        if (parseInt(data.properties[extension[key]]) > 0) {
          zoom = parseInt(data.properties[extension[key]]);
        } else if (parseInt(extension[key]) > 0) {
          zoom = parseInt(extension[key]);
        }
        if (zoom > 0) {
          featureExtension[key] = zoom > options.minzoom_limit ? options.minzoom_limit : zoom;
        }
        break;
      case 'maxzoom':
        if (parseInt(data.properties[extension[key]]) > 0) {
          zoom = parseInt(data.properties[extension[key]]);
        } else if (parseInt(extension[key]) > 0) {
          zoom = parseInt(extension[key]);
        }
        if (zoom > 0) {
          featureExtension[key] = zoom < options.maxzoom_limit ? options.maxzoom_limit : zoom;
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
  return featureExtension;
};

var createTippecanoeExtensionFromConfig = function(data, config) {
  // Extension from vectorforge config
  var dataPropertyValue,
      featureExtension,
      confProperty = config.propertyName;
  // Property name should be case insensitive
  if (data.properties.hasOwnProperty(confProperty)) {
    dataPropertyValue = data.properties[confProperty];
  } else if (data.properties.hasOwnProperty(confProperty.toUpperCase())) {
    dataPropertyValue = data.properties[confProperty.toUpperCase()];
  }
  if (config.properties.hasOwnProperty(dataPropertyValue)) {
    featureExtension = config.properties[dataPropertyValue];
  } else {
    featureExtension = {
      minzoom: config.minzoomDefault,
      maxzoom: config.maxzoomDefault
    }
  }
  return featureExtension;
};

// Modifies the GeoJSON feature.
var modifyGeoJSON = function(data) {
  ++numProcessedFeatures;
  if (!extension && !config) {
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
  var ext;
  // Add global extension
  if (extension) {
    ext = createTippecanoeExtensionFromGlobals(data);
  } else if (config) {
    ext = createTippecanoeExtensionFromConfig(data, config);
  }
  // Make sure layerid is a string
  if (data.properties.layerid != undefined) {
    data.properties.layerid = data.properties.layerid.toString();
  }
  if (data.properties.de == '') {
    data.properties.de = data.properties.name;
  }
  if (data.properties.fr == '') {
    data.properties.fr = data.properties.name;
  }
  if (data.properties.it == '') {
    data.properties.it = data.properties.name;
  }
  if (data.properties.roh == '') {
    data.properties.roh = data.properties.name;
  }
  // Adds a tippecanoe extension.
  data.tippecanoe = ext;
  return data;
}

var readAndWriteGeoJSON = function() {
  // Total number of features.

  exec('grep \'"type":"Feature"\' ' + tildePath(options.infile) + '| wc -l',
       function (error, results) {
           console.log("Number of input features: " + results);
           numTotalFeatures = parseInt(results);
  });

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
    this.write(modifyGeoJSON(data));
    var ratioProcessed =
        Math.round(100.0 * numProcessedFeatures / numTotalFeatures);
    if (numProcessedFeatures == numTotalFeatures) {
      process.stdout.write('Processed ' + ratioProcessed + '%');
    } else if (ratioProcessed % 5 == 0) {
      process.stdout.write('Processed ' + ratioProcessed + '%\r');
    }
  });

  // Emits anything from _after_ the last match
  readJSONStream.on('end', function(data) {
    if (data != undefined) {
      this.write(data);
      console.log('Footer:\n' + JSON.stringify(data));
    }

    console.log(' and modified ' +
                Math.round(100.0 * numModifiedFeatures / numTotalFeatures) +
                '% of all input features');
    console.log('\nWrote ' + numProcessedFeatures + ' features to \'' +
                tildePath(options.outfile) + '\'.');
  });

  var writeStream = fs.createWriteStream(tildePath(options.outfile));
  // The writeStream expects strings and not JSON objects.
  var jsonToStrings = JSONStream.stringify(
      open='[\n', sep=',\n', close='\n]\n');

  readStream
    .pipe(readJSONStream)
    .pipe(jsonToStrings)
    .pipe(writeStream);
}

/*
  config object structure:

  {filters : [...],
  propertName: 'objektart',
  properties:
   { 'Alpiner Gipfel': { minzoom: 7, maxzoom: 23 },
     Pass: { minzoom: 9, maxzoom: 23 },
     Wasserfall: { minzoom: 9, maxzoom: 23 },
     Hauptgipfel: { minzoom: 10, maxzoom: 23 },
     Strassenpass: { minzoom: 10, maxzoom: 23 } },
  minzoom: 7,
  maxzoom: 23,
  minzoomDefault: 13,
  maxzoomDefault: 23 }
*/
if (readStreamConfig) {
  var config = {};
  readJSONStreamConfig.on('data', function(data) {
    // Always assume equality operator for now and use only one val to filter
    var regexp = new RegExp(
        "([A-Za-z]*)\\s(=|!=|<|<=|>|>=){1}\\s(.*(?=\\s(and|or))|.*)");
    for (var i=0; i < data.filters.length; i++) {
      var val = data.filters[i].replace('(', '').replace(')', '');
      var matches = regexp.exec(val);
      config.propertyName = matches[1].toLowerCase();
      if (!config.filters) {
        config.filters = [];
      }
      config.filters.push(matches[3].replace(/\'/g, ''));
    }
    // Create min/max zoom for each property
    var minZoom = Infinity;
    var maxZoom = -Infinity;
    var minZoomDefault = Infinity;
    var maxZoomDefault = -Infinity;
    config.properties = {};
    for (var k in data.lods) {
      minZoom = Math.min(minZoom, parseInt(k));
      maxZoom = Math.max(maxZoom, parseInt(k));
      var filterIndices = data.lods[k].filterindices;
      if (filterIndices) {
        for (var j=0; j < filterIndices.length; j++) {
          val = config.filters[filterIndices[j]];
          if (!config.properties.hasOwnProperty(val)) {
            config.properties[val] = {
              minzoom: Math.max(minZoom, parseInt(k)),
              maxzoom: Math.min(maxZoom, parseInt(k))
            };
          } else {
            config.properties[val].minzoom = Math.min(
                config.properties[val].minzoom, parseInt(k));
            config.properties[val].maxzoom = Math.max(
                config.properties[val].maxzoom, parseInt(k));
          }
        }
      } else {
        // If no filters are defined the entire dataset is available
        // at this zoom level
        for (var prop in config.properties) {
          config.properties[prop].minzoom = Math.min(
              config.properties[prop].minzoom, parseInt(k));
          config.properties[prop].maxzoom = Math.max(
              config.properties[prop].maxzoom, parseInt(k));
        }
        // If filters are not defined (e.g. tile the entire dataset)
        // We set the default min and max zooms
        minZoomDefault = Math.min(minZoomDefault, parseInt(k));
        maxZoomDefault = Math.max(maxZoomDefault, parseInt(k));
      }
    }
    config.minzoom = minZoom;
    config.maxzoom = maxZoom;
    config.minzoomDefault = minZoomDefault;
    config.maxzoomDefault = maxZoomDefault;
    console.log('Configuration:');
    console.log(config);
    readAndWriteGeoJSON();
  });
  readStreamConfig
    .pipe(readJSONStreamConfig);
} else {
  readAndWriteGeoJSON();
}
