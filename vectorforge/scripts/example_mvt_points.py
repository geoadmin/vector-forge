# -*- coding: utf-8 -*-

import cStringIO
import time
import datetime
import sys
import traceback
import mapbox_vector_tile

from poolmanager import PoolManager
from multiprocessing import Value
from shapely.geometry.point import Point
from shapely.geometry.linestring import LineString
from shapely.geometry.polygon import Polygon

from sqlalchemy.orm import scoped_session, sessionmaker
from geoalchemy2.shape import to_shape
from vectorforge.lib.helpers import gzipFileObject
from vectorforge.lib.boto_s3 import s3Connect, getBucket, writeToS3
from vectorforge.lib.grid import Grid, RESOLUTIONS
from vectorforge.models.stopo import Vec200Namedlocation


def geoadminTileGrid(zoomlevels):
    for zoomLevel in zoomlevels:
        grid = Grid(zoomLevel)
        maxX = grid.maxX
        minY = grid.minY
        tileCol = 0
        tileRow = 0
        while grid.maxX >= maxX:
            while grid.minY <= minY:
                tileBounds = [minX, minY, maxX, maxY] = grid.tileBounds(tileCol, tileRow)
                yield (zoomLevel, tileBounds, tileCol, tileRow)
                tileRow += 1
            minY = grid.minY
            tileCol += 1
            tileRow = 0


def featureMVT(geometry, properties):
    return {
        'geometry': geometry,
        'properties': properties
    }


def layerMVT(layerName, features):
    return mapbox_vector_tile.encode({
        'name': layerName,
        'features': features
    })


def quantizeGeomToMVT(geometry, tileExtent):
    # geometry -> a shapely geometry
    # MVT tiles have a hardcoded tile extent of 4096 units
    MVT_EXTENT = 4096
    [minX, minY, maxX, maxY] = tileExtent
    xSpan = maxX - minX
    ySpan = maxY - minY

    def quantizeCoordToMVT(x, y):
        xq = int(round((x - minX) * MVT_EXTENT / xSpan))
        # Downward inversion is performed in encoder
        yq = int((round(y - minY) * MVT_EXTENT / ySpan))
        return (xq, yq)

    # Only simple types for now
    if isinstance(geometry, Point):
        coords = list(geometry.coords)
        qcoords = quantizeCoordToMVT(coords[0][0], coords[0][1])
        return Point(qcoords)
    elif isinstance(geometry, LineString):
        coords = list(geometry.coords) 
        qcoords = []
        for coord in coords[0]:
            qcoords.append(quantizeCoordToMVT(coord[0], coord[1]))
        return LineString(qcoords)
    elif isinstance(geometry, Polygon):
        coords = list(geometry.exterior.coords)
        qcoords = []
        for coord in coords[0]:
            qcoords.append(quantizeCoordToMVT(coord[0], coord[1]))
        return Polygon(qcoords)


skippedTilesCounter = 0
def createTile(tileSpec):
    fullPath = None
    try:
        (zoomLevel, tileBounds, tileCol, tileRow) = tileSpec
        model = Vec200Namedlocation
        layerBodId = model.__bodId__
        DBSession = scoped_session(sessionmaker())
        basePath = '1.0.0/%s/21781/default/' % layerBodId
        clippedGeometry = model.bboxClippedGeom(tileBounds)
        query = DBSession.query(model, clippedGeometry)
        query = query.filter(model.bboxIntersects(tileBounds))
        features = []
        for feature in query:
            properties = feature[0].getProperties()
            properties['id'] = feature[1].id
            qgeometry = quantizeGeomToMVT(to_shape(feature[1]), tileBounds)
            features.append(featureMVT(qgeometry, properties))
        if len(features) > 0:
            path = '%s/%s/%s.pbf' %(zoomLevel, tileCol, tileRow)
            mvt = layerMVT(model.__bodId__, features)
            f = cStringIO.StringIO()
            f.write(mvt)
            writeToS3(
                bucket, path, gzipFileObject(f), 'vector-forge',
                basePath, contentType='application/x-protobuf', contentEnc='gzip')
            fullPath = basePath + path
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print "*** Traceback:"
        traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
        print "*** Exception:"
        traceback.print_exception(exc_type, exc_value, exc_traceback,
                                  limit=2, file=sys.stdout)
    finally:
        DBSession.close()
    return fullPath


def callback(counter, fullPath):
    if fullPath is None:
        with skippedTiles.get_lock():
            skippedTiles.value += 1

    if counter % 1000 == 0:
        t1 = time.time()
        ti = t1 - t0
        if fullPath:
            print 'Last tile address was %s' % fullPath
        else:
            print 'Last tile address was skipped'
        print '%s tiles have been generated' % (counter - skippedTiles.value)
        print '%s tiles have been skipped' % skippedTiles.value
        print 'It took %s' % str(datetime.timedelta(seconds=ti))


def main():
    tileGrid = geoadminTileGrid(range(0, len(RESOLUTIONS[0:24])))
    pm = PoolManager(numProcs=2)
    pm.imap_unordered(tileGrid, createTile, 50, callback=callback)

    # End of process
    t3 = time.time()
    tf = t3 - t0
    print 'Tile generation process ended/stopped.'
    print 'It took %s' % str(datetime.timedelta(seconds=tf))


if __name__ == '__main__':
    t0 = time.time()
    skippedTiles = Value('i', 0)
    # Boto is thread safe
    conn = s3Connect('ltgal_aws_admin')
    bucket = getBucket(conn)
    main()
