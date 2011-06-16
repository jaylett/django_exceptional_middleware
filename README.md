# Django Exceptional Middleware

Middleware app that makes it easy to generate HTTP status codes as exceptions, with customisable templates, and making it easy to style them all the same way.

This was originally written at a [/dev/fort](http://devfort.com/), based on an initial implementation by Richard Boulton, and subsequently developed at other devforts; it was previously available as `django_custom_rare_http_responses`, and is now on PyPI as `django_exceptional_middleware`.

With Django 1.3's Class Based Views, this becomes particularly useful. Future versions of Django are likely to get some kind of support which will replace this approach.

## Basic use

Add `exceptional_middleware.middleware.ExceptionalMiddleware` to `MIDDLEWARE_CLASSES`, and `exceptional_middleware` to `INSTALLED_APPS`. Make sure you have `django.template.loaders.app_directories.Loader` in your `TEMPLATE_LOADERS`, and you can then raise the exceptions in `exceptional_middleware.responses` to get a (basic) error page.

To override the default template, put (eg) `http_responses/403.html` in a `TEMPLATE_DIRS` directory (assuming `django.template.loaders.filesystem.Loader` comes before `django.template.loaders.app_directories.Loader` in your `TEMPLATE_LOADERS`).

## Fallback templates and template context variables

If you don't want to write a different template for each response code, you can make a `default.html` template, which is how the automatic templating supplied by the app itself works. Templates are invoked with three context variables:

 * `http_code`: the HTTP response code
 * `http_message`: an (English) description of the response code; if you use this in your templates, you probably want to use it as a translation string
 * `http_response_exception`: the exception that caused this, allowing you to pass further information through

## Overriding render mechanism

By default, rendering happens using a vanilla invocation of `render_to_response`. If you want to override this, for instance to add further variables into the render context, you need to call `exceptional_middleware.middleware.set_renderer` with a callable that takes three parameters `request`, `template_name` and `context`. These will be as expected for this kind of work; the renderer should return an HttpResponse instance, which will then have the correct `status_code` set by the middleware before returning to the user agent.

Alternatively, you can subclass `ExceptionalMiddleware` and override the `render()` method.

## Other features

### HTTP 404 & 500

The middleware can catch Django's Http404 and turn it into one of its own (HttpNotFound), so you can use the same render code and template layout instead of having to write a `handler404`. To enable this, set `EXCEPTIONAL_INVASION=True` in `settings.py`.

Similarly, runtime errors will be turned into HttpServerError, so you don't have to write `handler500`.

Sadly, you'll still have to install a `handler404` to catch 404s generated when the URLconf cannot find a matching URL. You may need a `handler500` if you get exceptions during that processing (which may happen for memory issues, for instance, so it's wise to install one). You can use `exceptional_middleware.handler404` and `exceptional_middleware.handler500` (which will instantiate `ExceptionalMiddleware` and get it to handle the relevant exception). 

Note that `EXCEPTIONAL_INVASION` may be better than using `handler404` and `handler500` (except in the cases it cannot manage), because your template will get the original exception object.

### DEBUG = True

Only 3xx (redirect) processing happens in the middleware if settings.DEBUG = True.

### Sentry integration

Our exceptions are /not/ marked for Sentry to ignore, since that would mean that people are raising our exceptions without having loaded our middleware, which you'd want to know about promptly.

If we catch someone else's exception, we always propagate it out to Sentry, if it's installed; we don't do this for our own exceptions except for 5xx (since they aren't really errors), or the Django 1.3 Http404 exception (similarly).

### Extra HTTP headers

Each exception has a `headers` member, which is a dictionary of HTTP header names to values, which will be added into the final HTTP response.

Although there are no provided classes that use this, you can do something like the following:

    class HttpRedirect(RareHttpResponse):
        http_code = 302
        
        def __init__(self, url, *args, **kwargs):
            super(HttpRedirect, self).__init__(*args, **kwargs)
            self.headers['Location'] = url

### Augment response

Sometimes you may want to do something else to the response at the end of the cycle on a per-exception basis. To do this, override the `augment_response()` method on your exception before raising it. It takes the `response` object:

    from exceptional_middleware.responses import HttpConflict
    class MyConflict(HttpConflict):
        def augment_response(self, response):
            response.delete_cookie('mycookie')

### Problems

If you intercept "normal" exceptions rather than letting Django's 500 processing happening, the `got_request_exception` signal is fired with the `CustomRareHttpResponses` middleware class as sender, rather than the appropriate handler driving the request. This is because there's no way (short of walking the callstack) of figuring out the right one. Unless someone can explain to me why you need to know the handler in your signal processor, it doesn't seem worth fixing.


[James Aylett](http://tartarus.org/james/computers/django/)
