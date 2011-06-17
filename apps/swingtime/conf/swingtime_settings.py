from django.conf import settings
import datetime

swingtime_defaults = {
    'TIMESLOT_TIME_FORMAT' : '%I:%M %p',

    # Used for creating start and end time form selectors as well as time slot grids.
    # Value should be datetime.timedelta value representing the incremental
    # differences between temporal options
    'TIMESLOT_INTERVAL' : datetime.timedelta(minutes=15),

    # A datetime.time value indicting the starting time for time slot grids and form
    # selectors
    'TIMESLOT_START_TIME' : datetime.time(0),

    # A datetime.timedelta value indicating the offset value from
    # TIMESLOT_START_TIME for creating time slot grids and form selectors. The for
    # using a time delta is that it possible to span dates. For instance, one could
    # have a starting time of 3pm (15:00) and wish to indicate a ending value
    # 1:30am (01:30), in which case a value of datetime.timedelta(hours=10.5)
    # could be specified to indicate that the 1:30 represents the following date's
    # time and not the current date.
    'TIMESLOT_END_TIME_DURATION' : datetime.timedelta(hours=+23, minutes=+59),

    # Indicates a minimum value for the number grid columns to be shown in the time
    # slot table.
    'TIMESLOT_MIN_COLUMNS' : 4,

    # Indicate the default length in time for a new occurrence, specifed by using
    # a datetime.timedelta object
    'DEFAULT_OCCURRENCE_DURATION' : datetime.timedelta(hours=+1),

    # If not None, passed to the calendar module's setfirstweekday function.
    'CALENDAR_FIRST_WEEKDAY' : 6
}

def get_swingtime_setting(name, default_value = None):
    if not hasattr(settings, 'SWINGTIME_SETTINGS'):
        return swingtime_defaults.get(name, default_value)

    return settings.SWINGTIME_SETTINGS.get(name, swingtime_defaults.get(name, default_value))

TIMESLOT_TIME_FORMAT = get_swingtime_setting('TIMESLOT_TIME_FORMAT')
TIMESLOT_INTERVAL = get_swingtime_setting('TIMESLOT_INTERVAL')
TIMESLOT_START_TIME = get_swingtime_setting('TIMESLOT_START_TIME')
TIMESLOT_END_TIME_DURATION = get_swingtime_setting('TIMESLOT_END_TIME_DURATION')
TIMESLOT_MIN_COLUMNS = get_swingtime_setting('TIMESLOT_MIN_COLUMNS')
DEFAULT_OCCURRENCE_DURATION = get_swingtime_setting('DEFAULT_OCCURRENCE_DURATION')
CALENDAR_FIRST_WEEKDAY = get_swingtime_setting('CALENDAR_FIRST_WEEKDAY')
