from datetime import datetime, date, time
from typing import Tuple


def str_to_time(time_str: str) -> time:
    return datetime.strptime(time_str, "%I:%M %p").time() if time_str else None


def str_to_date(date_str: str) -> date:
    return datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else None


def seconds_to_hours_minutes(seconds) -> Tuple[int, int]:
    """Converts seconds to (hours, minutes)."""
    m, s = divmod(seconds, 60)
    return divmod(m, 60)


def get_time_diff(start, end):
    """Returns time difference in seconds."""
    return round(
        (
            datetime.combine(date.min, end) - datetime.combine(date.min, start)
        ).total_seconds(),
    )
