from django.contrib.auth.models import User
from piston.emitters import Emitter, JSONEmitter
from piston.handler import BaseHandler, AnonymousBaseHandler
from piston.utils import rc
from playaevents.api.utils import rc_response
from playaevents.api.emitters import TimeAwareJSONEmitter
from playaevents.models import Year, CircularStreet, ThemeCamp, ArtInstallation, PlayaEvent, TimeStreet
from swingtime.models import Occurrence, EventType

try:
    import json
except ImportError:
    import simplejson as json

import logging

log = logging.getLogger(__name__)

JSONEmitter.unregister('json')
Emitter.register('json', TimeAwareJSONEmitter, content_type='text/javascript; charset=utf-8')

art_fields = ('id', 'name', ('year', ('id','year')),
              'slug', 'artist', 'description', 'url',
              'contact_email', 'circular_street', 'time_address',
              'distance', 'location_string')
event_fields = ('id', 'title','description',
                'print_description', ('year', ('id','year')),
                'slug', 'event_type', ('hosted_by_camp', ('id','name')),
                ('located_at_art', ('id','name')),
                'other_location', 'check_location',
                'url', 'all_day',
                ('occurrence_set', ('start_time', 'end_time')))
event_full_fields = event_fields + (
                'contact_email',
                'password_hint',
                'password',
                'moderation',
                'list_online',
                'list_contact_online',
                'speaker_series')
camp_fields = ('id', ('year', ('id','year')),
               'name', 'description', 'url', 'contact_email')
camp_full_fields = camp_fields + (
               'location_string',
               ('circular_street', ('name',)),
               'time_address')
cstreet_fields = ('id', ('year', ('id','year')),
                  'name', 'order', 'width',
                  'distance_from_center')
tstreet_fields = ('id', ('year', ('id','year')),
                  'hour', 'minute', 'name', 'width')
year_fields = ('id', 'location', 'participants', 'theme')
user_fields = ('id', 'username', 'first_name', 'last_name', 'active')

class BaseArtHandler(object):
    model = ArtInstallation
    fields = art_fields

    def read(self, request, year_year=None, art_id=None):
        base = ArtInstallation.objects.filter()
        if(year_year):
            try:
                year = Year.objects.get(year=year_year)
            except Year.DoesNotExist:
                return rc_response(request, rc.NOT_HERE, 'Year not found #%s' % year_year)

            if art_id:
                art = base.filter(year=year,id=art_id)
            else:
                art = base.filter(year=year)
            return art
        else:
            return base.all()

class AnonymousArtInstallationHandler(BaseArtHandler, AnonymousBaseHandler):
    allow_methods = ('GET',)
    model = ArtInstallation

    def read(self, request, year_year=None, art_id=None):
        log.debug('AnonymousArtInstallationHandler GET')
        return super(AnonymousArtInstallationHandler, self).read(request, year_year=year_year, art_id=art_id)


class ArtInstallationHandler(BaseArtHandler, BaseHandler):
    allow_methods = ('GET','PUT','POST')
    anonymous = AnonymousArtInstallationHandler

    def read(self, request, year_year=None, art_id=None):
        log.debug('ArtInstallationHandler GET')
        return super(ArtInstallationHandler, self).read(request, year_year=year_year, art_id=art_id)

    def _create_or_update(self, request, year_year=None, art_id=None):
        user = request.user
        if not user.get_profile().api_allowed:
            return rc_response(request, rc.BAD_REQUEST, 'User not permitted to use the API')

        method = request.method

        if method == "PUT":
            data = request.PUT.copy()
        elif method == "POST":
            data = request.POST.copy()
        else:
            return rc_response(request, rc.BAD_REQUEST, 'Bad request method: %s' % method)

        if year_year and 'year' not in data:
            data['year'] = year_year

        if not (data and user):
            log.debug('Bad request: data=%s, user=%s', data, user)
            return rc_response(request, rc.BAD_REQUEST, 'Missing critical information')

        log.debug('data for create_or_update: %s', data)

        obj = None

        if art_id:
            try:
                obj = ArtInstallation.objects.get(pk=art_id)
                log.debug('got art #%i for update', obj.id)

            except ArtInstallation.DoesNotExist:
                return rc_response(request, rc.NOT_HERE, 'ArtInstallation not found #%s' % art_id)

            # no updating the year!
            if 'year' in data:
                del data['year']

        elif 'bm_fm_id' in data:
            log.debug('trying to get art installation from DB: bm_fm_id = %s', data['bm_fm_id'])
            try:
                obj = ArtInstallation.objects.get(bm_fm_id=int(data['bm_fm_id']))
            except ArtInstallation.DoesNotExist:
                pass

        if obj is None:
            log.debug('creating new ArtInstallation')
            obj = ArtInstallation()

        # get rid of illegal-to-update attributes
        for key in ('id','pk'):
            if key in data:
                del data[key]

        # now loop through the data, updating as needed
        if 'year' in data:
            try:
                year = Year.objects.get(year=data['year'])
            except Year.DoesNotExist:
                return rc_response(request, rc.NOT_HERE, 'No such year: %s' % data['year'])

            obj.year = year

        # text fields
        for key in ('description', 'name', 'artist', 'contact_email', 'url', 'slug', 'time_address', 'distance'):
            if key in data:
                val = data[key]
                log.debug('setting %s=%s', key, val)
                setattr(obj, key, val)

        #bm_fm_id
        if 'bm_fm_id' in data:
            obj.bm_fm_id = int(data['bm_fm_id'])

        obj.save()

        if method == 'PUT':
            response = rc.ALL_OK

        else:
            response = rc.CREATED

        response.content = json.dumps({'pk' : obj.id})
        return response

    def create(self, request, year_year=None, art_id=None):
        log.debug('ArtInstallationHandler CREATE: %s %s', year_year, art_id)
        ret = self._create_or_update(request, year_year=year_year, art_id=art_id)
        log.debug('create done')
        return ret

    def update(self, request, year_year=None, art_id=None):
        log.debug('ArtInstallationHandler UPDATE: %s %s', year_year, art_id)
        return self._create_or_update(request, year_year=year_year, art_id=art_id)


class BasePlayaEventHandler(object):
    model = PlayaEvent

    def read(self, request, year_year=None, playa_event_id=None, online_only = True):
        if(year_year):
            try:
                year = Year.objects.get(year=year_year)
            except Year.DoesNotExist:
                return rc_response(request, rc.NOT_HERE, 'Year not found #%s' % year_year)

            kw = {}
            if online_only:
                kw['list_online'] = True

            if playa_event_id:
                kw['year'] = year
                kw['id'] = playa_event_id
                events = PlayaEvent.objects.filter(*kw)

            else:
                if(request.GET.get('start_time') and request.GET.get('end_time')):
                    event_list = Occurrence.objects.filter(start_time__gte=request.GET.get('start_time'), end_time__lte=request.GET.get('end_time')).values_list('event', flat=True)

                    kw['id__in'] = event_list
                    events = PlayaEvent.objects.filter(**kw)

                elif(request.GET.get('start_time')):
                    event_list = Occurrence.objects.filter(start_time__gte=request.GET.get('start_time')).values_list('event', flat=True)

                    kw['id__in'] = event_list
                    events = PlayaEvent.objects.filter(**kw)

                elif(request.GET.get('end_time')):
                    event_list = Occurrence.objects.filter(end_time__lte=request.GET.get('end_time')).values_list('event', flat=True)

                    kw['id__in'] = event_list
                    events = PlayaEvent.objects.filter(**kw)
                else:
                    kw['year'] = year
                    kw['moderation'] = 'A'
                    events = PlayaEvent.objects.get_and_cache(**kw)

            return events
        else:
            return PlayaEvent.objects.get_and_cache(moderation='A', list_online=True)


class AnonymousPlayaEventHandler(BasePlayaEventHandler, AnonymousBaseHandler):
    fields = event_fields
    allow_methods = ('GET',)

    def read(self, request, year_year=None, playa_event_id=None):
        log.debug('AnonymousPlayaEventHandler GET')
        return super(AnonymousPlayaEventHandler, self).read(request, year_year=year_year, playa_event_id=playa_event_id)

class PlayaEventHandler(BasePlayaEventHandler, BaseHandler):
    fields = event_full_fields
    allow_methods = ('GET', 'DELETE', 'PUT', 'POST')
    anonymous = AnonymousPlayaEventHandler

    def _create_or_update(self, request, year_year=None, playa_event_id=None):
        user = request.user
        if not user.get_profile().api_allowed:
            return rc_response(request, rc.BAD_REQUEST, 'User not permitted to use the API')

        method = request.method

        if method == "PUT":
            data = request.PUT.copy()
        elif method == "POST":
            data = request.POST.copy()
        else:
            return rc_response(request, rc.BAD_REQUEST, 'Bad request method: %s' % method)

        if year_year and 'year' not in data:
            data['year'] = year_year

        if not (data and user):
            log.debug('Bad request: data=%s, user=%s', data, user)
            return rc_response(request, rc.BAD_REQUEST, 'Missing critical information')

        log.debug('data for create_or_update: %s', data)

        if playa_event_id:
            try:
                obj = PlayaEvent.objects.get(pk=playa_event_id)
                log.debug('got playaevent #%i for update', obj.id)

            except PlayaEvent.DoesNotExist:
                return rc_response(request, rc.NOT_HERE, 'Event not found #%s' % playa_event_id)

            # no updating the year!
            if 'year' in data:
                del data['year']

        else:
            log.debug('creating new event')
            obj = PlayaEvent()
            obj.creator = user
            if not 'event_type' in data:
                event_type = EventType.objects.get(pk=1)
            else:
                try:
                    event_type = EventType.objects.get(abbr=data['event_type'])
                except EventType.DoesNotExist:
                    return rc_response(request, rc.NOT_HERE, 'No such EventType: %s' % data['event_type'])

            obj.event_type = event_type

        # get rid of illegal-to-update attributes
        for key in ('id','pk'):
            if key in data:
                del data[key]

        # now loop through the data, updating as needed
        if 'year' in data:
            try:
                year = Year.objects.get(year=data['year'])
            except Year.DoesNotExist:
                return rc_response(request, rc.NOT_HERE, 'No such year: %s' % data['year'])

            obj.year = year

        # text fields
        for key in ('print_description', 'url', 'contact_email', 'other_location', 'slug'):
            if key in data:
                val = data[key]
                log.debug('setting %s=%s', key, val)
                setattr(obj, key, val)

        # moderation
        if 'moderation' in data:
            modkey = data['moderation'].upper()
            if modkey in ('U','A','R'):
                log.debug('setting moderation=%s', modkey)
                obj.moderation = modkey

        if 'hosted_by_camp' in data:
            key = data['hosted_by_camp']
            try:
                camp = ThemeCamp.objects.get(pk=key)
                log.debug('located at camp: %s', camp)
                obj.hosted_by_camp = camp
            except ThemeCamp.DoesNotExist:
                return rc_response(request, rc.NOT_HERE, 'No such camp: %s' % key)

        if 'located_at_art' in data:
            key = data['located_at_art']
            try:
                art = ArtInstallation.objects.get(pk=key)
                log.debug('located at art: %s', art)
                obj.located_at_art = art
            except ArtInstallation.DoesNotExist:
                return rc_response(request, rc.NOT_HERE, 'No such art: %s' % key)

        # booleans
        for key in ('check_location', 'all_day', 'list_online', 'list_contact_online'):
            if key in data:
                val = data[key].upper()
                val = val in ('1', 'T', 'Y', 'YES', 'TRUE', 'ON')
                log.debug('setting %s=%s', key, val)
                setattr(obj, key, val)

        obj.save()

        if method == 'PUT':
            response = rc.ALL_OK

        else:
            response = rc.CREATED

        response.content = json.dumps({'pk' : obj.id})
        return response

    def read(self, request, year_year=None, playa_event_id=None):
        log.debug('PlayaEventHandler GET')
        return super(PlayaEventHandler, self).read(request,
                                                   year_year=year_year,
                                                   playa_event_id=playa_event_id,
                                                   online_only=False)

    def delete(self, request, year_year=None, playa_event_id=None):
        log.debug('PlayaEventHandler DELETE: %s %s', year_year, playa_event_id)
        user = request.user
        if not user.get_profile().api_allowed:
            return rc_response(request, rc.BAD_REQUEST, 'User not permitted to use the API')

        if (playa_event_id):
            try:
                obj = PlayaEvent.objects.get(pk=playa_event_id)
                obj.moderation = 'R'
                obj.save()
                log.debug('Marking Event #%s rejected', playa_event_id)
                return rc_response(request, rc.DELETED, 'Event rejected #%s' % playa_event_id)
            except PlayaEvent.DoesNotExist:
                return rc_response(request, rc.NOT_HERE, 'Event not found #%s' % playa_event_id)
        else:
            return rc_response(request, rc.NOT_HERE, 'Event ID required')

    def create(self, request, year_year=None, playa_event_id=None):
        log.debug('PlayaEventHandler CREATE: %s %s', year_year, playa_event_id)
        ret = self._create_or_update(request, year_year=year_year, playa_event_id=playa_event_id)
        log.debug('create done')
        return ret

    def update(self, request, year_year=None, playa_event_id=None):
        log.debug('PlayaEventHandler UPDATE: %s %s', year_year, playa_event_id)
        return self._create_or_update(request, year_year=year_year, playa_event_id=playa_event_id)


class AnonymousThemeCampHandler(AnonymousBaseHandler):
    model = ThemeCamp
    fields = camp_fields

    allow_methods = ('GET',)

    def read(self, request, year_year=None, camp_id=None):
        if(year_year):
            try:
                year = Year.objects.get(year=year_year)
            except Year.DoesNotExist:
                return rc_response(request, rc.NOT_HERE, 'Year not found #%s' % year_year)

            if(camp_id):
                camp = ThemeCamp.objects.filter(year=year,id=camp_id,list_online=True)
            else:
                camp = ThemeCamp.objects.get_and_cache(year=year,list_online=True)
            return camp
        else:
            return ThemeCamp.objects.get_and_cache(list_online=True)


class ThemeCampHandler(BaseHandler):
    model = ThemeCamp
    fields = camp_full_fields

    allow_methods = ('GET', 'DELETE', 'PUT', 'POST')
    anonymous = AnonymousThemeCampHandler

    def _create_or_update(self, request, year_year=None, camp_id=None):
        user = request.user
        if not user.get_profile().api_allowed:
            return rc_response(request, rc.BAD_REQUEST, 'User not permitted to use the API')

        method = request.method

        if method == "PUT":
            data = request.PUT.copy()
        elif method == "POST":
            data = request.POST.copy()
        else:
            return rc_response(request, rc.BAD_REQUEST, 'Bad request method: %s' % method)

        if year_year and 'year' not in data:
            data['year'] = year_year

        if not (data and user):
            log.debug('Bad request: data=%s, user=%s', data, user)
            return rc_response(request, rc.BAD_REQUEST, 'Missing critical information')

        log.debug('data for create_or_update: %s', data)

        obj = None

        if camp_id:
            try:
                obj = ThemeCamp.objects.get(pk=camp_id)
                log.debug('got themecamp #%i for update', obj.id)

            except ThemeCamp.DoesNotExist:
                return rc_response(request, rc.NOT_HERE, 'ThemeCamp not found #%s' % camp_id)

            # no updating the year!
            if 'year' in data:
                del data['year']

        elif 'bm_fm_id' in data:
            log.debug('trying to get ThemeCamp from DB: bm_fm_id = %s', data['bm_fm_id'])
            try:
                obj = ThemeCamp.objects.get(bm_fm_id=int(data['bm_fm_id']))
            except ThemeCamp.DoesNotExist:
                pass

        if obj is None:
            log.debug('creating new event')
            obj = ThemeCamp()
            obj.creator = user

        # get rid of illegal-to-update attributes
        for key in ('id','pk','deleted'):
            if key in data:
                del data[key]

        # now loop through the data, updating as needed
        if 'year' in data:
            try:
                year = Year.objects.get(year=data['year'])
            except Year.DoesNotExist:
                return rc_response(request, rc.NOT_HERE, 'No such year: %s' % data['year'])

            obj.year = year

        if 'circular_street' in data:
            key = data['circular_street']
            try:
                street = CircularStreet.objects.get(pk=key)
                obj.circular_street = street
            except CircularStreet.DoesNotExist:
                return rc_response(request, rc.NOT_HERE, 'No such CircularStreet: %s' % key)
        elif 'circular_street_name' in data:
            key = data['circular_street_name']
            try:
                street = CircularStreet.objects.get(name__istartswith=key[0:2], year=obj.year)
                obj.circular_street = street
            except CircularStreet.DoesNotExist:
                return rc_response(request, rc.NOT_HERE, 'No such CircularStreet: %s' % key)


        if 'time_street' in data:
            key = data['time_street']
            try:
                street = TimeStreet.objects.get(pk=key)
                obj.time_address = street.name
            except TimeStreet.DoesNotExist:
                obj.time_address = data['time_address']
        elif 'time_street_name' in data:
            key = data['time_street_name']
            try:
                street = TimeStreet.objects.get(name=key, year=obj.year)
                obj.time_address = street.name
            except TimeStreet.DoesNotExist:
                obj.time_address = data['time_street_name']

        # text fields
        for key in ('name','description', 'url', 'hometown', 'location_string', 'slug'):
            if key in data:
                val = data[key]
                log.debug('setting %s=%s', key, val)
                setattr(obj, key, val)

        # booleans
        for key in ('list_online',):
            if key in data:
                val = data[key].upper()
                val = val in ('1', 'T', 'Y', 'YES', 'TRUE', 'ON')
                log.debug('setting %s=%s', key, val)
                setattr(obj, key, val)

        obj.save()

        if method == 'PUT':
            response = rc.ALL_OK

        else:
            response = rc.CREATED

        response.content = json.dumps({'pk' : obj.id})
        return response

    def read(self, request, year_year=None, camp_id=None):
        if(year_year):
            try:
                year = Year.objects.get(year=year_year)
            except Year.DoesNotExist:
                return rc_response(request, rc.NOT_HERE, 'Year not found #%s' % year_year)

            if(camp_id):
                camp = ThemeCamp.all_objects.filter(year=year,id=camp_id)
            else:
                camp = ThemeCamp.all_objects.get_and_cache(year=year)
            return camp
        else:
            return ThemeCamp.all_objects.get_and_cache()

    def delete(self, request, year_year=None, camp_id=None):
        log.debug('ThemeCampHandler DELETE: %s %s', year_year, camp_id)
        user = request.user
        if not user.get_profile().api_allowed:
            return rc_response(request, rc.BAD_REQUEST, 'User not permitted to use the API')

        if (camp_id):
            try:
                obj = ThemeCamp.objects.get(pk=camp_id)
                obj.deleted = True
                obj.save()
                log.debug('Marking Camp #%s deleted', camp_id)
                return rc_response(request, rc.DELETED, 'Camp deleted #%s' % camp_id)
            except ThemeCamp.DoesNotExist:
                return rc_response(request, rc.NOT_HERE, 'Camp not found #%s' % camp_id)
        else:
            return rc_response(request, rc.NOT_HERE, 'Camp ID required')

    def create(self, request, year_year=None, camp_id=None):
        log.debug('ThemeCampHandler CREATE: %s %s', year_year, camp_id)
        ret = self._create_or_update(request, year_year=year_year, camp_id=camp_id)
        log.debug('create done')
        return ret

    def update(self, request, year_year=None, camp_id=None):
        log.debug('ThemeCampHandler UPDATE: %s %s', year_year, camp_id)
        return self._create_or_update(request, year_year=year_year, camp_id=camp_id)


class AnonymousCircularStreetHandler(AnonymousBaseHandler):
    allow_methods = ('GET',)
    model = CircularStreet
    fields = cstreet_fields
    def read(self, request, year_year=None):
        base = CircularStreet.objects.filter()
        if(year_year):
            try:
                year = Year.objects.get(year=year_year)
            except Year.DoesNotExist:
                return rc_response(request, rc.NOT_HERE, 'Year not found #%s' % year_year)

            cstreet = CircularStreet.objects.filter(year=year)
            return cstreet
        else:
            return base.all()


class CircularStreetHandler(BaseHandler):
    allow_methods = ('GET',)
    model = CircularStreet
    fields = cstreet_fields
    anonymous = AnonymousCircularStreetHandler

class AnonymousTimeStreetHandler(AnonymousBaseHandler):
    allow_methods = ('GET',)
    model = TimeStreet
    fields = tstreet_fields
    def read(self, request, year_year=None):
        base = TimeStreet.objects.filter()
        if(year_year):
            try:
                year = Year.objects.get(year=year_year)
            except Year.DoesNotExist:
                return rc_response(request, rc.NOT_HERE, 'Year not found #%s' % year_year)

            tstreet = TimeStreet.objects.filter(year=year)
            return tstreet
        else:
            return base.all()


class TimeStreetHandler(BaseHandler):
    allow_methods = ('GET',)
    model = TimeStreet
    fields = tstreet_fields
    anonymous = AnonymousTimeStreetHandler

class AnonymousYearHandler(AnonymousBaseHandler):
    allow_methods = ('GET',)
    model = Year
    fields = year_fields

class YearHandler(BaseHandler):
    allow_methods = ('GET',)
    model = Year
    fields = year_fields
    anonymous = AnonymousYearHandler

class UserHandler(BaseHandler):
    allow_methods = ('GET',)
    model = User
    fields = user_fields
