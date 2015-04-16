# -*- coding: utf-8 -*-

import geojson
from httplib2 import Http
from geoalchemy2.shape import to_shape
from sqlalchemy.orm import scoped_session, sessionmaker
from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPBadRequest, HTTPBadGateway 

from vectorforge.models import layers


@view_config(route_name='home', renderer='templates/index.mako')
def homeView(request):
    return {'project': 'vector-forge'}


@view_config(route_name='ogcproxy')
def ogcproxyView(request):
    url = request.params.get('url')
    if url is None:
        raise HTTPBadRequest('Please provide a parameter url')
    http = Http(disable_ssl_certificate_validation=True)
    h = dict(request.headers)
    h.pop('Host', h)
    try:
      resp, content = http.request(url, method=request.method, body=request.body, headers=h)
    except:
      raise HTTPBadGateway()
    if 'content-type' in resp:
      ct = resp['content-type']
    else:
      raise HTTPBadGateway()
    return Response(content, status=resp.status, headers={'Content-Type': ct})


@view_config(route_name='geojson', renderer='json')
def geojsonView(request):
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
    properties = res.getProperties()
    DBSession.close()
    return  geojson.Feature(id=res.id, geometry=shapelyGeom, properties=properties)
