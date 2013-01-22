# (c) Nelen & Schuurmans.  MIT licensed, see LICENSE.rst.
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

from django.test import TestCase

from django.test.client import RequestFactory


class LayersTest(TestCase):

    def setUp(self):
        self.request = RequestFactory()

        from lizard_wms.tests import factories

        self.wms_connection = factories.WMSConnectionFactory.create()
        self.wms_source = factories.WMSSourceFactory.create(
            connection=self.wms_connection)

    def test_layer(self):
        from ddsc_site.views import LayerList as view
        instance = view.as_view()

        request = self.request.get('/layers/')
        instance(request)

    def test_serializer(self):
        from ddsc_site.views import WMSLayerSerializer as Serializer

        data = Serializer(self.wms_source).data

        keys = ['layer_name', 'display_name', 'url',
                'description', 'metadata', 'legend_url', 'enable_search',
                'styles', 'format', 'height', 'width', 'tiled',
                'transparent', 'wms_url', 'opacity', 'type', 'search_url']

        self.assertEquals(keys, data.keys())
        self.assertEquals('', data['styles'])
        self.assertEquals('wms', data['type'])
