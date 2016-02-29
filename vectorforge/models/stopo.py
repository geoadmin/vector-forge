# -*- coding: utf-8 -*-

from sqlalchemy import Column, Text, Integer, Float
from sqlalchemy.types import Numeric
from geoalchemy2.types import Geometry

from vectorforge.models import init, bases, register, Vector


if bases.get('stopo_int') is None:
    init()
Base = bases.get('stopo_int')


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

register('ch.swisstopo.vec200-names-namedlocation', Vec200Namedlocation)

# Lines
class Vec25Strassennetz(Base, Vector):
    __tablename__ = 'v25_str_25_l'
    __table_args__ = ({'autoload': False})
    __bodId__ = 'ch.swisstopo.vec25-strassennetz'
    id = Column('objectid', Integer, primary_key=True)
    length = Column('length', Numeric)
    yearofchan = Column('yearofchan', Float)
    objectval = Column('objectval', Text)
    the_geom = Column(Geometry(geometry_type='GEOMETRY',
                               dimension=2, srid=21781))

register('ch.swisstopo.vec25-strassennetz', Vec25Strassennetz)

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

register('ch.swisstopo.swissboundaries3d-gemeinde-flaeche.fill', SwissboundariesGemeinde)
