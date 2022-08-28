import logging
import signal
from typing import List

import dill

from emerge.compute import Data
from emerge.core.objects import Server
from emerge.fs.filesystem import FileSystemFactory


class NodeServer(Server):
    """Node server"""

    topic = "NODE"
    socket = None
    services: List = []

    class NodeAPI:
        """Expose RPC API for interacting with this node server.
        Often other nodes will need to make requests for objects from this
        server."""

        name = "NodeAPI"

        def __init__(self, fs):
            self.fs = fs

        def hello(self, address):
            logging.info("HELLO FROM {}".format(address))

        def get(self, path, page=0, size=-1):
            import BTrees.OOBTree

            print("PATH", path)
            obj = self.fs.objects[path]

            if isinstance(obj, BTrees.OOBTree.OOBTree):
                # return dill.dumps([dill.loads(obj[o]) for o in obj])
                return [dill.dumps(obj[o]) for o in obj]
            else:
                # _obj = dill.loads(obj)
                return obj

        def list(self, path, offset=0, size=0):
            import BTrees.OOBTree

            print("PATH", path)
            if path != "/":
                obj = self.fs.objects[path]
            else:
                obj = self.fs.objects

            if isinstance(obj, BTrees.OOBTree.OOBTree):
                print("BTREE", path, obj)
                files = [obj[o]["path"] + "/" + obj[o]["name"] for o in obj]
                print(path, files)
                return dill.dumps(files)
            else:
                print(obj.path + "/" + obj.name, "NOT BTREE!")
                return obj.path + "/" + obj.name

        def execute(self, oid, method):
            _obj = dill.loads(self.fs.objects[oid])
            _method = getattr(_obj, method)
            return _method()

        def store(self, id, path, name, obj):
            import datetime

            import BTrees.OOBTree
            import dill

            _obj = dill.loads(obj)

            file = {
                "date": str(datetime.datetime.now()),
                "path": _obj.path,
                "name": _obj.name,
                "id": _obj.id,
                "size": len(obj),
                "obj": obj,
            }

            with self.fs.session():
                if path in self.fs.objects:
                    directory = self.fs.objects[path]
                    print("GETTING BTREE FOR", path)
                    print([name for name in directory])
                else:
                    print("CREATING NEW BTREE FOR", path)
                    directory = BTrees.OOBTree.BTree()
                    self.fs.objects[path] = directory

                directory[id] = file

                if path[-1] != "/":
                    self.fs.objects[path + "/" + name] = file
                    print("ADDED", path + "/" + name)
                else:
                    self.fs.objects[path + name] = file
                    print("ADDED", path + name)

                logging.info("STORE OBJECT  %s %s", path + "/" + name, _obj)

        def get_data(self, oid):
            obj: Data = self.fs.objects[oid]

            return obj.data

    def shutdown(self) -> bool:
        import os

        logging.debug("[NodeServer] shutdown...")
        [service.shutdown() for service in self.services]
        logging.debug("[NodeServer] shutdown finished...")
        os.killpg(os.getpgid(os.getpid()), 15)
        os.kill(os.getpid(), signal.SIGKILL)
        return True

    def stop(self) -> bool:
        logging.debug("[NodeServer] stop...")
        # self.process.terminate()
        # self.rpc.terminate()

        [service.stop() for service in self.services]

        return True

    def setup(self, options: dict = {}) -> bool:
        import socket
        from contextlib import closing

        import zerorpc
        import zmq

        logging.debug("[NodeServer] Setup...")

        def find_free_port():
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
                s.bind(("", 0))
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                return s.getsockname()[1]

        self.rpcport = find_free_port()
        self.port = "5557"  # find_free_port()
        self.bindport = find_free_port()
        self.rpcport = "5558"  # find_free_port()

        def start_rpc():
            """Listen for RPC events"""
            s = zerorpc.Server(self.NodeAPI(self.fs))
            s.bind("tcp://0.0.0.0:{}".format(self.rpcport))
            s.run()

        def get_messages():
            """Listen for pub/sub messages"""
            self.context = zmq.Context()
            self.socket = self.context.socket(zmq.SUB)
            host = "127.0.0.1"

            """ Connect to pub/sub address """
            self.socket.bind("tcp://{}:{}".format(host, self.port))

            self.socket.subscribe("NODE")
            logging.debug(
                "Subscribed to NODE on %s", "tcp://{}:{}".format(host, self.port)
            )
            while True:
                logging.debug("get_messages")
                logging.debug("Waiting on message")
                string = self.socket.recv_string()
                logging.debug("Got message %s", string)
                parts = string.split(" ")
                if parts[1] == "HI":
                    client = zerorpc.Client()
                    client.connect(parts[2])
                    client.hello("tcp://0.0.0.0:{}".format(self.rpcport))

        fs = self.fs = FileSystemFactory.get()
        self.services += [fs]
        import threading

        self.process = threading.Thread(target=get_messages)
        self.rpc = threading.Thread(target=start_rpc)
        """ Add filesystem service """

        [service.setup() for service in self.services]

        """ Handle keyboard quit """

        def handler(signum, frame):
            self.stop()
            self.shutdown()

        signal.signal(signal.SIGINT, handler)  # type: ignore

        return True

    def start(self) -> bool:
        import time

        import zmq

        logging.debug("[NodeServer] start...")

        context = zmq.Context()
        socket = context.socket(zmq.PUB)
        socket.connect("tcp://127.0.0.1:%s" % str(self.port))

        # Receives a string format message

        self.process.start()
        self.rpc.start()

        time.sleep(1)

        socket.send_string("NODE HI {}".format("tcp://0.0.0.0:{}".format(self.rpcport)))

        [service.start() for service in self.services]

        objects = self.fs.objects

        logging.info("objects length: %s %s", objects, len(objects))

        for object_ in objects:
            object__: Data = objects[object_]

            if type(object__) is bytes:
                object__ = dill.loads(object__)
                # objects[object_] = object__
            try:
                logging.info(
                    "object: %s %s %s",
                    type(object__),
                    object__.id,
                    str(object__.unit_price),
                )
            except:
                pass
        from functools import reduce

        try:
            sum_a = reduce(
                lambda x, y: x + y,
                [
                    obj.unit_price
                    for obj in (dill.loads(objects[name]) for name in objects)
                    if hasattr(obj, "unit_price")
                ],
            )

            print("SUM:", sum_a)
        except:
            pass

        return True
