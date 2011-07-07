import calendar
import itertools
import logging

from datetime import datetime, time
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.core import urlresolvers
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext, loader
from django.utils.http import urlquote_plus
from django.views.generic.create_update import delete_object
from playaevents import forms as playaforms
from playaevents import export
from playaevents.models import Year, CircularStreet, ThemeCamp, ArtInstallation, PlayaEvent
from playaevents.utilities import get_current_year
from swingtime.conf import settings as swingtime_settings
from swingtime.models import Occurrence

log = logging.getLogger(__name__)

if swingtime_settings.CALENDAR_FIRST_WEEKDAY is not None:
    calendar.setfirstweekday(swingtime_settings.CALENDAR_FIRST_WEEKDAY)

def index(request, template_name="playaevents/index.html"):
    badyears = [str(y) for y in range(2006,2009)]
    years = Year.objects.exclude(year__in=badyears).order_by('-year')

    user=request.user
    if user and type(user) != AnonymousUser:
        my_events = PlayaEvent.objects.filter(year=get_current_year(True), creator=user)
        my_events = True if my_events.count() > 0 else False
    else:
        my_events = False

    log.debug('my_events %s', my_events)
    ctx = RequestContext(request,
                         {"years" : years,
                          "my_events" : my_events})

    return render_to_response(template_name, ctx)

# ---- Year Views ----

def year_info(request, year_year):
    xyear = Year.objects.filter(year=year_year)
    streets = CircularStreet.objects.filter(year=xyear[0])
    previous = int(year_year) -1
    next = int(year_year) + 1
    return render_to_response('playaevents/year.html', {'year': xyear[0],
                        'streets' : streets,
                        'previous' : previous,
                        'next' : next,}, context_instance=RequestContext(request))

# ---- Art Installations ----

def art_installation_id(request, year_year, art_installation_id):
    xyear = Year.objects.filter(year=year_year)
    xArtInstallation = ArtInstallation.objects.get(id=art_installation_id)
    events = PlayaEvent.objects.filter(located_at_art=xArtInstallation, moderation='A')
    map = ''
    #TODO: remove traces of maps
    ctx = RequestContext(request,
                         {'year': xyear[0],
                          'art_installation': xArtInstallation,
                          'events': events,'map':map})
    return render_to_response('playaevents/art_installation.html', ctx)

def art_installation_uuid(request, art_installation_id):
    xArtInstallation = ArtInstallation.objects.get(id=art_installation_id)
    xyear = xArtInstallation.year
    events = PlayaEvent.objects.filter(located_at_art=xArtInstallation, moderation='A')
    map = ''
    ctx = RequestContext(request,
                         {'year': xyear,
                          'art_installation': xArtInstallation,
                          'events': events,
                          'map':map})

    return render_to_response('playaevents/art_installation.html', ctx)

def art_installation_name(request, year_year, art_installation_name):
    xyear = Year.objects.filter(year=year_year)
    xArtInstallation = ArtInstallation.objects.filter(year=xyear[0],slug=art_installation_name)
    ctx = RequestContext(request,
                         {'year': xyear[0],
                          'art_installation': xArtInstallation[0]})
    return render_to_response('playaevents/art_installation.html', ctx)

def art_installations(request, year_year):
    xyear = Year.objects.filter(year=year_year)
    previous = int(year_year) -1
    next = int(year_year) + 1
    ArtInstallations = ArtInstallation.objects.filter(year=xyear[0]).extra(select={'lower_name': 'lower(name)'}).order_by('lower_name')
    ctx = RequestContext(request,
                         {'year': xyear[0],
                          'art_installations': ArtInstallations,
                          'previous' : previous,
                          'next' : next,})
    return render_to_response('playaevents/art_installations.html', ctx)

#---- ThemeCamps ----

def themecamps(request, year_year):
    year = Year.objects.get(year=year_year)
    previous = int(year_year) -1
    next = int(year_year) + 1
    ThemeCamps = ThemeCamp.objects.filter(year=year).extra(select={'lower_name': 'lower(name)'}).order_by('lower_name')

    return render_to_response('playaevents/themecamps.html',
                                  {'year': year,
                                   'theme_camps': ThemeCamps,
                                   'previous' : previous,
                                   'next' : next,},
                                  context_instance=RequestContext(request))

def themecampid(request, year_year, theme_camp_id):
    year = get_object_or_404(Year, year=year_year)
    camp = get_object_or_404(ThemeCamp, id=theme_camp_id)
    events = PlayaEvent.objects.filter(hosted_by_camp=camp, moderation='A')
    map = ''
    return render_to_response('playaevents/themecamp.html',
                              {'year': year,
                               'theme_camp': camp,
                               'events': events,
                               'map':map},
                              context_instance=RequestContext(request))

def themecampuuid(request, theme_camp_id):
    camp = get_object_or_404(ThemeCamp, id=theme_camp_id)
    year = camp.year
    events = PlayaEvent.objects.filter(hosted_by_camp=camp, moderation='A')
    map = ''
    return render_to_response('playaevents/themecamp.html',
                              {'year': year,
                               'theme_camp': camp,
                               'events': events,
                               'map':map},
                              context_instance=RequestContext(request))

def themecampname(request, year_year, theme_camp_name):
    year = get_object_or_404(Year, year=year_year)
    theme_camp_name = theme_camp_name.replace('-',' ')
    camp = ThemeCamp.objects.filter(year=year,name__iexact=theme_camp_name)[0]
    events = PlayaEvent.objects.filter(hosted_by_camp=camp)
    return render_to_response('playaevents/themecamp.html',
                              {'year': year,
                               'theme_camp': camp,
                               'events':events},
                              context_instance=RequestContext(request))

# ---- PlayaEvents ----

def playa_events_home(request,
    year_year,
    template='playaevents/playa_events_home.html',
    queryset=None):

    year = get_object_or_404(Year, year=year_year)

    user=request.user
    if user and type(user) != AnonymousUser:
        my_events = PlayaEvent.objects.filter(year=year, creator=user)
        my_events = True if len(my_events)>0 else False
    else:
        my_events = False
    data = {'year':year, 'user':request.user, 'my_events':my_events}
    return render_to_response(template,
                              data,
                              context_instance=RequestContext(request))

def all_playa_events(request,
    year_year,
    template='playaevents/all_playa_events.html',
    queryset=None):

    year = get_object_or_404(Year, year=year_year)
    previous = int(year.year) -1
    next = int(year.year) + 1

    if queryset:
        queryset = queryset._clone()
    else:
        queryset = Occurrence.objects.select_related().filter(
            event__playaevent__moderation='A', event__playaevent__list_online=True)

    occurrences=queryset.filter(
        start_time__range=(year.event_start, year.event_end)).order_by('start_time')

    by_day = [(dt, list(items))
              for dt,items in
              itertools.groupby(occurrences, lambda o: o.start_time.date())]

    data = dict(year=year,by_day=by_day,previous=previous,next=next,)

    return render_to_response(template,
                              data,
                              context_instance=RequestContext(request))

def playa_events_by_day(request,
                        year_year,
                        playa_day=1,
                        template='playaevents/playa_events_by_day.html',
                        queryset=None):
    '''
    View a day's worth of playa events

    Context parameters:

    year_year: The 4 digit year
    playa_day: The current day of the festival, defined as the index into a
        list from event_start to event_end, starting with 1
    '''

    year = get_object_or_404(Year, year=year_year)
    previous = int(year.year) -1
    next = int(year.year) + 1

    event_date_list = year.daterange()
    log.debug('year daterange: %s', event_date_list)

    # Normalize playa_day to start at 0
    playa_day =int(playa_day)-1

    date_ct = len(event_date_list)-1

    if playa_day < 0:
        return HttpResponseBadRequest('Bad Request: No such playa day=%s', playa_day+1)

    if playa_day > date_ct:
        return HttpResponseBadRequest('Bad Request: No such playa day=%s', playa_day+1)

    playa_day_dt = event_date_list[playa_day]
    log.debug('playa_day: %s', playa_day_dt)
    previous_playa_day = playa_day-1
    next_playa_day = playa_day+1

    if previous_playa_day < 0:
        previous_playa_day = None
        previous_playa_day_dt = None
    else:
        previous_playa_day_dt=event_date_list[previous_playa_day]

    if next_playa_day > date_ct:
        next_playa_day = None
        next_playa_day_dt = None
    else:
        next_playa_day_dt = event_date_list[next_playa_day]

    if queryset:
        queryset = queryset._clone()
    else:
        queryset = Occurrence.objects.select_related().filter(
            event__playaevent__moderation='A',
            event__playaevent__list_online=True)

    dt_begin = datetime.combine(playa_day_dt, time(0))
    dt_end = datetime.combine(playa_day_dt, time(23,30))

    occurrences=queryset.filter(
        start_time__range=(dt_begin, dt_end)).order_by('-event__playaevent__all_day', 'start_time')

    # This is an optimization to avoid making 2 trips to the database. We want
    # a list of all the events that are all, and another with those that are
    # not.
    #
    # The below will cause 2 database round trips.
    # all_day_occurrences = occurrences.filter(event__playaevent__all_day=True)
    # timed_occurrences = occurrences.filter(event__playaevent__all_day=False)
    #
    # Instead, if we do an iterator over the original queryset, we can group
    # them in memory. It's important to sort the original queryset by all_day,
    # since it would otherwise cause strange results from itertools.groupby

    by_all_day=dict(
        [(all_day, list(items))
         for all_day, items
         in itertools.groupby(occurrences, lambda o: o.event.playaevent.all_day)])

    all_day_occurrences = by_all_day.setdefault(True)
    timed_occurrences = by_all_day.setdefault(False)
    curr_year = get_current_year()
    is_current_year = int(curr_year) == int(year_year)

    log.debug('year = %s, current_year = %s, current = %s', year, curr_year, is_current_year)

    if previous_playa_day is not None:
        previous_playa_day += 1

    if next_playa_day is not None:
        next_playa_day += 1

    data = dict(
        year = year,
        playa_day = playa_day,
        is_current_year = is_current_year,
        day = playa_day_dt,
        next = next,
        previous = previous,
        next_day = next_playa_day,
        next_day_dt = next_playa_day_dt,
        prev_day = previous_playa_day,
        prev_day_dt = previous_playa_day_dt,
        event_dates = event_date_list,
        all_day_occ = all_day_occurrences,
        timed_occ = timed_occurrences)

    log.debug('data: %s %s %s', playa_day, previous_playa_day, next_playa_day)

    return render_to_response(
        template,
        data,
        context_instance=RequestContext(request))

def playa_event_search(request, year_year):

    if year_year is not None:
        if year_year == 'all':
            log.debug('searching all years')
            year = None
        else:
            year_year = str(year_year)
            log.debug('year = %s', year_year)
            year = get_object_or_404(Year, year=year_year)
    else:
        year = get_current_year()

    searchtext = request.GET.get('search', None)
    if searchtext is None:
        raise Http404('No search text sent')

    events = PlayaEvent.objects.search(searchtext, year=year_year)
    ids = [event.pk for event in events]
    ids = tuple(ids)
    filters = { 'event__id__in' : ids }

    if year is not None:
        filters['start_time__range'] = (year.event_start, year.event_end)

    occurrences = Occurrence.objects.select_related().filter(
        **filters).order_by('start_time')

    occ = [(dt, list(items))
              for dt, items in
              itertools.groupby(occurrences, lambda o: o.start_time.date())]


    ctx = RequestContext(
        request,
        {
            'searchtext' : searchtext,
            'searchtext_q' : urlquote_plus(searchtext),
            'year' : year,
            'events' : occ,
         })
    return render_to_response('playaevents/search.html', ctx)

def playa_event_view(request,
    year_year,
    playa_event_id,
    template='playaevents/playa_event_view.html',
    event_form_class=playaforms.PlayaEventForm,
    recurrence_form_class=playaforms.PlayaEventOccurrenceForm):

    '''
    View an ``PlayaEvent`` instance and optionally update either the event or its
    occurrences.

    Context parameters:

    event: the event keyed by ``pk``
    event_form: a form object for updating the event
        recurrence_form: a form object for adding occurrences
    '''

    event = get_object_or_404(PlayaEvent, pk=playa_event_id)
    year = get_object_or_404(Year, year=year_year)

    # event_form = recurrence_form = None
    # if request.method == 'POST':
    #     if '_update' in request.POST:
    #         event_form = event_form_class(request.POST, instance=event)
    #         if event_form.is_valid():
    #             event_form.save(event)
    #             return http.HttpResponseRedirect(request.path)
    # elif '_add' in request.POST:
    #     recurrence_form = recurrence_form_class(request.POST)
    #     if recurrence_form.is_valid():
    #         recurrence_form.save(event)
    #         return http.HttpResponseRedirect(request.path)
    #     else:
    #         return http.HttpResponseBadRequest('Bad Request')

    # event_form = event_form or event_form_class(instance=event)
    # if not recurrence_form:
    #     recurrence_form = recurrence_form_class(initial=dict(year=Year.objects.get(year=year_year)))

    data = dict(
        playa_event=event,
        event_form=event_form_class,
        recurrence_form=recurrence_form_class,
        year = year)

    return render_to_response(template, data,
        context_instance=RequestContext(request))


def playa_event_view_uuid(request,
    playa_event_id,
    template='playaevents/playa_event_view.html',
    event_form_class=playaforms.PlayaEventForm,
    recurrence_form_class=playaforms.PlayaEventOccurrenceForm):
    '''
    View an ``PlayaEvent`` instance and optionally update either the event or its
    occurrences.

    Context parameters:

    event: the event keyed by ``pk``
    event_form: a form object for updating the event
        recurrence_form: a form object for adding occurrences
    '''

    event = get_object_or_404(PlayaEvent, pk=playa_event_id)

        # year_year = event.year.year
    # '''
    # event_form = recurrence_form = None
    # if request.method == 'POST':
    #     if '_update' in request.POST:
    #         event_form = event_form_class(request.POST, instance=event)
    #         if event_form.is_valid():
    #             event_form.save(event)
    #             return http.HttpResponseRedirect(request.path)
    # elif '_add' in request.POST:
    #     recurrence_form = recurrence_form_class(request.POST)
    #     if recurrence_form.is_valid():
    #         recurrence_form.save(event)
    #         return http.HttpResponseRedirect(request.path)
    #     else:
    #         return http.HttpResponseBadRequest('Bad Request')

    # event_form = event_form or event_form_class(instance=event)
    # if not recurrence_form:
    #     recurrence_form = recurrence_form_class(initial=dict(year=Year.objects.get(year=year_year)))
    # '''

    data = dict(
        playa_event=event,
        event_form=event_form_class,
        recurrence_form=recurrence_form_class)

    return render_to_response(template,
                              data,
                              context_instance=RequestContext(request))

@login_required
def playa_events_view_mine(
    request,
    year_year,
    template='playaevents/playa_view_my_events.html'):

    '''
    View all of a users PlayaEvents
    '''

    user=request.user
    year = get_object_or_404(Year, year=year_year)

    my_events = PlayaEvent.objects.filter(year=year, creator=user).order_by('moderation')
    by_moderation=dict(
        [(moderation, list(items))
         for moderation, items
         in itertools.groupby(my_events, lambda e: e.moderation)])

    approved_events = by_moderation.setdefault('A')
    unmoderated_events = by_moderation.setdefault('U')
    rejected_events = by_moderation.setdefault('R')

    data = dict(
        year = year,
        approved_events = approved_events,
        unmoderated_events = unmoderated_events,
        rejected_events = rejected_events)

    return render_to_response(
        template,
        data,
        context_instance=RequestContext(request))

@login_required
def playa_occurrence_view(request,
    year_year,
    playa_event_id,
    playa_occurrence_id=None,
    template='playaevents/occurrence_detail.html',
    form_class=playaforms.PlayaEventOccurrenceForm):

    occurrence = None

    if playa_occurrence_id is not None:
        occurrence = get_object_or_404(Occurrence,
                                       pk=playa_occurrence_id,
                                       event__pk=playa_event_id)

    event = get_object_or_404(PlayaEvent, pk=playa_event_id)
    next = urlresolvers.reverse('playa_event_view', kwargs={'year_year' : event.year.year, 'playa_event_id' : event.id})

    if request.method == 'POST':
        form = form_class(request.POST, instance=occurrence)
        if form.is_valid():
            form.save(event, playa_occurrence_id)
            if(occurrence is not None):
                request.user.message_set.create(message="Your Event Occurrence was Updated successfully.")
            else:
                request.user.message_set.create(message="Your Event Occurrence was Added successfully.")
                return HttpResponseRedirect(next)
        else:
            form = form_class(instance=occurrence)
    else:
        form = form_class(instance=occurrence)

        data = dict(
            event=event,
            occurrence=occurrence,
            form=form, next=next)

    return render_to_response(template,
                              data,
                              context_instance=RequestContext(request))

@login_required
def create_or_edit_event(request,
    year_year,
    playa_day=1,
    playa_event_id=None,
    template_name='playaevents/add_event.html'):

    user = request.user
    year = get_object_or_404(Year, year=year_year)

    instance = None
    if playa_event_id is not None:
        instance = get_object_or_404(PlayaEvent, id=playa_event_id)

    if request.method=='POST':
        form=playaforms.PlayaEventForm(data=request.POST, instance=instance)
        if form.is_valid():
            event = form.save(year_year, user, playa_event_id)
            next = '/' + event.year.year + "/playa_event/" + str(event.id)

            if playa_event_id is not None:
                request.user.message_set.create(message="Your Event Updated successfully.")
            else:
                request.user.message_set.create(message="Your Event was Added successfully. Please wait for it to be moderated")
            return HttpResponseRedirect(next)
    else:
        initial = dict(year=year_year)
        if not instance:
            event_date_list = year.daterange()
            playa_day = int(playa_day)

            if playa_day > len(event_date_list):
                return HttpResponseBadRequest('Bad Request')

            playa_day_dt = event_date_list[playa_day-1]
            initial['day'] = datetime.combine(playa_day_dt, time(9))

        form=playaforms.PlayaEventForm(initial=initial, instance=instance)

    data = {
        "form": form,
        "year": year}

    return render_to_response(
        template_name,
        data,
        context_instance=RequestContext(request))

@login_required
def delete_event(request,
    year_year,
    playa_event_id,
    next=None):

    event = get_object_or_404(PlayaEvent, id=playa_event_id)
    url = urlresolvers.reverse('playa_events_by_day', kwargs={'year_year' : event.year.year,
                                                              'playa_day' : '1'})

    return delete_object(
        request,model = PlayaEvent,
        object_id = playa_event_id,
        post_delete_redirect = url,
        template_name = "playaevents/delete_event.html",
        extra_context = dict(next=url, year=event.year),
        login_required = login_required
    )

def delete_occurrence(request,
    year_year,
    occurrence_id,
    next=None):

    occurrence = get_object_or_404(Occurrence, id=occurrence_id)
    if(Occurrence.objects.filter(event=occurrence.event).count() == 1): #Last Occurrence
        event = get_object_or_404(PlayaEvent, id=occurrence.event.id)
        next = '/'
        return delete_object(
            request,model = PlayaEvent,
            object_id = occurrence.event.id,
            post_delete_redirect = next,
            template_name = "playaevents/delete_event.html",
            extra_context = dict(next=next, year=event.year,
                                 msg="This is the only occurrence of this event. By deleting it, you will delete the entire event. Are you sure you want to do this??"),
            login_required = login_required
        )
    else:
        next = urlresolvers.reverse('playa_event_view', kwargs={'playa_event_id' : event.id})
        return delete_object(
            request,model = Occurrence,
            object_id = occurrence_id,
            post_delete_redirect = next,
            template_name = "playaevents/delete_occurrence.html",
            extra_context = dict(next=next),
            login_required = login_required
        )


@login_required
def csv_onetime(request, year_year):

    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=onetime_events.csv'
    return export.csv_onetime_events(year_year, buf=response)

@login_required
def csv_repeating(request, year_year):

    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=repeating_events.csv'
    return export.csv_repeating_events(year_year, buf=response)

@login_required
def csv_all_day_onetime(request, year_year):

    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=all_day_onetime_events.csv'
    return export.csv_all_day_onetime_events(year_year, buf=response)

@login_required
def csv_all_day_repeating(request, year_year):
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=all_day_repeating_events.csv'
    return export.csv_all_day_repeating_events(year_year, buf=response)

def temporary_unavailable(request, template_name='503.html'):
    """
    Default 503 handler, which looks for the requested URL in the redirects
    table, redirects if found, and displays 404 page if not redirected.

    Templates: `503.html`
    Context:
        request_path
            The path of the requested URL (e.g., '/app/pages/bad_page/')
    """
    t = loader.get_template(template_name) # You need to create a 503.html template.
    content = t.render(RequestContext(request, {}))
    return HttpResponse(status=503, content=content)

def logged_in_only(request):
    return temporary_unavailable(request, 'logged_in_only.html')
