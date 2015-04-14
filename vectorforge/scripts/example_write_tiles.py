# -*- coding: utf-8 -*-

import time
import datetime
import geojson
from sqlalchemy.orm import scoped_session, sessionmaker
from geoalchemy2.shape import to_shape
from boto.s3.key import Key
from vectorforge.lib.boto_s3 import s3Connect, getBucket
from vectorforge.lib.grid import Grid, RESOLUTIONS
from vectorforge.models.stopo import Vec200Namedlocation


def preparePath(zoomLevel, tileCol, tileRow):
    return '%s/%s/%s.geojson' %(zoomLevel, tileCol, tileRow)


def setFileContent(b, path, featureCollection, contentType='application/json'):
    k = Key(b)
    k.key = path
    return k.set_contents_from_string(geojson.dumps(featureCollection), headers={'Content-Type': contentType})


def toGeoJSONFeature(ID, shapelyGeom):
    return geojson.Feature(ID, geometry=shapelyGeom, properties={})

    
t0 = time.time()

conn = s3Connect()
b = getBucket(conn)
model = Vec200Namedlocation
DBSession = scoped_session(sessionmaker())


try:
    for zoomLevel in range(0, len(RESOLUTIONS)):
        t1 = time.time()

        grid = Grid(zoomLevel)
        maxX = grid.maxX
        minY = grid.minY
        tileCol = 0
        tileRow = 0

        while grid.maxX >= maxX:
            while grid.minY <= minY:
                bbox = [minX, minY, maxX, maxY] = grid.tileBounds(tileCol, tileRow)
                clippedGeometry = model.bboxClippedGeom(bbox).label('clippedGeom')
                query = DBSession.query(model.id, clippedGeometry)
                query = query.filter(model.bboxIntersects(bbox))

                features = [toGeoJSONFeature(res.id, to_shape(res.clippedGeom)) for res in query]
                featureCollection = geojson.FeatureCollection(features, crs={'type': 'EPSG', 'properties': {'code': '21781'}})
                path = preparePath(zoomLevel, tileCol, tileRow)
                setFileContent(b, path, featureCollection)
                tileRow += 1
            minY = grid.minY
            tileCol += 1
            tileRow = 0
        t2 = time.time()
        ti = t2 - t1
        print 'All tiles have been generated for zoom level: %s' %zoomLevel
        print 'It took %s' %str(datetime.timedelta(seconds=ti))
except Exception as e:
    print e
finally:
    DBSession.close()
    t3 = time.time()
    tf = t3 - t0
    print 'Tile generation process ended/stopped.'
    print 'It took %s' %str(datetime.timedelta(seconds=tf))


