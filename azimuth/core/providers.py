import importlib
import typing as t

from .fetcher import Fetcher
from .models import QueryParams, Data

Q = t.TypeVar("Q", bound=QueryParams)
D = t.TypeVar("D", bound=Data)


class Provider(t.Generic[Q, D]):
    """ Base class for all data providers.
    """

    def fetch(self, data_type: t.Type[D], **kwargs: t.Any) -> Fetcher[Q, D]:
        """ Returns situated fetcher """


def get_provider(name: str):
    """ Return provider interface by name """
    name, *args = name.split(':')
    try:
        mod = importlib.import_module(f'azimuth.providers.{name}')
        return mod.Provider(*args)
    except ModuleNotFoundError:
        pass
    raise AttributeError(f"provider '{name}' has no found")
