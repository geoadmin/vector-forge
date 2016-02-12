# -*- coding: utf-8 -*-

import cStringIO
import time
import datetime
import sys
import traceback
import mapbox_vector_tile

from shapely.geometry.point import Point
from shapely.geometry.linestring import LineString
from shapely.geometry.polygon import Polygon

from sqlalchemy.orm import scoped_session, sessionmaker
from geoalchemy2.shape import to_shape
from vectorforge.lib.helpers import gzipFileObject
from vectorforge.lib.boto_s3 import s3Connect, getBucket, writeToS3
from vectorforge.lib.grid import Grid, RESOLUTIONS
from vectorforge.models.stopo import Vec200Namedlocation


t0 = time.time()

model = Vec200Namedlocation
layerId = model.__bodId__
DBSession = scoped_session(sessionmaker())


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
                yield zoomLevel, tileBounds, tileCol, tileRow
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


def toFile(data):
    with open('test_tile.pbf', 'rw') as f:
        f.write(data)


def main():

    try:
        basePath = '1.0.0/ch.swisstopo.vec200-names-namedlocation/21781/default/'
        conn = s3Connect('ltgal_aws_admin')
        bucket = getBucket(conn)
        counter = 0
        for zoomLevel, tileExtent, tileCol, tileRow in geoadminTileGrid(range(0, len(RESOLUTIONS[0:24]))):
            clippedGeometry = model.bboxClippedGeom(tileExtent)
            query = DBSession.query(model, clippedGeometry)
            query = query.filter(model.bboxIntersects(tileExtent))
            features = []
            for feature in query:
                properties = feature[0].getProperties()
                # Add id as used in encoder
                # https://github.com/mapzen/mapbox-vector-tile/blob/master/mapbox_vector_tile/encoder.py#L110
                properties['id'] = feature[1].id
                qgeometry = quantizeGeomToMVT(to_shape(feature[1]), tileExtent)
                features.append(featureMVT(qgeometry, properties))

            if len(features) > 0:
                # Test only for now
                path = '%s/%s/%s.pbf' %(zoomLevel, tileCol, tileRow)
                mvt = layerMVT(model.__bodId__, features)
                f = cStringIO.StringIO()
                f.write(mvt)
                writeToS3(
                    bucket, path, gzipFileObject(f), 'vector-forge',
                    basePath, contentType='application/x-protobuf', contentEnc='gzip')
                counter += 1
                if counter % 100 == 0:
                    t1 = time.time()
                    ti = t1 - t0
                    print 'Last tile addresss was %s' % basePath + path
                    print '%s tiles have been generated so far' % counter
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
        print 'It took %s' % str(datetime.timedelta(seconds=tf))


if __name__ == '__main__':
    main()
