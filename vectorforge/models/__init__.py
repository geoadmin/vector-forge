# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2.elements import WKBElement
from shapely.geometry import box

# Defined here to be called from outside the web app
host = 'localhost'
port = '5432'
dbs = ['bod', 'stopo']

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

def register(layerID, model):
    layers[layerID] = model

def init():
    for dbname in dbs:
        engine = create_engine('postgresql://%s:%s/%s' %(host, port, dbname))
        engines.add(engine, dbname)
        bases.add(engine, dbname)

class Vector(object):

    @classmethod
    def primaryKeyColumn(cls):
        return cls.__mapper__.primary_key[0]

    @classmethod
    def geometryColumn(cls):
        return cls.__mapper__.columns['the_geom']

    """
    Returns a sqlalchemy.sql.functions.Function clipping function
    :param bbox: A list of 4 coordinates [minX, minY, maxX, maxY]
    """
    @classmethod
    def bboxClippedGeom(cls, bbox, srid=21781):
        bboxGeom = shapelyBBox(bbox)
        wkbGeometry = WKBElement(buffer(bboxGeom.wkb), srid)
        geomColumn = cls.geometryColumn()
        return func.ST_Intersection(geomColumn, wkbGeometry)

    """
    Returns a slqalchemy.sql.functions.Function interesects function
    Use it as a filter to determine if a geometry should be returned (True or False)
    :params bbox: A list of 4 coordinates [minX, minX, maxX, maxY]
    """
    @classmethod
    def bboxIntersects(cls, bbox, srid=21781):
        bboxGeom = shapelyBBox(bbox)
        wkbGeometry = WKBElement(buffer(bboxGeom.wkb), srid)
        geomColumn = cls.geometryColumn()
        return func.ST_Intersects(geomColumn, wkbGeometry)

    def getProperties(self):
        """ 
        Expose all that is not an id and a geometry
        """
        properties = {}
        for column in self.__table__.columns:
          isPrimaryKey = bool(self.primaryKeyColumn() == column)
          isGeometry = bool(self.geometryColumn() == column)
          if not isPrimaryKey and not isGeometry:
              # As mapped on the model
              propertyName = self.__mapper__.get_property_by_column(column).key
              propertyValue = getattr(self, column.name)
              properties[propertyName] = propertyValue
        return properties


"""
Returns a shapely.geometry.polygon.Polygon
:param bbox: A list of 4 cooridinates [minX, minY, maxX, maxY]
"""
def shapelyBBox(bbox):
    return box(*bbox)
