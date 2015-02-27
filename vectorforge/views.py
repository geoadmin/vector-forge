# -*- coding: utf-8 -*-

from pyramid.view import view_config


@view_config(route_name='home', renderer='templates/index.mako')
def my_view(request):
    return {'project': 'vector-forge'}
