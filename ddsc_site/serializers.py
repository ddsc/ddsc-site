import json

from rest_framework import serializers

from lizard_wms.models import WMSSource
from .models import Collage, CollageItem, Workspace, WorkspaceItem, Annotation

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


class HyperlinkedIdModelSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field('id')


class CollageItemSerializer(HyperlinkedIdModelSerializer):
    class Meta:
        model = CollageItem


class CollageListSerializer(HyperlinkedIdModelSerializer):
    collageitems = CollageItemSerializer(source='collageitem_set')

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


class PointField(serializers.Field):
    def to_native(self, obj):
        return obj.coords


class AnnotationSerializer(serializers.ModelSerializer):
    location = PointField(source='location')
    related_model_str = serializers.CharField(source='get_related_model_str')

    def to_native(self, obj):
        # use the Postgres database object, instead of the search index result
        return super(AnnotationSerializer, self).to_native(obj.object)

    class Meta:
        model = Annotation
