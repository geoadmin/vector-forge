# -*- coding: utf-8 -*-

import time
import datetime
import geojson
import subprocess
from sqlalchemy import or_
from sqlalchemy.orm import scoped_session, sessionmaker
from geoalchemy2.shape import to_shape
from geoalchemy2.elements import WKBElement
from vectorforge.lib.boto_s3 import s3Connect, getBucket, setFileContent, preparePath
from vectorforge.lib.grid import Grid, RESOLUTIONS
from vectorforge.models.stopo import Vec25Strassennetz


"""
This script is simplifying lines on the fly using the Visvalingam’s algorithm
which is not currently available in postgis.
Explanations can be found at http://bost.ocks.org/mike/simplify/
We also use quantization and thematic filtering according to the zoom level.
"""

def writeGeojsonFile(data):
    with open('temp.json', 'w') as outfile:
        outfile.write(geojson.dumps(data))

def toTopojson(threshold, quantization, prop):
    """ Try quantization """
    fileName = 'output.json'
    subprocess.call([
        'node_modules/.bin/topojson', '-o', fileName,
        '--cartesian', '-s', str(threshold), '-q', str(quantization), '-p', prop, 'temp.json'
    ])
    return fileName

def clean():
    subprocess.call(['rm', '-f', 'temp.json'])
    subprocess.call(['rm', '-f', 'output.json'])

def applyFilters(query, propertyColumn, propertyValues):
    clauses = []
    if len(propertyValues) == 1 and propertyValues[0] == '*':
        return query
    for prop in propertyValues:
        clauses.append(propertyColumn == prop)
    return query.filter(or_(*clauses))


zoomFilters = {
  '0': ['Autobahn'],
  '1': ['Autobahn'],
  '2': ['Autobahn'],
  '3': ['Autobahn'],
  '4': ['Autobahn'],
  '5': ['Autobahn'],
  '6': ['Autobahn'],
  '7': ['Autobahn'],
  '8': ['Autobahn'],
  '9': ['Autobahn'],
  '10': ['Autobahn', 'Ein_Ausf'],
  '11': ['Autobahn', 'Ein_Ausf'],
  '12': ['Autobahn', 'Ein_Ausf'],
  '13': ['Autobahn', 'Ein_Ausf'],
  '14': ['Autobahn', 'Ein_Ausf'],
  '15': ['Autobahn', 'Ein_Ausf'],
  '16': ['Autobahn', 'Ein_Ausf', '1_Klass'],
  '17': ['Autobahn', 'Ein_Ausf', '1_Klass', '2_Klass'],
  '18': ['Autobahn', 'Ein_Ausf', '1_Klass', '2_Klass', '3_Klass'],
  '19': ['Autobahn', 'Ein_Ausf', '1_Klass', '2_Klass', '3_Klass', '4_Klass'],
  '20': ['Autobahn', 'Ein_Ausf', '1_Klass', '2_Klass', '3_Klass', '4_Klass', '5_Klass'],
  '21': ['Autobahn', 'Ein_Ausf', '1_Klass', '2_Klass', '3_Klass', '4_Klass', '5_Klass', '6_Klass'],
  '22': ['Autobahn', 'Ein_Ausf', '1_Klass', '2_Klass', '3_Klass', '4_Klass', '5_Klass', '6_Klass', 'Q_Klass'],
  '23': ['*']
}

t0 = time.time()

conn = s3Connect()
b = getBucket(conn)
model = Vec25Strassennetz
layerId = model.__bodId__
propertyColumn = model.objectval
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
        propertyValues = zoomFilters[str(zoomLevel)]

        while grid.maxX >= maxX:
            while grid.minY <= minY:
                bbox = [minX, minY, maxX, maxY] = grid.tileBounds(tileCol, tileRow)
                clippedGeometry = model.bboxClippedGeom(bbox).label('clippedGeom')
                # Convert multilinestrings to linestrings
                lineMerged = model.lineMerge()
                query = DBSession.query(model, lineMerged)
                query = query.filter(model.bboxIntersects(bbox))
                query = applyFilters(query, propertyColumn, propertyValues)

                features = []
                for res in query:
                    ID = res[0].id
                    properties = res[0].getProperties()
                    shapelyGeometry = to_shape(WKBElement(buffer(res[1]), 21781))
                    geoJSONFeature = geojson.Feature(ID, geometry=shapelyGeometry, properties=properties)
                    features.append(geoJSONFeature) 
                featureCollection = geojson.FeatureCollection(features, crs={'type': 'EPSG', 'properties': {'code': '21781'}})
                writeGeojsonFile(featureCollection)
                fileName = toTopojson(resolution*2, grid.tileSizeInPixel*grid.tileSizeInPixel, 'objectval')

                path = preparePath(layerId, zoomLevel, tileCol, tileRow, 'topojson')
                with open(fileName) as topjsonArcs:
                    setFileContent(b, path, topjsonArcs)
                clean()
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
    try:
        clean()
    except:
        pass
    DBSession.close()
    t3 = time.time()
    tf = t3 - t0
    print 'Tile generation process ended/stopped.'
    print 'It took %s' %str(datetime.timedelta(seconds=tf))
