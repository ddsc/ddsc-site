# (c) Nelen & Schuurmans.  MIT licensed, see LICENSE.rst.
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

import datetime
import random
import os

from django.db import models
from django.db.models.loading import get_model
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group, User
from django.contrib.gis.geos import GEOSGeometry, Point
from django.contrib.gis.db.models import PointField
from django.db.models.signals import post_save
from django.core.urlresolvers import reverse

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
            self.collage, self.graph_index, timeseries_len)


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
    opacity = models.IntegerField(null=False, blank=False, default=100)
    style = models.CharField(max_length=255, null=True, blank=True)

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


class Annotation(models.Model):
    category = models.CharField(
        max_length=255, null=True, blank=True,
    )
    text = models.TextField(
        null=True, blank=True,
    )
    username = models.CharField(
        max_length=255, null=True, blank=True,
    )
    picture_url = models.TextField(
        max_length=2048, null=True, blank=True,
    )
    # Note: model_name is a reserved word for django-haystack!
    the_model_name = models.CharField(
        max_length=255, null=True, blank=True,
    )
    the_model_pk = models.CharField(
        max_length=255, null=True, blank=True,
    )
    location = PointField(
        srid=4326, null=True, blank=True
    )
    datetime_from = models.DateTimeField(
        null=True, blank=True
    )
    datetime_until = models.DateTimeField(
        null=True, blank=True
    )
    visibility = models.SmallIntegerField(
        default=1, choices=VISIBILITY_CHOICES
    )
    tags = models.TextField(
        null=True, blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True, editable=False
    )
    # Keep the following column (used in get_updated_field of the search index).
    updated_at = models.DateTimeField(
        auto_now=True, editable=False
    )

    @staticmethod
    def create_test_data():
        Annotation.objects.all().delete()
        x_length = 10
        y_length = 10
        tags = ['tag{0}'.format(i) for i in range(10)]
        model_names = ['location', 'timeseries']
        picture_urls = [None, 'http://www.nelen-schuurmans.nl/images/476/0/2/0/58.jpg']
        for x in range(x_length):
            for y in range(y_length):
                i = x * y
                a = Annotation()
                a.category = 'ddsc'
                a.text = 'text {0} blah'.format(i)
                a.username = 'username{0}'.format(i)
                a.picture_url = random.choice(picture_urls)
                a.the_model_name = random.choice(model_names)
                a.the_model_pk = '{0}'.format(y)
                a.location = Point(
                    55 - (10 * y / y_length),
                    2 + (10 * x / x_length),
                    srid=4326
                )
                a.datetime_from = datetime.datetime.now()
                a.datetime_until = datetime.datetime.now() + datetime.timedelta(hours=4)
                a.visibility = Visibility.PUBLIC
                a.tags = '{0} {1}'.format(random.choice(tags), random.choice(tags))
                a.save()

    def find_model(self):
        if self.the_model_name and self.the_model_pk:
            app_label = 'ddsc_core'
            # find the Model class
            model = get_model(app_label, self.the_model_name)
            return model

    def get_related_model(self):
        model = self.find_model()
        if model:
            try:
                model_instance = model.objects.get(pk=self.the_model_pk)
            except model.DoesNotExist as ex:
                model_instance = None
            return model_instance

    def get_related_model_str(self):
        model_instance = self.get_related_model()
        if model_instance:
            return str(model_instance)

    def clean(self):
        # Following won't work: DjangoRestFramework only supplies a pre_save method.
        # This is called AFTER model.is_valid(), which is what runs this model.clean() method.
        #if not self.username:
        #    raise ValidationError('No username supplied.')
        if self.the_model_name:
            if self.the_model_name not in ['location', 'timeseries']:
                raise ValidationError('Model "{0}" not supported for annotations.'.format(self.the_model_name))
        if self.the_model_name is None and self.the_model_pk:
            raise ValidationError('Model PK is supplied, but no model name given.')

    def __unicode__(self):
        return "Annotation {0}".format(self.pk)


class AnnotationAttachment(models.Model):
    annotation = models.ForeignKey(Annotation, null=True, blank=True)
    name = models.CharField(null=True, blank=True, max_length=255)
    creator = models.ForeignKey(User)

    def __unicode__(self):
        return "AnnotationAttachment {0}, annotation {1}".format(self.pk, self.annotation)

    def filename(self):
        if self.pk is None:
            raise Exception('No primary key, save() first!')
        # Imitate the same extension
        fn = [str(self.pk)]
        # Note: ext includes the "."
        ext = os.path.splitext(self.name)[1]
        if ext:
            fn.append(ext)
        return ''.join(fn)

    def path(self):
        path = os.path.join(settings.ANNOTATION_ATTACHMENTS_DIR, self.filename())
        return os.path.abspath(path)

    def absurl(self, request):
        url = request.build_absolute_uri(reverse('annotations-files-get', kwargs={'pk': self.pk, 'filename': self.name}))
        return url


class UserProfileManager(models.Manager):
    def fetch_for_user(self, user):
        if not user:
            raise AttributeError('Cant get UserProfile without user')
        return self.get(user=user)


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    initial_period = models.CharField(max_length=16, null=True, blank=True, default='')
    initial_zoom = models.CharField(max_length=255, null=True, blank=True, default='')

    objects = UserProfileManager()

    def clean(self):
        valid_periods = ['', '24h', '48h', '1w', '1m', '1y']
        if self.initial_period not in valid_periods:
            raise ValidationError('Period "{}" is not a valid period; pick one of "{}"'.format(self.initial_period, valid_periods))

    def __unicode__(self):
        if self.user:
            return 'UserProfile {} ({}, {})'.format(self.pk, self.user, self.user.email)
        else:
            return 'UserProfile {}'.format(self.pk)

    @staticmethod
    def get_or_create_profile(user):
        """
        Return the UserProfile for the given user, creating one if it does not exist.
        """
        profile, c = UserProfile.objects.get_or_create(user=user)
        return profile

# have the creation of a User trigger the creation of a Profile
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


post_save.connect(create_user_profile, sender=User)
