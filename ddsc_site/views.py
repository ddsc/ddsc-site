# (c) Nelen & Schuurmans.  MIT licensed, see LICENSE.rst.
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

from django.conf import settings
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.filters import BaseFilterBackend

from lizard_wms.models import WMSSource

from ddsc_site import serializers
from ddsc_site.filters import objects_for_user_groups

from .serializers import WMSLayerSerializer
from .serializers import CollageSerializer, CollageItemSerializer
from .models import Collage, CollageItem, Workspace, WorkspaceItem


class GroupFilterBackend(BaseFilterBackend):
    DEFAULT_GROUP_FIELD = 'group'

    def filter_queryset(self, request, queryset, view):
        '''
        Returns a subset of the model instances, filtered on the groups the user is currently in.
        Instances with a null group are included as well.
        '''
        group_field = view.group_field if hasattr(view, 'group_field') else self.DEFAULT_GROUP_FIELD
        return objects_for_user_groups(view.model, request.user, queryset, group_field)


class CollageList(generics.ListCreateAPIView):
    model = Collage
    serializer_class = CollageSerializer
    filter_backend = GroupFilterBackend


class CollageDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Collage
    serializer_class = CollageSerializer
    filter_backend = GroupFilterBackend


class CollageItemList(generics.ListCreateAPIView):
    model = CollageItem
    serializer_class = CollageItemSerializer
    group_field = 'collage__group'
    filter_backend = GroupFilterBackend


class CollageItemDetail(generics.RetrieveUpdateDestroyAPIView):
    model = CollageItem
    serializer_class = CollageItemSerializer
    group_field = 'collage__group'
    filter_backend = GroupFilterBackend


class WorkspaceList(generics.ListCreateAPIView):
    model = Workspace
    serializer_class = serializers.WorkspaceListSerializer
    filter_backend = GroupFilterBackend
#    serializer_class_list = serializers.WorkspaceListSerializer
#    serializer_class_create = serializers.WorkspaceCreateSerializer
#
#    def get_serializer_class(self):
#        if self.request.method in ('POST', 'PUT'):
#            return self.serializer_class_create
#        else:
#            return self.serializer_class_list


class WorkspaceDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Workspace
    serializer_class = serializers.WorkspaceListSerializer
    filter_backend = GroupFilterBackend


class WorkspaceItemList(generics.ListCreateAPIView):
    model = WorkspaceItem
    serializer_class = serializers.WorkspaceItemSerializer
    group_field = 'workspace__group'
    filter_backend = GroupFilterBackend


class WorkspaceItemDetail(generics.RetrieveUpdateDestroyAPIView):
    model = WorkspaceItem
    serializer_class = serializers.WorkspaceItemSerializer
    group_field = 'workspace__group'
    filter_backend = GroupFilterBackend


class LayerList(generics.ListCreateAPIView):
    model = WMSSource
    serializer_class = WMSLayerSerializer


class LayerDetail(generics.RetrieveUpdateDestroyAPIView):
    model = WMSSource
    serializer_class = WMSLayerSerializer


class CurrentAccount(APIView):
    def get(self, request, format=None):
        """
        Return account information.
        """

        if request.user.is_authenticated():
            user = request.user
            data = {'authenticated': True,
                    'user': {'username': user.username,
                             'first_name': user.first_name,
                             'last_name': user.last_name}
                    }

        else:
            data = {'authenticated': False,
                    'user': {'username': '',
                             'first_name': '',
                             'last_name': ''}
                    }
        return Response(data)
