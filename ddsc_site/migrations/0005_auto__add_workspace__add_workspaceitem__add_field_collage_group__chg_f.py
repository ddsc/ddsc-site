# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Workspace'
        db.create_table('ddsc_site_workspace', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.Group'], null=True, blank=True)),
            ('lon_lat_zoom', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('ddsc_site', ['Workspace'])

        # Adding model 'WorkspaceItem'
        db.create_table('ddsc_site_workspaceitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('workspace', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ddsc_site.Workspace'])),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('wms_source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_wms.WMSSource'])),
        ))
        db.send_create_signal('ddsc_site', ['WorkspaceItem'])

        # Adding field 'Collage.group'
        db.add_column('ddsc_site_collage', 'group',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.Group'], null=True, blank=True),
                      keep_default=False)


        # Changing field 'Collage.name'
        db.alter_column('ddsc_site_collage', 'name', self.gf('django.db.models.fields.CharField')(default='', max_length=100))
        # Deleting field 'CollageItem.graph_id'
        db.delete_column('ddsc_site_collageitem', 'graph_id')

        # Adding field 'CollageItem.graph_index'
        db.add_column('ddsc_site_collageitem', 'graph_index',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'Workspace'
        db.delete_table('ddsc_site_workspace')

        # Deleting model 'WorkspaceItem'
        db.delete_table('ddsc_site_workspaceitem')

        # Deleting field 'Collage.group'
        db.delete_column('ddsc_site_collage', 'group_id')


        # Changing field 'Collage.name'
        db.alter_column('ddsc_site_collage', 'name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))
        # Adding field 'CollageItem.graph_id'
        db.add_column('ddsc_site_collageitem', 'graph_id',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Deleting field 'CollageItem.graph_index'
        db.delete_column('ddsc_site_collageitem', 'graph_index')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'ddsc_site.collage': {
            'Meta': {'object_name': 'Collage'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.Group']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'ddsc_site.collageitem': {
            'Meta': {'object_name': 'CollageItem'},
            'collage': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ddsc_site.Collage']"}),
            'graph_index': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'timeseries': ('jsonfield.fields.JSONField', [], {'default': '[]', 'null': 'True', 'blank': 'True'})
        },
        'ddsc_site.workspace': {
            'Meta': {'object_name': 'Workspace'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.Group']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lon_lat_zoom': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'ddsc_site.workspaceitem': {
            'Meta': {'ordering': "(u'order',)", 'object_name': 'WorkspaceItem'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'wms_source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_wms.WMSSource']"}),
            'workspace': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ddsc_site.Workspace']"})
        },
        'lizard_maptree.category': {
            'Meta': {'ordering': "('index', 'name')", 'object_name': 'Category'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.IntegerField', [], {'default': '1000'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_maptree.Category']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '20'})
        },
        'lizard_wms.wmsconnection': {
            'Meta': {'object_name': 'WMSConnection'},
            'category': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['lizard_maptree.Category']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'options': ('django.db.models.fields.TextField', [], {'default': 'u\'{"buffer": 0, "isBaseLayer": false, "opacity": 0.5}\''}),
            'params': ('django.db.models.fields.TextField', [], {'default': 'u\'{"height": "256", "width": "256", "styles": "", "format": "image/png", "tiled": "true", "transparent": "true"}\''}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'version': ('django.db.models.fields.CharField', [], {'default': "u'1.3.0'", 'max_length': '20'}),
            'xml': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'})
        },
        'lizard_wms.wmssource': {
            'Meta': {'ordering': "(u'index', u'display_name')", 'object_name': 'WMSSource'},
            '_params': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'bbox': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['lizard_maptree.Category']", 'null': 'True', 'blank': 'True'}),
            'connection': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_wms.WMSConnection']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'enable_search': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.IntegerField', [], {'default': '1000'}),
            'layer_name': ('django.db.models.fields.TextField', [], {}),
            'legend_url': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'null': 'True', 'blank': 'True'}),
            'metadata': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'options': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'show_legend': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['ddsc_site']