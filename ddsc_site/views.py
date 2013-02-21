# (c) Nelen & Schuurmans.  MIT licensed, see LICENSE.rst.
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse

from lizard_wms.models import WMSSource

from lizard_auth_client.views import get_sso_request

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


class CurrentAccount(APIView):

    def get(self, request, format=None):
        """
        Return account information.
        """

        data = {}
        data['login_url'] = reverse('ddsc_site.sso-login', request=request)

        if request.user.is_authenticated():
            user = request.user

            data['authenticated'] = True
            data['user'] = {'username': user.username,
                            'first_name': user.first_name,
                            'last_name': user.last_name}

        else:
            data['authenticated'] = False
            data['user'] = {'username': '',
                            'first_name': '',
                            'last_name': ''}

        return Response(data)


class SSOLogin(APIView):

    def get(self, request, format=None):

        request.session['sso_after_login_next'] = 'http://localhost:8000'
        import pdb; pdb.set_trace()
        print(request.COOKIES['sessionid'])
        sso_request = get_sso_request()
        if sso_request.status_code == 302:
            login_url = sso_request.message
            return Response({'login_url': login_url})
        return Response({'message': sso_request.message},
                        status=sso_request.status_code)
