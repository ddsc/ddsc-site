# (c) Nelen & Schuurmans.  MIT licensed, see LICENSE.rst.
from __future__ import unicode_literals

from django.contrib import admin

from ddsc_site import models

admin.site.register(models.Collage)
admin.site.register(models.CollageItem)
admin.site.register(models.Workspace)
admin.site.register(models.WorkspaceItem)
admin.site.register(models.ProxyHostname)
