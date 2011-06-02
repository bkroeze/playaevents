
from django.conf.urls.defaults import patterns, include, handler500, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
admin.autodiscover()

handler500 # Pyflakes

urlpatterns = patterns(
    '',
    url(r'^$', 'playaevents.views.index', name="index"),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^account/', include('django.contrib.auth.urls')),
    url(r'^(?P<year_year>\d{4})/$', 'playaevents.views.year_info', name="year_info"),
    url(r'^(?P<year_year>\d{4})/themecamp/(?P<theme_camp_id>\d{1,4})/$', 'playaevents.views.themecampid', name="themecamp"),
    url(r'^(?P<year_year>\d{4})/themecamps/$', 'playaevents.views.themecamps', name="themecamps"),
    url(r'^themecamp/(?P<theme_camp_id>\d{1,4})/$', 'playaevents.views.themecampuuid', name="themecamp"),
    url(r'^(?P<year_year>\d{4})/art_installation/(?P<art_installation_id>\d{1,4})/$', 'playaevents.views.art_installation_id', name="art_installation"),
    url(r'^(?P<year_year>\d{4})/art_installations/$', 'playaevents.views.art_installations', name="art_installations"),
    url(r'^art_installation/(?P<art_installation_id>\d{1,4})/$', 'playaevents.views.art_installation_uuid', name="art_installation"),
    url(r'^(?P<year_year>\d{4})/playa_events/$', 'playaevents.views.playa_events_home', name="playa_events"),
    url(r'^(?P<year_year>\d{4})/csv_onetime/$', 'playaevents.views.csv_onetime', name="csv_onetime"),
    url(r'^(?P<year_year>\d{4})/csv_all_day_onetime/$', 'playaevents.views.csv_all_day_onetime', name="csv_all_day_onetime"),
    url(r'^(?P<year_year>\d{4})/csv_repeating/$', 'playaevents.views.csv_repeating', name="csv_repeating"),
    url(r'^(?P<year_year>\d{4})/csv_all_day_repeating/$', 'playaevents.views.csv_all_day_repeating', name="csv_all_day_repeating"),
    url(r'^(?P<year_year>\d{4})/playa_events/my_events/$', 'playaevents.views.playa_events_view_mine', name="playa_events_view_mine"),
    url(r'^(?P<year_year>\d{4})/playa_events/(?P<playa_day>\d{1})/$', 'playaevents.views.playa_events_by_day', name="playa_events_by_day"),
    url(r'^(?P<year_year>\d{4})/playa_event/create/$', 'playaevents.views.create_or_edit_event', name="playa_event_add"),
    url(r'^(?P<year_year>\d{4})/playa_event/create/(?P<playa_day>\d{1})/$', 'playaevents.views.create_or_edit_event', name="playa_event_add"),
    url(r'^(?P<year_year>\d{4})/playa_event/edit/(?P<playa_event_id>\d+)/$', 'playaevents.views.create_or_edit_event', name="playa_event_edit"),
    url(r'^(?P<year_year>\d{4})/playa_event/delete/(?P<playa_event_id>\d+)/$', 'playaevents.views.delete_event', name="playa_event_delete"),
    url(r'^(?P<year_year>\d{4})/playa_event/delete_occurrence/(?P<occurrence_id>\d+)/$', 'playaevents.views.delete_occurrence', name="occurrence_delete"),
    url(r'^(?P<year_year>\d{4})/playa_event/(?P<playa_event_id>\d+)/$', 'playaevents.views.playa_event_view', name="playa_event_view"),
    url(r'^playa_event/(?P<playa_event_id>\d+)/$', 'playaevents.views.playa_event_view_uuid', name="playa_event_view"),
    url(r'^(?P<year_year>\d{4})/playa_event/(?P<playa_event_id>\d+)/(?P<playa_occurrence_id>\d+)/$', 'playaevents.views.playa_occurrence_view', name="playa_occurrence_view"),
    url(r'^(?P<year_year>\d{4})/playa_event/edit/(?P<playa_event_id>\d+)/(?P<playa_occurrence_id>\d+)/$', 'playaevents.views.playa_occurrence_view', name="playa_occurrence_edit"),
    url(r'^(?P<year_year>\d{4})/playa_event/add_occurrence/(?P<playa_event_id>\d+)/$', 'playaevents.views.playa_occurrence_view', name="playa_occurrence_add"),
    url(r'^swingtime/', include('swingtime.urls')),


)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + staticfiles_urlpatterns()
