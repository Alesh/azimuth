from abc import abstractmethod
from collections.abc import AsyncIterator, Iterator
from typing import TypeVar, Generic

import httpx
from httpx import URL, Response

from azimuth.core.models import QueryParams, Data

try:
    import pandas as pd

    def _to_dataframe(iter_: Iterator[Data]) -> pd.DataFrame:
        return pd.DataFrame.from_dict([item.model_dump() for item in iter_])

except ImportError:
    def _to_dataframe(*args, **kwargs):
        raise ImportError("Pandas is not installed.")

Q = TypeVar("Q", bound=QueryParams)
D = TypeVar("D", bound=Data)


class Fetcher(Generic[Q, D], Iterator[D], AsyncIterator[D]):
    """ Data fetcher base class
    """

    def __init__(self, query: Q, url: URL | str) -> None:
        self.query = query
        self._url = URL(url) if isinstance(url, str) else url
        self._data = []  # type: list[D]

    def __next__(self) -> D:
        if not self._data and self._url:
            with httpx.Client() as client:
                resp = client.get(self._url)
                if resp.status_code == 200:
                    self._data, self._url = self.parse_response(resp)
                else:
                    resp.raise_for_status()
        if not self._data:
            raise StopIteration
        return self._data.pop(0)

    async def __anext__(self) -> D:
        if not self._data and self._url:
            async with httpx.AsyncClient() as client:
                resp = await client.get(self._url)
                if resp.status_code == 200:
                    self._data, self._url = self.parse_response(resp)
                else:
                    resp.raise_for_status()
        if not self._data:
            raise StopAsyncIteration
        return self._data.pop(0)

    @abstractmethod
    def parse_response(self, resp: Response) -> tuple[list[D], URL | None]:
        """ Parse data from response """

    def to_dataframe(self, limit: int = None) -> 'pd.DataFrame':
        """ Returns result as pandas dataframe. """
        limit = limit or -1

        def iter_():
            try:
                cnt = 0
                while limit < 0 or cnt < limit:
                    yield next(self)
                    cnt += 1
            except StopIteration:
                pass

        return _to_dataframe(iter_())

    to_df = to_dataframe
