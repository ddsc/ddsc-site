# (c) Nelen & Schuurmans.  MIT licensed, see LICENSE.rst.
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

import datetime
from haystack.indexes import *
from ddsc_site.models import Annotation

class AnnotationIndex(SearchIndex, Indexable):
    category = CharField(model_attr='category', null=True)
    text = CharField(document=True, use_template=False, model_attr='text', null=True)
    username = CharField(model_attr='username', null=True)
    picture_url = CharField(model_attr='picture_url', null=True)
    the_model_name = CharField(model_attr='the_model_name', null=True)
    the_model_pk = CharField(model_attr='the_model_pk', null=True)
    location = LocationField(model_attr='location', null=True)
    datetime_from = DateTimeField(model_attr='datetime_from', null=True)
    datetime_until = DateTimeField(model_attr='datetime_until', null=True)
    visibility = CharField(model_attr='visibility', null=True)
    tags = CharField(model_attr='tags', null=True)

    def get_model(self):
        return Annotation

    def index_queryset(self, using=None):
        return self.get_model().objects.all()
