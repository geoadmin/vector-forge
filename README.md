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
| filters                     | A List of defined filters                              | []                                      |
| lods                        | The levels of details on which to apply the filters on | No filters applied                      |
| lods -> z                   | A zoom level entry                                     | Not applicable                          |
| lods -> z -> tablename      | The tablename to use at a given zoom level             | Not applicable                          |
| lods -> z -> filterindices  | An list of indices referencing a filter in filters     | Not applicable                          |
| lods -> z -> operatorfilter | An unique operator to combine the filters with         | Not applicable                          |
