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

    def __init__(self, oid):
        self.oid = oid

    @property
    def id(self):
        return self.oid


class Block(Object):
    """Holds references to block"""

    pass


class File(Object):
    """Holds references to file"""

    pass


class FileSystem(Server, Object):
    """A persistent filesystem"""

    def start(self) -> bool:
        pass

    def stop(self) -> bool:
        pass

    def shutdown(self) -> bool:
        pass

    def setup(self, options: dict) -> bool:
        pass
