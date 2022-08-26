import ZODB
import ZODB.FileStorage

from typing import Any
from emerge.core.objects import FileSystem


class FileSystemFactory:
    pass


class Z0DBFileSystem(FileSystem):
    root: Any = None

    def setup(self, options: dict) -> bool:
        storage = ZODB.FileStorage.FileStorage("emerge.fs")
        db = ZODB.DB(storage)
        connection = db.open()
        self.root = connection.root
        return True

    def start(self) -> bool:
        return True

    def stop(self) -> bool:
        return True

    def shutdown(self) -> bool:
        return True

    @property
    def id(self):
        pass
