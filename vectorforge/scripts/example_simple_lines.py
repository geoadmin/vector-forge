# -*- coding: utf-8 -*-

import time
import datetime
import geojson
import itertools
from sqlalchemy.orm import scoped_session, sessionmaker
from geoalchemy2.shape import to_shape
from geoalchemy2.elements import WKBElement
from vectorforge.lib.boto_s3 import s3Connect, getBucket, setFileContent, preparePath
from vectorforge.lib.grid import Grid, RESOLUTIONS
from vectorforge.models.stopo import Vec25Strassennetz
from vectorforge.lib.visvaligam import VisvalingamSimplificationFix


"""
This script is simplifying lines on the fly using the Visvalingam’s algorithm
which is not currently available in postgis. Additionnaly, segments smaller than
the resolution are dropped (brute force approach for testing sake).
Explanations can be found at http://bost.ocks.org/mike/simplify/
"""


t0 = time.time()

conn = s3Connect()
b = getBucket(conn)
model = Vec25Strassennetz
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
        resolution = RESOLUTIONS[zoomLevel]

        while grid.maxX >= maxX:
            while grid.minY <= minY:
                bbox = [minX, minY, maxX, maxY] = grid.tileBounds(tileCol, tileRow)
                clippedGeometry = model.bboxClippedGeom(bbox).label('clippedGeom')
                # Convert multilinestrings to linestrings
                lineMerged = model.lineMerge()
                query = DBSession.query(model, lineMerged)
                query = query.filter(model.bboxIntersects(bbox))
                # Brute force, drop all segments smaller than the resolution
                query = query.filter(model.length >= float(resolution))

                features = []
                for res in query:
                    ID = res[0].id
                    properties = res[0].getProperties()
                    shapelyGeometry = to_shape(WKBElement(buffer(res[1]), 21781))
                    geoJSONFeature = geojson.Feature(ID, geometry=shapelyGeometry, properties=properties)
                    # Convert tuples to list
                    coordinates = map(list, geoJSONFeature['geometry']['coordinates'])
                    simplify = VisvalingamSimplificationFix(coordinates)
                    coordinates = simplify.simplifyLineString(float(resolution))
                    # Convert back to tuples
                    geoJSONFeature['geometry']['coordinates'] = tuple(itertools.imap(tuple, coordinates))
                    time.sleep(1)
                    features.append(geoJSONFeature) 
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
except Exception as e:
    print e
finally:
    DBSession.close()
    t3 = time.time()
    tf = t3 - t0
    print 'Tile generation process ended/stopped.'
    print 'It took %s' %str(datetime.timedelta(seconds=tf))
