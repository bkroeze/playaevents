from django.shortcuts import render_to_response
from django.template import RequestContext

def apidocs(request):
    ctx = RequestContext(request, {
            'server' : request.get_host()
            })
    return render_to_response('playaevents/apidocs.html', ctx)
