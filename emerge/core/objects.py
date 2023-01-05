""" Handlers are responsible for handling message types received by a node server """
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass

from emerge.data import EmergeData


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

    def __str__(self):
        import json

        return json.dumps(
            {
                "name": self.name,
                "path": self.path,
                "id": self.id,
                "perms": self.perms,
                "type": self.type,
                "data": self.data,
            }
        )


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
