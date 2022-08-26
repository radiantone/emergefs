""" Handlers are responsible for handling message types received by a node server """
from abc import ABCMeta, abstractmethod

import persistent


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


class Object(persistent.Persistent, metaclass=ABCMeta):
    """Any object in emerge"""

    @property
    @abstractmethod
    def id(self):
        pass


class Block(Object):
    """Holds references to block"""

    @property
    def id(self):
        pass


class File(Object):
    """Holds references to file"""

    @property
    def id(self):
        pass


class FileSystem(Server, Object):
    """A persistent filesystem"""

    @property
    @abstractmethod
    def id(self):
        pass
