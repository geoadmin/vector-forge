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

#### Personal notes:

18, 13, 13
ch.swisstopo.swissboundaries3d-gemeinde-flaeche.fill
[586400.0, 170800.0, 599200.0, 183600.0]

"""
SELECT ST_GeometryType(ST_Intersection((ST_Dump(the_geom)).geom
       ST_SetSrid(ST_GeomFromText('POLYGON ((600200 179800, 600200 184600, 585400 184600, 585400 169800, 600200 179800))'), 21781)))
       FROM tlm.swissboundaries_gemeinden
       WHERE ST_Intersects(the_geom, ST_SetSrid(ST_GeomFromText('POLYGON ((600200 179800, 600200 184600, 585400 184600, 585400 169800, 600200 179800))'), 21781))
       LIMIT 2
"""

http://postgis.net/docs/manual-2.2/ST_Dump.html
