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

        return class_()


class Z0DBFileSystem(FileSystem):
    root: Any = None
    objects: Any = None
    uuids: Any = None

    def setup(self, options: dict = {}) -> bool:
        import transaction

        logging.info("Z0DBFileSystem setup")
        storage = ZODB.FileStorage.FileStorage("emerge.fs")
        db = self.db = ZODB.DB(storage)
        self.connection = db.open()
        # self.root.hello = "".join(["there" for i in range(0,100)])
        self.root = self.connection.root()
        logging.info("self.root %s", self.root)
        try:
            # transaction.commit()
            logging.info("self.root len %d", len(self.root))
        except Exception as ex:
            logging.error(ex)

        logging.info("Creating new objects collection")

        if not hasattr(self.root, "objects"):
            logging.info("Creating new filesystem")
            transaction.begin()
            self.root.objects = BTrees.OOBTree.BTree()
            self.objects = self.root.objects

            self.registry = self.root.registry = BTrees.OOBTree.BTree()

            self.classes = self.root.classes = BTrees.OOBTree.BTree()

            self.nodes = self.root.nodes = BTrees.OOBTree.BTree()

            self.uuids = self.root.uuids = BTrees.OOBTree.BTree()

            transaction.commit()
        else:
            logging.info("Using loaded filesystem")
            self.registry = self.root.registry
            self.classes = self.root.classes
            self.uuids = self.root.uuids
            self.nodes = self.root.nodes
            self.objects = self.root.objects
        logging.info("self.root.objects %d", len(self.root.objects))

        return True

    @contextmanager
    def session(self):
        import transaction

        logging.info("transaction begin")
        yield transaction.begin()

        logging.info("transaction commit")
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
