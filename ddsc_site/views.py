# (c) Nelen & Schuurmans.  MIT licensed, see LICENSE.rst.
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

import logging
import urlparse
import urllib
import os
import mimetypes

from django.core.exceptions import ImproperlyConfigured
from django.views.generic import View
from django.http import HttpResponse, HttpResponseForbidden, Http404
from django.core.exceptions import ValidationError
from django import forms
from django.utils import simplejson
from django.shortcuts import get_object_or_404
from django.core.servers.basehttp import FileWrapper
from django.contrib.gis.geos import Point
from django.db.models.fields import FieldDoesNotExist

import requests
from pkginfo.installed import Installed
from haystack.query import SQ, SearchQuerySet
import dateutil.parser

from rest_framework import generics, permissions, authentication
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
    AnnotationAttachment,
    Visibility,
    UserProfile
)


logger = logging.getLogger(__name__)


class NoCsrfSessionAuthentication(authentication.BaseAuthentication):
    """
    Use Django's session framework for authentication.
    """

    def authenticate(self, request):
        """
        Returns a `User` if the request session currently has a logged in user.
        Otherwise returns `None`.
        """

        # Get the underlying HttpRequest object
        http_request = request._request
        user = getattr(http_request, 'user', None)

        # Unauthenticated, CSRF validation not required
        if not user or not user.is_active:
            return None

        # CSRF code removed due to POST'ing from another site

        # CSRF passed with authenticated user
        return (user, None)


class FixedRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    '''
    Workaround for
    https://github.com/tomchristie/django-rest-framework/issues/682 .
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
        obj = super(
            FixedRetrieveUpdateDestroyAPIView, self).get_object(queryset)
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
            raise ImproperlyConfigured(
                u"'%s' must define 'queryset' or 'model'"
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

    def parse_url(self, url):
        url_parsed = urlparse.urlparse(url)
        if not url_parsed.scheme in self.allowed_schemes:
            raise ProxyUrlNotAllowed(
                'Scheme {0} not allowed.'.format(url_parsed.scheme))
        hostname = url_parsed.hostname.lower()
        if not ProxyHostname.objects.filter(hostname=hostname).exists():
            raise ProxyUrlNotAllowed(
                'Hostname {0} not in ProxyHostname table.'.format(hostname))
        # Add authentication details
        parts = list(url_parsed)
        if self.request.user.is_authenticated():
            qs_dict = urlparse.parse_qs(parts[4], keep_blank_values=True)
            qs_dict['viewparams'] = 'usr:{0}'.format(
                self.request.user.username)
            parts[4] = urllib.urlencode(qs_dict, doseq=True)
        return urlparse.urlunparse(parts)

    def copy_request_headers(self):
        headers = {}
        for django_header, http_header in self.copy_headers.items():
            value = self.request.META.get(django_header, None)
            if value is not None:
                logger.debug(
                    'proxy: proxying header to actual server: %s: %s',
                    http_header, value)
                headers[http_header] = value
        return headers

    def translate_to_wsgi_response(self, proxied_response):
        response = HttpResponse()
        response.status_code = proxied_response.status_code
        # Copy response headers to the response we send to the client.
        for header, value in proxied_response.headers.items():
            if header.lower() in ['content-encoding', 'content-length']:
                # Gzipped content is already decompressed by the Python
                # requests library. Don't pass this header.
                # Also have Django calculate Content-Length.
                continue
            logger.debug(
                'proxy: got header from actual server: %s: %s', header, value)
            response[header] = value
        response.content = proxied_response.content
        return response

    def _handle(self, request, requestsmethod, urlbase=None, **kwargs):
        # Parse requested URL and disallow unknown sites.
        try:
            if urlbase is None:
                url = self.request.GET.get('url', None)
            else:
                if request.META['QUERY_STRING']:
                    url = urlbase + '?' + request.META['QUERY_STRING']
                else:
                    url = urlbase
            url = self.parse_url(url)
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
        logger.debug(
            'proxy: proxied %s bytes from %s', len(response.content), url)
        # Send the data.
        return response

    def get(self, request, *args, **kwargs):
        return self._handle(request, requests.get, *args, **kwargs)

    def head(self, request, *args, **kwargs):
        return self._handle(request, requests.head, *args, **kwargs)


class CollageList(generics.ListAPIView):
    model = Collage
    serializer_class = serializers.CollageListSerializer
    filter_backend = WorkspaceCollageFilterBackend


class CollageCreate(generics.CreateAPIView):
    authentication_classes = (NoCsrfSessionAuthentication,)
    model = Collage
    serializer_class = serializers.CollageCreateSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, IsCreatorOrReadOnly)
    filter_backend = WorkspaceCollageFilterBackend

    def pre_save(self, obj):
        obj.creator = self.request.user


class CollageDetail(generics.RetrieveDestroyAPIView):
    authentication_classes = (NoCsrfSessionAuthentication,)
    model = Collage
    serializer_class = serializers.CollageListSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, IsCreatorOrReadOnly)
    filter_backend = WorkspaceCollageFilterBackend


class CollageItemList(generics.ListAPIView):
    model = CollageItem
    serializer_class = serializers.CollageItemSerializer
    filter_field_prefix = 'collage__'
    filter_backend = WorkspaceCollageFilterBackend


class CollageItemCreate(generics.CreateAPIView):
    authentication_classes = (NoCsrfSessionAuthentication,)
    model = CollageItem
    serializer_class = serializers.CollageItemCreateSerializer
    permission_classes = (permissions.IsAuthenticated, IsCreatorOrReadOnly)
    filter_field_prefix = 'collage__'
    filter_backend = WorkspaceCollageFilterBackend


class CollageItemDetail(generics.RetrieveAPIView):
    authentication_classes = (NoCsrfSessionAuthentication,)
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


class WorkspaceDetail(generics.RetrieveUpdateDestroyAPIView):
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


class WorkspaceItemDetail(generics.RetrieveUpdateDestroyAPIView):
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
    authentication_classes = (NoCsrfSessionAuthentication,)

    def get(self, request, format=None):
        """
        Return account information.
        """

        if request.user.is_authenticated():
            user = request.user
            profile = UserProfile.get_or_create_profile(user)
            data = {'authenticated': True,
                    'user': {'username': user.username,
                             'first_name': user.first_name,
                             'last_name': user.last_name},
                    'initialPeriod': profile.initial_period,
                    'initialZoom': profile.initial_zoom,
                    'panner': profile.panner
                    }
        else:
            data = {'authenticated': False,
                    'user': {'username': 'n.v.t.',
                             'first_name': 'n.v.t.',
                             'last_name': 'n.v.t.'},
                    'initialPeriod': '',
                    'initialZoom': '',
                    'panner': False
                    }
        return Response(data)

    def post(self, request, format=None):
        if request.user.is_authenticated():
            user = request.user
            profile = UserProfile.get_or_create_profile(user)
            profile.initial_period = request.DATA.get('initialPeriod')
            profile.initial_zoom = request.DATA.get('initialZoom')
            profile.panner = request.DATA.get('panner')
            try:
                profile.full_clean()
                profile.save()
            except ValidationError as ex:
                data = {'result': 'error', 'detail': '; '.join(ex.messages)}
                status = 400
            else:
                data = {'result': 'ok'}
                status = 200
        else:
            data = {'result': 'error', 'detail': 'not logged in'}
            status = 400
        return Response(data, status=status)


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
            bottom_left = '48.0', '4.0'
            top_right = '52.0', '10.0'
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
    # As decided during the UAT on 2014-09-09: no more private annotations,
    # all annotations will be public. Hence, we don't need filtering.
    ### user
    ##username = request.user.username
    ### allow username overriding in DEBUG mode
    ### this is a possible security leak
    ##username_override = request.GET.get('username_override')
    ##if settings.DEBUG and username_override:
    ##    username = username_override
    ##sqs = sqs.filter(
    ##    # either private and linked to the current user
    ##    SQ(username__exact=username, visibility=Visibility.PRIVATE) |
    ##    # or public
    ##    SQ(visibility=Visibility.PUBLIC)
    ##)
    # relation to model instances
    the_model_name = request.GET.get('model_name')
    the_model_pk = request.GET.get('model_pk')
    if the_model_name and the_model_pk:
        sqs = sqs.filter(
            the_model_name__exact=the_model_name,
            the_model_pk__exact=the_model_pk)
    else:
        # allow multiple models and pks
        model_names_pks = request.GET.get('model_names_pks')
        if model_names_pks:
            model_names_pks = model_names_pks.split(';')
            sq = SQ()
            for model_name_pk in model_names_pks:
                model_name, model_pk = model_name_pk.split(',')
                sq.add(
                    SQ(the_model_name__exact=model_name,
                       the_model_pk__exact=model_pk),
                    SQ.OR)
            sqs = sqs.filter(sq)
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


class AnnotationsCreateView(generics.CreateAPIView):
    model = Annotation
    serializer_class = serializers.AnnotationCreateSerializer
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (NoCsrfSessionAuthentication,)

    def pre_save(self, obj):
        obj.username = self.request.user.username

    def post_save(self, obj, created):
        attachment_pk = self.request.POST.get('attachment_pk')
        if attachment_pk:
            try:
                attachment = AnnotationAttachment.objects.get(pk=attachment_pk)
                attachment.annotation = obj
                attachment.save()
            except AnnotationAttachment.DoesNotExist:
                pass
        # Copy location coordinates of anything related to a Location
        if obj.the_model_name:
            related_model = obj.get_related_model()
            if related_model:
                try:
                    if (related_model._meta.get_field('point_geometry')
                        and related_model.point_geometry):
                        coords = related_model.point_geometry.coords
                        obj.location = Point(
                            coords[0],
                            coords[1],
                            srid=4326
                        )
                        obj.save()
                except FieldDoesNotExist:
                    pass


class AnnotationsDetailView(generics.RetrieveUpdateDestroyAPIView):
    model = Annotation
    serializer_class = serializers.AnnotationDetailSerializer
    permission_classes = (permissions.IsAuthenticated, IsCreatorOrReadOnly)
    authentication_classes = (NoCsrfSessionAuthentication,)

    def post_save(self, obj, created):
        attachment_pk = self.request.POST.get('attachment_pk')
        if attachment_pk:
            try:
                attachment = AnnotationAttachment.objects.get(pk=attachment_pk)
                attachment.annotation = obj
                attachment.save()
            except AnnotationAttachment.DoesNotExist:
                pass


class AnnotationsFileForm(forms.Form):
    attachment = forms.FileField(required=True)

    def clean_attachment(self):
        attachment = self.cleaned_data.get('attachment')
        if attachment:
            if attachment._size > 10 * 1024 * 1024:
                raise ValidationError("File too large ( > 10mb )")
            return attachment


class AnnotationsFileView(APIView):
    authentication_classes = (NoCsrfSessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk=None, filename=None, **kwargs):
        '''
        Note: this won't work with GzipMiddleware, which some whatever reason
        can't be disable per view.
        '''

        attachment = get_object_or_404(AnnotationAttachment, pk=pk)
        if attachment.annotation:
            if attachment.annotation.visibility == Visibility.PRIVATE:
                if request.user.username != attachment.annotation.username:
                    raise Http404('Attachment not found.')

        path = attachment.path()
        file_url = urllib.pathname2url(path)
        content_type = mimetypes.guess_type(file_url)[0]

        response = HttpResponse(
            content=FileWrapper(open(path, 'rb')),
            content_type=content_type
        )
        response['Content-Length'] = os.path.getsize(path)
        return response

    def post(self, request, *args, **kwargs):
        form = AnnotationsFileForm(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.cleaned_data['attachment']

            # create the model containing metadata
            attachment_model = AnnotationAttachment(
                name=attachment.name,
                creator=request.user
            )
            attachment_model.save()

            # write the uploaded file to disk
            with open(attachment_model.path(), 'wb+') as destination:
                for chunk in attachment.chunks():
                    destination.write(chunk)

            # determine the response
            data = {
                'success': True,
                'filename': attachment_model.name,
                'url': attachment_model.absurl(request),
                'attachment_pk': attachment_model.pk,
            }
            status = 200
        else:
            data = {'success': False, 'errors': form.errors}
            status = 200  # Keep this 200

        # Yes, we need to use text/plain for this to support IE9.
        # return Response(data, status=status)
        return HttpResponse(
            content=simplejson.dumps(data),
            status=status, content_type='text/plain')


class VersionView(APIView):
    def get(self, request, format=None):
        # Only import ddsc_api here so that ddsc_site can be tested on its
        # own, as long as this view isn't called.
        import ddsc_api
        response = {'version': Installed(ddsc_api).version}

        return Response(response)
