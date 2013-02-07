# (c) Nelen & Schuurmans.  MIT licensed, see LICENSE.rst.
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

from lizard_wms.models import WMSSource

from rest_framework import generics

from .serializers import WMSLayerSerializer
from .serializers import CollageSerializer, CollageItemSerializer
from .models import Collage, CollageItem


class CollageList(generics.ListCreateAPIView):
    model = Collage
    serializer_class = CollageSerializer


class CollageDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Collage
    serializer_class = CollageSerializer


class CollageItemList(generics.ListCreateAPIView):
    model = CollageItem
    serializer_class = CollageItemSerializer


class CollageItemDetail(generics.RetrieveUpdateDestroyAPIView):
    model = CollageItem
    serializer_class = CollageItemSerializer


class LayerList(generics.ListCreateAPIView):
    model = WMSSource
    serializer_class = WMSLayerSerializer


class LayerDetail(generics.RetrieveUpdateDestroyAPIView):
    model = WMSSource
    serializer_class = WMSLayerSerializer
