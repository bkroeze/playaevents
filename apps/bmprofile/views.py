#from django.shortcuts import get_object_or_404
from django.http import Http404
from profiles.views import profile_detail
import logging

log = logging.getLogger(__name__)

def my_profile(request, username=None):
    if request.user.is_anonymous():
        return Http404('No user, please login')

    profile = request.user.profile

    if profile :
        if username is not None and profile.user.username != username:
            raise Http404('Cannot view other users: %s != %s', profile.user.username, username)

        log.debug('my_profile step 2 for %s', request.user.username)
        return profile_detail(request, request.user.username)
    else:
        raise Http404('Not logged in')

