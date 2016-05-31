# -*- coding: utf-8 -*-

import cStringIO
import time
import datetime
import sys
import json
import traceback
import mapbox_vector_tile

from gatilegrid import GeoadminTileGrid
from poolmanager import PoolManager
from multiprocessing import Value

from sqlalchemy import text, not_
from sqlalchemy.sql import func
from sqlalchemy.orm import scoped_session, sessionmaker
from geoalchemy2.shape import to_shape
from geoalchemy2.elements import WKBElement
from vectorforge.models.stopo import getModelFromBodId
from vectorforge.lib.helpers import gzipFileObject
from vectorforge.lib.boto_s3 import s3Connect, getBucket, writeToS3


def featureMVT(geometry, properties):
    return {
        'geometry': geometry,
        'properties': properties
    }


def layerMVT(layerName, features, bounds):
    return mapbox_vector_tile.encode({
        'name': layerName,
        'features': features
    }, quantize_bounds=bounds)


def parseJsonConf(pathToConf):
    with open(pathToConf, 'r') as f:
        conf = json.load(f)
    return conf


def createQueryFilter(filters, filterIndices, operatorFilter):
    # Only ascii characters are supported
    count = 0
    txt = ''
    for i in filterIndices:
        fltr = filters[i]
        count += 1
        txt += fltr
        if count < len(filterIndices):
            txt += operatorFilter
    return text(txt)


def extendBounds(b, d):
    return [b[i] - d if i < 2 else b[i] + d for i in range(0, len(b))]


def applyQueryFilters(query, filterIndices, operatorFilter):
    # Apply custom filters
    if filters is not None:
        query = query.filter(
            createQueryFilter(
                filters,
                filterIndices,
                operatorFilter))
    return query


skippedTilesCounter = 0

def createTile(tileSpec):

    def simplifyGeom(geomDef, simplifyTol, simplifyType):
        if simplifyTol and simplifyType:
            return func.ST_AsEWKB(func.ST_Simplify(geomDef, simplifyTol))
        return geomDef

    def clippedMultiShape():
        clipped = model.bboxIntersects(
            bounds).label('clipped')
        clippedGeoms = model.bboxClippedGeom(
            bounds, geomcolumn=geometryColumnToReturn)
        sub = DBSession.query(
            (func.ST_Dump(clippedGeoms)).geom.label('clipped_geom'),
            *model.propertyColumns(includePkey=True)).\
                filter(clipped).subquery()
        query = DBSession.query(
            simplifyGeom(sub.c.clipped_geom, simplify, simplifyType).label('final_geom'),
            *[sub.c[k] for k in sub.c.keys() if k != 'clipped_geom']).\
                filter(func.ST_Dimension(sub.c.clipped_geom) == geometryDim)
        query = applyQueryFilters(query, filterIndices, operatorFilter)
        propsKeys = model.getPropertiesKeys(includePkey=True)
        for feature in query:
            properties = {}
            for propKey in propsKeys:
                prop = properties[propKey] = getattr(feature, propKey)
                if hasattr(prop, '__float__'):
                    prop = prop.__float__()
                    if prop % 1 == 0.0:
                        properties[propKey] = properties[propKey].__int__()
            finalGeom = feature.final_geom
            if finalGeom is not None:
                if not isinstance(finalGeom, WKBElement):
                    geometry = to_shape(WKBElement(feature.final_geom))
                else:
                    geometry = to_shape(feature.final_geom)
                yield featureMVT(geometry, properties)

    def clippedSimpleShape():
        clipped = model.bboxIntersects(
             bounds).label('clipped')
        clippedGeoms = model.bboxClippedGeom(
            bounds, geomcolumn=geometryColumnToReturn)
        query = DBSession.query(
            simplifyGeom(clippedGeoms, simplify, simplifyType).label('final_geom'),
            *model.propertyColumns(includePkey=True)).\
                filter(clipped)
        query = applyQueryFilters(query, filterIndices, operatorFilter)
        propsKeys = model.getPropertiesKeys(includePkey=True)
        for feature in query:
            properties = {}
            for propKey in propsKeys:
                prop = properties[propKey] = getattr(feature, propKey)
                if hasattr(prop, '__float__'):
                    prop = prop.__float__()
                    if prop % 1 == 0.0:
                        properties[propKey] = properties[propKey].__int__()
            finalGeom = feature.final_geom
            if finalGeom is not None:
                if not isinstance(finalGeom, WKBElement):
                    geometry = to_shape(WKBElement(finalGeom))
                else:
                    geometry = to_shape(finalGeom)
                yield featureMVT(geometry, properties)

    queryPerGeometryType = {
        'POINT': clippedSimpleShape,
        'MULTIPOINT': clippedSimpleShape,
        'LINESTRING': clippedSimpleShape,
        'MULTILINESTRING': clippedMultiShape,
        'POLYGON': clippedSimpleShape,
        'MULTIPOLYGON': clippedMultiShape,
        'GEOMETRYCOLLECTION': None, # No support yet
        'CURVE': None # No support yet
    }

    geometryDimension = {
        'POINT': 0,
        'MULTIPOINT': 0,
        'LINESTRING': 1,
        'MULTILINESTRING': 1,
        'POLYGON': 2,
        'MULTIPOLYGON': 2,
        'GEOMETRYCOLLECTION': None, # No support yet
        'CURVE': None # No support yet
    }

    simplifyTypes = {
        'POINT': False,
        'MULTIPOINT': False,
        'LINESTRING': True,
        'MULTILINESTRING': True,
        'POLYGON': True,
        'MULTIPOLYGON': True,
        'GEOMETRYCOLLECTION': False, # No support yet
        'CURVE': False # No support yet
    }

    geometrycolumn = 'the_geom'
    simplify = lod = tableName = filterIndices = operatorFilter = fullPath = None

    try:
        (tileBounds, zoomLevel, tileCol, tileRow) = tileSpec
        # DB query is lod dependent
        if lods is not None:
            lod = lods[str(zoomLevel)]
            filterIndices = lod.get('filterindices')
            operatorFilter = lod.get('operatorfilter')
            tableName = lod.get('tablename')
            geometrycolumn = lod.get('geometrycolumn', 'the_geom')
            simplify = lod.get('simplify')
            model = getModelFromBodId(layerBodId, tablename=tableName)
        else:
            model = getModelFromBodId(layerBodId)

        bounds = tileBounds
        # Apply buffer for points
        if gutter:
            buff = gagrid.getResolution(zoomLevel) * gutter
            bounds = extendBounds(bounds, buff)

        geometryColumn = model.geometryColumn()
        geometryColumnToReturn = model.geometryColumn(
            geometryColumnName=geometrycolumn)
        geometryType = geometryColumn.type.geometry_type
        geometryDim = geometryDimension[geometryType]
        simplifyType = simplifyTypes[geometryType]
        spatialQuery = queryPerGeometryType[geometryType]

        DBSession = scoped_session(sessionmaker())
        features = []
        for feat in spatialQuery():
            features.append(feat)
        if len(features) > 0:
            basePath = '2.1.0/%s/21781/default/current/' % layerBodId
            path = '%s/%s/%s.pbf' % (zoomLevel, tileCol, tileRow)
            fullPath = basePath + path
            mvt = layerMVT(model.__bodId__, features, tileBounds)
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
        print 'Failed during the creation of tile %s' % fullPath
        if debug:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=10, file=sys.stdout)
        raise Exception(str(e))
    finally:
        DBSession.close()
        if debug:
            debugCounter.value += 1
            callback(debugCounter.value, fullPath)

    return fullPath


def callback(counter, fullPath):
    if fullPath is None:
        with skippedTiles.get_lock():
            skippedTiles.value += 1

    if counter % 200 == 0:
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
    global layerBodId
    global lods
    global filters
    global gutter
    global gagrid
    global debug

    if len(sys.argv) < 2:
        print 'Please provide a json configuration. Exit.'
        sys.exit(1)

    if len(sys.argv) == 3:
        print 'Multiprocessing disabled: running in debug mode'
        debug = True
    else:
        print 'Multiprocessing enabled'
        debug = False

    try:
        conf = parseJsonConf(sys.argv[1])
    except Exception as e:
        print 'Error while parsing json file'
        raise Exception(e)


    layerBodId = conf.get('layerBodId')
    lods = conf.get('lods')
    filters = conf.get('filters', [])
    gutter = float(conf.get('gutter', 100.0))

    extent = conf.get('extent')
    tileSizePx = conf.get('tileSizePx', 256.0)
    gagrid = GeoadminTileGrid(extent=extent, tileSizePx=float(tileSizePx))

    minZoom = conf.get('minZoom', 0)
    maxZoom = conf.get('maxZoom', 26)
    tileGrid = gagrid.iterGrid(minZoom, maxZoom)

    if debug:
        map(createTile, tileGrid)
    else:
        pm = PoolManager(factor=2)
        pm.imap_unordered(tileGrid, createTile, 50, callback=callback)

    # End of process
    t3 = time.time()
    tf = t3 - t0
    print 'Tile generation process ended/stopped.'
    print 'It took %s' % str(datetime.timedelta(seconds=tf))


if __name__ == '__main__':
    t0 = time.time()
    skippedTiles = Value('i', 0)
    debugCounter = Value('i', 0)
    # Boto is thread safe
    conn = s3Connect('ltgal_aws_admin')
    bucket = getBucket(conn)
    main()
