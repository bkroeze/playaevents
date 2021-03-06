"""
 Command to load art from a CSV
"""

from django.core.management.base import BaseCommand
from django.utils.encoding import smart_unicode
from optparse import make_option
from playaevents.models import ArtInstallation, Year
from playaevents.utilities import get_current_year
from playaevents.utilities.unique_id import slugify
import csv
import sys

class Command(BaseCommand):

    help = "Import a CSV file of art installations"
    option_list = BaseCommand.option_list + (
        make_option('--file', dest='fname',
                    default = '',
                    help='Read installations from file'),
        make_option('--year', dest='year',
                    default = get_current_year(),
                    help='Year, default = this year')
        )

    def handle(self, *args, **options):
        if not 'fname' in options or options['fname'] == '':
            print "I need an art csv file to load"
            sys.exit(1)

        fname = options['fname']
        year = options['year']

        self.import_art(fname, year)

    def import_art(self, fname, year):
        reader = csv.reader(open(fname, 'r'))
        y = Year.objects.get(year = year)
        artct = 0
        for row in reader:
            if row:
                name = smart_unicode(row[1], errors='ignore')
                name = name.replace('"', '')
                slug = slugify(name)

                a = ArtInstallation(name=name,
                                    year=y,
                                    slug=slug,
                                    bm_fm_id = int(row[0]))
                a.save()
                artct += 1

        print ("done, loaded %i art installations" % artct)

