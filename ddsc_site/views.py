""" Cornice services.
"""
from cornice import Service
from cornice.resource import resource
from cornice.resource import view
from pyramid.view import view_config


hello = Service(name='hello', path='/api', description="Simplest app")
# data_source = Service(name='data_source', path='/api/')


@view_config(context='repoze.folder.Folder',
             renderer='ddsc_site:templates/default_folder.jinja2')
class DefaultFolderView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def _name(self, obj):
        if hasattr(obj, 'name'):
            return obj.name
        return obj.__name__

    @property
    def folder_name(self):
        return self._name(self.context)

    @property
    def contents(self):
        return [{'url': self.request.resource_url(resource),
                 'name': self._name(resource)}
                for resource in self.context.values()]

    def __call__(self):
        return {}


@hello.get()
def get_info(request):
    """Returns Hello in JSON."""
    return {'Hello': 'World'}


@resource(collection_path='/api/data_sources', path='/api/data_sources/{id}')
class DataSource(object):

    def __init__(self, request):
        self.request = request
        self.wms_sources = self.request.root['wms_sources']

    def collection_get(self):
        return {'wms_sources': list(self.wms_sources.keys())}

    @view(renderer='json')
    def get(self):
        # Should be a dict.
        return self.wms_sources.get(self.request.matchdict['id'])
