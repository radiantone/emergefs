""" Handlers are responsible for handling message types received by a node server """
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass

from emerge.data import EmergeData


def _default(self, obj):
    return getattr(obj.__class__, "to_json", _default.default)(obj)


# _default.default = JSONEncoder().default
# JSONEncoder.default = _default


class Server(metaclass=ABCMeta):
    @abstractmethod
    def setup(self, options: dict) -> bool:
        pass

    @abstractmethod
    def start(self) -> bool:
        pass

    @abstractmethod
    def stop(self) -> bool:
        pass

    @abstractmethod
    def shutdown(self) -> bool:
        pass


@dataclass
class EmergeObject(EmergeData):
    """Class for keeping track of an item in inventory."""

    pass


class EmergeBlock(EmergeObject):
    """Holds references to block"""

    pass


@dataclass
class EmergeFile(EmergeObject):
    """Holds references to file"""

    name: str = ""
    path: str = "/"
    perms: str = "rwxrwxrwx"
    type: str = "file"
    data: str = ""
    uuid: str = ""
    node: str = ""
    version: int = 0

    def str(self):
        return self.to_json()

    def to_json(self):
        import json
        from types import ModuleType

        import persistent.list

        ser = {}

        for i in [
            v
            for v in dir(self)
            if not callable(getattr(self, v))
            and v[0] != "_"
            and isinstance(getattr(self, v), ModuleType) is False
        ]:
            if isinstance(getattr(self, i), EmergeObject):
                ser[i] = getattr(self, i)
            if isinstance(getattr(self, i), persistent.list.PersistentList):
                ser[i] = [str(o) for o in getattr(self, i)]
            else:
                ser[i] = getattr(self, i)

        return json.dumps(ser)


class FileSystem(Server):
    """A persistent filesystem"""

    def start(self) -> bool:
        pass

    def stop(self) -> bool:
        pass

    def shutdown(self) -> bool:
        pass

    def setup(self, options: dict) -> bool:
        pass
