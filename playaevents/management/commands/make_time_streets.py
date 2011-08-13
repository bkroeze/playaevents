"""
 Command to make time streets for a year
"""

from django.core.management.base import BaseCommand
from optparse import make_option
from playaevents.models import Year, TimeStreet
from playaevents.utilities import get_current_year

class Command(BaseCommand):

    help = "Import a CSV file of Theme Camps"
    option_list = BaseCommand.option_list + (
        make_option('--year', dest='year',
                    default=get_current_year(),
                    help='Year, default = this year'),
        )

    def handle(self, *args, **options):
        year = options['year']

        y = Year.objects.get(year = year)
        for hour in range(2,11):
            for minute in (0,5,10,15,20,25,30,35,40,45,50,55):
                name = '%i:%02i' % (hour, minute)
                print "Creating %s" % name
                print "args: %s" % str(dict(year = y, hour=hour, minute=minute, name=name))
                TimeStreet.objects.create(year = y, hour=hour, minute=minute, name=name)

        print ("done, built timestreets")

