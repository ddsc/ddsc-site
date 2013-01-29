# Base Django settings, suitable for production.
# Imported (and partly overridden) by developmentsettings.py which also
# imports localsettings.py (which isn't stored in svn).  Buildout takes care
# of using the correct one.
# So: "DEBUG = TRUE" goes into developmentsettings.py and per-developer
# database ports go into localsettings.py.  May your hear turn purple if you
# ever put personal settings into this file or into developmentsettings.py!

import os
import tempfile

from lizard_ui.layout import Action
from lizard_ui.settingshelper import STATICFILES_FINDERS
from lizard_ui.settingshelper import setup_logging

STATICFILES_FINDERS = STATICFILES_FINDERS

# Set matplotlib defaults.
# Uncomment this when using lizard-map.
# import matplotlib
# # Force matplotlib to not use any Xwindows backend.
# matplotlib.use('Agg')
# import lizard_map.matplotlib_settings

# SETTINGS_DIR allows media paths and so to be relative to this settings file
# instead of hardcoded to c:\only\on\my\computer.
SETTINGS_DIR = os.path.dirname(os.path.realpath(__file__))

# BUILDOUT_DIR is for access to the "surrounding" buildout, for instance for
# BUILDOUT_DIR/var/static files to give django-staticfiles a proper place
# to place all collected static files.
BUILDOUT_DIR = os.path.abspath(os.path.join(SETTINGS_DIR, '..'))

# Set up logging. No console logging. By default, var/log/django.log and
# sentry at 'WARN' level.
LOGGING = setup_logging(BUILDOUT_DIR, console_level=None, sentry_level='WARN')

# Triple blast.  Needed to get matplotlib from barfing on the server: it needs
# to be able to write to some directory.
if 'MPLCONFIGDIR' not in os.environ:
    os.environ['MPLCONFIGDIR'] = tempfile.gettempdir()

# Production, so DEBUG is False. developmentsettings.py sets it to True.
DEBUG = False
# Show template debug information for faulty templates.  Only used when DEBUG
# is set to True.
TEMPLATE_DEBUG = True

# ADMINS get internal error mails, MANAGERS get 404 mails.
ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)
MANAGERS = ADMINS

# TODO: Switch this to the real production database.
# ^^^ 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
# In case of geodatabase, prepend with: django.contrib.gis.db.backends.(postgis)
DATABASES = {
    'default': {
        'NAME': 'ddsc_site',
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'USER': 'ddsc_site',
        'PASSWORD': 'xxxxxxxx',
        'HOST': 'yyyyyyyy',
        'PORT': '5432',
        }
    }

# Almost always set to 1.  Django allows multiple sites in one database.
SITE_ID = 1

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name although not all
# choices may be available on all operating systems.  If running in a Windows
# environment this must be set to the same as your system time zone.
TIME_ZONE = 'Europe/Amsterdam'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'nl-NL'
# For at-runtime language switching.  Note: they're shown in reverse order in
# the interface!
LANGUAGES = (
#    ('en', 'English'),
    ('nl', 'Nederlands'),
)
# If you set this to False, Django will make some optimizations so as not to
# load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds user-uploaded media.
MEDIA_ROOT = os.path.join(BUILDOUT_DIR, 'var', 'media')
# Absolute path to the directory where django-staticfiles'
# "bin/django build_static" places all collected static files from all
# applications' /media directory.
STATIC_ROOT = os.path.join(BUILDOUT_DIR, 'var', 'static')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
MEDIA_URL = '/media/'
# URL for the per-application /media static files collected by
# django-staticfiles.  Use it in templates like
# "{{ MEDIA_URL }}mypackage/my.css".
STATIC_URL = '/static_media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'zzzzzzzz'

ROOT_URLCONF = 'ddsc_site.urls'

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

CACHES = {
    'default': {
        'KEY_PREFIX': BUILDOUT_DIR,
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

MIDDLEWARE_CLASSES = (
    # Gzip needs to be at the top.
    'django.middleware.gzip.GZipMiddleware',
    # Below is the default list, don't modify it.
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Lizard security.
    'tls.TLSRequestMiddleware',
    'lizard_security.middleware.SecurityMiddleware',
)

INSTALLED_APPS = (
    'ddsc_site',
    'lizard_wms',
    'lizard_maptree',
    'lizard_map',
    'lizard_ui',
    'lizard_security',
    'rest_framework',
    'south',
    'compressor',
    'staticfiles',
    'raven.contrib.django',
    'django_extensions',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.gis',
    'django.contrib.markup',
    'django.contrib.sessions',
    'django.contrib.sites',
    'gunicorn',
)

USE_TZ = True

# TODO: Put your real url here to configure Sentry.
SENTRY_DSN = 'http://77c3b9cbccd44e93b4dc25b0a7903490:fc64db9f24ad457ca1ab7378f8153215@sentry.lizardsystem.nl/3'

# TODO: add gauges ID here. Generate one separately for the staging, too.
UI_GAUGES_SITE_ID = ''  # Staging has a separate one.


LIZARD_SITE = 'http://test.dijkdata.nl/'
MANAGEMENT_SITE = 'http://test.beheer.dijkdata.nl/'

UI_SITE_ACTIONS = [
    Action(
        name="Kaart",
        # description="",
        # icon="icon-info-sign",
        # klass="has_popover_south"
    ),
    Action(
        name="Grafieken",
    ),
    Action(
        name="Overzichten",
    ),
    Action(
        name="Beheer",
        url=MANAGEMENT_SITE,
        # description="",
        # icon="icon-info-sign",
        # klass="has_popover_south"
    ),
]

REST_FRAMEWORK = {
    'FILTER_BACKEND': 'rest_framework.filters.DjangoFilterBackend',
    'PAGINATE_BY': 10,
    'PAGINATE_BY_PARAM': 'page_size'
}


SKIP_SOUTH_TESTS = True
SOUTH_TESTS_MIGRATE = False

try:
    from ddsc_site.localproductionsettings import *
    # For local production overrides (DB passwords, for instance)
except ImportError:
    pass
