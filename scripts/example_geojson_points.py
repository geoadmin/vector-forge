# -*- coding: utf-8 -*-

import time
import datetime
import geojson
import sys
import traceback
from gatilegrid import GeoadminTileGrid
from sqlalchemy.orm import scoped_session, sessionmaker
from geoalchemy2.shape import to_shape
from vectorforge.lib.helpers import printProgress
from vectorforge.lib.boto_s3 import s3Connect, getBucket, setFileContent, preparePath
from vectorforge.models.stopo import Vec200Namedlocation


t0 = time.time()

conn = s3Connect('ltgal_aws_admin')
b = getBucket(conn)
model = Vec200Namedlocation
layerId = model.__bodId__
DBSession = scoped_session(sessionmaker())


try:
    minZoom = 0
    maxZoom = 24
    gagrid = GeoadminTileGrid()
    tileGrid = gagrid.iterGrid(minZoom, maxZoom)

    currentZ = minZoom
    t1 = time.time()
    for tileBounds, zoom, col, row in tileGrid:
        if currentZ != zoom:
            printProgress(t1, currentZ)
            currentZ = zoom
            t1 = time.time()
        features = []
        bbox = gagrid.tileBounds(zoom, col, row)
        clippedGeometry = model.bboxClippedGeom(bbox)
        query = DBSession.query(model, clippedGeometry)
        query = query.filter(model.bboxIntersects(bbox))
        for res in query:
            features.append(
                geojson.Feature(
                    res[0].id,
                    geometry=to_shape(
                        res[1]),
                    properties=res[0].getProperties()))
        featureCollection = geojson.FeatureCollection(
            features, crs={'type': 'EPSG', 'properties': {'code': '21781'}}
        )
        path = preparePath(layerId, zoom, col, row)
        setFileContent(b, path, featureCollection)
    # Print progress for the last zoom level
    printProgress(t1, zoom)
except Exception:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    print "*** Traceback:"
    traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
    print "*** Exception:"
    traceback.print_exception(exc_type, exc_value, exc_traceback,
                              limit=2, file=sys.stdout)
finally:
    DBSession.close()
    t3 = time.time()
    tf = t3 - t0
    print 'Tile generation process ended/stopped.'
    print 'It took %s' % str(datetime.timedelta(seconds=tf))
