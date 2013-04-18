# (c) Nelen & Schuurmans.  MIT licensed, see LICENSE.rst.
from django.conf.urls.defaults import include
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from django.contrib import admin
from django.conf import settings
from lizard_ui.urls import debugmode_urlpatterns

from ddsc_site import views
from lizard_auth_client.views import LoginApiView, LogoutApiView

admin.autodiscover()

urlpatterns = patterns(
    '',

    url(r'^v1/collages/?$', views.CollageList.as_view(), name='collage-list'),
    url(r'^v1/collages/(?P<pk>\d+)/?$', views.CollageDetail.as_view(),
        name='collage-detail'),
    url(r'^v1/collages/create/?$', views.CollageCreate.as_view(), name='collage-create'),

    url(r'^v1/collageitems/?$', views.CollageItemList.as_view(),
        name='collageitem-list'),
    url(r'^v1/collageitems/(?P<pk>\d+)/?$',
        views.CollageItemDetail.as_view(),
        name='collageitem-detail'),
    url(r'^v1/collageitems/create/?$', views.CollageItemCreate.as_view(), name='collageitem-create'),

    url(r'^v1/workspaces/?$', views.WorkspaceList.as_view(), name='workspace-list'),
    url(r'^v1/workspaces/(?P<pk>\d+)/?$', views.WorkspaceDetail.as_view(),
        name='workspace-detail'),

    url(r'^v1/workspaceitems/?$', views.WorkspaceItemList.as_view(),
        name='workspaceitem-list'),
    url(r'^v1/workspaceitems/(?P<pk>\d+)/?$',
        views.WorkspaceItemDetail.as_view(),
        name='workspaceitem-detail'),

    url(r'^v1/layers/?$', views.LayerList.as_view(), name='layer-list'),
    url(r'^v1/layers/(?P<pk>\d+)/?$', views.LayerDetail.as_view(),
        name='layer-detail'),

    url(r'^v1/account/?$', views.CurrentAccount.as_view(), name='account'),
    url(r'^v1/account/login-url/?$', LoginApiView.as_view(),
        name='ddsc_site.sso-login'),
    url(r'^v1/account/logout-url/?$', LogoutApiView.as_view(),
        name='ddsc_site.sso-logout'),

    url(r'^v1/proxy/?$', views.ProxyView.as_view(), name='proxy'),

    url(r'^v1/annotations/search/$', views.AnnotationsSearchView.as_view(), name='annotations-search'),
    url(r'^v1/annotations/detail/(?P<pk>\d+)/?$', 
        views.AnnotationsDetailView.as_view(), name='annotations-detail'),
    url(r'^v1/annotations/count/$',  views.AnnotationsCountView.as_view(),  name='annotations-count'),
    url(r'^v1/annotations/create/$', views.AnnotationsCreateView.as_view(), name='annotations-create'),
    url(r'^', include('lizard_auth_client.urls')),
)
urlpatterns += debugmode_urlpatterns()


if settings.DEBUG is True:
    urlpatterns += patterns(
        '',
        url(r'^admin/', include(admin.site.urls)),
    )
