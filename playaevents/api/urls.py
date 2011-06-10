from django.conf import settings
from django.conf.urls.defaults import patterns, url
from piston.resource import Resource
from playaevents.api import handlers
from signedauth.authentication import IPUserAuthentication
from playaevents.api.views import apidocs

auth = IPUserAuthentication()

year_handler = Resource(handlers.YearHandler, authentication=auth)
camp_handler = Resource(handlers.ThemeCampHandler, authentication=auth)
art_handler = Resource(handlers.ArtInstallationHandler, authentication=auth)
event_handler = Resource(handlers.PlayaEventHandler, authentication=auth)
user_handler = Resource(handlers.UserHandler, authentication=auth)
cstreet_handler = Resource(handlers.CircularStreetHandler, authentication=auth)
tstreet_handler = Resource(handlers.TimeStreetHandler, authentication=auth)

urlpatterns = patterns(
    '',
    url(r'^docs/', apidocs),
    url(r'^user/', user_handler),
    url(r'^year/', year_handler),
    url(r'^(?P<year_year>\d{4})/camp/(?P<camp_id>\d+)/$', camp_handler),
    url(r'^(?P<year_year>\d{4})/camp/', camp_handler),
    url(r'^(?P<year_year>\d{4})/art/(?P<art_id>\d+)/$', art_handler),
    url(r'^(?P<year_year>\d{4})/art/', art_handler),
    url(r'^(?P<year_year>\d{4})/event/(?P<playa_event_id>\d+)/$', event_handler),
    url(r'^(?P<year_year>\d{4})/event/', event_handler),
    url(r'^(?P<year_year>\d{4})/cstreet/', cstreet_handler),
    url(r'^(?P<year_year>\d{4})/tstreet/', tstreet_handler),
)

if settings.DEBUG:
    from signedauth.explore.handlers import EchoHandler
    echo = Resource(handler=EchoHandler, authentication=auth)

    urlpatterns += patterns(
        '',
        url(r'^explore/$', 'signedauth.explore.views.explore', name="exploreform"),
        url(r'^ipecho\.(?P<emitter_format>[-\w]+)/$', echo, name="echohandler")
        )
