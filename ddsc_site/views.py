# (c) Nelen & Schuurmans.  MIT licensed, see LICENSE.rst.
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

import logging
from urlparse import urlparse

from django.conf import settings
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ImproperlyConfigured
from django.views.decorators.gzip import gzip_page
from django.views.generic import View
from django.http import HttpResponse, HttpResponseForbidden

import requests

from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.settings import api_settings
from lizard_wms.models import WMSSource

from ddsc_site import serializers
from ddsc_site.filters import WorkspaceCollageFilterBackend
from ddsc_site.permissions import IsCreatorOrReadOnly

from .models import Collage, CollageItem, Workspace, WorkspaceItem, ProxyHostname


logger = logging.getLogger(__name__)

class FixedRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    '''
    Workaround for https://github.com/tomchristie/django-rest-framework/issues/682 .
    '''
    filter_backend = api_settings.FILTER_BACKEND

    def filter_queryset(self, queryset):
        """
        Given a queryset, filter it with whichever filter backend is in use.
        """
        if not self.filter_backend:
            return queryset
        backend = self.filter_backend()
        return backend.filter_queryset(self.request, queryset, self)

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)
        obj = super(FixedRetrieveUpdateDestroyAPIView, self).get_object(queryset)
        if not self.has_permission(self.request, obj):
            self.permission_denied(self.request)
        return obj

    def get_queryset(self):
        """
        Get the list of items for this view. This must be an interable, and may
        be a queryset (in which qs-specific behavior will be enabled).
        """
        if self.queryset is not None:
            queryset = self.queryset
            if hasattr(queryset, '_clone'):
                queryset = queryset._clone()
        elif self.model is not None:
            queryset = self.model._default_manager.all()
        else:
            raise ImproperlyConfigured(u"'%s' must define 'queryset' or 'model'"
                                       % self.__class__.__name__)
        return queryset


class ProxyUrlNotAllowed(Exception):
    pass


class ProxyView(View):
    '''
    View that proxies requests to external sources, like GeoServer.

    This allows external data to be shown in a clients browser
    due to the same-origin policy.

    Because of the danger of code injection, a whitelist of proxyable
    hostnames is kept in the ProxyHostname model.
    '''
    http_method_names = ['get', 'head']
    copy_headers = {
        'HTTP_ACCEPT': 'Accept',
        'HTTP_ACCEPT_LANGUAGE': 'Accept-Language',
        'HTTP_USER_AGENT': 'User-Agent',
    }
    allowed_schemes = ['http', 'https']

    def parse_url(self):
        url = self.request.GET.get('url', None)
        url_parsed = urlparse(url)
        if not url_parsed.scheme in self.allowed_schemes:
            raise ProxyUrlNotAllowed('Scheme {0} not allowed.'.format(url_parsed.scheme))
        hostname = url_parsed.hostname.lower()
        if not ProxyHostname.objects.filter(hostname=hostname).exists():
            raise ProxyUrlNotAllowed('Hostname {0} not in ProxyHostname table.'.format(hostname))
        return url

    def copy_request_headers(self):
        headers = {}
        for django_header, http_header in self.copy_headers.items():
            value = self.request.META.get(django_header, None)
            if value is not None:
                logger.debug('proxy: proxying header to actual server: %s: %s', http_header, value)
                headers[http_header] = value
        return headers

    def translate_to_wsgi_response(self, proxied_response):
        response = HttpResponse()
        response.status_code = proxied_response.status_code
        # Copy response headers to the response we send to the client.
        for header, value in proxied_response.headers.items():
            if header.lower() == 'content-encoding':
                # Gzipped content is already decompressed by the Python
                # requests library. Don't pass this header.
                continue
            logger.debug('proxy: got header from actual server: %s: %s', header, value)
            response[header] = value
        response.content = proxied_response.content
        return response

    def _handle(self, request, requestsmethod, *args, **kwargs):
        # Parse requested URL and disallow unknown sites.
        try:
            url = self.parse_url()
        except ProxyUrlNotAllowed as e:
            return HttpResponseForbidden(e.message)
        # Copy a subset of headers from the current request.
        headers = self.copy_request_headers()
        # Perform the call to the actual server.
        proxied_response = requestsmethod(
            url,
            allow_redirects=True,
            headers=headers
        )
        # Translate requests response to a Django compatible one.
        response = self.translate_to_wsgi_response(proxied_response)
        logger.debug('proxy: proxied %s bytes from %s', len(response.content), url)
        # Send the data.
        return response

    def get(self, request, *args, **kwargs):
        return self._handle(request, requests.get, *args, **kwargs)

    def head(self, request, *args, **kwargs):
        return self._handle(request, requests.head, *args, **kwargs)


class CollageList(generics.ListCreateAPIView):
    model = Collage
    serializer_class = serializers.CollageListSerializer
    filter_backend = WorkspaceCollageFilterBackend


class CollageDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Collage
    serializer_class = serializers.CollageListSerializer
    filter_backend = WorkspaceCollageFilterBackend


class CollageItemList(generics.ListCreateAPIView):
    model = CollageItem
    serializer_class = serializers.CollageItemSerializer
    filter_field_prefix = 'collage__'
    filter_backend = WorkspaceCollageFilterBackend


class CollageItemDetail(generics.RetrieveUpdateDestroyAPIView):
    model = CollageItem
    serializer_class = serializers.CollageItemSerializer
    filter_field_prefix = 'collage__'
    filter_backend = WorkspaceCollageFilterBackend


class WorkspaceList(generics.ListCreateAPIView):
    model = Workspace
    serializer_class = serializers.WorkspaceListSerializer
    filter_backend = WorkspaceCollageFilterBackend
    permission_classes = (
        IsCreatorOrReadOnly,
    )

    def pre_save(self, obj):
        obj.creator = self.request.user

#    def get(self, request, *args, **kwargs):

#    serializer_class_list = serializers.WorkspaceListSerializer
#    serializer_class_create = serializers.WorkspaceCreateSerializer
#
#    def get_serializer_class(self):
#        if self.request.method in ('POST', 'PUT'):
#            return self.serializer_class_create
#        else:
#            return self.serializer_class_list


class WorkspaceDetail(FixedRetrieveUpdateDestroyAPIView):
    model = Workspace
    serializer_class = serializers.WorkspaceListSerializer
    filter_backend = WorkspaceCollageFilterBackend
    permission_classes = (
        IsCreatorOrReadOnly,
    )

    def pre_save(self, obj):
        obj.creator = self.request.user

class WorkspaceItemList(generics.ListCreateAPIView):
    model = WorkspaceItem
    serializer_class = serializers.WorkspaceItemSerializer
    filter_field_prefix = 'workspace__'
    filter_backend = WorkspaceCollageFilterBackend
    permission_classes = (
        IsCreatorOrReadOnly,
    )


class WorkspaceItemDetail(FixedRetrieveUpdateDestroyAPIView):
    model = WorkspaceItem
    serializer_class = serializers.WorkspaceItemSerializer
    filter_field_prefix = 'workspace__'
    filter_backend = WorkspaceCollageFilterBackend
    permission_classes = (
        IsCreatorOrReadOnly,
    )


class LayerList(generics.ListCreateAPIView):
    model = WMSSource
    serializer_class = serializers.WMSLayerSerializer


class LayerDetail(generics.RetrieveUpdateDestroyAPIView):
    model = WMSSource
    serializer_class = serializers.WMSLayerSerializer


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
