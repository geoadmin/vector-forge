# -*- coding: utf-8 -*-

import time
import datetime
import geojson
import sys
import traceback
from sqlalchemy.orm import scoped_session, sessionmaker
from geoalchemy2.shape import to_shape
from vectorforge.lib.boto_s3 import s3Connect, getBucket, setFileContent, preparePath
from vectorforge.lib.grid import Grid, RESOLUTIONS
from vectorforge.models.stopo import Vec200Namedlocation


t0 = time.time()

conn = s3Connect()
b = getBucket(conn)
model = Vec200Namedlocation
layerId = model.__bodId__
DBSession = scoped_session(sessionmaker())


try:
    for zoomLevel in range(0, len(RESOLUTIONS[0:24])):
        t1 = time.time()

        grid = Grid(zoomLevel)
        maxX = grid.maxX
        minY = grid.minY
        tileCol = 0
        tileRow = 0

        while grid.maxX >= maxX:
            while grid.minY <= minY:
                bbox = [minX, minY, maxX, maxY] = grid.tileBounds(tileCol, tileRow)
                clippedGeometry = model.bboxClippedGeom(bbox)
                query = DBSession.query(model, clippedGeometry)
                query = query.filter(model.bboxIntersects(bbox))

                features = [
                    geojson.Feature(res[0].id, geometry=to_shape(res[1]), properties=res[0].getProperties()) for res in query
                ]
                featureCollection = geojson.FeatureCollection(features, crs={'type': 'EPSG', 'properties': {'code': '21781'}})
                path = preparePath(layerId, zoomLevel, tileCol, tileRow)
                setFileContent(b, path, featureCollection)
                tileRow += 1
            minY = grid.minY
            tileCol += 1
            tileRow = 0
        t2 = time.time()
        ti = t2 - t1
        print 'All tiles have been generated for zoom level: %s' %zoomLevel
        print 'It took %s' %str(datetime.timedelta(seconds=ti))
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
    print 'It took %s' %str(datetime.timedelta(seconds=tf))
