import json

from rest_framework import serializers

from django.forms import widgets
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError

from lizard_wms.models import WMSSource

from ddsc_site.models import (
    Annotation, Collage, CollageItem, VISIBILITY_CHOICES, Visibility,
    Workspace, WorkspaceItem
    )
from ddsc_site.filters import filter_objects_for_creator


class JSONField(serializers.Field):
    """Get a Field that is in a JSONField in Django."""
    def __init__(self, source, dict_name):
        super(JSONField, self).__init__(source)
        self.dict_name = dict_name

    def field_to_native(self, obj, field_name):
        """
        Given an object and a field name, returns the value that should be
        serialized for that field.
        """
        if obj is None:
            return self.empty

        data = getattr(obj, self.dict_name)
        if data is None:
            value = None
        else:
            value = data.get(self.source, None)
        return self.to_native(value)


class VisibilityField(serializers.ChoiceField):
    # to json
    def to_native(self, obj):
        vis2str = {
            Visibility.PUBLIC: 'public',
            Visibility.PRIVATE: 'private',
        }
        return vis2str.get(obj)

    # from json
    def from_native(self, obj):
        result = None
        if isinstance(obj, basestring):
            str2vis = {
                'public': Visibility.PUBLIC,
                'private': Visibility.PRIVATE,
            }
            result = str2vis.get(obj)
        return (
            result if result is not None
            else super(VisibilityField, self).from_native(obj)
            )


class HyperlinkedIdModelSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field('id')


class FilteredCollageField(serializers.HyperlinkedRelatedField):
    def initialize(self, *args, **kwargs):
        result = super(FilteredCollageField, self).initialize(*args, **kwargs)
        if 'request' in self.context:
            self.queryset = filter_objects_for_creator(
                Collage, self.context['request'].user, self.queryset)
        return result


class CollageItemSerializer(HyperlinkedIdModelSerializer):
    class Meta:
        model = CollageItem


class CollageItemCreateSerializer(HyperlinkedIdModelSerializer):
    collage = FilteredCollageField(view_name='collage-detail')

    class Meta:
        model = CollageItem


class CollageListSerializer(HyperlinkedIdModelSerializer):
    visibility = VisibilityField()
    collageitems = CollageItemSerializer(source='collageitem_set')

    class Meta:
        model = Collage
        exclude = ('creator',)


class CollageCreateSerializer(HyperlinkedIdModelSerializer):
    creator = serializers.Field()
    visibility = VisibilityField(required=True, choices=VISIBILITY_CHOICES)

    class Meta:
        model = Collage
        exclude = ('creator',)


class WMSLayerSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='layer-detail')

    styles = JSONField('styles', '_params')
    format = JSONField('format', '_params')
    height = JSONField('height', '_params')
    width = JSONField('width', '_params')
    tiled = JSONField('tiled', '_params')
    transparent = JSONField('transparent', '_params')

    opacity = serializers.SerializerMethodField('get_opacity')
    type = serializers.SerializerMethodField('get_type')

    options = serializers.SerializerMethodField('get_options')
    legend_url = serializers.SerializerMethodField('get_legend_url')

    wms_url = serializers.Field('url')

    def get_wms_url(self, obj):
        return obj.url

    def get_opacity(self, obj):
        options = obj.options
        if isinstance(options, basestring):
            try:
                options = json.loads(options)
            except ValueError:
                options = {}
        return getattr(options, 'opacity', None)

    def get_options(self, obj):
        if isinstance(obj.options, basestring):
            try:
                return json.loads(obj.options)
            except ValueError:
                return {}

    def get_legend_url(self, obj):
        if obj.legend_url:
            # use the overridden custom legend URL
            return obj.legend_url
        else:
            # automagically build GeoServer compatible legend URL
            return (
                '{0}'
                '?REQUEST=GetLegendGraphic'
                '&VERSION=1.0.0'
                '&FORMAT=image/png'
                '&WIDTH=20&HEIGHT=20'
                '&LAYER={1}'
            ).format(obj.url, obj.layer_name)

    def get_type(self, obj):
        return 'wms'

    class Meta:
        model = WMSSource
        fields = ('layer_name', 'display_name', 'url',
                  'description', 'metadata', 'legend_url', 'enable_search',
                  'styles', 'format', 'height', 'width', 'tiled',
                  'transparent', 'wms_url', 'opacity', 'type', 'options')


class FilteredGroupField(serializers.PrimaryKeyRelatedField):
    # keep this, so DRF generates a null choice!
    empty_label = '-------------'

    def initialize(self, *args, **kwargs):
        result = super(FilteredGroupField, self).initialize(*args, **kwargs)
        if 'request' in self.context:
            self.queryset = self.context['request'].user.groups.all()
        return result


class FilteredWorkspaceField(serializers.HyperlinkedRelatedField):
    def initialize(self, *args, **kwargs):
        result = super(FilteredWorkspaceField, self
                       ).initialize(*args, **kwargs)
        if 'request' in self.context:
            self.queryset = filter_objects_for_creator(
                Workspace, self.context['request'].user, self.queryset)
        return result


class WorkspaceItemSerializer(HyperlinkedIdModelSerializer):
    wms_source = WMSLayerSerializer(source='wms_source')
    workspace = FilteredWorkspaceField(view_name='workspace-detail')
    wms_source_pk = serializers.PrimaryKeyRelatedField(source='wms_source')

    class Meta:
        model = WorkspaceItem


class WorkspaceListSerializer(HyperlinkedIdModelSerializer):
    workspaceitems = WorkspaceItemSerializer(source='workspaceitem_set')

    class Meta:
        model = Workspace
        exclude = ('creator',)


class PointField(serializers.WritableField):
    # to json
    def to_native(self, obj):
        if obj:
            return obj.coords

    # from json
    def from_native(self, obj):
        if obj:
            if isinstance(obj, basestring):
                try:
                    obj = obj.split(',')
                    x, y = float(obj[0]), float(obj[1])
                except Exception as ex:
                    raise ValidationError(
                        'location must be a comma separated pair of '
                        'coordinates: {0}'.format(ex)
                    )
                return Point(x, y)
            elif isinstance(obj, (list, tuple)):
                try:
                    x, y = float(obj[0]), float(obj[1])
                except Exception as ex:
                    raise ValidationError(
                        'location must be an array of floats: {0}'.format(ex)
                    )
                return Point(x, y)


class AnnotationSerializer(HyperlinkedIdModelSerializer):
    location = PointField(source='location')
    related_model_str = serializers.CharField(source='get_related_model_str')
    visibility = VisibilityField(
        required=True,
        choices=(
            (Visibility.PRIVATE, 'private'),
            (Visibility.PUBLIC, 'public'),
        )
    )

    def to_native(self, obj):
        # use the Postgres database object (obj.object),
        # instead of the search index result
        return super(AnnotationSerializer, self).to_native(obj.object)

    class Meta:
        model = Annotation


class AnnotationCreateSerializer(serializers.ModelSerializer):
    category = serializers.CharField(required=False, default='ddsc')
    text = serializers.CharField(required=False, widget=widgets.Textarea)
    picture_url = serializers.CharField(required=False)
    the_model_name = serializers.CharField(required=False)
    the_model_pk = serializers.CharField(required=False)
    location = PointField(required=False)
    datetime_from = serializers.DateTimeField(required=False)
    datetime_until = serializers.DateTimeField(required=False)
    tags = serializers.CharField(required=False, widget=widgets.Textarea)
    visibility = VisibilityField(
        required=True,
        choices=(
            (Visibility.PRIVATE, 'private'),
            (Visibility.PUBLIC, 'public'),
        )
    )
    username = serializers.Field()

    class Meta:
        model = Annotation


class AnnotationDetailSerializer(serializers.ModelSerializer):
    visibility = VisibilityField(
        required=True,
        choices=(
            (Visibility.PRIVATE, 'private'),
            (Visibility.PUBLIC, 'public'),
        )
    )
    location = PointField(required=False)

    class Meta:
        model = Annotation
        read_only = ('username',)
