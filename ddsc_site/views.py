# (c) Nelen & Schuurmans.  MIT licensed, see LICENSE.rst.
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

from lizard_wms.models import WMSSource

from rest_framework import generics

from ddsc_site import serializers
from ddsc_site.filters import objects_for_user_groups

from .serializers import WMSLayerSerializer
from .serializers import CollageSerializer, CollageItemSerializer
from .models import Collage, CollageItem, Workspace, WorkspaceItem


class GroupFilterMixin(object):
    group_field = 'group'

    def get_queryset(self):
        '''
        Returns a subset of the model instances, filtered on the groups the user is currently in.
        Instances with a null group are included as well.
        '''
        return objects_for_user_groups(self.model, self.request.user, self.group_field)


class CollageList(GroupFilterMixin, generics.ListCreateAPIView):
    model = Collage
    serializer_class = CollageSerializer


class CollageDetail(GroupFilterMixin, generics.RetrieveUpdateDestroyAPIView):
    model = Collage
    serializer_class = CollageSerializer


class CollageItemList(GroupFilterMixin, generics.ListCreateAPIView):
    model = CollageItem
    serializer_class = CollageItemSerializer
    group_field = 'collage__group'


class CollageItemDetail(GroupFilterMixin, generics.RetrieveUpdateDestroyAPIView):
    model = CollageItem
    serializer_class = CollageItemSerializer
    group_field = 'collage__group'


class WorkspaceList(GroupFilterMixin, generics.ListCreateAPIView):
    model = Workspace
    serializer_class = serializers.WorkspaceListSerializer
#    serializer_class_list = serializers.WorkspaceListSerializer
#    serializer_class_create = serializers.WorkspaceCreateSerializer
#
#    def get_serializer_class(self):
#        if self.request.method in ('POST', 'PUT'):
#            return self.serializer_class_create
#        else:
#            return self.serializer_class_list


class WorkspaceDetail(GroupFilterMixin, generics.RetrieveUpdateDestroyAPIView):
    model = Workspace
    serializer_class = serializers.WorkspaceListSerializer


class WorkspaceItemList(GroupFilterMixin, generics.ListCreateAPIView):
    model = WorkspaceItem
    serializer_class = serializers.WorkspaceItemSerializer
    group_field = 'workspace__group'


class WorkspaceItemDetail(GroupFilterMixin, generics.RetrieveUpdateDestroyAPIView):
    model = WorkspaceItem
    serializer_class = serializers.WorkspaceItemSerializer
    group_field = 'workspace__group'


class LayerList(generics.ListCreateAPIView):
    model = WMSSource
    serializer_class = WMSLayerSerializer


class LayerDetail(generics.RetrieveUpdateDestroyAPIView):
    model = WMSSource
    serializer_class = WMSLayerSerializer
