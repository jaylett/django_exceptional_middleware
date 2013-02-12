"""
A simple test view that just raises a suitable exception from exceptional_middleware.responses.
"""

from django.http import Http404
import exceptional_middleware.responses

def raise_view(request, type, **kwargs):
    """
    A simple view for testing that will raise an exception based on
    its first parameter (typically a path component in the URL).
    """

    full_type = "Http%s" % type
    if hasattr(exceptional_middleware.responses, full_type):
        exc_class = getattr(exceptional_middleware.responses, full_type)
        raise exc_class()

    # what should we do here? it's a user-constructable URL, so it's
    # a 404. Use Django's internal one, because you can generate
    # an exceptional_middleware one using NotFound as the type.
    raise Http404()
