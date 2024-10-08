from abc import ABC

from pydantic import field_validator

from azimuth.core.models import CandleData, CandleQueryParams
from azimuth.core.providers import get_provider


class CryptoCandleQueryParams(CandleQueryParams, ABC):
    """ Base crypto candle query params model
    """

    @field_validator("symbol", mode="before")
    @classmethod
    def validate_symbol(cls, value: str):
        if "/" in value:
            return value.upper()
        raise ValueError("Invalid symbol, base and quote assets must be separated by '/'.")


class CryptoCandleData(CandleData):
    """ Base crypto candle data model
    """


def candles(symbol: str, /, provider: str = None, **query_params):
    """ Candles data source """
    assert provider, "Default provider in not implemented"  # ToDo: Sets default provider
    return get_provider(provider).fetch(CryptoCandleData, symbol=symbol, **query_params)


def __getattr__(name):
    raise AttributeError(f"extension 'az.{__name__.split('.')[-1]}' has no attribute '{name}'")
