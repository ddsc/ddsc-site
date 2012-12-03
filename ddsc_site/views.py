# (c) Nelen & Schuurmans.  MIT licensed, see LICENSE.rst.
from __future__ import unicode_literals

from django.utils.translation import ugettext as _
# from django.core.urlresolvers import reverse
# from lizard_map.views import MapView
from lizard_ui.views import UiView

# from ddsc_site import models


# class TodoView(UiView):
#     """Simple view without a map."""
#     template_name = 'ddsc_site/todo.html'
#     page_title = _('TODO view')


# class Todo2View(MapView):
#     """Simple view with a map."""
#     template_name = 'ddsc_site/todo2.html'
#     page_title = _('TODO 2 view')

class SentryTestView(UiView):
    # Temp test for new sentry setup :-)
    template_name = 'ddsc_site/todo.html'
    page_title = _('TODO view')

    def get(self, request):
        print(does_not_exist)
