# (c) Nelen & Schuurmans.  MIT licensed, see LICENSE.rst.
from django.conf.urls.defaults import include
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from django.contrib import admin
from django.conf import settings
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
    url(r'^v0/collageitems/(?P<pk>\d+)/$',
        views.CollageItemDetail.as_view(),
        name='collageitem-detail'),

    url(r'^v0/workspaces/$', views.WorkspaceList.as_view(), name='workspace-list'),
    url(r'^v0/workspaces/(?P<pk>\d+)/$', views.WorkspaceDetail.as_view(),
        name='workspace-detail'),

    url(r'^v0/workspaceitems/$', views.WorkspaceItemList.as_view(),
        name='workspaceitem-list'),
    url(r'^v0/workspaceitems/(?P<pk>\d+)/$',
        views.WorkspaceItemDetail.as_view(),
        name='workspaceitem-detail'),

    url(r'^v0/layers/$', views.LayerList.as_view(), name='layer-list'),
    url(r'^v0/layers/(?P<pk>\d+)/$', views.LayerDetail.as_view(),
        name='layer-detail'),

    url(r'^v0/account/$', views.CurrentAccount.as_view(), name='account'),
    url(r'^v0/account/login-url/$', views.SSOLogin.as_view(),
        name='ddsc_site.sso-login'),

    url(r'^v0/account/$', views.CurrentAccount.as_view(), name='account'),
    url(r'^v0/account/login-url/$', views.SSOLogin.as_view(),
        name='ddsc_site.sso-login'),
    url(r'^v0/account/logout-url/$', views.SSOLogout.as_view(),
        name='ddsc_site.sso-logout'),

)
urlpatterns += debugmode_urlpatterns()


if settings.DEBUG is True:
    urlpatterns += patterns(
        '',

        url(r'^', include('lizard_auth_client.urls')),
        url(r'^admin/', include(admin.site.urls)),
    )
