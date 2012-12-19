DDSC-site: front-end Lizard site
==========================================

We're the http://test.dijkdata.nl/ site, installed on ``s-ddsc-ws-d1.external-nens.local``.


Symlink a buildout configuration
--------------------------------

Initially, there's no ``buildout.cfg``. You need to make that a symlink to the
correct configuration. On your development machine, that is
``development.cfg`` (and ``staging.cfg`` or ``production.cfg``, for instance
on the server)::

    $ ln -s development.cfg buildout.cfg


Sample data
-----------

For testing out the various "reinout-api" branches and lizard-structure, load
the "demodata" fixture. It contains an empty home screen and a bunch of WMS
layers (those layers are copied from deltaportaal, btw)::

    $ bin/django loaddata demodata
