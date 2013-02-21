import json

from rest_framework import serializers

from lizard_wms.models import WMSSource
from .models import Collage, CollageItem, Workspace, WorkspaceItem

from ddsc_site.filters import objects_for_user_groups

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
        fields = ('id', 'url', 'collage', 'graph_index', 'timeseries')
        model = CollageItem


class CollageSerializer(HyperlinkedIdModelSerializer):
    collageitems = CollageItemSerializer(source='collageitem_set')

    class Meta:
        fields = ('id', 'url', 'name', 'collageitems')
        model = Collage


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

    wms_url = serializers.Field('url')

    def get_wms_url(self, obj):
        return obj.url

    def get_opacity(self, obj):
        options = obj.options
        if isinstance(options, basestring):
            options = json.loads(options)
        return options['opacity']

    def get_type(self, obj):
        return 'wms'

    class Meta:
        model = WMSSource
        fields = ('layer_name', 'display_name', 'url',
                  'description', 'metadata', 'legend_url', 'enable_search',
                  'styles', 'format', 'height', 'width', 'tiled',
                  'transparent', 'wms_url', 'opacity', 'type')


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
        result = super(FilteredWorkspaceField, self).initialize(*args, **kwargs)
        if 'request' in self.context:
            self.queryset = objects_for_user_groups(Workspace, self.context['request'].user, self.queryset)
        return result


class WorkspaceItemSerializer(HyperlinkedIdModelSerializer):
    #wms_source = serializers.HyperlinkedRelatedField(view_name='layer-detail')
    wms_source = WMSLayerSerializer(source='wms_source')
    workspace = FilteredWorkspaceField(view_name='workspace-detail')

    class Meta:
        model = WorkspaceItem


class WorkspaceListSerializer(HyperlinkedIdModelSerializer):
    workspaceitems = WorkspaceItemSerializer(source='workspaceitem_set')
    # null=True is deprecated, but there's no viable alternative yet!
    group = FilteredGroupField(null=True, required=False)

    class Meta:
        model = Workspace
