# -*- coding: utf-8 -*-

from sqlalchemy import Column, Text, Integer, Float
from sqlalchemy.types import Numeric
from geoalchemy2.types import Geometry

from vectorforge.models import init, bases, register, Vector, layers


if bases.get('stopo') is None:
    init()
Base = bases.get('stopo')

GeomPoint = Geometry(
    geometry_type='POINT',
    dimension=2,
    srid=21781)
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

register(Vec200Namedlocation)

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

register(Vec25Strassennetz)

# Multi Polygons
class SwissboundariesKanton(Base, Vector):
    __tablename__ = 'prodas_spatialseltype_kanton'
    __table_args__ = ({'schema': 'tlm', 'autoload': False})
    __bodId__ = 'ch.swisstopo.swissboundaries3d-kanton-flaeche.fill'
    id = Column('id', Integer, primary_key=True)
    bez = Column('bez', Text)
    kanton = Column('kanton', Text)
    flaeche = Column('flaeche', Integer)
    the_geom = Column(GeomMultiPolygon)
    the_geom_topo = Column('the_geom_topo', GeomMultiPolygon)

register(SwissboundariesKanton)


class SwissboundariesBezirk(Base, Vector):
    __tablename__ = 'prodas_spatialseltype_bezirk'
    __table_args__ = ({'schema': 'tlm', 'autoload': False})
    __bodId__ = 'ch.swisstopo.swissboundaries3d-bezirk-flaeche.fill'
    id = Column('id', Integer, primary_key=True)
    gemname = Column('displayname', Text)
    bez = Column('bez', Text)
    kanton = Column('kanton', Text)
    the_geom = Column(GeomMultiPolygon)
    the_geom_topo = Column('the_geom_topo', GeomMultiPolygon)

register(SwissboundariesBezirk)


class SwissboundariesGemeinde(Base, Vector):
    __tablename__ = 'prodas_spatialseltype_gemeinde_forge'
    __table_args__ = ({'schema': 'tlm', 'autoload': False})
    __bodId__ = 'ch.swisstopo.swissboundaries3d-gemeinde-flaeche.fill'
    id = Column('id', Integer, primary_key=True)
    gemname = Column('displayname', Text)
    bezirk = Column('bezirk', Text)
    kanton = Column('kanton', Text)
    the_geom = Column(GeomMultiPolygon)
    the_geom_topo = Column('the_geom_topo', GeomMultiPolygon)

register(SwissboundariesGemeinde)

# Carto layers


class CartoBodenbedeckung:
    __table_args__ = ({'schema': 'karto', 'autoload': False})
    id = Column('objectid', Integer, primary_key=True)
    objektart = Column('objektart', Integer)
    rid1 = Column('rid1', Integer)
    the_geom = Column(GeomMultiPolygon)


class CartoBodenbedeckung10(Base, CartoBodenbedeckung, Vector):
    __tablename__ = 'dkm10_bodenbedeckung'
    __bodId__ = 'dkm10_bodenbedeckung'
    the_geom_topo = Column('the_geom_topo', GeomMultiPolygon)


class CartoBodenbedeckung500(Base, CartoBodenbedeckung, Vector):
    __tablename__ = 'dkm500_bodenbedeckung'
    __bodId__ = 'dkm500_bodenbedeckung'

register(CartoBodenbedeckung10)
register(CartoBodenbedeckung500)


class CartoHoheitsgrenze:
    __table_args__ = ({'schema': 'karto', 'autoload': False})
    id = Column('objectid', Integer, primary_key=True)
    objekart = Column('objektart', Integer)
    rid1 = Column('rid1', Integer)
    the_geom = Column(GeomMultiLinestring)


class CartoHoheitsgrenze10(Base, CartoHoheitsgrenze, Vector):
    __tablename__ = 'dkm10_hoheitsgrenze'
    __bodId__ = 'dkm10_hoheitsgrenze'


class CartoHoheitsgrenze25(Base, CartoHoheitsgrenze, Vector):
    __tablename__ = 'dkm25_hoheitsgrenze'
    __bodId__ = 'dkm25_hoheitsgrenze'


class CartoHoheitsgrenze50(Base, CartoHoheitsgrenze, Vector):
    __tablename__ = 'dkm50_hoheitsgrenze'
    __bodId__ = 'dkm50_hoheitsgrenze'


class CartoHoheitsgrenze500(Base, CartoHoheitsgrenze, Vector):
    __tablename__ = 'dkm500_hoheitsgrenze'
    __bodId__ = 'dkm500_hoheitsgrenze'

register(CartoHoheitsgrenze10)
register(CartoHoheitsgrenze25)
register(CartoHoheitsgrenze50)
register(CartoHoheitsgrenze500)


class CartoGewaesserLin:
    __table_args__ = ({'schema': 'karto', 'autoload': False})
    id = Column('objectid', Integer, primary_key=True)
    objekart = Column('objektart', Integer)
    name = Column('name', Text)
    verlauf = Column('verlauf', Integer)
    rid1 = Column('rid1', Integer)
    the_geom = Column(GeomMultiLinestring)


class CartoGewaesserLin10(Base, CartoGewaesserLin, Vector):
    __tablename__ = 'dkm10_gewaesser_lin'
    __bodId__ = 'dkm10_gewaesser_lin'
    lb = Column('lb', Float)


class CartoGewaesserLin25(Base, CartoGewaesserLin, Vector):
    __tablename__ = 'dkm25_gewaesser_lin'
    __bodId__ = 'dkm25_gewaesser_lin'
    lb = Column('lb', Float)


class CartoGewaesserLin50(Base, CartoGewaesserLin, Vector):
    __tablename__ = 'dkm50_gewaesser_lin'
    __bodId__ = 'dkm50_gewaesser_lin'
    lb = Column('lb50', Float)


class CartoGewaesserLin500(Base, CartoGewaesserLin, Vector):
    __tablename__ = 'dkm500_gewaesser_lin'
    __bodId__ = 'dkm500_gewaesser_lin'
    lb = Column('lb500', Float)

register(CartoGewaesserLin10)
register(CartoGewaesserLin25)
register(CartoGewaesserLin50)
register(CartoGewaesserLin500)


class CartoGewaesserPly:
    __table_args__ = ({'schema': 'karto', 'autoload': False})
    id = Column('objectid', Integer, primary_key=True)
    objekart = Column('objektart', Integer)
    rid1 = Column('rid1', Integer)
    the_geom = Column(GeomMultiPolygon)


class CartoGewaesserPly10(Base, CartoGewaesserPly, Vector):
    __tablename__ = 'dkm10_gewaesser_ply'
    __bodId__ = 'dkm10_gewaesser_ply'
    name = Column('name', Text)


class CartoGewaesserPly500(Base, CartoGewaesserPly, Vector):
    __tablename__ = 'dkm500_gewaesser_ply'
    __bodId__ = 'dkm500_gewaesser_ply'
    name = Column('namn1', Text)

register(CartoGewaesserPly10)
register(CartoGewaesserPly500)


class CartoSiedlungsname:
    __table_args__ = ({'schema': 'karto', 'autoload': False})
    id = Column('objectid', Integer, primary_key=True)
    objekart = Column('objektart', Integer)
    rid1 = Column('rid1', Integer)


class CartoSiedlungsname10(Base, CartoSiedlungsname, Vector):
    __tablename__ = 'dkm10_siedlungsname'
    __bodId__ = 'dkm10_siedlungsname'
    name = Column('name', Text)
    the_geom = Column(GeomMultiPolygon)


class CartoSiedlungsname500(Base, CartoSiedlungsname, Vector):
    __tablename__ = 'dkm500_ortschaft_pkt'
    __bodId__ = 'dkm500_ortschaft_pkt'
    name = Column('namn1', Text)
    the_geom = Column(GeomPoint)

register(CartoSiedlungsname10)
register(CartoSiedlungsname500)


class CartoSiedlungsnameAnno:
    __table_args__ = ({'schema': 'karto', 'autoload': False})
    id = Column('objectid', Integer, primary_key=True)
    annotationclassid = Column('annotationclassid', Integer)
    textstring = Column('textstring', Text)
    fontsize = Column('fontsize', Integer)
    bold = Column('bold', Integer)
    italic = Column('italic', Integer)
    the_geom = Column(GeomPoint)


class CartoSiedlungsnameAnno10(Base, CartoSiedlungsnameAnno, Vector):
    __tablename__ = 'dkm10_siedlungsname_anno'
    __bodId__ = 'dkm10_siedlungsname_anno'


class CartoSiedlungsnameAnno25(Base, CartoSiedlungsnameAnno, Vector):
    __tablename__ = 'dkm25_siedlungsname_anno'
    __bodId__ = 'dkm25_siedlungsname_anno'


class CartoSiedlungsnameAnno50(Base, CartoSiedlungsnameAnno, Vector):
    __tablename__ = 'dkm50_siedlungsname_anno'
    __bodId__ = 'dkm50_siedlungsname_anno'


class CartoSiedlungsnameAnno500(Base, CartoSiedlungsnameAnno, Vector):
    __tablename__ = 'dkm500_siedlungsname_anno'
    __bodId__ = 'dkm500_siedlungsname_anno'

register(CartoSiedlungsnameAnno10)
register(CartoSiedlungsnameAnno25)
register(CartoSiedlungsnameAnno50)
register(CartoSiedlungsnameAnno500)

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


register(Swissnames3dRaster00)
register(Swissnames3dRaster01)
register(Swissnames3dRaster02)
register(Swissnames3dRaster03)
register(Swissnames3dRaster04)
register(Swissnames3dRaster05)
register(Swissnames3dRaster06)
register(Swissnames3dRaster07)
register(Swissnames3dRaster08)
register(Swissnames3dRaster09)
register(Swissnames3dRaster10)
register(Swissnames3dRaster11)
register(Swissnames3dRaster12)
register(Swissnames3dRaster13)


def getModelFromBodId(bodId, tablename=None):
    models = layers.get(bodId)
    if len(models) == 1:
        return models[0]
    if tablename is not None:
        for model in models:
            if model.__tablename__ == tablename:
                return model
