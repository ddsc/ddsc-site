# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Collage'
        db.create_table('ddsc_site_collage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('ddsc_site', ['Collage'])

        # Adding model 'CollageItem'
        db.create_table('ddsc_site_collageitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('collage', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ddsc_site.Collage'])),
        ))
        db.send_create_signal('ddsc_site', ['CollageItem'])


    def backwards(self, orm):
        # Deleting model 'Collage'
        db.delete_table('ddsc_site_collage')

        # Deleting model 'CollageItem'
        db.delete_table('ddsc_site_collageitem')


    models = {
        'ddsc_site.collage': {
            'Meta': {'object_name': 'Collage'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'ddsc_site.collageitem': {
            'Meta': {'object_name': 'CollageItem'},
            'collage': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ddsc_site.Collage']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['ddsc_site']