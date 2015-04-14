# -*- coding: utf-8 -*-

from pyramid.config import Configurator
from vectorforge.models import init


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('pyramid_mako')

    # Init models
    init()

    # Static
    config.add_static_view('static', 'static', cache_max_age=3600)

    # Routes
    config.add_route('home', '/')
    config.add_route('ogcproxy', '/ogcproxy')
    config.add_route('geojson', '/rest/{layerID}')

    config.scan(ignore=['vectorforge.scripts'])
    return config.make_wsgi_app()
