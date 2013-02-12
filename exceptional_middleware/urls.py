"""
urlconf to include and get test targets.

Or you could use views.raise_view directly.

Note that these will be live even when DEBUG=False, because you need that for
exceptional_middleware to do its thing at all (DEBUG=True gives you the
"technical" exception output with stack trace and the like).
"""

from django.conf import settings
from django.conf.urls import patterns, url
from exceptional_middleware.views import raise_view

urlpatterns = patterns('',
    url(r'^(?P<type>.*)/$', raise_view),
)
