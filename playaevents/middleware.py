"""A middleware which prevents non-logged-in acesss if settings.LOGGED_IN_ONLY is True.

Based on "MaintenanceMode" at: http://code.google.com/p/django-maintenancemode/
"""
from django.conf import settings
from django.core import urlresolvers

from django.conf.urls import defaults
defaults.handler503 = 'playaevents.views.logged_in_only'
defaults.__all__.append('handler503')

class LoggedInMiddleware(object):
    def process_request(self, request):
        # Allow access if middleware is not activated
        if not settings.LOGGED_IN_ONLY:
            return None

        # Allow access if the user doing the request is logged in and a
        # staff member.
        if hasattr(request, 'user') and request.user.is_staff:
            return None

        login = urlresolvers.reverse('auth_login')
        if request.path == login:
            return None

        # Otherwise show the user the 503 page
        resolver = urlresolvers.get_resolver(None)

        callback, param_dict = resolver._resolve_special('503')
        return callback(request, **param_dict)
