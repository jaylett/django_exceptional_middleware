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
    def process_exception(self, request, exception):
        if settings.DEBUG:
            # don't do any smart processing; 404 & 500 will get normal Django processing, everything else becomes a stacktrace
            return None

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
                receivers = signals.got_request_exception.send(sender=self.__class__, request=request)
                exception = HttpServerError(exception)

        if isinstance(exception, RareHttpResponse):
            renderer = custom_renderer
            if renderer==None:
                renderer = (
                    lambda request, template_name, context: \
                    render_to_response(
                        template_name,
                        context,
                        context_instance = RequestContext(
                            request,
                            processors = [ context_processors.request ]
                        )
                    )
                )

            def do_render(template=None):
                if template:
                    template = 'http_responses/%s.html' % (template,)
                else:
                    template = 'http_responses/%i.html' % (exception.http_code, ),
                return renderer(
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
            return response
        return None
