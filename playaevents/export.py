from playaevents.models import Year, PlayaEvent
import csv
from django.db.models import Count
import itertools
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

def _map_to_ascii(t):
    punctuation = { 0x2018:0x27, 0x2019:0x27, 0x201C:0x22, 0x201D:0x22 }
    new_string=t.translate(punctuation).encode('ascii', 'xmlcharrefreplace')
    return new_string

def _tf(val):
    if val is None:
        return False
    return val

def csv_onetime_events(year_year, buf = None):
    year= Year.objects.filter(year=year_year)

    events = PlayaEvent.objects.filter(
        year=year, moderation='A').order_by('id').annotate(num_occurrences=Count('occurrence'))[:980]

    timed_events= itertools.ifilter(lambda e: e.all_day==False, events)

    onetime_events = list(itertools.ifilter(lambda e: e.num_occurrences==1, timed_events))

    if buf is None:
        buf = StringIO()

    writer = csv.writer(buf)
    writer.writerow(
        ['Title',
         'Description',
         'Start Date',
         'Start Time',
         'End Date',
         'End Time',
         'Location',
         'Placement',
         'Event Type',
         'Speaker Series'])

    for e in onetime_events:
        o = e.next_occurrence()
        title = _map_to_ascii(e.title)
        start_date = o.start_time.strftime('%A')
        if o.start_time.day == 7:
            start_date = 'Lastday'
        start_time = o.start_time.strftime('%H:%M')
        end_date = o.end_time.strftime('%a %b %d')
        if o.end_time.day == 7:
            end_date = 'Lastday'
        end_time = o.end_time.strftime('%H:%M')
        print_description = e.print_description
        if not print_description:
            print_description = e.description
        print_description = _map_to_ascii(e.print_description)
        placement_location = ''
        if e.check_location:
            location = 'Check @ Play Info'
            placement_location = 'Check @ Playa Info'
        if e.other_location:
            location = e.other_location
        elif e.located_at_art:
            location = e.located_at_art.name
            placement_location = e.located_at_art.location_string
        else:
            location = e.hosted_by_camp.name
            placement_location = e.hosted_by_camp.location_string
        event_type = e.event_type

        speaker = _tf(e.speaker_series)

        writer.writerow(
            [title,
             print_description,
             start_date,
             start_time,
             end_date,
             end_time,
             location,
             placement_location,
             event_type,
             speaker])

    return buf

def csv_repeating_events(year_year, buf = None):

    year = Year.objects.filter(year=year_year)
    events = PlayaEvent.objects.filter(
        year=year, moderation='A').order_by('id').annotate(num_occurrences=Count('occurrence'))[:980]

    timed_events= itertools.ifilter(lambda e: e.all_day==False, events)

    repeating_events = list(itertools.ifilter(lambda e: e.num_occurrences>1, timed_events))

    if buf is None:
        buf = StringIO()

    writer = csv.writer(buf)

    writer.writerow(
        ['Title',
         'Description',
         'Start Date',
         'Start Time',
         'End Date',
         'End Time',
         'Location',
         'Placement',
         'Event Type',
         'Speaker Series'])

    for e in repeating_events:
        occurrences = e.upcoming_occurrences().order_by('start_time')
        title = _map_to_ascii(e.title)
        print_description = e.print_description
        if not print_description:
            print_description = e.description
        print_description = _map_to_ascii(e.print_description)
        placement_location = ''
        if e.check_location:
            location = 'Check @ Play Info'
            placement_location = 'Check @ Playa Info'
        if e.other_location:
            location = e.other_location
        elif e.located_at_art:
            location = e.located_at_art.name
            placement_location = e.located_at_art.location_string
        else:
            location = e.hosted_by_camp.name
            placement_location = e.hosted_by_camp.location_string
        event_type = e.event_type
        speaker = _tf(e.speaker_series)
        for o in occurrences:
            start_date = o.start_time.strftime('%A')
            if o.start_time.day == 7:
                start_date = 'Lastday'
            start_time = o.start_time.strftime('%H:%M')
            end_date = o.end_time.strftime('%a %b %d')
            if o.end_time.day == 7:
                end_date = 'Lastday'
            end_time = o.end_time.strftime('%H:%M')


            writer.writerow(
                [title,
                 print_description,
                 start_date,
                 start_time,
                 end_date,
                 end_time,
                 location,
                 placement_location,
                 event_type,
                 speaker])

            # Blank out the descriptive items of the event so we only have base data for the repeat occurrences
            title=''
            print_description = ''
            location = ''
            placement_location=''
            event_type=''
            speaker=''

    return buf

def csv_all_day_onetime_events(year_year, buf=None):
    year= Year.objects.filter(year=year_year)
    events = PlayaEvent.objects.filter(year=year, moderation='A').order_by('id').annotate(num_occurrences=Count('occurrence'))[:980]
    all_day_events= itertools.ifilter(lambda e: e.all_day==True, events)

    onetime_all_day_events = list(itertools.ifilter(lambda e: e.num_occurrences==1, all_day_events))

    if buf is None:
        buf = StringIO()

    writer = csv.writer(buf)

    writer.writerow(
        ['Title',
         'Description',
         'Start Date',
         'Location',
         'Placement',
         'Event Type',
         'Speaker Series'])

    for e in onetime_all_day_events:
        occurrences = e.upcoming_occurrences().order_by('start_time')
        title = _map_to_ascii(e.title)
        print_description = e.print_description
        if not print_description:
            print_description = e.description
        print_description = _map_to_ascii(e.print_description)
        placement_location = ''
        if e.check_location:
            location = 'Check @ Play Info'
            placement_location = 'Check @ Playa Info'
        if e.other_location:
            location = e.other_location
        elif e.located_at_art:
            location = e.located_at_art.name
            placement_location = e.located_at_art.location_string
        else:
            location = e.hosted_by_camp.name
            placement_location = e.hosted_by_camp.location_string
        event_type = e.event_type
        speaker = _tf(e.speaker_series)
        for o in occurrences:
            start_date = o.start_time.strftime('%A')
            if o.start_time.day == 7:
                start_date = 'Lastday'

            writer.writerow(
                [title,
                 print_description,
                 start_date,
                 location,
                 placement_location,
                 event_type,
                 speaker])
            # Blank out the descriptive items of the event so we only have base data for the repeat occurrences
            title=''
            print_description = ''
            location = ''
            placement_location=''
            event_type=''
            speaker=''

    return buf

def csv_all_day_repeating_events(year_year, buf = None):
    year= Year.objects.filter(year=year_year)
    events = PlayaEvent.objects.filter(
        year=year, moderation='A').order_by('id').annotate(num_occurrences=Count('occurrence'))

    all_day_events= itertools.ifilter(lambda e: e.all_day==True, events)

    repeating_events = list(itertools.ifilter(lambda e: e.num_occurrences>1, all_day_events))

    if buf is None:
        buf = StringIO()

    writer = csv.writer(buf)

    writer.writerow(
        ['Title',
         'Description',
         'Start Date',
         'Location',
         'Placement',
         'Event Type',
         'Speaker Series'])

    for e in repeating_events:
        occurrences = e.upcoming_occurrences().order_by('start_time')
        title = _map_to_ascii(e.title)
        print_description = e.print_description
        if not print_description:
            print_description = e.description
        print_description = _map_to_ascii(e.print_description)
        placement_location = ''
        if e.check_location:
            location = 'Check @ Play Info'
            placement_location = 'Check @ Playa Info'
        if e.other_location:
            location = e.other_location
        elif e.located_at_art:
            location = e.located_at_art.name
            placement_location = e.located_at_art.location_string
        else:
            location = e.hosted_by_camp.name
            placement_location = e.hosted_by_camp.location_string
        event_type = e.event_type
        speaker = _tf(e.speaker_series)

        for o in occurrences:
            start_date = o.start_time.strftime('%A')
            if o.start_time.day == 7:
                start_date = 'Lastday'


            writer.writerow(
                [title,
                 print_description,
                 start_date,
                 location,
                 placement_location,
                 event_type,
                 speaker])

            # Blank out the descriptive items of the event so we only have base data for the repeat occurrences
            title=''
            print_description = ''
            location = ''
            placement_location=''
            event_type=''
            speaker=''

    return buf

