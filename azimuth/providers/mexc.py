import typing as t
from datetime import datetime
from warnings import warn

from httpx import URL, Response
from pydantic import field_validator

import azimuth.core
from azimuth.core.utils import start_date_timestamp, end_date_timestamp
from azimuth.extensions.crypto import CryptoCandleData, CryptoCandleQueryParams


class MEXCCandleData(CryptoCandleData):
    """ MEXC candle data.
    """

    @field_validator("date", mode="before")
    @classmethod
    def date_validate(cls, value):
        return datetime.fromtimestamp(value / 1000)


class MEXCCandleQueryParams(CryptoCandleQueryParams):
    """ MEXC candle query params.
    """

    @field_validator("interval")
    @classmethod
    def interval_validate(cls, value):
        value = '60m' if value == '1h' else value
        options = ('1m', '5m', '15m', '30m', '60m', '4h', '1d', '1W', '1M')
        if value in options:
            return value
        raise ValueError("Interval must be one of {}".format(options))


class MEXCCandleFetcher(azimuth.core.Fetcher[MEXCCandleQueryParams, list[MEXCCandleData]]):
    """ MEXC candle data fetcher.
    """

    def __init__(self, query: MEXCCandleQueryParams, /, market):
        assert market == 'spot', "Only spot market is supported"
        self.start_time = start_date_timestamp(query.start_date)
        self.end_time = end_date_timestamp(query.end_date)
        super().__init__(query, self.make_url(query, self.start_time, self.end_time))
        self.count = 0

    @staticmethod
    def make_url(query: MEXCCandleQueryParams, start_time: int, end_time: int) -> URL:
        return URL(f"https://api.mexc.com/api/v3/klines?symbol={query.symbol.upper()}&"
                   f"interval={query.interval}&limit=1000&timeZone=0&"
                   f"startTime={start_time}&endTime={end_time}")

    def parse_response(self, resp: Response) -> tuple[list[MEXCCandleData], URL | None]:
        result = []
        next_url = None
        symbol = self.query.symbol
        data = resp.json()
        if data:
            self.count += len(data)
            self.start_time = data[-1][6] + 1
            if self.start_time < self.end_time:
                next_url = self.make_url(self.query, self.start_time, self.end_time)
            result.extend([MEXCCandleData(**dict(zip(['date', 'open', 'high', 'low', 'close', 'volume', 'value'],
                                                     item[:6] + [item[7]])))
                           for item in data])
        else:
            if self.count == 0:
                warn(f"Symbol Error: No data found for {symbol}")
        return result, next_url


class Provider(azimuth.core.Provider):
    """ MEXC data provider.
    """

    def __init__(self, market: str = 'spot'):
        self.kwargs = dict(market=market)

    def fetch(self, data_type: t.Type[CryptoCandleData], **kwargs):
        map = {
            CryptoCandleData: lambda: MEXCCandleFetcher(MEXCCandleQueryParams(**kwargs), **self.kwargs)
        }
        if fetcher_factory := map.get(data_type):
            return fetcher_factory()
        raise ValueError(f"Cannot resolve fetcher for: '{data_type.__qualname__}'")
