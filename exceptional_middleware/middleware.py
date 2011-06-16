from django.shortcuts import render_to_response
from django.template import RequestContext, TemplateDoesNotExist
from django.core import context_processors, signals
from django.conf import settings
from django.core.handlers.wsgi import STATUS_CODE_TEXT
from django.http import Http404
from django.core.urlresolvers import Resolver404
from responses import RareHttpResponse, HttpNotFound, HttpServerError
import sys

custom_renderer = None
def set_renderer(renderer):
    global custom_renderer
    custom_renderer = renderer

class ExceptionalMiddleware(object):
    def render(self, request, template_name, context):
        if custom_renderer==None:
            return render_to_response(
                template_name,
                context,
                context_instance = RequestContext(
                    request,
                    processors = [ context_processors.request ]
                )
            )
        else:
            return custom_renderer(request, template_name, context)
        
    def process_exception(self, request, exception):
        # first, make sure the exception is handled by sentry, if installed
        # we don't pass through our exceptions unless http_code >= 500, or
        # the Django 1.3 Http404 exception, since these are raised in normal
        # circumstances and so aren't useful to Sentry.
        #
        # (Sentry should pick up the 404s using the Sentry 404 middleware,
        # which it separates out from exceptions. Ideally, Sentry would
        # track other 4xx responses similarly.)
        if 'sentry' in settings.INSTALLED_APPS:
            if isinstance(exception, RareHttpResponse) and exception.http_code < 500:
                pass
            elif isinstance(exception, Http404) or isinstance(exception, Resolver404):
                pass
            else:
                try:
                    from sentry.client.models import sentry_exception_handler
                    sentry_exception_handler(request=request)
                except ImportError:
                    pass
        if settings.DEBUG:
            # unless 3xx, don't do any smart processing; 404 & 500 will get normal
            # Django processing, everything else becomes a stacktrace
            if not isinstance(exception, RareHttpResponse) or exception.http_code // 100 != 3:
                return None

        if hasattr(settings, 'EXCEPTIONAL_INVASION') and settings.EXCEPTIONAL_INVASION==True:
            if isinstance(exception, Http404) or isinstance(exception, Resolver404):
                exception = HttpNotFound(exception)
            if not isinstance(exception, RareHttpResponse):
                if isinstance(exception, SystemExit):
                    raise
                else:
                    # we're emulating Django's 500 processing, but using our render system to make it pretty
                    # most importantly, we fire off the ``got_request_exception`` signal so people know something
                    # has gone wrong. We *DON'T* email admins, since we don't really believe that's a good idea --
                    # you should do something in a signal handler instead (shove it in a queue, db, or something else
                    # more manageable than email; or send an email from the handler).
                    #
                    # (If you disagree, you probably want to refactor the handler in Django itself and expose the
                    # mail admin functionality so we can use it in a couple of lines, rather than copying all the code
                    # out.)
                    receivers = signals.got_request_exception.send(sender=self.__class__, request=request)
                    # FIXME: sender is wrong. It should be the handler class that handled the request
                    # (django.core.handlers.wsgi.WsgiHandler or whatever). We could look through the stack trace
                    # for a subclass of django.core.handlers.base.BaseHandler?
                    exception = HttpServerError(exception)

        if isinstance(exception, RareHttpResponse):
            def do_render(template=None):
                if template:
                    template = 'http_responses/%s.html' % (template,)
                else:
                    template = 'http_responses/%i.html' % (exception.http_code, ),
                return self.render(
                    request,
                    template,
                    {
                        'http_code': exception.http_code,
                        'http_message': STATUS_CODE_TEXT.get(exception.http_code, 'UNKNOWN'), # TRANSLATE IN TEMPLATE
                        'http_response_exception': exception,
                    }
                )

            try:
                response = do_render()
            except TemplateDoesNotExist:
                response = do_render('default')
            response.status_code = exception.http_code
            exception.augment_response(response)
            if exception.headers:
                for k,v in exception.headers.items():
                    response[k] = v
            return response
        return None

def handler404(request):
    """
    Utility handler for people wanting EXCEPTIONAL_INVASION, since we can't trap the Http404 raised when the
    URLconf fails to recognise a URL completely. Just drop this in as handler404 in your urls.py. (Note that
    if you subclass ExceptionalMiddleware to override its render() method, you won't be able to use this.)
    
    Don't reference this from here, it's imported into exceptional_middleware directly.
    """
    em = ExceptionalMiddleware()
    return em.process_exception(request, HttpNotFound())

def handler500(request):
    """
    Utility handler for people wanting EXCEPTIONAL_INVASION, since we can't trap exceptions raised during Http404
    processing when the URLconf fails to recognise a URL completely. Just drop this in as handler500in your
    urls.py. (Note that if you subclass ExceptionalMiddleware to override its render() method, you won't be
    able to use this.)
    
    Don't reference this from here, it's imported into exceptional_middleware directly.
    """
    em = ExceptionalMiddleware()
    return em.process_exception(request, HttpServerError())
