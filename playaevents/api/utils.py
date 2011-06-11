def rc_response(request, response, msg):
    content = {}

    if isinstance(msg, basestring):
        content.update({'message':msg})
    elif isinstance(msg, Exception):
        content.update({'exception':"%s: %s" % (msg.__class__.__name__, str(msg))})
    else:
        content = msg

    response.content = content

    return response
