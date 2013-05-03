from setuptools import setup

version = '0.1dev'

long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CREDITS.rst').read(),
    open('CHANGES.rst').read(),
])

install_requires = [
    'Django',
    'django-celery',
    'django-extensions',
    'django-nose',
    'django-filter',
    'django-cors-headers',
    'django-haystack', # should be at least 2.0.0-beta, but PyPI is broken, so use development checkout from github
    'geopy', # optional dependency of django-haystack
    'pysolr', # optional dependency of django-haystack
    'cssselect', # optional dependency of django-haystack
    'lxml >= 3.0', # implicit dependency of django-haystack
    'python-dateutil',
    'gunicorn',
    'lizard-map >= 4.13',
    'lizard-wms',
    'lizard-ui >= 4.0b5',
    'lizard-auth-client',
    'python-memcached',
    'raven',
    'requests',
    'werkzeug',
],

setup(name='ddsc-site',
      version=version,
      description="Lizard site for showing the data from the DDSC api ",
      long_description=long_description,
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Programming Language :: Python',
                   'Framework :: Django',
                   ],
      keywords=[],
      author='Reinout van Rees',
      author_email='reinout.vanrees@nelen-schuurmans.nl',
      url='https://github.com/ddsc/ddsc-site',
      license='MIT',
      packages=['ddsc_site'],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      entry_points={
          'console_scripts': [
          ]},
      )
