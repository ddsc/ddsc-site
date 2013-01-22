# (c) Nelen & Schuurmans.  MIT licensed, see LICENSE.rst.
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

import json

from rest_framework import generics, serializers
from lizard_wms.models import WMSSource


class WMSLayerSerializer(serializers.HyperlinkedModelSerializer):

    url = serializers.HyperlinkedIdentityField(view_name='layer-detail')

    styles = serializers.SerializerMethodField('get_styles')
    format = serializers.SerializerMethodField('get_format')
    height = serializers.SerializerMethodField('get_height')
    width = serializers.SerializerMethodField('get_width')
    tiled = serializers.SerializerMethodField('get_tiled')
    transparent = serializers.SerializerMethodField('get_transparent')
    wms_url = serializers.SerializerMethodField('get_wms_url')
    opacity = serializers.SerializerMethodField('get_opacity')

    def get_styles(self, obj):
        return obj._params['styles']

    def get_format(self, obj):
        return obj._params['format']

    def get_height(self, obj):
        return obj._params['height']

    def get_width(self, obj):
        return obj._params['width']

    def get_tiled(self, obj):
        return obj._params['tiled']

    def get_transparent(self, obj):
        return obj._params['transparent']

    def get_wms_url(self, obj):
        return obj.url

    def get_opacity(self, obj):
        options = obj.options
        if isinstance(options, basestring):
            options = json.loads(options)
        return options['opacity']

    class Meta:
        model = WMSSource
        fields = ('layer_name', 'display_name', 'url',
                  'description', 'metadata', 'legend_url', 'enable_search',
                  'styles', 'format', 'height', 'width', 'tiled',
                  'transparent', 'wms_url', 'opacity')


class LayerList(generics.ListCreateAPIView):
    model = WMSSource
    serializer_class = WMSLayerSerializer


class LayerDetail(generics.RetrieveUpdateDestroyAPIView):
    model = WMSSource
    serializer_class = WMSLayerSerializer
