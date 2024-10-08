from abc import abstractmethod, ABC
from datetime import datetime, date, time
from typing import Optional

import pydantic
from pydantic import Field, PositiveFloat, field_validator, NonNegativeFloat

from azimuth.core.utils import DateType, Interval, normalize_date


class QueryParams(pydantic.BaseModel):
    """ Base query parameters model
    """

    @abstractmethod
    def make_url(self, base: str, **kwargs) -> str:
        """ Makes internal url with query parameters. """


class Data(pydantic.BaseModel):
    """ Base data model
    """


class CandleQueryParams(QueryParams, ABC):
    """ Base candle query params model
    """
    symbol: str = Field(description="Symbol.")
    start_date: Optional[DateType] = Field(default=datetime.combine(date.today(), time.min),
                                           description="Start of data range.")
    end_date: Optional[DateType] = Field(default=datetime.combine(date.today(), time.max),
                                         description="End of data range.")
    interval: Interval = Field(default="1d", description="Data range.")

    @field_validator("start_date", "end_date", mode="before")
    @classmethod
    def date_validate(cls, value):
        return normalize_date(value)


class CandleData(Data):
    """ Base candle data model
    """

    date: DateType = Field(description="Open time")
    open: PositiveFloat = Field(description="Open price")
    high: PositiveFloat = Field(description="High price")
    low: PositiveFloat = Field(description="Low price")
    close: PositiveFloat = Field(description="Close price")
    volume: NonNegativeFloat = Field(description="Volume")
    value: NonNegativeFloat = Field(description="Quote asset volume")

    @field_validator("date", mode="before")
    @classmethod
    def date_validate(cls, value):
        return normalize_date(value).astimezone()
