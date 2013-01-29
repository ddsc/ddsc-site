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
    'gunicorn',
    'lizard-map >= 4.13',
    'lizard-wms',
    'lizard-ui >= 4.0b5',
    'python-memcached',
    'raven',
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
