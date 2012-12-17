DDSC-site: front-end Lizard site
==========================================

We're the http://test.dijkdata.nl/ site, installed on ``s-ddsc-ws-d1.external-nens.local``.


Building DDSC-site
--------------------------------

To get up and running issue the following commands::
  
    $ git clone https://github.com/ddsc/ddsc-site.git
    $ cd ddsc-site
    $ pip install --user nensbuild
    $ nensbuild

The postgis database ddsc_site is needed. Create one with createdb.
