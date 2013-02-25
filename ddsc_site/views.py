# (c) Nelen & Schuurmans.  MIT licensed, see LICENSE.rst.
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

from django.conf import settings

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response

from lizard_wms.models import WMSSource

from lizard_auth_client.views import get_sso_request, get_sso_logout

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


class SSOLogin(APIView):

    def get(self, request, format=None):
        # Redirect to the webclient after the SSO server dance
        request.session['sso_after_login_next'] = settings.WEBCLIENT

        # Get the login url with the token
        sso_request = get_sso_request()

        # The response is a redirect (302) to the SSO server
        if sso_request.status_code == 302:
            login_url = sso_request.message
            return Response({'login_url': login_url})

        # Return the error message to the user
        return Response({'message': sso_request.message},
                        status=sso_request.status_code)


class SSOLogout(APIView):
    def get(self, request, format=None):
        # Redirect to the webclient after the SSO server dance
        request.session['sso_after_logout_next'] = settings.WEBCLIENT

        logout_url = get_sso_logout()
        return Response({'logout_url': logout_url})
