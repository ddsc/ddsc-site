# (c) Nelen & Schuurmans.  MIT licensed, see LICENSE.rst.
from django.conf.urls.defaults import include
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from django.contrib import admin
from lizard_ui.urls import debugmode_urlpatterns

from .views import LayerList, LayerDetail

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^v0/layers/$', LayerList.as_view(), name='layer-list'),
    url(r'^v0/layers/(?P<pk>\d+)/$', LayerDetail.as_view(),
        name='layer-detail'),
    url(r'^v0/layers/(?P<pk>\d+)/search/$', LayerDetail.as_view(),
        name='layer-search'),

    url(r'^admin/', include(admin.site.urls)),
)
urlpatterns += debugmode_urlpatterns()
