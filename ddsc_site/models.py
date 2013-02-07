# (c) Nelen & Schuurmans.  MIT licensed, see LICENSE.rst.
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

from django.db import models

from jsonfield.fields import JSONField


class Collage(models.Model):
    """Collages."""

    data = JSONField(null=True, blank=True)

    def __unicode__(self):
        return self.data
