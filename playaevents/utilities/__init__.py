from datetime import datetime

def get_current_year(full_object=False):
    now = datetime.now()
    if now.month < 10:
        y = now.year
    else:
        if now.month > 0:
            y = now.year+1

    if full_object:
        from playaevents.models import Year
        return Year.objects.filter(year=y)
    return y

