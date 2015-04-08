# -*- coding: utf-8 -*-

from pyramid.config import Configurator
from vectorforge.models import init


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('pyramid_mako')
    init()

    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('geojson', '/rest/{layerID}')
    config.scan(ignore=['vectorforge.scripts'])
    return config.make_wsgi_app()
