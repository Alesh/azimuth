from datetime import datetime, date, time


def start_date_timestamp(value: datetime | date) -> int:
    return int(datetime.combine(value, time.min).timestamp() * 1000
               if isinstance(value, date) else value.timestamp())


def end_date_timestamp(value: datetime | date) -> int:
    return int(datetime.combine(value, time.max).timestamp() * 1000
               if isinstance(value, date) else value.timestamp())
