from datetime import datetime, date, time
from typing import Literal, cast

from pydantic_core import core_schema


DateType = datetime | date
TimeSpan = Literal['s', 'm', 'h', 'd', 'W', 'M', 'Q', 'Y']


class Interval(str):
    """ Data range """

    def __new__(cls, value: str):
        inst = cast(Interval, super().__new__(cls, value))
        if inst.multiplier > 0 and inst.timespan in ('s', 'm', 'h', 'd', 'W', 'M', 'Q', 'Y'):
            return inst
        raise ValueError(f'Interval {inst} is not valid')

    @property
    def multiplier(self) -> int:
        """ Time multiplier """
        return int(self[:-1])

    @property
    def timespan(self) -> TimeSpan:
        """ Time span """
        return cast(TimeSpan, self[-1:])

    @classmethod
    def validate(cls, field_value, _):
        return cls(field_value)

    @classmethod
    def __get_pydantic_core_schema__(cls, source, handler) -> core_schema.CoreSchema:
        return core_schema.with_info_plain_validator_function(cls.validate)


def interval_to_timestamp(interval: Interval) -> int:
    """ Interval to a timestamp value. """
    match interval.timespan:
        case 's':
            return interval.multiplier * 1000
        case 'm':
            return interval.multiplier * 60 * 1000
        case 'h':
            return interval.multiplier * 60 * 60 * 1000
        case 'd':
            return interval.multiplier * 24 * 60 * 60 * 1000
        case 'W':
            return interval.multiplier * 7 * 24 * 60 * 60 * 1000
    raise NotImplementedError(f"Time stamp {interval.timespan} is not supported")


def times_for_reverse(start_date: datetime | date, end_date: datetime | date, interval: Interval, limit: int):
    times = []
    interval = interval_to_timestamp(interval) * limit
    start_time = start_to_timestamp(start_date)
    end_time = end_to_timestamp(end_date)
    start_time_, end_time_ = start_time, start_time + interval - 1
    while end_time_ < end_time:
        times.append([start_time_, end_time_])
        start_time_, end_time_ = start_time_ + interval, end_time_ + interval
    times.append([start_time_, end_time])
    return times


def start_to_timestamp(value: datetime | date | str) -> int:
    """ Converts the start time of a data range to a timestamp. """
    return to_timestamp(value)


def end_to_timestamp(value: datetime | date | str) -> int:
    """ Converts the end time of a data range to a timestamp. """
    value = normalize_date(value) if isinstance(value, str) else value
    value = value if isinstance(value, datetime) else datetime.combine(value, time.max)
    return to_timestamp(value)


def to_timestamp(value: datetime | str) -> int:
    """ Converts the datetime to a timestamp. """
    value = normalize_date(value) if isinstance(value, str) else value
    value = value if isinstance(value, datetime) else datetime.combine(value, time.min)
    return int(value.timestamp() * 1000)


def normalize_date(value: int | str | DateType) -> DateType:
    """ Convert to date type and localize date value. """
    if not isinstance(value, (date, datetime)):
        if isinstance(value, str):
            if ":" in str(value):
                value = datetime.fromisoformat(value)
            else:
                value = date.fromisoformat(value)
        elif isinstance(value, int):
            value = datetime.fromtimestamp(value / 1000)
        else:
            raise TypeError(f"Invalid date type: {value}")
    return value

