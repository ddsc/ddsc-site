# (c) Nelen & Schuurmans.  MIT licensed, see LICENSE.rst.
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

from haystack import indexes
from ddsc_site.models import Annotation


class AnnotationIndex(indexes.SearchIndex, indexes.Indexable):
    category = indexes.CharField(model_attr='category', null=True)
    text = indexes.CharField(
        document=True,
        use_template=False,
        model_attr='text',
        null=True)
    username = indexes.CharField(model_attr='username', null=True)
    picture_url = indexes.CharField(model_attr='picture_url', null=True)
    the_model_name = indexes.CharField(model_attr='the_model_name', null=True)
    the_model_pk = indexes.CharField(model_attr='the_model_pk', null=True)
    location = indexes.LocationField(model_attr='location', null=True)
    datetime_from = indexes.DateTimeField(
        model_attr='datetime_from', null=True)
    datetime_until = indexes.DateTimeField(
        model_attr='datetime_until', null=True)
    visibility = indexes.CharField(model_attr='visibility', null=True)
    tags = indexes.CharField(model_attr='tags', null=True)

    def get_model(self):
        return Annotation

    def index_queryset(self, using=None):
        return self.get_model().objects.all()

    def get_updated_field(self):
        return 'updated_at'