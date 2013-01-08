from fanstatic import Library
from fanstatic import Resource
from fanstatic import Group
# from js.lesscss import LessResource
from js.lesscss import lesscss_js

library = Library('ddsc_site', 'resources')
# css_resource = Resource(library, 'main.css')
js_resource = Resource(library, 'main.js', bottom=True)
# less_resource = LessResource(library, 'main.less')
less_resource = Resource(library, 'main.less')
ddsc_site_layout = Group([
        #css_resource,
        js_resource,
        less_resource,
        lesscss_js,
        ])


# Reinout wonders whether this one is needed. It works just fine without.
def pserve():
    """A script aware of static resource"""
    import pyramid.scripts.pserve
    import pyramid_fanstatic
    import os

    dirname = os.path.dirname(__file__)
    dirname = os.path.join(dirname, 'resources')
    pyramid.scripts.pserve.add_file_callback(
                pyramid_fanstatic.file_callback(dirname))
    pyramid.scripts.pserve.main()
