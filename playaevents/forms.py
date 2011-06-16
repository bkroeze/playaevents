import logging
from django import forms
from django.forms import widgets
from django.template.defaultfilters import slugify
from playaevents.models import Year, PlayaEvent, ArtInstallation, ThemeCamp
from playaevents.utilities import get_current_year
from swingtime.conf import settings as swingtime_settings
from swingtime.models import Occurrence, EventType
#from swingtime.forms import timeslot_options
from swingtime import utils
from datetime import datetime, date, time
from django.shortcuts import get_object_or_404

MINUTES_INTERVAL = swingtime_settings.TIMESLOT_INTERVAL.seconds // 60
SECONDS_INTERVAL = utils.time_delta_total_seconds(swingtime_settings.DEFAULT_OCCURRENCE_DURATION)


#-------------------------------------------------------------------------------
def timeslot_options(
    interval=swingtime_settings.TIMESLOT_INTERVAL,
    start_time=swingtime_settings.TIMESLOT_START_TIME,
    end_delta=swingtime_settings.TIMESLOT_END_TIME_DURATION,
    fmt=swingtime_settings.TIMESLOT_TIME_FORMAT):

    '''
    Create a list of time slot options for use in swingtime forms.

    The list is comprised of 2-tuples containing a 24-hour time value and a
    12-hour temporal representation of that offset.

    '''
    dt = datetime.combine(date.today(), time(0))
    dtstart = datetime.combine(dt.date(), start_time)
    dtend = dtstart + end_delta
    options = []

    while dtstart <= dtend:
        options.append((str(dtstart.time()), dtstart.strftime(fmt)))
        dtstart += interval

    return options

#-------------------------------------------------------------------------------
def timeslot_offset_options(
    interval=swingtime_settings.TIMESLOT_INTERVAL,
    start_time=swingtime_settings.TIMESLOT_START_TIME,
    end_delta=swingtime_settings.TIMESLOT_END_TIME_DURATION,
    fmt=swingtime_settings.TIMESLOT_TIME_FORMAT):

    '''
    Create a list of time slot options for use in swingtime forms.

    The list is comprised of 2-tuples containing the number of seconds since the
    start of the day and a 12-hour temporal representation of that offset.

    '''
    dt = datetime.combine(date.today(), time(0))
    dtstart = datetime.combine(dt.date(), start_time)
    dtend = dtstart + end_delta
    options = []

    delta = utils.time_delta_total_seconds(dtstart - dt)
    seconds = utils.time_delta_total_seconds(interval)
    while dtstart <= dtend:
        options.append((delta, dtstart.strftime(fmt)))
        dtstart += interval
        delta += seconds

    return options

default_timeslot_options = timeslot_options()
default_timeslot_offset_options = timeslot_offset_options()

class PlayaSplitDateTimeWidget(forms.MultiWidget):
    '''
    A Widget that splits datetime input into a custom Select for dates and
    Select widget for times.
        '''
    #---------------------------------------------------------------------------
    def __init__(self, choices, attrs=None):
        widgets = (
            forms.Select(choices=choices, attrs=attrs),
            forms.Select(choices=default_timeslot_options, attrs=attrs)
        )
        super(PlayaSplitDateTimeWidget, self).__init__(widgets, attrs)

    #---------------------------------------------------------------------------
    def decompress(self, value):
        if value:
            return [value.date(), value.time().replace(microsecond=0)]
        return [None, None]

#===============================================================================
class MultipleIntegerField(forms.MultipleChoiceField):
    '''
    A form field for handling multiple integers.

    '''

    #---------------------------------------------------------------------------
    def __init__(self, choices, size=None, label=None, widget=None):
        if widget is None:
            widget = forms.SelectMultiple(attrs={'size' : size or len(choices)})
        super(MultipleIntegerField, self).__init__(
            required=False,
            choices=choices,
            label=label,
            widget=widget,
        )

class PlayaModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name


#===============================================================================
class PlayaEventForm(forms.ModelForm):
    '''
    A simple form for adding and updating Event attributes
    '''

    curr_year=get_current_year()
    year = get_object_or_404(Year, year=curr_year)
    playa_day_choices=[(d, d.strftime('%A, %B %d')) for d in year.daterange()]
    playa_day_choices_short=[(d, d.strftime('%A %d')) for d in year.daterange()]

    title  = forms.CharField(required=True, max_length=50, label='Title')

    print_description  = forms.CharField(
        required=True, max_length=150,
        label='Print Description',
        help_text="Print description for publication in the What Where When. 150 characters max.",
        widget=widgets.Textarea(attrs={'rows':'5', 'cols':'40'}))

    description  = forms.CharField(
        required=True, max_length=2000,
        label='Online Description',
        widget=widgets.Textarea(attrs={'rows':'5', 'cols':'40'}))

    event_type = forms.ModelChoiceField(
        queryset=EventType.objects.all(),
        empty_label=None, label='Event Type')

    speaker_series = forms.BooleanField(
        required=False,
        label='Is your event part of the &ldquo;Training for a &reg;evolution&rdquo; series?',
        initial=False)

    url  = forms.URLField(
        required=False,
        verify_exists=True,
        label='URL')

    contact_email = forms.EmailField(required=False, label='Contact email')

    other_location = forms.CharField(required=False,
                                     label='Other Location', max_length=150)

    hosted_by_camp = PlayaModelChoiceField(
        required=False,
        label='Hosted By Camp',
        queryset=ThemeCamp.objects.filter(year=year).extra(
            select={'lower_name': 'lower(name)'}).order_by('lower_name'))

    located_at_art = PlayaModelChoiceField(
        required=False,
        label='Located at Art Installation',
        queryset=ArtInstallation.objects.filter(year=year).extra(
            select={'lower_name': 'lower(name)'}).order_by('lower_name'))

    start_time = forms.DateTimeField(
        label='Start', required=True,
        widget=PlayaSplitDateTimeWidget(choices=playa_day_choices))

    check_location = forms.BooleanField(
        required=False, label='Check Playa Info for camp location',
        initial=False)

    end_time = forms.DateTimeField(
        label='End',
        required=True,
        widget=PlayaSplitDateTimeWidget(choices=playa_day_choices))

    all_day = forms.BooleanField(required=False, label='All Day Event')

    repeats = forms.BooleanField(
        required=False,
        label='Repeats',
        help_text='If your event repeats at different times over several days or multiple times in a day you will need to create separate events for the different times.')

    repeat_days = MultipleIntegerField(
        playa_day_choices_short,
        label='Repeat Days',widget=forms.CheckboxSelectMultiple)

    list_online = forms.BooleanField(
        required=False,
        label='List Event Online', initial=False)

    list_contact_online = forms.BooleanField(
        required=False, label='List Contact Info Online', initial=False)

    password = forms.CharField(
        required=False, max_length=40,
        widget=widgets.PasswordInput(render_value=True),
        label='Event Password',
        help_text='On the Playa Info Directory, you will be able to use this password to update the event.')

    password_hint = forms.CharField(
        required=False, max_length=120,
        widget=widgets.Textarea(attrs={'rows':'5', 'cols':'40'}),
        label='Event Password Hint',
        help_text='On the PlayaInfo Directory, you or other people involved with the event will be able to use this hint to remember your password.')

    def __init__(self, *args, **kwargs):
        super(PlayaEventForm, self).__init__(*args, **kwargs)

        # if this is an edit, load the occurrences associated with this event
        if kwargs.get('instance'):
            occurrences = Occurrence.objects.filter(event=self.instance).all()
            # set the start and end time based on the first occurrence (all
            # should be the same date time).  If they aren't, they will be
            # after we're done editing
            self.initial.setdefault('start_time', occurrences[0].start_time)
            self.initial.setdefault('end_time', occurrences[0].end_time)
            # Set the initial form values properly for recurring events
            if len(occurrences) > 1:
                self.initial.setdefault('repeats', True)
                self.initial.setdefault('repeat_days',
                    [o.start_time.date() for o in occurrences])
        elif 'initial' in kwargs and 'day' in kwargs['initial']:
            self.initial.setdefault('start_time', kwargs['initial']['day'])
            self.initial.setdefault('end_time', kwargs['initial']['day'])


    def clean(self):
        start=self.cleaned_data['start_time']
        end = self.cleaned_data['end_time']

        if self.cleaned_data['all_day']:
            pass
        elif self.instance:
            pass
        elif end < start:
            raise forms.ValidationError("Event cannot end before it starts!")
        elif end == start:
            raise forms.ValidationError("Event cannot start and end at the same time!")


        if(self.cleaned_data['hosted_by_camp'] and self.cleaned_data['located_at_art']):
            raise forms.ValidationError("Your Event can be located at EITHER a camp or an art installation (but not both)")

        if((self.cleaned_data['hosted_by_camp'] is None) and (self.cleaned_data['located_at_art'] is None) and (len(self.cleaned_data['other_location'].strip())<1)):
            raise forms.ValidationError("Your Event must be located at a Camp, or an Art Installation or some Other Location (cant be nowhere)")

        # Always return the full collection of cleaned data.
        return self.cleaned_data

    def save(self, year, user, playa_event_id):
        if(playa_event_id is not None):
            existing_event = True
            logging.debug("existing_event = True")
            playa_event = self.instance
        else:
            existing_event = False
            logging.debug("existing_event = False")
            playa_event = PlayaEvent()

        data = self.cleaned_data

        playa_event.year=self.year
        playa_event.creator=user
        playa_event.title = data['title']
        playa_event.slug = slugify(data['title'])
        playa_event.description = data['description'].strip()
        playa_event.print_description = data['print_description'].strip()
        playa_event.event_type = data['event_type']
        playa_event.url=data['url']
        playa_event.contact_email=data['contact_email']
        playa_event.hosted_by_camp=data['hosted_by_camp']
        playa_event.located_at_art = data['located_at_art']
        playa_event.other_location=data['other_location']
        playa_event.check_location=data['check_location']
        playa_event.all_day = data['all_day']
        playa_event.list_online=data['list_online']
        playa_event.list_contact_online=data['list_contact_online']
        playa_event.list_contact_online=data['list_contact_online']
        playa_event.speaker_series=data['speaker_series']
        playa_event.password=data['password']
        playa_event.password_hint=data['password_hint']

        playa_event.save()

        if existing_event:
            # delete the existing occurrences, they will be replaced
            for occurrence in Occurrence.objects.filter(event=self.instance).all():
                occurrence.delete()

        # add occurrences
        if data['repeats']:
            if(data['all_day']):
                start_time = datetime.strptime("1/1/01 00:00", "%d/%m/%y %H:%M").time()
                end_time = datetime.strptime("1/1/01 23:59", "%d/%m/%y %H:%M").time()
            else:
                start_time = data['start_time'].time()
                end_time = data['end_time'].time()
            for day in data['repeat_days'] :
                event_start = datetime.combine(datetime.strptime(day, "%Y-%m-%d"), start_time)
                event_end = datetime.combine(datetime.strptime(day, "%Y-%m-%d"), end_time)
                playa_event.add_occurrences(event_start,event_end)
        elif(data['all_day']):
            start_time = datetime.strptime("1/1/01 00:00", "%d/%m/%y %H:%M").time()
            end_time = datetime.strptime("1/1/01 23:59", "%d/%m/%y %H:%M").time()
            event_start = datetime.combine(data['start_time'].date(), start_time)
            event_end = datetime.combine(data['end_time'].date(), end_time)
            playa_event.add_occurrences(event_start, event_end)
        else:
            playa_event.add_occurrences(data['start_time'], data['end_time'])

        return playa_event

    class Meta:
        model = PlayaEvent
        exclude = ('year', 'slug', 'location_point', 'location_track', 'creator')
        fields = ['title', 'print_description', 'description','event_type','speaker_series','url','contact_email','hosted_by_camp','located_at_art','other_location','check_location','all_day', 'start_time','end_time', 'repeats', 'repeat_days', 'list_online', 'list_contact_online', 'password', 'password_hint']

class PlayaEventOccurrenceForm(forms.ModelForm):
    '''
    For use in editing occurrences
    '''
    curr_year=get_current_year()
    year = Year.objects.filter(year=curr_year)[0]
    playa_day_choices=[(d, d.strftime('%A, %B %d')) for d in year.daterange()]
    start_time=forms.DateTimeField(label='Start', widget=PlayaSplitDateTimeWidget(choices=playa_day_choices))
    end_time=forms.DateTimeField(label='End', widget=PlayaSplitDateTimeWidget(choices=playa_day_choices))

    def clean(self):
        '''
        cleaned_data = self.cleaned_data
        start=cleaned_data.get('start_time')
        end = cleaned_data.get('end_time')

        if(self.instance.event.playaevent.all_day):
            pass
        elif end < start:
            raise forms.ValidationError("Event cannot end before it starts!")

        # Always return the full collection of cleaned data.
        return cleaned_data
        '''
        return self.cleaned_data

    def save(self, event, occurrence_id):
        if occurrence_id is not None:
            if(event.playaevent.all_day):
                start_time = datetime.strptime("1/1/01 00:00", "%d/%m/%y %H:%M").time()
                end_time = datetime.strptime("1/1/01 23:59", "%d/%m/%y %H:%M").time()
                self.instance.start_time = datetime.combine(self.cleaned_data['start_time'], start_time)
                self.instance.end_time = datetime.combine(self.cleaned_data['start_time'], end_time)
                self.instance.save()
            else:
                self.instance.start_time = self.cleaned_data['start_time']
                self.instance.end_time = self.cleaned_data['end_time']
                self.instance.save()
        else:
            # Add new Occurrence
            event.add_occurrences(self.cleaned_data['start_time'], self.cleaned_data['end_time'])
    class Meta:
        model = Occurrence
