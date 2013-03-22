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

Annotations
-----------

Annotations are indexed by the Apache Solr search engine using ``django-haystack``.
Currently, the latest versions of these modules must be used, to support spatial search.

For django-haystack, this is ``2.0.0-beta``. This module is current loaded straight from
its git repo using buildout's ``auto-checkout``.

Apache Solr 3.6.2 is included in the subdirectory ``solr/``. This needs to be added as a webapp
in tomcat6 using a config file (mind the two absolute paths).

/etc/tomcat6/Catalina/localhost/solr.xml::

    <Context docBase="/srv/dijkdata.nl/src/ddsc-site/solr/solr.war" debug="0" privileged="true" allowLinking="true" crossContext="true">
        <Environment name="solr/home" type="java.lang.String" value="/srv/dijkdata.nl/src/ddsc-site/solr" override="true" />
    </Context>

The connection to Solr needs to be configured in your ``settings.py``::

    HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
            'URL': 'http://127.0.0.1:8080/solr'
        },
    }

When changing the Annotation model, the Solr schema needs updating as well::

    $ bin/django build_solr_schema > src/ddsc-site/solr/conf/schema.xml

When the index has to be rebuilt entirely::

    $ bin/django rebuild_index

When the index has to be rebuilt partially, for example in a cron job that runs each hour,
you can do::

    $ bin/django update_index --age=1

Searching annotations is easy::

    $ wget "http://api.dijkdata.nl/api/v0/annotations/count/?bbox=test&tags=tag2%20tag1&datetime_from=2013-03-21T14:46:46.000&datetime_until=2013-03-21T14:46:50.000"
    >> {"result": 17928}
    $ wget "http://api.dijkdata.nl/api/v0/annotations/search/?bbox=test&tags=tag2%20tag1&datetime_from=2013-03-21T14:46:46.000&datetime_until=2013-03-21T14:46:50.000"
    >> {
        "count": 774,
        "next": "http://api.dijkdata.nl/api/v0/annotations/search/?datetime_from=2013-03-21T14%3A46%3A46.000&datetime_until=2013-03-21T14%3A46%3A50.000&tags=tag2+tag1&bbox=test&page=2&username_override=username+99975",
        "previous": null,
        "results": [
            {
                "id": "ddsc_site.annotation.45525",
                "category": "ddsc",
                "text": "text 45343",
                "username": "username 45343",
                "picture_url": "picture_url 45343",
                "the_model_name": "model_name 45343",
                "the_model_pk": "model_pk 45343",
                "location": "POINT (-80.4656999999999982 44.5343000000000018)",
                "datetime_from": "2013-03-21T14:46:46",
                "datetime_until": "2013-03-21T14:46:46",
                "visibility": "3",
                "tags": "tag1 tag2",
                "created_at": null,
                "updated_at": null
            },
            ...
        ]
    }

Possible ``GET`` parameters::

category
  Search in a category. Probably always 'ddsc'.
bbox
  Comma-separated bounding box for the locations. Default WMS format, like, so "west,south,east,north". SRID 4258. When equal to "test", uses some fixed coordinates which are compatible with Annotation.create_test_data().
west,south,east,north
  Alternative, if bbox isn't defined.
bottom_left,top_right
  Alternative, if bbox isn't defined. Comma separated.
username_override
  Only available in DEBUG mode. Test private/public annotation visibility with this.
model_name, model_pk
  Search for annotations related to a specific model instance. For example a Timeseries with a specific UUID.
datetime_from, datetime_until
  Search annotations in a specific time range. Takes any dateutil.parser compatible format, for example ISO8601: "2013-03-21T14:46:50.000".
text
  Fulltext search in the text of the annotation.
tags
  A set of space-separated tags to search.

Create a set of test annotations::

    $ bin/django shell
    >> from ddsc_site.models import Annotation
    >> Annotation.create_test_data()
