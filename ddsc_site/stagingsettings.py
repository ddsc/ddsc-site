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

CORS_ORIGIN_WHITELIST = (
    'test.dijkdata.nl',
)

WEBCLIENT = 'http://test.dijkdata.nl'


try:
    from ddsc_site.localstagingsettings import *
    # For local staging overrides (DB passwords, for instance)
except ImportError:
    pass
