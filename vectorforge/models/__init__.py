# -*- coding: utf-8 -*-

import decimal
import datetime
from sqlalchemy import create_engine
from sqlalchemy.sql import func
from sqlalchemy.exc import NoSuchColumnError
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2.elements import WKBElement
from geoalchemy2.types import Geometry
from shapely.geometry import box

# Defined here to be called from outside the web app
dbhost = 'pg-0.dev.bgdi.ch'
dbport = '5432'
dbs = ['bod_int', 'stopo_master']


class Engines(object):

    def __init__(self, engines={}):
        self.engines = engines

    def get(self, dbname):
        if dbname in self.engines:
            return self.engines[dbname]
        else:
            return None

    def add(self, engine, dbname):
        name = dbname.split('_')[0]
        self.engines[name] = engine


class Bases(object):

    def __init__(self):
        self.bases = {}

    def get(self, dbname):
        if dbname in self.bases:
            return self.bases[dbname]
        else:
            return None

    def add(self, engine, dbname):
        name = dbname.split('_')[0]
        base = declarative_base()
        base.metadata.bind = engine
        self.bases[name] = base

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
    for dbname in dbs:
        engine = create_engine(
            'postgresql://%s:%s/%s' %
            (dbhost, dbport, dbname))
        engines.add(engine, dbname)
        bases.add(engine, dbname)


class Vector(object):

    @classmethod
    def primaryKeyColumn(cls):
        return cls.__mapper__.primary_key[0]

    @classmethod
    def geometryColumn(cls, geometryColumnName='the_geom'):
        if geometryColumnName not in cls.__mapper__.columns:
            raise NoSuchColumnError()
        return cls.__mapper__.columns[geometryColumnName]

    """
    Returns a sqlalchemy.sql.functions.Function clipping function
    :param bbox: A list of 4 coordinates [minX, minY, maxX, maxY]
    :params geomcolumn: Another geometry column (or expression) than the one defined on the childe model.
    """
    @classmethod
    def bboxClippedGeom(
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
        return func.ST_Intersection(geomColumn, wkbGeometry)

    """
    Returns a slqalchemy.sql.functions.Function interesects function
    Use it as a filter to determine if a geometry should be returned (True or False)
    :params bbox: A list of 4 coordinates [minX, minX, maxX, maxY]
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
        return func.ST_Intersects(geomColumn, wkbGeometry)

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
