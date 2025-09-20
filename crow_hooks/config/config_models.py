import toml
from typing import Dict, Any, TypeVar, Generic

T = TypeVar("T")


class ConfigSection(Generic[T]):
    def __init__(self, data: Dict[str, Any]):
        self.data = data

    def __getattr__(self, name: str) -> Any:
        value = self.data[name]
        if isinstance(value, dict):
            return ConfigSection(value)
        return value

    def as_dict(self) -> Dict[str, Any]:
        return self.data


class ConfigurationMeta(type):
    _data: Dict[str, Any] = {}

    def __getattr__(cls, name: str) -> Any:
        value = cls._data[name]
        if isinstance(value, dict):
            return ConfigSection(value)
        return value


class Configuration(metaclass=ConfigurationMeta):
    @classmethod
    def load(cls, path: str = "config.toml") -> None:
        with open(path) as f:
            cls._data = toml.load(f)
