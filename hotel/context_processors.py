import calendar
from datetime import datetime
from django.utils import timezone

def datetime_info(request):
    now_local = timezone.now()
    now_utc = datetime.utcnow().replace(tzinfo=timezone.utc)
    cal = calendar.TextCalendar(calendar.MONDAY)
    return {
        'user_timezone': timezone.get_current_timezone_name(),
        'current_date_local': now_local.strftime('%d/%m/%Y %H:%M:%S'),
        'current_date_utc': now_utc.strftime('%d/%m/%Y %H:%M:%S'),
        'text_calendar': cal.formatmonth(now_local.year, now_local.month),
    }
