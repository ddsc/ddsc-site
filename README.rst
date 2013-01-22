DDSC-site: front-end Lizard site
==========================================

We're going to be the http://test.dijkdata.nl/ site, installed on ``s-ddsc-ws-d1.external-nens.local``.

This webapplication's primary purpose is to speak REST according to
the rest-api defined at http://ddsc.github.com/api .


Building DDSC-site
--------------------------------

To get up and running issue the following commands::

    $ git clone https://github.com/ddsc/ddsc-site.git
    $ cd ddsc-site
    $ pip install --user nensbuild
    $ nensbuild

The postgis database ddsc_site is needed. Create one with createdb.

Sample data
-----------

For testing out the various "reinout-api" branches and lizard-structure, load
the "demodata" fixture. It contains an empty home screen and a bunch of WMS
layers (those layers are copied from deltaportaal, btw)::

    $ bin/django loaddata demodata
