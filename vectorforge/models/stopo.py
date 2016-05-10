# -*- coding: utf-8 -*-

from sqlalchemy import Column, Text, Integer, Float
from sqlalchemy.types import Numeric
from geoalchemy2.types import Geometry

from vectorforge.models import init, bases, register, Vector, layers


if bases.get('stopo') is None:
    init()
Base = bases.get('stopo')

GeomMultiPoint = Geometry(
        geometry_type='MULTIPOINT',
        dimension=2,
        srid=21781)
GeomMultiLinestring = Geometry(
        geometry_type='MULTILINESTRING',
        dimension=2,
        srid=21781)
GeomMultiPolygon = Geometry(
        geometry_type='MULTIPOLYGON',
        dimension=2,
        srid=21781)

# Multi Points


class Vec200Namedlocation(Base, Vector):
    __tablename__ = 'vec200_namedlocation'
    __table_args__ = ({'autoload': False})
    __bodId__ = 'ch.swisstopo.vec200-names-namedlocation'
    id = Column('gtdboid', Text, primary_key=True)
    objname1 = Column('objname1', Text)
    objname2 = Column('objname2', Text)
    altitude = Column('altitude', Integer)
    the_geom = Column(GeomMultiPoint)

register('ch.swisstopo.vec200-names-namedlocation', Vec200Namedlocation)

# Multi Lines


class Vec25Strassennetz(Base, Vector):
    __tablename__ = 'v25_str_25_l'
    __table_args__ = ({'autoload': False})
    __bodId__ = 'ch.swisstopo.vec25-strassennetz'
    id = Column('objectid', Integer, primary_key=True)
    length = Column('length', Numeric)
    yearofchan = Column('yearofchan', Float)
    objectval = Column('objectval', Text)
    the_geom = Column(GeomMultiLinestring)

register('ch.swisstopo.vec25-strassennetz', Vec25Strassennetz)

# Multi Polygons


class SwissboundariesGemeinde(Base, Vector):
    __tablename__ = 'swissboundaries_gemeinden'
    __table_args__ = ({'schema': 'tlm', 'autoload': False})
    __bodId__ = 'ch.swisstopo.swissboundaries3d-gemeinde-flaeche.fill'
    id = Column('id', Integer, primary_key=True)
    gemname = Column('gemname', Text)
    gemflaeche = Column('gemflaeche', Numeric)
    perimeter = Column('perimeter', Numeric)
    kanton = Column('kanton', Text)
    the_geom = Column(GeomMultiPolygon)

register(
    'ch.swisstopo.swissboundaries3d-gemeinde-flaeche.fill',
    SwissboundariesGemeinde)

# Carto layers


class CartoBodenbedeckung(Base, Vector):
    __tablename__ = 'dkm10_bodenbedeckung'
    __table_args__ = ({'schema': 'karto', 'autoload': False})
    __bodId__ = 'dkm10_bodenbedeckung'
    id = Column('objectid', Integer, primary_key=True)
    objektart = Column('objektart', Integer)
    rid1 = Column('rid1', Integer)
    the_geom = Column(GeomMultiPolygon)

register('dkm10_bodenbedeckung', CartoBodenbedeckung)


class CartoHoheitsgrenze(Base, Vector):
    __tablename__ = 'dkm10_hoheitsgrenze'
    __table_args__ = ({'schema': 'karto', 'autoload': False})
    __bodId__ = 'dkm10_hoheitsgrenze'
    id = Column('objectid', Integer, primary_key=True)
    objekart = Column('objektart', Integer)
    rid1 = Column('rid1', Integer)
    the_geom = Column(GeomMultiLinestring)

register('dkm10_hoheitsgrenze', CartoHoheitsgrenze)


class CartoGewaesserLin(Base, Vector):
    __tablename__ = 'dkm10_gewaesser_lin'
    __table_args__ = ({'schema': 'karto', 'autoload': False})
    __bodId__ = 'dkm10_gewaesser_lin'
    id = Column('objectid', Integer, primary_key=True)
    objekart = Column('objektart', Integer)
    name = Column('name', Text)
    verlauf = Column('verlauf', Integer)
    lb = Column('lb', Float)
    rid1 = Column('rid1', Integer)
    the_geom = Column(GeomMultiLinestring)

register('dkm10_gewaesser_lin', CartoGewaesserLin)


class CartoGewaesserPly(Base, Vector):
    __tablename__ = 'dkm10_gewaesser_ply'
    __table_args__ = ({'schema': 'karto', 'autoload': False})
    __bodId__ = 'dkm10_gewaesser_ply'
    id = Column('objectid', Integer, primary_key=True)
    objekart = Column('objektart', Integer)
    name = Column('name', Text)
    rid1 = Column('rid1', Integer)
    the_geom = Column(GeomMultiPolygon)

register('dkm10_gewaesser_ply', CartoGewaesserPly)


class CartoSiedlungsname(Base, Vector):
    __tablename__ = 'dkm10_siedlungsname'
    __table_args__ = ({'schema': 'karto', 'autoload': False})
    __bodId__ = 'dkm10_siedlungsname'
    id = Column('objectid', Integer, primary_key=True)
    objekart = Column('objektart', Integer)
    name = Column('name', Text)
    rid1 = Column('rid1', Integer)
    the_geom = Column(GeomMultiPolygon)

register('dkm10_siedlungsname', CartoSiedlungsname)


class CartoSiedlungsnameAnno(Base, Vector):
    __tablename__ = 'dkm10_siedlungsname_anno'
    __table_args__ = ({'schema': 'karto', 'autoload': False})
    __bodId__ = 'dkm10_siedlungsname_anno'
    id = Column('objectid', Integer, primary_key=True)
    annotationclassid = Column('annotationclassid', Integer)
    textstring = Column('textstring', Text)
    fontsize = Column('fontsize', Integer)
    bold = Column('bold', Integer)
    italic = Column('italic', Integer)
    the_geom = Column(GeomMultiPolygon)

register('dkm10_siedlungsname_anno', CartoSiedlungsnameAnno)

# Swissnames only


class Swissnames3d:
    __table_args__ = ({'schema': 'tlm', 'autoload': False})
    __bodId__ = 'ch.swisstopo.swissnames3d'
    id = Column('bgdi_id', Integer, primary_key=True)
    objektart = Column('objektart', Text)
    objektklasse = Column('objektklasse', Text)
    name = Column('name', Text)
    sprachcode = Column('sprachcode', Text)
    namen_typ = Column('namen_typ', Text)
    bgdi_type = Column('bgdi_type', Text)
    the_geom = Column(Geometry(geometry_type='GEOMETRY',
                               dimension=2, srid=21781))

# Eventually use scale directly


class Swissnames3dRaster00(Base, Swissnames3d, Vector):
    __tablename__ = 'swissnames3d_raster_00'
    __maxscale__ = 25000000
    __minscale__ = 2100000


class Swissnames3dRaster01(Base, Swissnames3d, Vector):
    __tablename__ = 'swissnames3d_raster_01'
    __maxscale__ = 2100000
    __minscale__ = 1700000


class Swissnames3dRaster02(Base, Swissnames3d, Vector):
    __tablename__ = 'swissnames3d_raster_02'
    __maxscale__ = 1700000
    __minscale__ = 940000


class Swissnames3dRaster03(Base, Swissnames3d, Vector):
    __tablename__ = 'swissnames3d_raster_03'
    __maxscale__ = 940000
    __minscale__ = 370000


class Swissnames3dRaster04(Base, Swissnames3d, Vector):
    __tablename__ = 'swissnames3d_raster_04'
    __maxscale__ = 370000
    __minscale__ = 180000


class Swissnames3dRaster05(Base, Swissnames3d, Vector):
    __tablename__ = 'swissnames3d_raster_05'
    __maxscale__ = 180000
    __minscale__ = 75000


class Swissnames3dRaster06(Base, Swissnames3d, Vector):
    __tablename__ = 'swissnames3d_raster_06'
    __maxscale__ = 75000
    __minscale__ = 35000


class Swissnames3dRaster07(Base, Swissnames3d, Vector):
    __tablename__ = 'swissnames3d_raster_07'
    __maxscale__ = 35000
    __minscale__ = 18000


class Swissnames3dRaster08(Base, Swissnames3d, Vector):
    __tablename__ = 'swissnames3d_raster_08'
    __maxscale__ = 18000
    __minscale__ = 9000


class Swissnames3dRaster09(Base, Swissnames3d, Vector):
    __tablename__ = 'swissnames3d_raster_09'
    __maxscale__ = 9000
    __minscale__ = 7000


class Swissnames3dRaster10(Base, Swissnames3d, Vector):
    __tablename__ = 'swissnames3d_raster_10'
    __maxscale__ = 7000
    __minscale__ = 3500


class Swissnames3dRaster11(Base, Swissnames3d, Vector):
    __tablename__ = 'swissnames3d_raster_11'
    __maxscale__ = 3500
    __minscale__ = 1800


class Swissnames3dRaster12(Base, Swissnames3d, Vector):
    __tablename__ = 'swissnames3d_raster_12'
    __maxscale__ = 1800
    __minscale__ = 900


class Swissnames3dRaster13(Base, Swissnames3d, Vector):
    __tablename__ = 'swissnames3d_raster_13'
    __maxscale__ = 900
    __minscale__ = 1


register('ch.swisstopo.swissnames3d', Swissnames3dRaster00)
register('ch.swisstopo.swissnames3d', Swissnames3dRaster01)
register('ch.swisstopo.swissnames3d', Swissnames3dRaster02)
register('ch.swisstopo.swissnames3d', Swissnames3dRaster03)
register('ch.swisstopo.swissnames3d', Swissnames3dRaster04)
register('ch.swisstopo.swissnames3d', Swissnames3dRaster05)
register('ch.swisstopo.swissnames3d', Swissnames3dRaster06)
register('ch.swisstopo.swissnames3d', Swissnames3dRaster07)
register('ch.swisstopo.swissnames3d', Swissnames3dRaster08)
register('ch.swisstopo.swissnames3d', Swissnames3dRaster09)
register('ch.swisstopo.swissnames3d', Swissnames3dRaster10)
register('ch.swisstopo.swissnames3d', Swissnames3dRaster11)
register('ch.swisstopo.swissnames3d', Swissnames3dRaster12)
register('ch.swisstopo.swissnames3d', Swissnames3dRaster13)


def getModelFromBodId(bodId, tablename=None):
    models = layers.get(bodId)
    if len(models) == 1:
        return models[0]
    if tablename is not None:
        for model in models:
            if model.__tablename__ == tablename:
                return model
