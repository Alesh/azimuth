import typing as t
from warnings import warn

from httpx import Response, URL
from pydantic import field_validator

import azimuth.core
from azimuth.core.utils import start_to_timestamp, end_to_timestamp, interval_to_timestamp, normalize_date, \
    times_for_reverse
from azimuth.extensions.crypto import CryptoCandleData, CryptoCandleQueryParams

_INTERVA_CNV = {'1m': '1', '3m': '3', '5m': '5', '15m': '15', '30m': '30',
                '1h': '60', '2h': '120', '4h': '240', '6h': '360', '12h': '720', '1d': 'D', '1W': 'W', '1M': 'M'}


class BybitCandleData(CryptoCandleData):
    """ Bybit candle data.
    """

    @field_validator("date", mode="before")
    @classmethod
    def date_validate(cls, value):
        return normalize_date(int(value))


class BybitCandleQueryParams(CryptoCandleQueryParams):
    """ Bybit candle query params.
    """

    @field_validator("interval")
    @classmethod
    def interval_validate(cls, value):
        options = ('1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '12h', '1d', '1W', '1M')
        if value in options:
            return value
        raise ValueError("Interval must be one of {}".format(options))

    def make_url(self, base_url, start_time: int = None, end_time: int = None) -> str:
        """ Makes internal url with query parameters. """
        start_time = start_time or start_to_timestamp(self.start_date)
        end_time = end_time or end_to_timestamp(self.end_date)
        interval = _INTERVA_CNV.get(self.interval)
        return (f"{base_url}?category=spot&symbol={self.symbol.replace('/', '')}&"
                f"interval={interval}&limit=1000&"
                f"start={start_time}&end={end_time}")


class BybitCandleFetcher(azimuth.core.Fetcher[BybitCandleQueryParams, list[BybitCandleData]]):
    """ Bybit candle data fetcher.
    """
    BASE_URL = 'https://api.bybit.com/v5/market/kline'

    def __init__(self, query: BybitCandleQueryParams, /, market):
        assert market == 'spot', "Only spot market is supported"
        self.times = times_for_reverse(query.start_date, query.end_date, query.interval, 1000)
        super().__init__(query, query.make_url(self.BASE_URL, *self.times.pop(0)))
        self.count = 0

    def parse_response(self, resp: Response) -> tuple[list[BybitCandleData], URL | None]:
        result = []
        next_url = None
        symbol = self.query.symbol
        data = resp.json()
        if data and data['retCode'] == 0 and data['result']['list']:
            data = list(reversed(data['result']['list']))
            self.count += len(data)
            if self.times:
                next_url = self.query.make_url(self.BASE_URL, *self.times.pop(0))
            result.extend([
                BybitCandleData(**dict(zip(['date', 'open', 'high', 'low', 'close', 'volume', 'value'], item)))
                for item in data
            ])
        else:
            if self.count == 0:
                warn(f"Symbol Error: No data found for {symbol}")
        return result, next_url

# 'https://api.bybit.com/v5/market/kline?category=spot&symbol=BTCUSDT&interval=60&limit=3&start=1728248400000&end=1731848400000'

class Provider(azimuth.core.Provider):
    """ Bybit data provider.
    """

    def __init__(self, market: str = 'spot'):
        self.kwargs = dict(market=market)

    def fetch(self, data_type: t.Type[CryptoCandleData], **kwargs):
        map = {
            CryptoCandleData: lambda: BybitCandleFetcher(BybitCandleQueryParams(**kwargs), **self.kwargs)
        }
        if fetcher_factory := map.get(data_type):
            return fetcher_factory()
        raise ValueError(f"Cannot resolve fetcher for: '{data_type.__qualname__}'")
