# (c) Nelen & Schuurmans.  MIT licensed, see LICENSE.rst.
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

from django.db import models

from jsonfield.fields import JSONField


class Collage(models.Model):
    """Collages."""

    name = models.CharField(max_length=100, null=True, blank=True)

    def __unicode__(self):
        return self.name


class CollageItem(models.Model):
    """Collage Items."""

    collage = models.ForeignKey(Collage)
    graph_id = models.IntegerField(null=True, blank=True)
    timeseries = JSONField(null=True, blank=True)

    def __unicode__(self):
        timeseries_len = 0
        if isinstance(self.timeseries, list):
            timeseries_len = len(self.timeseries)

        return 'Collage: {}, Graph: {}, {} timeseries'.format(
            self.collage, self.graph_id, timeseries_len)
