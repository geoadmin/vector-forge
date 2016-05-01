vector-forge
============

## Description

This repo is a sandbox where tests are performed.


## Getting started

Create your own `rc` file:

    $ cp rc_ltgal rc_{username}

Edit this file with your own variables.

Build:

    $ source rc_{username}
    $ make all

Serve your web app:

    $ make dev

Activate virtualenv:

    $ source venv/bin/activate


## Configuration of a new layer

First start by defining your model in `vectorforge/models/{dbname}.py`.

Create a json config file `config/{layerBodId}.json`.


| Attribute                   | Description                                            | Default                                 |
|-----------------------------|--------------------------------------------------------|-----------------------------------------|
| layerBodId                  | The layer id as defined on the model                   | Not applicable (Required)               |
| tileSizePx                  | The size of the tile in pixels                         | 256                                     |
| minZoom                     | The minimal zoom where to start the tileing from       | 0                                       |
| maxZoom                     | The maximal zoom where to stop the tileing at          | 26                                      |
| gutter                      | The buffer in pixels around the tile                   | 20                                      |
| extent                      | The intersection extent selecting the tiles            | [420000.0, 30000.0, 900000.0, 350000.0] |
| filters                     | A List of filters                                      | []                                      |
| lods                        | The levels of details on which to apply the filters on | No filters applied                      |
| lods -> z                   | A zoom level entry                                     | Not applicable                          |
| lods -> z -> tablename      | The tablename to use at a given zoom level             | Not applicable                          |
| lods -> z -> filterindices  | An list of indices referencing a filter in filters     | Not applicable                          |
| lods -> z -> operatorfilter | An unique operator to combine the filters with         | Not applicable                          |


## Configuration example

```json
{
  "layerBodId": "ch.swisstopo.swissnames3d",
  "tileSizePx": 256,
  "minZoom": 10,
  "maxZoom": 26,
  "gutter": 20,
  "extent": null,
  "filters": ["bgdi_type = 'point'"],
  "lods": {
    "10": {
      "tablename": "swissnames3d_raster_00",
      "filterindices": [0],
      "operatorfilter": null
    },
    "11": {
      "tablename": "swissnames3d_raster_00",
      "filterindices": [0],
      "operatorfilter": null
    },
    "12": {
      "tablename": "swissnames3d_raster_00",
      "filterindices": [0],
      "operatorfilter": null
    },
    "13": {
      "tablename": "swissnames3d_raster_00",
      "filterindices": [0],
      "operatorfilter": null
    },
    "14": {
      "tablename": "swissnames3d_raster_01",
      "filterindices": [0],
      "operatorfilter": null
    },
    "15": {
      "tablename": "swissnames3d_raster_02",
      "filterindices": [0],
      "operatorfilter": null
    },
    "16": {
      "tablename": "swissnames3d_raster_03",
      "filterindices": [0],
      "operatorfilter": null
    },
    "17": {
      "tablename": "swissnames3d_raster_04",
      "filterindices": [0],
      "operatorfilter": null
    },
    "18": {
      "tablename": "swissnames3d_raster_05",
      "filterindices": [0],
      "operatorfilter": null
    },
    "19": {
      "tablename": "swissnames3d_raster_06",
      "filterindices": [0],
      "operatorfilter": null
    },
    "20": {
      "tablename": "swissnames3d_raster_07",
      "filterindices": [0],
      "operatorfilter": null
    },
    "21": {
      "tablename": "swissnames3d_raster_08",
      "filterindices": [0],
      "operatorfilter": null
    },
    "22": {
      "tablename": "swissnames3d_raster_09",
      "filterindices": [0],
      "operatorfilter": null
    },
    "23": {
      "tablename": "swissnames3d_raster_10",
      "filterindices": [0],
      "operatorfilter": null
    },
    "24": {
      "tablename": "swissnames3d_raster_11",
      "filterindices": [0],
      "operatorfilter": null
    },
    "25": {
      "tablename": "swissnames3d_raster_12",
      "filterindices": [0],
      "operatorfilter": null
    },
    "26": {
      "tablename": "swissnames3d_raster_13",
      "filterindices": [0],
      "operatorfilter": null
    }
  }
}
```
