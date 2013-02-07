# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'CollageItem'
        db.delete_table('ddsc_site_collageitem')

        # Deleting field 'Collage.name'
        db.delete_column('ddsc_site_collage', 'name')

        # Adding field 'Collage.data'
        db.add_column('ddsc_site_collage', 'data',
                      self.gf('jsonfield.fields.JSONField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding model 'CollageItem'
        db.create_table('ddsc_site_collageitem', (
            ('collage', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ddsc_site.Collage'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('ddsc_site', ['CollageItem'])


        # User chose to not deal with backwards NULL issues for 'Collage.name'
        raise RuntimeError("Cannot reverse this migration. 'Collage.name' and its values cannot be restored.")
        # Deleting field 'Collage.data'
        db.delete_column('ddsc_site_collage', 'data')


    models = {
        'ddsc_site.collage': {
            'Meta': {'object_name': 'Collage'},
            'data': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['ddsc_site']