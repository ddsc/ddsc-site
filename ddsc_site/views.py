# (c) Nelen & Schuurmans.  MIT licensed, see LICENSE.rst.
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

from lizard_wms.models import WMSSource

from rest_framework import generics

from .serializer import WMSLayerSerializer
from .models import Collage, CollageItem


class CollageList(generics.ListCreateAPIView):
    model = Collage


class CollageDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Collage


class CollageItemList(generics.ListCreateAPIView):
    model = CollageItem


class CollageItemDetail(generics.RetrieveUpdateDestroyAPIView):
    model = CollageItem


class LayerList(generics.ListCreateAPIView):
    model = WMSSource
    serializer_class = WMSLayerSerializer


class LayerDetail(generics.RetrieveUpdateDestroyAPIView):
    model = WMSSource
    serializer_class = WMSLayerSerializer
