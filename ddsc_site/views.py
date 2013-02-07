# (c) Nelen & Schuurmans.  MIT licensed, see LICENSE.rst.
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

from lizard_wms.models import WMSSource

from rest_framework import generics

from .serializers import WMSLayerSerializer
from .serializers import CollageSerializer
from .models import Collage


class CollageList(generics.ListCreateAPIView):
    model = Collage
    serializer_class = CollageSerializer


class CollageDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Collage
    serializer_class = CollageSerializer


class LayerList(generics.ListCreateAPIView):
    model = WMSSource
    serializer_class = WMSLayerSerializer


class LayerDetail(generics.RetrieveUpdateDestroyAPIView):
    model = WMSSource
    serializer_class = WMSLayerSerializer
