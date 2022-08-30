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

    id: str


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


class FileSystem(Server, EmergeObject):
    """A persistent filesystem"""

    def start(self) -> bool:
        pass

    def stop(self) -> bool:
        pass

    def shutdown(self) -> bool:
        pass

    def setup(self, options: dict) -> bool:
        pass
