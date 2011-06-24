"""
 Command to export events to a CSV
"""

from django.core.management.base import BaseCommand
from optparse import make_option
from playaevents import export
from playaevents.utilities import get_current_year
import sys

class Command(BaseCommand):

    help = "Export a CSV file of Events"
    option_list = BaseCommand.option_list + (
        make_option('--year', dest='year',
                    default = get_current_year(),
                    help='Year, default = this year'),
        make_option('--onetime', dest='onetime',
                    default = False,
                    action="store_true",
                    help="Output onetime events"),
        make_option('--repeating', dest="repeating",
                    default = False,
                    action="store_true",
                    help="Output repeating events"),
        make_option('--allday', dest="allday",
                    default = False,
                    action="store_true",
                    help="Output All-day non-repeating events"),
        make_option('--alldayrepeating', dest="alldayrepeating",
                    default = False,
                    action="store_true",
                    help="Output All-day repeating events"),


        )

    def handle(self, *args, **options):
        year = options['year']

        opts = {
            'onetime' : options['onetime'],
            'repeating' : options['repeating'],
            'allday' : options['allday'],
            'alldayrepeating' : options['alldayrepeating']
            }

        t = 0
        which = None
        for k,v in opts.items():
            if v:
                t += 1
                which = k

        if t==0:
            print "I need an option for output"
            sys.exit(1)
        if t>1:
            print "You can select only one output type at a time"
            sys.exit(1)

        self.export_events(year, which)

    def export_events(self, year, which):

        func = None
        if which == "onetime":
            func = export.csv_onetime_events
        elif which == "repeating":
            func = export.csv_repeating_events
        elif which == "allday":
            func = export.csv_all_day_onetime_events
        elif which == "alldayrepeating":
            func = export.csv_all_day_repeating_events
        else:
            print "Unknown"
            sys.exit(1)

        print func(year, buf=sys.stdout)
