# (c) Nelen & Schuurmans.  MIT licensed, see LICENSE.rst.
from django.conf.urls.defaults import include
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from django.contrib import admin
from lizard_ui.urls import debugmode_urlpatterns

from ddsc_site import views

admin.autodiscover()

urlpatterns = patterns(
    '',

    url(r'^v0/collages/$', views.CollageList.as_view(), name='collage-list'),
    url(r'^v0/collages/(?P<pk>\d+)/$', views.CollageDetail.as_view(),
        name='collage-detail'),

    url(r'^v0/collageitems/$', views.CollageItemList.as_view(),
        name='collageitem-list'),
    url(r'^v0/collageitem-detal/(?P<pk>\d+)/$',
        views.CollageItemDetail.as_view(),
        name='collageitem-detail'),

    url(r'^v0/layers/$', views.LayerList.as_view(), name='layer-list'),
    url(r'^v0/layers/(?P<pk>\d+)/$', views.LayerDetail.as_view(),
        name='layer-detail'),

    url(r'^admin/', include(admin.site.urls)),
)
urlpatterns += debugmode_urlpatterns()
