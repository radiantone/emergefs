import logging
import signal
from typing import List

import BTrees.OOBTree
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

        def __init__(self):
            self.fs = FileSystemFactory.get()
            self.fs.setup()
            self.fs.start()

        def sum(self):

            inventory = self.fs.objects["/inventory"]

            logging.info("objects length: %s %s", inventory, len(inventory))

            for object_ in inventory:
                object__: Data = inventory[object_]

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
                        dill.loads(inventory[name]["obj"]).unit_price
                        for name in inventory
                    ],
                )

                print("SUM:", sum_a)
            except:
                import traceback
                print(traceback.format_exc())

        def hello(self, address):
            logging.info("HELLO FROM {}".format(address))

        def getobject(self, path, page=0, size=-1):

            logging.info("getobject: path = %s", path)
            obj = self.fs.root.registry[path]
            d = dill.loads(obj["obj"])
            logging.info("OBJ %s", d.name)
            if obj["type"] == "file":
                return obj["obj"]
            elif obj["type"] == "directory":
                return [obj[o]["obj"] for o in obj["dir"]]

        def get(self, path, page=0, size=-1):

            logging.info("get: path = %s", path)
            obj = self.fs.root.registry[path]

            if obj["type"] == "directory":
                obj["size"] = len(obj["dir"])
            else:
                obj["size"] = obj["size"]
            file = {
                "date": obj["date"],
                "path": obj["path"],
                "name": obj["name"],
                "id": obj["id"],
                "perms": obj["perms"],
                "type": obj["type"],
                "size": obj["size"],
            }

            return file

        def getdir(self, path, page=0, size=-1):

            logging.info("getdir: path = %s", path)
            obj = self.fs.root.registry[path]

            if obj["type"] == "directory":
                return [dill.dumps(obj["dir"][o]) for o in obj["dir"]]

            if isinstance(obj, BTrees.OOBTree.OOBTree):
                # return dill.dumps([dill.loads(obj[o]) for o in obj])
                return [dill.dumps(obj[o]) for o in obj]
            else:
                # _obj = dill.loads(obj)
                return obj

        def list(self, path, offset=0, size=0):
            logging.info("list: path %s", path)
            logging.info("root id is %s", self.fs.root.objects)

            logging.info("ROOT IS %s", [o for o in self.fs.root.objects])
            if path != "/":
                paths = path.split("/")[1:]
                dir = self.fs.objects
                for p in paths:
                    logging.info("list: p %s of paths %s",p, paths)
                    file = dir[p]
                    if file["type"] == "directory":
                        dir = file["dir"]
                    elif file["type"] == "file":
                        return dill.dumps(file)
                obj = dir
                logging.info("found %s in %s %s", path, dir, len(obj))
            else:
                obj = self.fs.root.objects
                logging.info("obj is self.fs.objects %s", len(obj))

            logging.info("LIST: %s", list(obj))

            files = []

            for name in obj:
                file = obj[name]
                if file["type"] == "directory":
                    files += ["dir:" + file["name"]]
                elif file["type"] == "file":
                    files += [file["path"] + "/" + file["name"]]
                else:
                    files += [file["path"]]

            logging.info("RETURNING FILES: %s", files)
            return dill.dumps(files)

        def execute(self, oid, method):
            _obj = dill.loads(self.fs.registry[oid]["obj"])
            _method = getattr(_obj, method)
            return _method()

        def store(self, id, path, name, obj):
            import datetime
            import BTrees.OOBTree
            import dill

            _obj = dill.loads(obj)

            file = {
                "date": str(datetime.datetime.now().strftime("%b %d %Y %H:%M:%S")),
                "path": _obj.path,
                "name": _obj.name,
                "id": _obj.id,
                "perms": _obj.perms,
                "type": _obj.type,
                "size": len(obj),
                "obj": obj,
            }

            with self.fs.session():

                """ If the path is already created, set the directory to that path """
                if path in self.fs.root.objects:
                    directory = self.fs.root.objects[path]
                    logging.info("Found %s in self.fs.root.objects", path)
                else:
                    """ Create all the BTree objects for each section in the path """
                    paths = path.split("/")[1:]
                    base = ""
                    root = _root = self.fs.root.objects
                    logging.info("store: paths: %s", paths)
                    logging.info("root id %s", root)

                    """ Create BTree directories for each subpath if it doesn't exist 
                    then set the directory to the last BTree in the path """
                    for p in paths:
                        _path = base + "/" + p
                        logging.info("store: _path is now %s",_path)
                        if p in root:
                            logging.info("store: p %s found in root %s", p, root)
                            root = directory = root[p]["dir"]
                            logging.info("store: new root is %s", root)
                            base = _path
                        else:
                            dir = {
                                "date": str(
                                    datetime.datetime.now().strftime(
                                        "%b %d %Y %H:%M:%S"
                                    )
                                ),
                                "path": _path,
                                "name": _path,
                                "id": _path,
                                "perms": "rwxrwxrwx",
                                "type": "directory",
                                "size": 0,
                                "dir": BTrees.OOBTree.BTree()
                            }

                            logging.info("store: new dir id is %s", dir["dir"])
                            root[p] = dir
                            logging.info("store: added new dir id %s to current root %s with key %s", dir, root, p)
                            logging.info("store: added dir is %s", root[p])
                            directory = root = dir["dir"]
                            self.fs.root.registry[_path] = dir

                        logging.info("root id is now %s", root)
                logging.info("Adding file  %s to directory  [%s]", id, directory)
                directory[id] = file

                if path[-1] != "/" and len(name) > 0:
                    self.fs.root.registry[path + "/" + name] = file
                    logging.info("Adding to registry %s %s",path + "/" + name, file)
                else:
                    self.fs.root.registry[path + name] = file
                    logging.info("Adding to registry %s %s",path + name, file)

            logging.info("ROOT IS %s", [o for o in self.fs.root.objects])
            assert self.fs.objects == self.fs.root.objects
            # logging.info("STORE OBJECT  %s %s", path + "/" + name, _obj)
            # logging.info("OBJECTS LENGTH %s", len(self.fs.objects))

        def get_data(self, oid):
            obj: Data = self.fs.objects[oid]

            return obj.data

    def __init__(self, port=5558):
        self.rpcport = port
        logging.info("Starting NodeServer on port: {}".format(port))

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
            s = zerorpc.Server(self.NodeAPI())
            s.bind("tcp://0.0.0.0:{}".format(self.rpcport))
            s.run()

        def get_messages():
            import os
            import platform

            """Listen for pub/sub messages"""
            self.context = zmq.Context()
            self.socket = self.context.socket(zmq.SUB)

            """ Connect to pub/sub address """

            if "BROKER" in os.environ:
                host = os.environ["BROKER"]
                self.socket.connect("tcp://{}:{}".format(host, self.port))
            else:
                host = "0.0.0.0"
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
                    client.connect(parts[3])
                    client.hello("tcp://{}:{}".format(platform.node(), self.rpcport))

        # fs = self.fs = FileSystemFactory.get()
        # self.services += [fs]
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
        socket.connect("tcp://broker:%s" % str(self.port))

        # Receives a string format message

        self.process.start()
        self.rpc.start()

        time.sleep(1)
        import platform

        message = "NODE HI {} {}".format(
            platform.node(), "tcp://{}:{}".format(platform.node(), self.rpcport)
        )
        logging.info("Sending message: %s", message)
        socket.send_string(message)

        [service.start() for service in self.services]

        return True
