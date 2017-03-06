# -*- coding: utf-8 -*-

from sqlalchemy import Column, Unicode, Integer
from geoalchemy2.types import Geometry

from vectorforge.models import init, bases, register, Vector


if bases.get('stopo_test') is None:
    init()
Base = bases.get('stopo_test')

GeomPoint = Geometry(
    geometry_type='Point',
    dimension=3,
    srid=3857)

GeomLineString = Geometry(
    geometry_type='LineString',
    dimension=3,
    srid=3857)

# Multi Points


class Swissnames3dLabelsPoint(Base, Vector):
    __tablename__ = 'swissnames3d_labels_points'
    __table_args__ = ({'autoload': False})
    __bodId__ = 'ch.swisstopo.swissnames3d_labels_points'
    uuid = Column('uuid', Unicode, primary_key=True)
    objektart = Column('objektart', Unicode)
    name = Column('name', Unicode)
    layerid = Column('layerid', Unicode)
    minzoom = Column('minzoom', Integer)
    the_geom = Column(GeomPoint)

register(Swissnames3dLabelsPoint)


class Swissnames3dLabelsLineString(Base, Vector):
    __tablename__ = 'swissnames3d_labels_lines'
    __table_args__ = ({'autoload': False})
    __bodId__ = 'ch.swisstopo.swissnames3d_labels_lines'
    uuid = Column('uuid', Unicode, primary_key=True)
    objektart = Column('objektart', Unicode)
    name = Column('name', Unicode)
    layerid = Column('layerid', Unicode)
    minzoom = Column('minzoom', Integer)
    the_geom = Column(GeomLineString)


register(Swissnames3dLabelsLineString)
