import logging
import sys
from typing import Any

import ZODB
import ZODB.FileStorage

from emerge.core.objects import FileSystem


class FileSystemFactory:

    instance_class = "Z0DBFileSystem"

    @classmethod
    def get(cls):
        current_module = sys.modules[__name__]

        class_ = getattr(current_module, cls.instance_class)

        return class_()


class Z0DBFileSystem(FileSystem):
    root: Any = None

    def setup(self, options: dict = {}) -> bool:
        logging.info("Z0DBFileSystem setup")
        storage = ZODB.FileStorage.FileStorage("emerge.fs")
        db = ZODB.DB(storage)
        connection = db.open()
        self.root = connection.root
        return True

    def start(self) -> bool:
        logging.info("Z0DBFileSystem start")
        return True

    def stop(self) -> bool:
        logging.info("Z0DBFileSystem stop")
        return True

    def shutdown(self) -> bool:
        logging.info("Z0DBFileSystem shutdown")
        return True

    @property
    def id(self):
        pass
