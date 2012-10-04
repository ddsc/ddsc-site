from ddsc_site.settings import *

DATABASES = {
    # Changed server from production to staging
    'default': {
        'NAME': 'ddsc_site',
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'USER': 'ddsc_site',
        'PASSWORD': 'xxxxxxxx',
        'HOST': 'yyyyyyyy',
        'PORT': '5432',
        },
    }

# TODO: add staging gauges ID here.
UI_GAUGES_SITE_ID = ''  # Staging has a separate one.
