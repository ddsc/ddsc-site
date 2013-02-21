# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CollageItem'
        db.create_table('ddsc_site_collageitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('collage', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ddsc_site.Collage'])),
            ('graph_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('timeseries', self.gf('jsonfield.fields.JSONField')(null=True, blank=True)),
        ))
        db.send_create_signal('ddsc_site', ['CollageItem'])

        # Deleting field 'Collage.data'
        db.delete_column('ddsc_site_collage', 'data')

        # Adding field 'Collage.name'
        db.add_column('ddsc_site_collage', 'name',
                      self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'CollageItem'
        db.delete_table('ddsc_site_collageitem')

        # Adding field 'Collage.data'
        db.add_column('ddsc_site_collage', 'data',
                      self.gf('jsonfield.fields.JSONField')(null=True, blank=True),
                      keep_default=False)

        # Deleting field 'Collage.name'
        db.delete_column('ddsc_site_collage', 'name')


    models = {
        'ddsc_site.collage': {
            'Meta': {'object_name': 'Collage'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'ddsc_site.collageitem': {
            'Meta': {'object_name': 'CollageItem'},
            'collage': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ddsc_site.Collage']"}),
            'graph_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'timeseries': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['ddsc_site']