from django.conf.urls.defaults import patterns, include, handler500, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from playaevents.utilities import get_current_year
admin.autodiscover()

handler500 # Pyflakes

curryear = get_current_year()

urlpatterns = patterns(
    '',
    url(r'^$', 'playaevents.views.index',
        name="index"),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^api/0.2/', include('playaevents.api.urls')),

    url(r'^accounts/profile/create/$',
        'profiles.views.create_profile',
        name='profiles_create_profile'),

    url(r'^accounts/profile/edit/$',
        'profiles.views.edit_profile',
        name='profiles_edit_profile'),

    url(r'^accounts/profile/$',
        'bmprofile.views.my_profile',
        name='profiles_profile_my_detail'),

    url(r'^accounts/profile/(?P<username>\w+)/$',
        'bmprofile.views.my_profile',
        name='profiles_profile_detail'),

    url(r'^accounts/', include('registration.urls')),

    url(r'^(?P<year_year>\d{4})/$', 'playaevents.views.year_info',
        name="year_info"),

    url(r'^(?P<year_year>\d{4})/themecamp/(?P<theme_camp_id>\d{1,4})/$',
        'playaevents.views.themecampid',
        name="themecamp"),
    url(r'^themecamp/(?P<theme_camp_id>\d{1,4})/$',
        'playaevents.views.themecampid',
        {'year_year' : curryear},
        name="themecamp_thisyear"),

    url(r'^(?P<year_year>\d{4})/themecamps/$',
        'playaevents.views.themecamps',
        name="themecamps"),
    url(r'^themecamps/$',
        'playaevents.views.themecamps',
        {'year_year' : curryear},
        name="themecamps_thisyear"),

    url(r'^themecamp/(?P<theme_camp_id>\d{1,4})/$',
        'playaevents.views.themecampuuid',
        name="themecamp"),

    url(r'^(?P<year_year>\d{4})/art_installation/(?P<art_installation_id>\d{1,4})/$',
        'playaevents.views.art_installation_id',
        name="art_installation"),
    url(r'^art_installation/(?P<art_installation_id>\d{1,4})/$',
        'playaevents.views.art_installation_id',
        {'year_year' : curryear},
        name="art_installation_thisyear"),

    url(r'^(?P<year_year>\d{4})/art_installations/$',
        'playaevents.views.art_installations',
        name="art_installations"),
    url(r'^art_installations/$',
        'playaevents.views.art_installations',
        {'year_year' : curryear},
        name="art_installations_thisyear"),

    url(r'^art_installation/(?P<art_installation_id>\d{1,4})/$',
        'playaevents.views.art_installation_uuid',
        name="art_installation"),

    url(r'^(?P<year_year>\d{4})/playa_events/$',
        'playaevents.views.playa_events_home',
        name="playa_events"),
    url(r'^playa_events/$',
        'playaevents.views.playa_events_home',
        {'year_year' : curryear},
        name="playa_events_thisyear"),

    url(r'^(?P<year_year>\d{4})/csv_onetime/$',
        'playaevents.views.csv_onetime',
        name="csv_onetime"),

    url(r'^(?P<year_year>\d{4})/csv_all_day_onetime/$',
        'playaevents.views.csv_all_day_onetime',
        name="csv_all_day_onetime"),

    url(r'^(?P<year_year>\d{4})/csv_repeating/$',
        'playaevents.views.csv_repeating',
        name="csv_repeating"),

    url(r'^(?P<year_year>\d{4})/csv_all_day_repeating/$',
        'playaevents.views.csv_all_day_repeating',
        name="csv_all_day_repeating"),

    url(r'^(?P<year_year>\d{4})/playa_events/my_events/$',
        'playaevents.views.playa_events_view_mine',
        name="playa_events_view_mine"),
    url(r'^playa_events/my_events/$',
        'playaevents.views.playa_events_view_mine',
        {'year_year' : curryear},
        name="playa_events_view_mine_thisyear"),

    url(r'^(?P<year_year>\d{4})/playa_events/(?P<playa_day>\d{1})/$',
        'playaevents.views.playa_events_by_day',
        name="playa_events_by_day"),
    url(r'^playa_events/(?P<playa_day>\d{1})/$',
        'playaevents.views.playa_events_by_day',
        {'year_year' : curryear},
        name="playa_events_by_day_thisyear"),

    url(r'^(?P<year_year>\d{4})/playa_event/create/$',
        'playaevents.views.create_or_edit_event',
        name="playa_event_add"),
    url(r'^playa_event/create/$',
        'playaevents.views.create_or_edit_event',
        {'year_year' : curryear},
        name="playa_event_add_thisyear"),

    url(r'^(?P<year_year>\d{4})/playa_event/create/(?P<playa_day>\d{1})/$',
        'playaevents.views.create_or_edit_event',
        name="playa_event_add"),
    url(r'^playa_event/create/(?P<playa_day>\d{1})/$',
        'playaevents.views.create_or_edit_event',
        {'year_year' : curryear},
        name="playa_event_add_thisyear"),

    url(r'^(?P<year_year>\d{4})/playa_event/edit/(?P<playa_event_id>\d+)/$',
        'playaevents.views.create_or_edit_event',
        name="playa_event_edit"),
    url(r'^playa_event/edit/(?P<playa_event_id>\d+)/$',
        'playaevents.views.create_or_edit_event',
        {'year_year' : curryear},
        name="playa_event_edit_thisyear"),

    url(r'^(?P<year_year>\d{4})/playa_event/delete/(?P<playa_event_id>\d+)/$', 'playaevents.views.delete_event',
        name="playa_event_delete"),
    url(r'^playa_event/delete/(?P<playa_event_id>\d+)/$', 'playaevents.views.delete_event',
        {'year_year' : curryear},
        name="playa_event_delete_thisyear"),

    url(r'^(?P<year_year>\d{4})/playa_event/delete_occurrence/(?P<occurrence_id>\d+)/$',
        'playaevents.views.delete_occurrence',
        name='occurence_delete'),
    url(r'^playa_event/delete_occurrence/(?P<occurrence_id>\d+)/$', 'playaevents.views.delete_occurrence',
        {'year_year' : curryear},
        name="occurrence_delete_thisyear"),

    url(r'^(?P<year_year>\d{4})/playa_event/(?P<playa_event_id>\d+)/$', 'playaevents.views.playa_event_view',
        name="playa_event_view"),
    url(r'^playa_event/(?P<playa_event_id>\d+)/$', 'playaevents.views.playa_event_view',
        {'year_year' : curryear},
        name="playa_event_view_thisyear"),

    url(r'^playa_event/(?P<playa_event_id>\d+)/$', 'playaevents.views.playa_event_view_uuid',
        name="playa_event_view"),

    url(r'^(?P<year_year>\d{4})/playa_event/(?P<playa_event_id>\d+)/(?P<playa_occurrence_id>\d+)/$',
        'playaevents.views.playa_occurrence_view',
        name='playa_occurrence_view'),
    url(r'^playa_event/(?P<playa_event_id>\d+)/(?P<playa_occurrence_id>\d+)/$',
        'playaevents.views.playa_occurrence_view',
        {'year_year' : curryear},
        name="playa_occurrence_view_thisyear"),

    url(r'^(?P<year_year>\d{4})/playa_event/edit/(?P<playa_event_id>\d+)/(?P<playa_occurrence_id>\d+)/$',
        'playaevents.views.playa_occurrence_view',
        name="playa_occurrence_edit"),
    url(r'^playa_event/edit/(?P<playa_event_id>\d+)/(?P<playa_occurrence_id>\d+)/$',
        'playaevents.views.playa_occurrence_view',
        {'year_year' : curryear},
        name="playa_occurrence_edit_thisyear"),

    url(r'^(?P<year_year>\d{4})/playa_event/add_occurrence/(?P<playa_event_id>\d+)/$',
        'playaevents.views.playa_occurrence_view',
        name="playa_occurrence_add"),
    url(r'^playa_event/add_occurrence/(?P<playa_event_id>\d+)/$',
        'playaevents.views.playa_occurrence_view',
        {'year_year' : curryear},
        name="playa_occurrence_add_thisyear"),

    url(r'^swingtime/', include('swingtime.urls')),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + staticfiles_urlpatterns()
