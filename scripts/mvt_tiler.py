# -*- coding: utf-8 -*-

import cStringIO
import time
import datetime
import os
import sys
import json
import traceback
import mapbox_vector_tile
import vectorforge.models.stopo
import vectorforge.models.stopo_test

from gatilegrid import GeoadminTileGrid
from poolmanager import PoolManager
from multiprocessing import Value
from PIL import ImageFont

from sqlalchemy import text
from sqlalchemy.sql import func
from sqlalchemy.orm import scoped_session, sessionmaker
from geoalchemy2.shape import to_shape
from geoalchemy2.elements import WKBElement
from vectorforge.models import getModelFromBodId
from vectorforge.lib.helpers import gzipFileObject
from vectorforge.lib.boto_s3 import s3Connect, getBucket, writeToS3
from vectorforge.lib.grids import GlobalGeodeticTileGrid, GlobalMercatorTileGrid


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


def estimateLetterSizePx(maxFontSizePx):
    # Estimate the dimension of one letter in pixels using the provided
    # font. For now the freely available Liberation Sans TrueType font is used
    # which shows the same text width as the Arial ttf.
    # The computed letter width is over-estimated as typical labels have a
    # lower percentage of wide upper-case characters.
    fontDir = "/usr/share/fonts/truetype/liberation/"
    fontType = "LiberationSans-Regular.ttf"
    fontPath = os.path.join(fontDir, fontType)
    if not os.path.exists(fontPath):
        print 'Using default dimensions for letter size'
        return (11, 21)
    refText = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    textSize = ImageFont.truetype(fontPath, maxFontSizePx).getsize(refText)
    letterSize = (textSize[0] / len(refText), textSize[1])
    return letterSize


def extendBounds(b, d):
    return [b[i] - d if i < 2 else b[i] + d for i in range(0, len(b))]


def applyQueryFilters(query, filterIndices, operatorFilter):
    # Apply custom filters
    if filters is not None and filterIndices is not None:
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
            bounds, srid=srid).label('clipped')
        clippedGeoms = model.bboxClippedGeom(
            bounds, srid=srid, geomcolumn=geometryColumnToReturn)
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
             bounds, srid=srid).label('clipped')
        clippedGeoms = model.bboxClippedGeom(
            bounds, srid=srid, geomcolumn=geometryColumnToReturn)
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

    def annotationShape():
        query = DBSession.query(model)
        query = query.filter(model.bboxIntersectsAnnotation(
            bounds, letterSizeMeters, srid=srid))
        query = applyQueryFilters(query, filterIndices, operatorFilter)
        for feature in query:
            properties = feature.getProperties(includePkey=True)
            theGeom = feature.the_geom
            if theGeom is not None:
                if not isinstance(theGeom, WKBElement):
                    geometry = to_shape(WKBElement(theGeom))
                else:
                    geometry = to_shape(theGeom)
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
    tileAddressTemplate = '{zoom}/{tileCol}/{tileRow}.pbf'

    try:
        (tileBounds, zoomLevel, tileCol, tileRow) = tileSpec
        resolutionMetersPerPixel = gagrid.getResolution(zoomLevel)
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
        # Extend tile extent for including features near tile boundaries.
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
        letterSizeMeters = None
        if isAnnotationLayer:
            spatialQuery = annotationShape
            letterSizeMeters = (
                letterSizePx[0] * resolutionMetersPerPixel,
                letterSizePx[1] * resolutionMetersPerPixel
            )

        DBSession = scoped_session(sessionmaker())
        features = []
        for feat in spatialQuery():
            features.append(feat)
        if len(features) > 0:
            basePath = '2.1.0/%s/%s/default/current/' % (layerBodId, srid)
            path = tileAddressTemplate.replace('{zoom}', '%s' % zoomLevel) \
                                      .replace('{tileCol}', '%s' % tileCol) \
                                      .replace('{tileRow}', '%s' % tileRow)
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
    global letterSizePx
    global isAnnotationLayer
    global gagrid
    global debug
    global srid

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
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback,
                                 limit=10, file=sys.stdout)
        print 'Error while parsing json file'
        raise Exception(e)


    layerBodId = conf.get('layerBodId')
    lods = conf.get('lods')
    filters = conf.get('filters', [])
    gutter = float(conf.get('gutter', 100.0))

    extent = conf.get('extent')
    tileSizePx = conf.get('tileSizePx', 256.0)
    minZoom = conf.get('minZoom', 0)
    maxZoom = conf.get('maxZoom', 26)

    srid = conf.get('srid', 21781)

    if srid == 21781:
        gagrid = GeoadminTileGrid(extent=extent, tileSizePx=float(tileSizePx))
        tileGrid = gagrid.iterGrid(minZoom, maxZoom)
    elif srid == 3857:
        gagrid = GlobalMercatorTileGrid(extent=extent, tileSizePx=float(tileSizePx))
        tileGrid = gagrid.iterGrid(minZoom, maxZoom)
    elif srid == 4326:
        gagrid = GlobalGeodeticTileGrid(extent=extent, tileSizePx=float(tileSizePx))
        tileGrid = gagrid.iterGrid(minZoom, maxZoom)

    isAnnotationLayer = conf.get('isAnnotationLayer', False)
    if isAnnotationLayer:
        letterSizePx = estimateLetterSizePx(conf.get('maxFontSize', 20))

    if debug:
        map(createTile, tileGrid)
    else:
        pm = PoolManager(factor=2)
        pm.imap_unordered(createTile, tileGrid, 50, callback=callback)

    # End of process
    t3 = time.time()
    tf = t3 - t0
    print 'Tile generation process ended/stopped.'
    print 'It took %s' % str(datetime.timedelta(seconds=tf))


if __name__ == '__main__':
    t0 = time.time()
    skippedTiles = Value('i', 0)
    debugCounter = Value('i', 0)
    user = os.environ.get('USER')
    # Boto is thread safe
    conn = s3Connect('%s_aws_admin' % user)
    bucket = getBucket(conn)
    main()
