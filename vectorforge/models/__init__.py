# -*- coding: utf-8 -*-

import re
import ConfigParser
import decimal
import datetime
from sqlalchemy import create_engine, Integer
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import cast
from sqlalchemy.exc import NoSuchColumnError
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2.elements import WKBElement
from geoalchemy2.types import Geometry
from shapely.geometry import box


class Engines(object):

    def __init__(self, engines={}):
        self.engines = engines

    def get(self, dbname):
        if dbname in self.engines:
            return self.engines[dbname]
        else:
            return None

    def add(self, engine, dbname):
        self.engines[dbname] = engine


class Bases(object):

    def __init__(self):
        self.bases = {}

    def get(self, dbname):
        if dbname in self.bases:
            return self.bases[dbname]
        else:
            return None

    def add(self, engine, dbname):
        base = declarative_base()
        base.metadata.bind = engine
        self.bases[dbname] = base

engines = Engines()
bases = Bases()
layers = {}


def register(model):
    layerId = model.__bodId__
    if layerId not in layers:
        layers[layerId] = [model]
    else:
        layers[layerId].append(model)


def init():
    srvMain = 'server:main'
    config = ConfigParser.ConfigParser()
    config.read('production.ini')
    options = config.options(srvMain)
    for option in options:
        if option.startswith('sqlalchemy.'):
            dbUrl = config.get(srvMain, option)
            engine = create_engine(dbUrl)
            dbName = re.search('sqlalchemy.([a-z_]*).url', option).groups()[0]
            engines.add(engine, dbName)
            bases.add(engine, dbName)


class Vector(object):

    @classmethod
    def primaryKeyColumn(cls):
        return cls.__mapper__.primary_key[0]

    @classmethod
    def geometryColumn(cls, geometryColumnName='the_geom'):
        if geometryColumnName not in cls.__mapper__.columns:
            raise NoSuchColumnError()
        return cls.__mapper__.columns[geometryColumnName]

    @classmethod
    def annotationColumn(cls, annotationColumnName='name'):
        if annotationColumnName not in cls.__mapper__.columns:
            raise NoSuchColumnError()
        return cls.__mapper__.columns[annotationColumnName]

    """
    Returns a sqlalchemy.sql.functions.Function
    :params srid: the target srid.
    :params geometrycolumn: Another geometry column (or expression) than the one defined on the childe model.
    """
    @classmethod
    def transform(cls, srid, geomcolumn=None):
        geomColumn = geomcolumn if geomcolumn is not None else cls.geometryColumn()
        return func.ST_Transform(geomColumn, cast(srid, Integer))

    """
    Returns a sqlalchemy.sql.functions.Function clipping function
    :params bbox: A list of 4 coordinates [minX, minY, maxX, maxY]
    :params srid: the srid of the bbox and returned geometry.
    :params geomcolumn: Another geometry column (or expression) than the one defined on the child model.
    """
    @classmethod
    def bboxClippedGeom(
            cls,
            bbox,
            srid=21781,
            extended=False,
            geomcolumn=None):
        bboxGeom = shapelyBBox(bbox)
        geomColumn = geomcolumn if geomcolumn is not None else cls.geometryColumn()
        wkbGeometry = WKBElement(
            buffer(
                bboxGeom.wkb),
            srid=srid,
            extended=extended)
        # Transform bbox and cut geometries using the target srid
        if geomColumn.type.srid != srid:
            wkbGeometry = cls.transform(
                geomColumn.type.srid, geomcolumn=wkbGeometry)
            return cls.transform(
                srid, func.ST_Intersection(
                    geomColumn, wkbGeometry))
        return func.ST_Intersection(geomColumn, wkbGeometry)

    """
    Returns a slqalchemy.sql.functions.Function interesects function
    Use it as a filter to determine if a geometry should be returned (True or False)
    :params bbox: A list of 4 coordinates [minX, minX, maxX, maxY]
    :params srid: the srid of the bbox and returned geometry.
    :params geomcolumn: Another geometry column (or expression) than the one defined on the child model.
    """
    @classmethod
    def bboxIntersects(
            cls,
            bbox,
            srid=21781,
            extended=False,
            geomcolumn=None):
        bboxGeom = shapelyBBox(bbox)
        wkbGeometry = WKBElement(
            buffer(
                bboxGeom.wkb),
            srid=srid,
            extended=extended)
        geomColumn = geomcolumn if geomcolumn is not None else cls.geometryColumn()
        if geomColumn.type.srid != srid:
            wkbGeometry = cls.transform(
                geomColumn.type.srid, geomcolumn=wkbGeometry)
        return func.ST_Intersects(geomColumn, wkbGeometry)

    """
    Returns a slqalchemy.sql.functions.Function interesects function
    Use it as a filter to determine if an annotation feature should be returned
    (True or False)
    :params bbox: A list of 4 coordinates [minX, minX, maxX, maxY]
    :params letterSizMeters: A list of 2 integers expressing the width and the height of a letter in meters.
    """
    @classmethod
    def bboxIntersectsAnnotation(cls,
                                 bbox,
                                 letterSizMeters,
                                 srid=21781,
                                 extended=False,
                                 geomcolumn=None):
        bboxGeom = shapelyBBox(bbox)
        geomColumn = geomcolumn if geomcolumn is not None else cls.geometryColumn()
        wkbGeometry = WKBElement(
            buffer(
                bboxGeom.wkb),
            srid=srid,
            extended=extended)
        if geomColumn.type.srid != srid:
            wkbGeometry = cls.transform(
                geomColumn.type.srid, geomcolumn=wkbGeometry)
        query = func.ST_Intersects(
            func.ST_SetSRID(
                func.ST_MakeBox2D(
                    func.ST_Point(
                        func.st_x(geomColumn) -
                        func.char_length(
                            cls.annotationColumn()) /
                        2 *
                        letterSizMeters[0],
                        func.st_y(geomColumn) -
                        letterSizMeters[1] /
                        2),
                    func.ST_Point(
                        func.st_x(geomColumn) +
                        func.char_length(
                            cls.annotationColumn()) /
                        2 *
                        letterSizMeters[0],
                        func.st_y(geomColumn) +
                        letterSizMeters[1] /
                        2)),
                geomColumn.type.srid),
            wkbGeometry)
        return query

    """
    Returns a sqlalchemy.sql.functions.Function line merge function
    It creates a (set of) LineString(s) formed by sewing together a MULTILINESTRING.
    If can't be merged - original MULTILINESTRING is returned
    """
    @classmethod
    def lineMerge(cls):
        geomColumn = cls.geometryColumn()
        return func.ST_AsEWKB(func.ST_LineMerge(geomColumn))

    @classmethod
    def propertyColumns(cls, includePkey=False):
        columns = []
        for c in cls.__mapper__.columns:
            isPrimarykey = c.primary_key
            isGeometry = isinstance(c.type, Geometry)
            if (isPrimarykey and includePkey) or (
                    not isPrimarykey and not isGeometry):
                columns.append(c)
        return columns

    @classmethod
    def getPropertiesKeys(cls, includePkey=False):
        columns = cls.propertyColumns(includePkey=includePkey)
        return [c.key for c in columns]

    def getProperties(self, includePkey=False):
        """
        Expose all that is not an id and a geometry
        """
        properties = {}
        for c in self.__table__.columns:
            isPrimaryKey = c.primary_key
            isGeometry = isinstance(c.type, Geometry)
            if (isPrimaryKey and includePkey) or (
                    not isPrimaryKey and not isGeometry):
                # As mapped on the model
                propertyName = self.__mapper__.get_property_by_column(c).key
                propertyValue = getattr(self, c.name)
                properties[propertyName] = formatPropertyValue(propertyValue)
        return properties


"""
Returns a shapely.geometry.polygon.Polygon
:param bbox: A list of 4 cooridinates [minX, minY, maxX, maxY]
"""


def shapelyBBox(bbox):
    return box(*bbox)


"""
Returns a primitive type like value (int, str, bool, ...)
:param prop: A feature property
"""


def formatPropertyValue(prop):
    if isinstance(prop, decimal.Decimal):
        return prop.__float__()
    elif isinstance(prop, datetime.datetime):
        return prop.strftime("%d.%m.%Y")
    elif isinstance(prop, str) or isinstance(prop, unicode):
        return prop.rstrip()
    return prop


def getModelFromBodId(bodId, tablename=None):
    models = layers.get(bodId)
    if models and len(models) == 1:
        return models[0]
    if tablename is not None:
        for model in models:
            if model.__tablename__ == tablename:
                return model
