from django.shortcuts import render_to_response
from django.template import RequestContext, TemplateDoesNotExist
from django.core import context_processors, signals
from django.conf import settings
from django.core.handlers.wsgi import STATUS_CODE_TEXT
from django.http import Http404
from responses import RareHttpResponse, HttpNotFound
import sys

custom_renderer = None
def set_renderer(renderer):
    global custom_renderer
    custom_renderer = renderer

class CustomRareHttpResponses:
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
        if settings.DEBUG:
            # don't do any smart processing; 404 & 500 will get normal Django processing, everything else becomes a stacktrace
            return None

        if hasattr(settings, 'EXCEPTIONAL_INVASION') and setings.EXCEPTIONAL_INVASION=True:
            if isinstance(exception, Http404):
                exception = HttpNotFound(exception)
            if not isinstance(exception, RareHttpResponse):
                if isinstance(SystemExit):
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
                return self.renderer(
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
