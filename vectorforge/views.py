# -*- coding: utf-8 -*-

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest 
from sqlalchemy.orm import scoped_session, sessionmaker
from geoalchemy2.shape import to_shape
import geojson

from vectorforge.models import layers


@view_config(route_name='home', renderer='templates/index.mako')
def home_view(request):
    return {'project': 'vector-forge'}


@view_config(route_name='geojson', renderer='json')
def geojson_view(request):
    layerID = request.matchdict.get('layerID')
    tolerance = request.params.get('tolerance')
    if tolerance is not None:
      tolerance = float(tolerance)
    if layerID not in layers.keys():
        raise HTTPBadRequest('Bad layerID: %s' %layerID)
    model = layers[layerID]
    DBSession = scoped_session(sessionmaker())
    res = DBSession.query(model).first()
    shapelyGeom = to_shape(res.the_geom)
    DBSession.close()
    return  geojson.Feature(id=res.id, geometry=shapelyGeom, properties={})
