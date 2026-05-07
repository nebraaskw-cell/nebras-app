import calendar

from django.core.exceptions import ValidationError
from django.utils import timezone


def add_months(source_date, months):
    month_index = source_date.month - 1 + months
    year = source_date.year + month_index // 12
    month = month_index % 12 + 1
    day = min(source_date.day, calendar.monthrange(year, month)[1])
    return source_date.replace(year=year, month=month, day=day)


def calculate_cycle_end_date(start_date):
    return add_months(start_date, 3)


def validate_cycle_dates(start_date, end_date):
    if start_date and end_date and end_date != calculate_cycle_end_date(start_date):
        raise ValidationError({"end_date": "Cycle end date must be exactly three calendar months after start date."})


def validate_session_time_window(start_time, end_time):
    if start_time and end_time and end_time <= start_time:
        raise ValidationError({"default_session_end_time": "Session end time must be after start time."})


def archive_cycle(cycle):
    cycle.status = cycle.Status.ARCHIVED
    cycle.archived_at = timezone.now()
    cycle.save(update_fields=["status", "archived_at", "updated_at"])
    return cycle

