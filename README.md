vector-forge
============

## Description

This repo is a sandbox where tests are performed.


## Getting started

Add your AWS access key in `.boto`.

Add your Database username and password in `.pgpass`

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


## Create a new Mapbox vector tiled layer

First start by defining your model in `vectorforge/models/${dbname}.py`.

Check your styling code using:

```
make lint
```

Create a json config file `config/${layerBodId}.json`.

Launch a new tile generation using:

```
${PYTHON_VENV} scripts/mvt_tiler.py ${path_to_config} ${debug}
```

If debug parameter is provided, then multiprocessing is disabled.


## Configuration of a new layer

Create a json config file `config/${layerBodId}.json`.


| Attribute                   | Description                                                  | Default                                    | Possible values                                                        |
|-----------------------------|--------------------------------------------------------------|--------------------------------------------|------------------------------------------------------------------------|
| layerBodId                  | The layer id as defined on the model                         | Not applicable (Required)                  |                                                                        |
| tileSizePx                  | The size of the tile in pixels                               | 256                                        | A multiple of 128                                                      |
| minZoom                     | The minimal zoom where to start the tileing from             | 0                                          | An integer >= 0                                                        |
| maxZoom                     | The maximal zoom where to stop the tileing at                | 26                                         | An integer >= 0                                                        |
| gutter                      | The buffer in pixels around the tile                         | 100                                        | An integer in pixel values                                             |
| isAnnotationLayer           | True if this is an annotation layer                          | false                                      | true|false                                                             |
| maxFontSize                 | The maximum font size in pixels                              | 20                                         | An integer                                                             |
| extent                      | The intersection extent selecting the tiles                  | [420000.0, 30000.0, 900000.0, 350000.0]    | [minx, miny, maxx, maxy]                                               |
| filters                     | A List of filters                                            | []                                         | A sql filter in plain text                                             |
| srid                        | A srid to determine the tiling scheme and output coordinates | 21781                                      | 21781 (CH1903/LV03), 4326 (Global Geodetic) and 3857 (Global Mercator) |
| lods                        | The levels of details on which to apply the filters on       | No filters applied                         | A dictionary {'lod': 'zoom': {'tabelname': 'name', ...}}               |
| lods -> z                   | A zoom level entry                                           | Not applicable (Required if lod is defined |                                                                        |
| lods -> z -> tablename      | The tablename to use at a given zoom level                   | Not applicable (Required)                  |                                                                        |
| lods -> z -> filterindices  | An list of indices referencing a filter in filters           | null                                       |                                                                        |
| lods -> z -> operatorfilter | An unique operator to combine the filters with               | null                                       |                                                                        |
| lods -> z -> simplify       | The simplification tolerance in map unit                     | null                                       |                                                                        |
| lods -> z -> geometrycolumn | The topogeometry to use in case simplification is used       | the_geom                                   |                                                                        |


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


## Simplification and generalization

Polygons with topology preserving simplification based on:

https://trac.osgeo.org/postgis/wiki/UsersWikiSimplifyPreserveTopology

Which in turn uses heavily:

http://postgis.net/docs/ST_SimplifyPreserveTopology.html

