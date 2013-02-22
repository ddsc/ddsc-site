# (c) Nelen & Schuurmans.  MIT licensed, see LICENSE.rst.
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

from django.db import models
from django.contrib.auth.models import Group, User
from django.contrib.gis.geos import GEOSGeometry
from lizard_wms.models import WMSSource

from jsonfield.fields import JSONField


class Visibility:
    PRIVATE = 1
    USERGROUPS = 2
    PUBLIC = 3

VISIBILITY_CHOICES = (
    (Visibility.PRIVATE, 'private'),
    (Visibility.USERGROUPS, 'usergroups'),
    (Visibility.PUBLIC, 'public'),
)

class Collage(models.Model):
    """Collages."""

    name = models.CharField(max_length=100, null=False, blank=False)
    visibility = models.SmallIntegerField(default=1, choices=VISIBILITY_CHOICES)
    creator = models.ForeignKey(User)

    def __unicode__(self):
        return "Collage {0}".format(self.name)


class CollageItem(models.Model):
    """Collage Items."""

    collage = models.ForeignKey(Collage)
    graph_index = models.IntegerField(null=False, blank=False)
    timeseries = JSONField(null=True, blank=True, default=[])

    def __unicode__(self):
        timeseries_len = 0
        if isinstance(self.timeseries, list):
            timeseries_len = len(self.timeseries)

        return 'Collage: {}, Graph: {}, {} timeseries'.format(
            self.collage, self.graph_id, timeseries_len)


class Workspace(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    visibility = models.SmallIntegerField(default=1, choices=VISIBILITY_CHOICES)
    creator = models.ForeignKey(User)
    lon_lat_zoom = models.CharField(max_length=255, null=True, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ('order',)

    def __unicode__(self):
        return "Workspace {0}".format(self.name)


class WorkspaceItem(models.Model):
    workspace = models.ForeignKey(Workspace)
    order = models.IntegerField(default=0)
    wms_source = models.ForeignKey(WMSSource)
    visibility = models.BooleanField(default=True)

    class Meta:
        ordering = ('order',)

    def __unicode__(self):
        return "WorkspaceItem {0} in {1}".format(self.pk, self.workspace.name)


class ProxyHostname(models.Model):
    '''
    Table which is used to check whether or not a hostname
    is allowed to be proxied in the /api/v0/proxy/?url=url API.
    '''
    name = models.CharField(
        max_length=255, null=True, blank=True,
        help_text='Optional name of the site, to identify why it needs to be proxied.'
    )
    hostname = models.CharField(
        max_length=255, null=False, blank=False,
        help_text='Hostname of the site that needs to be proxyable.'
    )

    def __unicode__(self):
        return "ProxyHostname {0}, with name {1}".format(self.hostname, self.name)
