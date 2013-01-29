# (c) Nelen & Schuurmans.  MIT licensed, see LICENSE.rst.
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

from django.db import models


class Collage(models.Model):
    """Collages."""

    name = models.CharField(max_length=100)


class CollageItem(models.Model):
    """Collage Items."""

    name = models.CharField(max_length=100)
    collage = models.ForeignKey(Collage)
