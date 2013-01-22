# (c) Nelen & Schuurmans.  MIT licensed, see LICENSE.rst.

from django.test import TestCase

from django.test.client import RequestFactory


class LayersTest(TestCase):
    def setUp(self):
        self.request = RequestFactory()

        from lizard_wms.tests.factories import WMSSourceFactory
        self.wms_source = WMSSourceFactory.create()

    def test_layer(self):
        from ddsc_site.views import LayerList as view
        instance = view.as_view()

        request = self.request.get('/layers/')
        instance(request)

    def test_serializer(self):
        from ddsc_site.views import WMSLayerSerializer as Serializer
        data = Serializer(self.wms_source)
        data.data
