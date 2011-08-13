"""
 Command to load Camps from a CSV
"""

from django.core.management.base import BaseCommand
from optparse import make_option
from playaevents.models import ThemeCamp
from playaevents.utilities import get_current_year
import csv
import sys

class Command(BaseCommand):

    help = "Import a CSV file of Theme Camps"
    option_list = BaseCommand.option_list + (
        make_option('--file', dest='fname',
                    default = '',
                    help='Read camps from file'),
        make_option('--year', dest='year',
                    default = get_current_year(),
                    help='Year, default = this year')
        )

    def handle(self, *args, **options):
        if not 'fname' in options or options['fname'] == '':
            print "I need a camp csv file to load"
            sys.exit(1)

        fname = options['fname']
        year = options['year']

        self.import_camps(fname, year)

    def import_camps(self, fname, year):
        reader = csv.reader(open(fname, 'r'))
        campct = 0
        for row in reader:
            if row:
                t = None
                try:
                    t = ThemeCamp.objects.get(bm_fm_id = row[0])
                except:
                    print 'cannot find camp id #%s' % row[0]
                if not t:
                    try:
                        t = ThemeCamp.objects.get(name = row[1])
                    except:
                        print 'cannot find, second try name = %s' % row[1]
                if t is not None:
                    print "Updating %s" % t.name
                    t.location_string = row[2]
                    t.save()
                    campct += 1

        print ("done, updated %i Camps" % campct)

