from datetime import datetime, date, time
from typing import Optional

import pydantic
from pydantic import Field, PositiveFloat, field_validator, NonNegativeFloat

DateType = datetime | date


class QueryParams(pydantic.BaseModel):
    """ Base query model
    """


class Data(pydantic.BaseModel):
    """ Base data model
    """


class CandleQueryParams(QueryParams):
    """ Base candle query params model
    """
    symbol: str = Field(description="Symbol.")
    start_date: Optional[DateType] = Field(default=datetime.combine(date.today(), time.min),
                                           description="Start of data range.")
    end_date: Optional[DateType] = Field(default=datetime.combine(date.today(), time.max),
                                         description="End of data range.")
    interval: str = Field(default="1d", description="Data range.")

    @field_validator("start_date", "end_date", mode="before")
    @classmethod
    def start_date_validate(cls, value):
        if not isinstance(value, (datetime, date)):
            if ":" in str(value):
                return datetime.fromisoformat(value)
            return date.fromisoformat(value)
        return value


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
        if not isinstance(value, (datetime, date)):
            if ":" in str(value):
                return datetime.fromisoformat(value)
            return datetime.fromisoformat(value)
        return value
