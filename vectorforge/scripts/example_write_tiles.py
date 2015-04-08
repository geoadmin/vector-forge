# -*- coding: utf-8 -*-

import time
import geojson
from sqlalchemy.orm import scoped_session, sessionmaker
from geoalchemy2.shape import to_shape
from boto.s3.key import Key
from vectorforge.lib.boto_s3 import s3Connect, getBucket
from vectorforge.lib.grid import Grid
from vectorforge.models.stopo import Vec200Namedlocation


zoomLevel = 17
tileCol = 0
tileRow = 0

grid = Grid(zoomLevel)

maxX = grid.maxX
minY = grid.minY

def preparePath(zoomLevel, tileCol, tileRow):
    return '%s/%s/%s.json' %(zoomLevel, tileCol, tileRow)


def setFileContent(b, path, featureCollection, contentType='application/json'):
    k = Key(b)
    k.key = path
    return k.set_contents_from_string(geojson.dumps(featureCollection), headers={'Content-Type': contentType})

def toGeoJSONFeature(ID, shapelyGeom):
    return geojson.Feature(ID, geometry=shapelyGeom, properties={})
    

conn = s3Connect()
b = getBucket(conn)
model = Vec200Namedlocation
DBSession = scoped_session(sessionmaker())

try:
    while grid.maxX >= maxX:
        while grid.minY <= minY:
            bbox = [minX, minY, maxX, maxY] = grid.tileBounds(tileCol, tileRow)
            clippedGeometry = model.bboxClippedGeom(bbox).label('clippedGeom')
            query = DBSession.query(model.id, clippedGeometry)
            query = query.filter(model.bboxIntersects(bbox))

            features = [toGeoJSONFeature(res.id, to_shape(res.clippedGeom)) for res in query]
            featureCollection = geojson.FeatureCollection(features, crs='EPSG:21781')
            path = preparePath(zoomLevel, tileCol, tileRow)
            setFileContent(b, path, featureCollection)
            tileRow += 1
        minY = grid.minY
        tileCol += 1
        tileRow = 0
except Exception as e:
    print e
finally:
    DBSession.close()
