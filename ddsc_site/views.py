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
from django.core.paginator import Paginator

import requests
from haystack.utils.geo import generate_bounding_box, Point
from haystack.query import SQ, SearchQuerySet, RelatedSearchQuerySet
import dateutil.parser

from rest_framework import generics, permissions, pagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.settings import api_settings
from lizard_wms.models import WMSSource

from ddsc_site import serializers
from ddsc_site.filters import WorkspaceCollageFilterBackend
from ddsc_site.permissions import IsCreatorOrReadOnly

from ddsc_site.models import (
    Collage,
    CollageItem,
    Workspace,
    WorkspaceItem,
    ProxyHostname,
    Annotation,
    Visibility
)


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


class WorkspaceDetail(generics.RetrieveUpdateDestroyAPIView): #FixedRetrieveUpdateDestroyAPIView):
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


class WorkspaceItemDetail(generics.RetrieveUpdateDestroyAPIView): #FixedRetrieveUpdateDestroyAPIView):
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


def filter_annotations(request, sqs):
    # category
    category = request.GET.get('category')
    if category:
        sqs = sqs.filter(category__exact=category)
    # location
    bbox = request.GET.get('bbox')
    bottom_left = request.GET.get('bottom_left')
    top_right = request.GET.get('top_right')
    north = request.GET.get('north')
    east = request.GET.get('east')
    south = request.GET.get('south')
    west = request.GET.get('west')
    if bbox:
        if bbox == 'test':
            bottom_left = '-79.23592948913574', '43.97127105172941'
            top_right = '-82.23592948913574', '46.97127105172941'
        else:
            # lon_min, lat_min, lon_max, lat_max
            # west, south, east, north
            x_min, y_min, x_max, y_max = bbox.split(',')
            bottom_left = y_min, x_min
            top_right = y_max, x_max
    elif bottom_left and top_right:
        bottom_left = bottom_left.split(',')
        top_right = top_right.split(',')
    elif north and east and south and west:
        bottom_left = south, west
        top_right = north, east
    else:
        bottom_left = None
        top_right = None
    if bottom_left and top_right:
        bottom_left = Point(float(bottom_left[0]), float(bottom_left[1]))
        top_right = Point(float(top_right[0]), float(top_right[1]))
        sqs = sqs.within('location', bottom_left, top_right)
    # user
    username = request.user.username
    # allow username overriding in DEBUG mode
    # this is a possible security leak
    username_override = request.GET.get('username_override')
    if settings.DEBUG and username_override:
        username = username_override
    sqs = sqs.filter(
        SQ(username__exact=username, visibility=Visibility.PRIVATE) |
        SQ(visibility=Visibility.PUBLIC)
    )
    # relation to model instances
    the_model_name = request.GET.get('model_name')
    the_model_pk = request.GET.get('model_pk')
    if the_model_name and the_model_pk:
        sqs = sqs.filter(the_model_name__exact=the_model_name, the_model_pk__exact=the_model_pk)
    # date range
    datetime_from = request.GET.get('datetime_from')
    if datetime_from:
        datetime_from = dateutil.parser.parse(datetime_from)
        sqs = sqs.filter(datetime_from__gte=datetime_from)
    datetime_until = request.GET.get('datetime_until')
    if datetime_until:
        datetime_until = dateutil.parser.parse(datetime_until)
        sqs = sqs.filter(datetime_until__lte=datetime_until)
    # full text
    text = request.GET.get('text')
    if text:
        sqs = sqs.filter(text__contains=text)
    tags = request.GET.get('tags')
    if tags:
        sqs = sqs.filter(tags__contains=tags)

    return sqs


class AnnotationsSearchView(generics.ListAPIView):
    model = Annotation
    serializer_class = serializers.AnnotationSerializer
    # effectively disable pagination,
    # but stick to the same response format
    paginate_by = 10000

    def get_queryset(self):
        sqs = SearchQuerySet().models(Annotation)
        sqs = filter_annotations(self.request, sqs)
        return sqs


class AnnotationsCountView(APIView):
    def get(self, request, *args, **kwargs):
        sqs = SearchQuerySet().models(Annotation)
        sqs = filter_annotations(self.request, sqs)
        result = {
            'count': sqs.count()
        }
        return Response(result)


class AnnotationsCreateView(APIView):
    def post(self, request, format=None):
        # TODO: implement me
        pass
