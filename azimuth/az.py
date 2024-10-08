import importlib


class Settings:
    """ Settings """


settings = Settings()


def __getattr__(name):
    try:
        return importlib.import_module(f'azimuth.extensions.{name}')
    except ModuleNotFoundError:
        raise AttributeError(f"'az' has no extension '{name}'")
