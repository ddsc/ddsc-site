""" Cornice services.
"""
from cornice import Service
from cornice.resource import resource
from cornice.resource import view


hello = Service(name='hello', path='/', description="Simplest app")
# data_source = Service(name='data_source', path='/api/')


@hello.get()
def get_info(request):
    """Returns Hello in JSON."""
    return {'Hello': 'World'}


@resource(collection_path='/api/data_sources', path='/api/data_sources/{id}')
class DataSource(object):

    def __init__(self, request):
        self.request = request
        self.wms_sources = self.request.root.wms_sources

    def collection_get(self):
        return {'wms_sources': self.wms_sources.keys()}

    @view(renderer='json')
    def get(self):
        # Should be a dict.
        return self.wms_sources.get(self.request.matchdict['id'])
