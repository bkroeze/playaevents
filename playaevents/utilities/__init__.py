from datetime import datetime

def get_current_year():
    now = datetime.now()
    if now.month < 10:
        return now.year
    else:
        if now.month > 0:
            return now.year
    return now.year+1

