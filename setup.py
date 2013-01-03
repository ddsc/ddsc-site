from setuptools import setup

version = '0.1dev'

long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CREDITS.rst').read(),
    open('CHANGES.rst').read(),
    ])

install_requires = [
    'cornice',
    'pyramid',
    'waitress',
    'PasteScript',
    # 'gunicorn',
    # 'raven',
    ],

setup(name='ddsc-site',
      version=version,
      description="Site for providing various JSON data for the DDSC browser client",
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
          ],
          'paste.app_factory': [
            'main = ddsc_site:main',
            ],
          },
      )
