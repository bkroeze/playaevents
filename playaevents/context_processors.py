"""
Add common variables to all pages
"""

from django.conf import settings
from django.contrib.sites.models import Site

def add_keys(request):
    """Add commonly needed keys to request context."""

    ctx = {
        'site' : Site.objects.get_current(),
        'MEDIA_URL' : settings.MEDIA_URL,
        'debug' : settings.DEBUG
        }

    return ctx

