from django.shortcuts import _get_queryset
from responses import *
from middleware import handler404, handler500

def get_object_or_403(klass, *args, **kwargs):
    """
    Uses get() to return an object, or raises a Http403 exception if the object does not exist.
    This is useful if you don't want to expose that the object doesn't exist; 

    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the get() query.

    Note: Like with get(), an MultipleObjectsReturned will be raised if more than one
    object is found.
    
    (Taken, with slight modification, from django.shortcuts.)
    """
    queryset = _get_queryset(klass)
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        raise HttpForbidden()
