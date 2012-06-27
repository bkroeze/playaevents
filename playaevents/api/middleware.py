class ContentTypeMiddleware(object):
    def process_request(self, request):
        if request.method in ('POST', 'PUT'):
            # dont break the multi-part headers !
            if 'CONTENT_TYPE' in request.META and 'boundary=' not in request.META['CONTENT_TYPE']:
                del request.META['CONTENT_TYPE']
