from datetime import datetime, date, time


def str_to_time(time_str: str) -> time:
    return datetime.strptime(time_str, "%I:%M %p").time() if time_str else None


def str_to_date(date_str: str) -> date:
    return datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else None
