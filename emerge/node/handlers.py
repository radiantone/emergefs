""" Handlers are responsible for handling message types received by a node server """
from abc import ABCMeta, abstractmethod


class Handler(metaclass=ABCMeta):
    """Base Handler class"""

    @abstractmethod
    def handle(self, message: dict) -> bool:
        pass


class BlockHandler(Handler):
    """Handle requests for blocks"""

    def handle(self, message: dict) -> bool:
        pass


class FileHandler(Handler):
    """Handle requests for files"""

    def handle(self, message: dict) -> bool:
        pass


class StreamHandler(Handler):
    """Stream files to a client"""

    def handle(self, message: dict) -> bool:
        pass
