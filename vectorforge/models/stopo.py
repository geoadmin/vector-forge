# -*- coding: utf-8 -*-

from sqlalchemy import Column, Text, Integer
from sqlalchemy.types import Numeric
from geoalchemy2.types import Geometry

from vectorforge.models import init, bases, Vector


if bases.get('stopo') is None:
    init()
Base = bases.get('stopo')


# Points
class Vec200Namedlocation(Base, Vector):
    __tablename__ = 'vec200_namedlocation'
    __table_args__ = ({'autoload': False})
    __bodId__ = 'ch.swisstopo.vec200-names-namedlocation'
    id = Column('gtdboid', Text, primary_key=True)
    objname1 = Column('objname1', Text)
    objname2 = Column('objname2', Text)
    altitude = Column('altitude', Integer)
    the_geom = Column(Geometry(geometry_type='GEOMETRY',
                               dimension=2, srid=21781))

# Lines
class Vec25Strassennetz(Base, Vector):
    __tablename__ = 'v25_str_25_l_tooltip'
    __table_args__ = ({'autoload': False})
    __bodId__ = 'ch.swisstopo.vec25-strassennetz'
    id = Column('objectid', Integer, primary_key=True)
    length = Column('length', Numeric)
    the_geom = Column(Geometry(geometry_type='GEOMETRY',
                               dimension=2, srid=21781))

# Polygons
class SwissboundariesGemeinde(Base, Vector):
    __tablename__ = 'swissboundaries_gemeinden'
    __table_args__ = ({'schema': 'tlm', 'autoload': False})
    __bodId__ = 'ch.swisstopo.swissboundaries3d-gemeinde-flaeche.fill'
    id = Column('id', Integer, primary_key=True)
    gemname = Column('gemname', Text)
    gemflaeche = Column('gemflaeche', Numeric)
    perimeter = Column('perimeter', Numeric)
    kanton = Column('kanton', Text)
    the_geom = Column(Geometry(geometry_type='GEOMETRY',
                               dimension=2, srid=21781))
