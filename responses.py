# Don't take this list as a suggestion that others aren't useful, but these are (probably)
# the most common. The middleware will pick up anything that's a subclass of RareHttpResponse
# raised as an exception during request processing, and render a suitable template.

class RareHttpResponse(Exception):
    http_code = 500 # because this means you've instantiated the wrong thing
    
    def augment_response(self, response):
        pass

class Http400(RareHttpResponse):
    http_code = 403
    
class Http403(RareHttpResponse):
    http_code = 403

class Http404(RareHttpResponse):
    http_code = 404

class Http409(RareHttpResponse):
    http_code = 409

class Http410(RareHttpResponse):
    http_code = 410

class Http501(RareHttpResponse):
    http_code = 501

HttpBadRequest = Http400
HttpForbidden = Http403
HttpNotFound = Http404
HttpConflict = Http409
HttpGone = Http410
HttpNotImplemented = Http501
