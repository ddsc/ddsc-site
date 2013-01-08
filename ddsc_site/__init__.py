"""Main entry point.
"""
from pyramid.config import Configurator
from pyramid_zodbconn import get_connection

from ddsc_site.models import appmaker


def root_factory(request):
    conn = get_connection(request)
    return appmaker(conn.root())


def main(global_config, **settings):
    config = Configurator(root_factory=root_factory, settings=settings)
    config.include("pyramid_fanstatic")
    config.include("pyramid_jinja2")
    config.include("cornice")
    config.scan("ddsc_site.views")
    return config.make_wsgi_app()
