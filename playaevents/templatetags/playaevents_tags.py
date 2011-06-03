from django import template
from playaevents.utilities import get_current_year

register = template.Library()

@register.filter
def is_current_year(year):
    return str(year) == str(get_current_year())

@register.filter
def last_year(year):
    last = int(year)
    return last-1
