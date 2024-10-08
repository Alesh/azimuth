import typing as t
from warnings import warn

from httpx import URL, Response
from pydantic import field_validator

import azimuth.core
from azimuth.core.utils import start_to_timestamp, end_to_timestamp
from azimuth.extensions.crypto import CryptoCandleData, CryptoCandleQueryParams


class MEXCCandleData(CryptoCandleData):
    """ MEXC candle data.
    """


class MEXCCandleQueryParams(CryptoCandleQueryParams):
    """ MEXC candle query params.
    """

    @field_validator("interval")
    @classmethod
    def interval_validate(cls, value):
        options = ('1m', '5m', '15m', '30m', '1h', '4h', '1d', '1W', '1M')
        if value in options:
            return value
        raise ValueError("Interval must be one of {}".format(options))

    def make_url(self, base_url, start_time: int = None) -> str:
        """ Makes internal url with query parameters. """
        start_time = start_time or start_to_timestamp(self.start_date)
        end_time = end_to_timestamp(self.end_date)
        interval = "60m" if self.interval == '1h' else self.interval
        return (f"{base_url}?symbol={self.symbol.replace('/', '')}&"
                f"interval={interval}&limit=1000&"
                f"startTime={start_time}&endTime={end_time}")


class MEXCCandleFetcher(azimuth.core.Fetcher[MEXCCandleQueryParams, list[MEXCCandleData]]):
    """ MEXC candle data fetcher.
    """
    BASE_URL = 'https://api.mexc.com/api/v3/klines'

    def __init__(self, query: MEXCCandleQueryParams, /, market):
        assert market == 'spot', "Only spot market is supported"
        super().__init__(query, query.make_url(self.BASE_URL))
        self.count = 0

    def parse_response(self, resp: Response) -> tuple[list[MEXCCandleData], URL | None]:
        result = []
        next_url = None
        symbol = self.query.symbol
        data = resp.json()
        if data:
            self.count += len(data)
            start_time = data[-1][6] + 1
            if start_time < end_to_timestamp(self.query.end_date):
                next_url = self.query.make_url(self.BASE_URL, start_time)
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
