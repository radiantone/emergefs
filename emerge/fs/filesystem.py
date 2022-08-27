import logging
import sys
from contextlib import contextmanager
from typing import Any

import BTrees.OOBTree
import ZODB
import ZODB.FileStorage

from emerge.core.objects import FileSystem


class FileSystemFactory:

    instance_class = "Z0DBFileSystem"

    @classmethod
    def get(cls):
        current_module = sys.modules[__name__]

        class_ = getattr(current_module, cls.instance_class)

        return class_("fs")


class Z0DBFileSystem(FileSystem):
    root: Any = None
    objects: Any = None

    def setup(self, options: dict = {}) -> bool:
        import transaction

        logging.info("Z0DBFileSystem setup")
        storage = ZODB.FileStorage.FileStorage("emerge.fs")
        db = self.db = ZODB.DB(storage)
        connection = db.open()
        self.root = connection.root()
        if not hasattr(self.root, "objects"):

            transaction.begin()
            logging.info("Creating new objects collection")
            self.root.objects = BTrees.OOBTree.BTree()

            transaction.commit()
        self.objects = self.root.objects

        return True

    @contextmanager
    def session(self):
        import transaction

        yield transaction.begin()

        transaction.commit()

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
