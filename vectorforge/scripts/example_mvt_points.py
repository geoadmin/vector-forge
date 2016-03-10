# -*- coding: utf-8 -*-

import cStringIO
import time
import datetime
import sys
import json
import mapbox_vector_tile

from gatilegrid import GeoadminTileGrid
from poolmanager import PoolManager
from multiprocessing import Value

from sqlalchemy.orm import scoped_session, sessionmaker
from geoalchemy2.shape import to_shape
from vectorforge.models.stopo import getModelFromBodId
from vectorforge.lib.helpers import gzipFileObject
from vectorforge.lib.boto_s3 import s3Connect, getBucket, writeToS3


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


def parseJsonConf(pathToConf):
    with open(pathToConf, 'r') as f:
        conf = json.load(f)
    return conf


skippedTilesCounter = 0


def createTile(tileSpec):
    try:
        (tileBounds, zoomLevel, tileCol, tileRow) = tileSpec
        basePath = '1.0.0/%s/21781/default/' % layerBodId
        path = '%s/%s/%s.pbf' % (zoomLevel, tileCol, tileRow)
        fullPath = basePath + path

        if lods is not None:
            tablename = lods[str(zoomLevel)]
            model = getModelFromBodId(layerBodId, tablename=tablename)
        else:
            model = getModelFromBodId(layerBodId)

        DBSession = scoped_session(sessionmaker())
        clippedGeometry = model.bboxClippedGeom(tileBounds)
        query = DBSession.query(model, clippedGeometry)
        query = query.filter(model.bboxIntersects(tileBounds))
        features = []
        for feature in query:
            properties = feature[0].getProperties()
            properties['id'] = feature[1].id
            geometry = to_shape(feature[1])
            features.append(featureMVT(geometry, properties))
        if len(features) > 0:
            mvt = layerMVT(model.__bodId__, features)
            f = cStringIO.StringIO()
            f.write(mvt)
            writeToS3(
                bucket,
                path,
                gzipFileObject(f),
                'vector-forge',
                basePath,
                contentType='application/x-protobuf',
                contentEnc='gzip')
    except Exception as e:
        raise Exception(str(e))
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
    if len(sys.argv) != 2:
        print 'Please provide a json configuration. Exit.'
        sys.exit(1)
    try:
        conf = parseJsonConf(sys.argv[1])
    except Exception as e:
        print 'Error while parsing json file'
        raise Exception(e)

    global layerBodId
    global lods
    layerBodId = conf.get('layerBodId')
    lods = conf.get('lods')

    extent = conf.get('extent')
    tileSizePx = conf.get('tileSizePx', 256.0)
    gagrid = GeoadminTileGrid(extent=extent, tileSizePx=float(tileSizePx))

    minZoom = conf.get('minZoom', 0)
    maxZoom = conf.get('maxZoom', 0)
    tileGrid = gagrid.iterGrid(minZoom, maxZoom)

    pm = PoolManager(numProcs=4)
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
