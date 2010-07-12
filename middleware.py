from django.shortcuts import render_to_response
from django.template import RequestContext, TemplateDoesNotExist
from django.core import context_processors
from django.conf import settings
from django.core.handlers.wsgi import STATUS_CODE_TEXT
from django.http import Http404
from responses import RareHttpResponse, HttpNotFound

custom_renderer = None
def set_renderer(renderer):
    global custom_renderer
    custom_renderer = renderer

class CustomRareHttpResponses:
    def process_exception(self, request, exception):
        if settings.DEBUG: # don't do any smart processing
            return None

        if isinstance(exception, Http404):
            exception = HttpNotFound(Http404)
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
