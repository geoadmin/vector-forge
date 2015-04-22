# -*- coding: utf-8 -*-

import sys
import time
import datetime
import geojson
import subprocess
import traceback
from sqlalchemy import or_
from sqlalchemy.orm import scoped_session, sessionmaker
from geoalchemy2.shape import to_shape
from geoalchemy2.elements import WKBElement
from vectorforge.lib.boto_s3 import s3Connect, getBucket, setFileContent, preparePath
from vectorforge.lib.grid import Grid, RESOLUTIONS
from vectorforge.lib.encoders import gzippedFileContent
from vectorforge.models.stopo import Vec25Strassennetz


"""
This script is simplifying lines on the fly using the Visvalingam’s algorithm
which is not currently available in postgis.
Explanations can be found at http://bost.ocks.org/mike/simplify/
We also use quantization which is more or less like rasterinzing the input
and thematic filtering to only keep the main road segments at low resolutions.
"""

def writeGeojsonFile(data, fileName):
    with open(fileName, 'w') as outfile:
        outfile.write(geojson.dumps(data))

def toTopojson(threshold, quantization, prop, inputFileName, outputFileName):
    """ Try quantization """
    subprocess.call([
        'node_modules/.bin/topojson', '-o', outputFileName,
        '--cartesian', '-s', str(threshold), '-q', str(quantization), '-p', prop, inputFileName
    ])
    return outputFileName

def clean(inputFileName, outputFileName):
    subprocess.call(['rm', '-f', inputFileName])
    subprocess.call(['rm', '-f', outputFileName])

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
        inputFileName = u'temp.json'
        outputFileName = u'output.json'

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
                writeGeojsonFile(featureCollection, inputFileName)
                fileName = toTopojson(resolution*2, grid.tileSizeInPixel, 'objectval', inputFileName, outputFileName)

                path = preparePath(layerId, zoomLevel, tileCol, tileRow, 'json')
                print path
                compressedContent = gzippedFileContent(fileName)
                setFileContent(b, path, compressedContent)
                clean(inputFileName, outputFileName)
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
    try:
        clean(inputFileName, outputFileName)
    except:
        pass
    DBSession.close()
    t3 = time.time()
    tf = t3 - t0
    print 'Tile generation process ended/stopped.'
    print 'It took %s' %str(datetime.timedelta(seconds=tf))
