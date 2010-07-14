# Don't take this list as a suggestion that others aren't useful, but these are (probably)
# the most common. The middleware will pick up anything that's a subclass of RareHttpResponse
# raised as an exception during request processing, and render a suitable template.

class RareHttpResponse(Exception):
    http_code = 500 # because this means you've instantiated the wrong thing
    headers = {} # extra headers for the final HTTP response
    
    def augment_response(self, response):
        pass

# We don't provide exceptions for every 400 and 500:
#
# 401 Unauthorized
# 407 ProxyAuthenticationRequired
#  are part of HTTP authentication
#
# 402 PaymentRequired
#  is reserved (and unspecified beyond its existence)

class HttpBadRequest(RareHttpResponse):
    http_code = 400

class HttpForbidden(RareHttpResponse):
    http_code = 403

class HttpNotFound(RareHttpResponse):
    http_code = 404

class HttpMethodNotAllowed(RareHttpResponse):
    # needs Allow header
    #
    # however you probably want to use Django's built in HttpResponseNotAllowed
    # (in django.http) in most cases; it's unlikely you'll detect this halfway
    # down the stack from your view function, which is generally where exceptions
    # come in handy. HttpResponseNotAllowed has a dedicated mechanism for
    # conveniently creating Allow.
    http_code = 405

class HttpNotAcceptable(RareHttpResponse):
    http_code = 406

class HttpRequestTimeout(RareHttpResponse):
    http_code = 408

class HttpConflict(RareHttpResponse):
    http_code = 409

class HttpGone(RareHttpResponse):
    http_code = 410

class HttpLengthRequired(RareHttpResponse):
    http_code = 411

class HttpPreconditionFailed(RareHttpResponse):
    http_code = 412

class HttpRequestEntityTooLarge(RareHttpResponse):
    # may include Retry-After
    http_code = 413

class HttpRequestURITooLong(RareHttpResponse):
    http_code = 414

class HttpUnsupportedMediaType(RareHttpResponse):
    http_code = 415

class HttpRequestedRangeNotSatisfiable(RareHttpResponse):
    # should include Content-Range
    # (must not use multipart/byteranges)
    http_code = 416

class HttpExpectationFailed(RareHttpResponse):
    http_code = 417

class HttpServerError(RareHttpResponse):
    http_code = 500

class HttpNotImplemented(RareHttpResponse):
    http_code = 501

class HttpBadGateway(RareHttpResponse):
    http_code = 502

class HttpServiceUnavailable(RareHttpResponse):
    # may include Retry-After
    http_code = 503

class HttpGatewayTimeout(RareHttpResponse):
    http_code = 504

class HttpVersionNotSupported(RareHttpResponse):
    http_code = 505
