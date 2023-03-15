import logging
import os
import platform
import signal
import threading
from typing import List
from urllib.parse import urlparse

import BTrees.OOBTree
import dill
import graphene
from littletable import Table

from emerge.compute import Data
from emerge.core.client import Client
from emerge.core.objects import EmergeFile, Server
from emerge.fs.filesystem import FileSystemFactory

IS_BROKER = "ISBROKER" in os.environ

global broker

if not IS_BROKER:
    BROKER = os.environ["BROKER"]
    broker = Client(BROKER, "5558")
    logging.info("Connected to BROKER %s:5558", BROKER)
    logging.info("Contacting broker...")
    logging.info("broker object %s", broker)

    # Add myself to the brokers node list
    logging.info("Contacted broker...")


class QueryClass(graphene.ObjectType):
    pass


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
            self.fs.registry["/hello"] = {"status": "ok", "message": "hello there"}

            connection = self.fs.db.open()

            fsroot = connection.root()
            logging.info("ROOT IS %s", [o for o in fsroot])
            # with self.fs.session():
            #    """If the path is already created, set the directory to that path"""
            #    self.fs.root.objects["hello"] = ["hello", "there"]
            self.schemas = {}

            self.objects = Table("objects")
            for oid in fsroot.uuids:
                if type(fsroot.uuids[oid]) is dict:
                    _obj = fsroot.uuids[oid]
                else:
                    _obj = dill.loads(fsroot.uuids[oid])
                logging.info("Building schema for %s", _obj.__class__)
                _fields, self.schema = self._make_graphql(_obj)

                logging.info("_fields: %s", _fields)
                self.schemas[_obj.__class__.__name__] = self.schema

                try:
                    self.objects.insert(_obj)
                except KeyError:
                    self.objects.delete(id=oid)
                    self.objects.insert(_obj)

                try:
                    self.objects.create_index("uuid", unique=True)
                except:
                    pass

                for key in _fields.keys():
                    try:
                        logging.info("Creating index: %s", key)
                        self.objects.create_index(key, unique=False)
                    except:
                        pass

        def graphql(self, query):
            import json

            logging.info("graphql: query: %s", query)
            result = self.schema.execute(query)
            logging.info("RESULT %s", json.dumps(result.data, indent=4))

            return result.data

        def hello(self, address):
            logging.info("HELLO FROM {}".format(address))
            connection = self.fs.db.open()
            import transaction

            transaction.begin()
            root = connection.root()
            transaction.commit()

        def registry(self):
            import platform

            for name in self.fs.registry:
                logging.info("NAME OBJ: %s", self.fs.registry[name])

            registry = [
                self.fs.registry[name]
                for name in self.fs.registry
                if "type" in self.fs.registry[name]
                and self.fs.registry[name]["type"] == "file"
            ]

            return {"registry": registry, "host": platform.node()}

        def query(self, path, page=0, size=-1):
            import transaction

            connection = self.fs.db.open()

            fsroot = connection.root()
            logging.info("CALLING QUERY")
            obj = self.getobject(path, True)
            logging.info("query: obj %s %s", obj, type(obj))
            if hasattr(obj, "query"):
                # Object implements query method and receives the database reference
                # From there, the query method can scan the database and build a list of
                # results
                transaction.begin()
                r = obj.query(self)
                fsroot.uuids[obj.uuid] = dill.dumps(obj)
                transaction.commit()
                return dill.dumps(r)

        def getobject(self, path, nodill, page=0, size=-1):

            connection = self.fs.db.open()

            fsroot = connection.root()
            try:
                logging.info("getobject: path = %s", path)

                obj = fsroot.registry[path]
                logging.info("getobject: object %s", obj)

                if nodill:
                    the_obj = dill.loads(fsroot.uuids[obj["uuid"]])
                    return the_obj

                if obj["type"] == "reference":
                    logging.info("getobject: fetch file %s from %s", obj, obj["node"])
                    node = fsroot.registry["/nodes/" + obj["node"]]
                    logging.info("getobject: remote node %s", str(node))
                    _remote = urlparse(node["id"])
                    client = Client(_remote.hostname, _remote.port)
                    _obj = client.getobject(path, nodill)
                    logging.info("getobject: remote object %s", str(_obj))
                    if nodill:
                        return _obj
                    else:
                        return dill.dumps(_obj)

                if obj["type"] == "file":
                    the_obj = fsroot.uuids[obj["uuid"]]
                    logging.info("getobject: return file %s", obj)
                    return the_obj

                if obj["type"] == "node":
                    the_obj = fsroot.uuids[obj["uuid"]]
                    logging.info("getobject: return node %s", the_obj)
                    return the_obj

                elif obj["type"] == "directory":
                    return [dill.dumps(fsroot.uuids[o["uuid"]]) for o in obj["dir"]]
            except KeyError as ex:
                logging.error(ex)
                if not IS_BROKER:
                    logging.info("Contacting broker %s", BROKER)
                    broker = Client(BROKER, "5558")
                    obj = broker.getobject(path, nodill)
                    logging.info("getobject: from broker %s", obj)
                    return dill.dumps(obj)
            finally:
                connection.close()

        def get(self, path, page=0, size=-1):

            connection = self.fs.db.open()

            try:
                fsroot = connection.root()
                logging.info("get: path = %s", path)

                if path in fsroot.registry:
                    obj = fsroot.registry[path]

                    if obj["type"] == "directory":
                        obj["size"] = len(obj["dir"])
                    else:
                        obj["size"] = obj["size"]

                    logging.info("get: obj %s", obj)
                    file = {
                        "date": obj["date"],
                        "path": obj["path"],
                        "name": obj["name"],
                        "id": obj["id"],
                        "perms": obj["perms"],
                        "source": obj["source"] if "source" in obj else "",
                        "type": obj["type"],
                        "class": obj.__class__.__name__,
                        "size": obj["size"],
                        "version": obj["version"] if "version" in obj else 0,
                    }

                    return file
                else:
                    return {"error": True, "message": "Path not found"}
            finally:
                connection.close()

        def getdir(self, path, page=0, size=-1):

            connection = self.fs.db.open()

            fsroot = connection.root()
            logging.info("getdir: path = %s", path)
            obj = fsroot.registry[path]

            if obj["type"] == "directory":
                return [dill.dumps(obj["dir"][o]) for o in obj["dir"]]

            if isinstance(obj, BTrees.OOBTree.OOBTree):
                # return dill.dumps([dill.loads(obj[o]) for o in obj])
                return [dill.dumps(obj[o]) for o in obj]
            else:
                # _obj = dill.loads(obj)
                return obj

        def mkdir(self, path):

            connection = self.fs.db.open()

            fsroot = connection.root()
            logging.info("mkdir: path is %s", path)
            try:
                fsroot.registry[path]
                raise Exception("Path {} already exists".format(path))
            except KeyError:
                import datetime

                import transaction

                logging.info("mkdir: making new path is %s", path)
                splits = path.split("/")
                name = path.rsplit("/")[-1]

                dir_obj = {
                    "date": str(datetime.datetime.now().strftime("%b %d %Y %H:%M:%S")),
                    "path": path,
                    "name": path,
                    "id": path,
                    "perms": "rwxrwxrwx",
                    "type": "directory",
                    "size": 0,
                    "dir": BTrees.OOBTree.BTree(),
                }
                paths = splits[1:]
                dir = fsroot.objects

                for p in paths:
                    logging.info("mkdir: name %s p %s of paths %s", name, p, paths)
                    try:
                        file = dir[p]
                        if file["type"] == "directory":
                            dir = file["dir"]
                    except KeyError:
                        if p != name:
                            raise Exception("Path {} not found".format(p))

                        logging.info("{} directory created".format(p))
                        dir[name] = dir_obj
                        fsroot.registry[path] = dir_obj
                transaction.commit()

        def rm(self, path):
            import transaction

            connection = self.fs.db.open()

            fsroot = connection.root()
            try:
                paths = path.split("/")[1:]
                logging.info("rm: path is %s", path)
                dir = fsroot.objects
                file = None

                for p in paths:
                    logging.info("rm: p %s of paths %s", p, paths)
                    try:
                        file = dir[p]
                        logging.info("file: %s", file)
                        if file["type"] == "directory":
                            dir = file["dir"]
                            logging.info("dir: %s", list(dir))
                        elif file["type"] == "file":
                            logging.info("rm: removing %s", file)
                            # self.objects.remove(dir[p])
                            del dir[p]
                            transaction.commit()
                            return
                    except KeyError as ex:
                        logging.error(ex)
                        raise Exception("Path {} not found".format(path))

                if not file:
                    raise Exception("Path {} not found".format(path))

                if file and file["type"] == "directory" and len(file["dir"]) > 0:
                    raise Exception("Directory {} not empty".format(path))

                if file and dir != fsroot.objects:
                    logging.info("dir %s", file)
                    del file["parent"][p]
                    transaction.commit()

            except KeyError as ex:
                logging.error(ex)
                raise Exception("Path {} not found".format(path))

        def cp(self, source, dest):
            connection = self.fs.db.open()

            fsroot = connection.root()
            try:
                _source = fsroot.objects[source]
            except KeyError:
                raise Exception("Path {} not found".format(source))

            file = dill.dumps(_source)

            fsroot.objects[dest] = dill.loads(file)

        def dir(self, path):
            objs = self.list(path, True)
            for oid in objs:
                yield self.getobject(oid, True)

        def list(self, path, nodill, offset=0, size=0):
            connection = self.fs.db.open()

            try:
                fsroot = connection.root()
                logging.info("list: path %s", path)
                logging.info("root id is %s", fsroot.objects)

                logging.info("ROOT IS %s", [o for o in fsroot.objects])
                if path != "/":
                    paths = path.split("/")[1:]
                    dir = fsroot.objects
                    for p in paths:
                        logging.info("list: p %s of paths %s", p, paths)
                        try:
                            file = dir[p]
                            if file["type"] == "directory":
                                dir = file["dir"]
                            elif file["type"] == "file":
                                if not nodill:
                                    return dill.dumps(file)
                                else:
                                    return file
                        except KeyError:
                            raise Exception("Path {} not found".format(path))

                    if dir == fsroot.objects:
                        raise Exception("Path {} not found".format(path))
                    obj = dir
                    logging.info("found %s in %s %s", path, dir, len(obj))
                else:
                    obj = fsroot.objects
                    logging.info("obj is self.fs.objects %s", len(obj))

                files = []

                for name in obj:
                    file = obj[name]
                    if file["type"] == "directory":
                        files += ["dir:" + file["name"]]
                    elif file["type"] == "file" or file["type"] == "reference":
                        files += [file["path"] + "/" + file["name"]]
                    else:
                        files += [file["path"]]

                    if len(files) >= 200:
                        break

                if not nodill:
                    return dill.dumps(files)
                else:
                    return files
            finally:
                connection.close()

        def execute(self, oid, method):
            import inspect

            connection = self.fs.db.open()

            fsroot = connection.root()
            import transaction

            transaction.begin()
            try:
                obj = fsroot.registry[oid]

                if obj["type"] == "directory":
                    results = []
                    for name in obj["dir"]:
                        child = fsroot.registry[obj["path"] + "/" + name]
                        logging.info("%s", child)
                        the_obj = dill.loads(fsroot.uuids[child["uuid"]])

                        if hasattr(the_obj, method):
                            _method = getattr(the_obj, method)
                            results += [_method()]
                            fsroot.uuids[child["uuid"]] = dill.dumps(the_obj)
                    return results
                else:
                    the_obj = dill.loads(fsroot.uuids[obj["uuid"]])

                    if hasattr(the_obj, method):
                        _method = getattr(the_obj, method)
                        logging.info("Calling method %s on %s", method, the_obj)
                        if "fs" in inspect.getfullargspec(_method).args:
                            result = _method(fs=self)
                        else:
                            result = _method()
                        logging.info("after method obj %s", str(the_obj))
                        fsroot.uuids[obj["uuid"]] = dill.dumps(the_obj)
                        logging.info("After calling method %s: %s", method, the_obj)
                        logging.info("result: %s", result)
                        return result
                    else:
                        raise Exception("No such method on object")
            except KeyError as ex:
                import traceback

                logging.info("%s", traceback.format_exc())
                logging.error(ex)
                return "No such object {}".format(oid)
            finally:
                transaction.commit()

        def register(self, entry):
            import transaction

            logging.info("BROKER:register %s", entry)
            file = EmergeFile(**entry)
            self.store(entry["id"], entry["path"], entry["name"], "", dill.dumps(file))

            transaction.commit()

        def searchtext(self, field, query):
            base = getattr(self.objects.search, field)
            results = base(query)
            logging.info("ST RESULTS %s", results)
            _results = []

            for result in results:
                _results += [str(result)]
            logging.info("SEARCHTEXT %s", _results)
            return _results

        def search(self, where):
            lamd = dill.loads(where)
            logging.info("SEARCH LAMBDA: %s", lamd)
            results = self.objects.where(lamd)

            _results = []

            for result in results:
                _results += [str(result)]

            logging.info("SEARCH %s", _results)
            return _results

        def _make_graphql(self, obj):
            import json
            from functools import partial

            if isinstance(obj, EmergeFile):
                data = json.loads(str(obj))
            else:
                if type(obj) is dict:
                    data = obj

            fields = {}
            fields["uuid"] = graphene.String()

            for key, value in data.items():
                if type(value) is str:
                    fields[key] = graphene.String()

                if type(value) is int:
                    fields[key] = graphene.Int()

                if type(value) is float:
                    fields[key] = graphene.Float()

            logging.info("FIELDS: %s %s", obj.__class__.__name__, fields)
            item = type(
                obj.__class__.__name__ + "Resolver", (graphene.ObjectType,), fields
            )
            setattr(graphene.types.objecttype, item.__name__, item)

            def resolver(root, info, **kwargs):
                import json

                connection = self.fs.db.open()

                fsroot = connection.root()
                logging.info("resolve_widget: kwargs %s %s", info.field_name, kwargs)

                # use search indices
                def search_func(o):
                    logging.info("search_func: %s %s", o, kwargs)
                    for key, val in kwargs.items():
                        if val:
                            value = getattr(o, key)
                            logging.info("search_func: val %s value %s", val, value)
                            if value != val:
                                logging.info("search_func: returning False")
                                return False
                    logging.info("search_func: returning True")
                    return True

                results = self.objects.where(search_func)
                logging.info("resolver RESULTS %s", [str(result) for result in results])

                try:
                    _results = [json.loads(str(result)) for result in results]
                    logging.info(
                        "resolver _results1 %s", [result for result in _results]
                    )
                    fobjs = []
                    for result in _results:
                        robj = json.loads(str(dill.loads(fsroot.uuids[result["uuid"]])))
                        logging.info("R %s", robj)
                        fobjs += [robj]

                    logging.info("FOBJS %s", fobjs)
                    _results = [item(**result) for result in fobjs]
                except Exception as ex:
                    logging.error(ex)
                logging.info("resolver _results2 %s", _results)

                if info.field_name.find("List") >= 0:
                    return _results
                else:
                    return _results[0]

            qfields = {}
            qfields[obj.__class__.__name__] = graphene.Field(item, **fields)
            qfields[obj.__class__.__name__ + "List"] = graphene.List(item)
            params = {}

            for key in fields.keys():
                params[key] = None

            logging.info("make_grapql: params: %s", params)
            qfields["resolve_" + obj.__class__.__name__] = partial(resolver, **params)
            qfields["resolve_" + obj.__class__.__name__ + "List"] = partial(
                resolver, **params
            )
            logging.info("make_grapql: fields: %s", fields)
            logging.info("make_grapql: qfields: %s", qfields)
            query = type(obj.__class__.__name__ + "Query", (QueryClass,), qfields)
            setattr(graphene.types.objecttype, query.__name__, query)
            logging.info("make_grapql: query: %s", query)

            schema = graphene.Schema(query=query)
            logging.info(
                "_make_graphql: schema %s %s ::%s:: %s",
                schema,
                item,
                item.name,
                fields,
            )

            return fields, schema

        def _make_paths(self, paths, root, fsroot):
            import datetime

            base = ""
            directory = root

            for p in paths:
                _path = base + "/" + p
                logging.info("store: _path is now %s", _path)
                if p in root:
                    logging.info("store: p %s found in root %s", p, root)
                    root = directory = root[p]["dir"]
                    logging.info("store: new root is %s", root)
                    base = _path
                else:
                    dir = {
                        "date": str(
                            datetime.datetime.now().strftime("%b %d %Y %H:%M:%S")
                        ),
                        "path": _path,
                        "name": _path,
                        "id": _path,
                        "perms": "rwxrwxrwx",
                        "parent": root,
                        "type": "directory",
                        "node": platform.node(),
                        "size": 0,
                        "dir": BTrees.OOBTree.BTree(),
                    }

                    logging.info("store: new dir id is %s", dir["dir"])

                    root[p] = dir
                    logging.info(
                        "store: added new dir id %s to current root %s with key %s",
                        dir,
                        root,
                        p,
                    )
                    logging.info("store: added dir is %s", root[p])
                    directory = root = dir["dir"]

                    # I created a new directory from a path and need to add it
                    # to my registry for lookups
                    fsroot.registry[_path] = dir
                logging.info("root id is now %s", root)

            return root, directory

        def reindex(self):

            connection = self.fs.db.open()

            try:
                fsroot = connection.root()
                for uuid in fsroot.uuids:
                    the_obj = dill.loads(fsroot.uuids[uuid])
                    _fields, self.schema = self._make_graphql(the_obj)

                    logging.info("_fields: %s", _fields)
                    self.schemas[the_obj.__class__.__name__] = self.schema
                    try:
                        self.objects.create_index("uuid", unique=True)
                    except:
                        pass

                    for key in _fields.keys():
                        try:
                            self.objects.create_index(key, unique=False)
                        except:
                            pass
                        try:
                            logging.info("Creating index: %s", key)
                            self.objects.create_search_index(key, force=True)
                        except Exception as ex:
                            logging.error(ex)
            finally:
                connection.close()
            return

        def store(self, id, path, name, source, obj):
            import datetime
            import json
            from uuid import uuid4

            import dill
            import transaction

            if type(obj) is dict:
                _obj = obj
                _obj["node"] = platform.node()
            else:
                _obj = dill.loads(obj)
                _obj.node = platform.node()

            connection = self.fs.db.open()

            try:
                fsroot = connection.root()

                # TODO: Move this to the class so it can rebuild the schema
                # from the objects when it starts up new

                # Make graphql schema for object
                logging.info("_OBJ %s %s", type(_obj), obj)
                _fields, self.schema = self._make_graphql(_obj)

                # Store the schema
                logging.info("_fields: %s", _fields)
                self.schemas[_obj.__class__.__name__] = self.schema

                # Store the objects class in the classes registry
                logging.info("_OBJ %s %s", _obj.__class__, _obj)
                transaction.begin()
                fsroot.classes[_obj.__class__.__name__] = dill.dumps(_obj.__class__)
                transaction.commit()

                # Ensure object has a unique identifier
                _uuid = str(uuid4())

                # BEGIN TRANSACTION
                transaction.begin()

                if _obj.uuid is None or len(_obj.uuid) == 0:
                    _obj.uuid = _uuid
                else:
                    _uuid = _obj.uuid

                fsroot.uuids[_uuid] = dill.dumps(_obj)
                logging.info("NODE is %s", platform.node())
                file = {
                    "date": str(datetime.datetime.now().strftime("%b %d %Y %H:%M:%S")),
                    "path": _obj.path,
                    "name": _obj.name,
                    "id": _obj.id,
                    "perms": _obj.perms,
                    "source": source,
                    "type": _obj.type,
                    "class": _obj.__class__.__name__,
                    "size": len(obj),
                    "node": platform.node(),
                    "uuid": _uuid,
                    "obj": json.loads(str(_obj)),
                    "version": _obj.version if _obj.version else 0,
                }

                logging.info("STORE: %s", file)

                """If the path is already created, set the directory to that path"""
                if path in fsroot.objects:
                    directory = fsroot.objects[path]
                    logging.info("Found %s in root.objects", path)
                else:
                    """Create all the BTree objects for each section in the path"""
                    paths = path.split("/")[1:]
                    root = _root = fsroot.objects
                    logging.info("store: paths: %s", paths)
                    logging.info("root id %s", root)

                    """ Create BTree directories for each subpath if it doesn't exist
                    then set the directory to the last BTree in the path """
                    root, directory = self._make_paths(paths, root, fsroot)

                logging.info("Adding file  %s to directory  [%s]", id, directory)
                directory[id] = file

                if path[-1] != "/" and len(name) > 0:
                    fsroot.registry[path + "/" + name] = file
                    logging.info("Adding to registry %s %s", path + "/" + name, file)

                    if not IS_BROKER:
                        broker = Client(BROKER, "5558")
                        logging.info("broker object %s", broker)

                        # Add my object reference to the brokers directory,
                        # pointing back to me
                        logging.info(
                            "registering %s",
                            {
                                "path": file["path"],
                                "name": file["name"],
                                "type": "reference",
                                "id": file["id"],
                                "uuid": file["uuid"],
                                "node": platform.node(),
                            },
                        )
                        broker.register(
                            {
                                "path": file["path"],
                                "name": file["name"],
                                "type": "reference",
                                "id": file["id"],
                                "uuid": file["uuid"],
                                "node": platform.node(),
                            }
                        )
                else:
                    fsroot.registry[path + name] = file
                    logging.info("Adding to registry %s %s", path + name, file)

                    if not IS_BROKER:
                        broker = Client(BROKER, "5558")
                        logging.info("broker object %s", broker)

                        # Add my object reference to the brokers directory,
                        # pointing back to me
                        logging.info(
                            "registering %s",
                            {
                                "path": file["path"],
                                "name": file["name"],
                                "type": "reference",
                                "id": file["id"],
                                "uuid": file["uuid"],
                                "node": platform.node(),
                            },
                        )
                        broker.register(
                            {
                                "path": file["path"],
                                "name": file["name"],
                                "type": "reference",
                                "id": file["id"],
                                "uuid": file["uuid"],
                                "node": platform.node(),
                            }
                        )

                logging.info("_OBJ str %s", str(_obj))

                # Insert object in the searchable index
                try:
                    self.objects.insert(_obj)
                except KeyError:
                    self.objects.delete(id=_uuid)
                    self.objects.insert(_obj)

                # Create uuid index if it's not already there
                try:
                    self.objects.create_index("uuid", unique=True)
                except:
                    pass

                # Ensure there are indexes for the fields of the object
                for key in _fields.keys():
                    try:
                        self.objects.create_index(key, unique=False)
                    except:
                        pass
                    try:
                        logging.info("Creating index: %s", key)
                        self.objects.create_search_index(key, force=True)
                    except Exception as ex:
                        logging.error(ex)

                transaction.commit()
                # COMPLETE TRANSACTION

            finally:
                connection.close()

        def get_data(self, oid):
            obj: Data = self.fs.objects[oid]

            return obj.data

    def __init__(self, port=5558):
        self.rpcport = port
        logging.info("Starting NodeServer on port: {}".format(port))
        self.api = self.NodeAPI()

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
            s = zerorpc.Server(self.api)
            s.bind("tcp://0.0.0.0:{}".format(self.rpcport))
            s.run()

        def get_messages():
            import json
            import os
            import platform
            from uuid import uuid4

            import transaction

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

                logging.debug("IS_BROKER %s", IS_BROKER)
                if parts[1] == "HI":

                    connection = self.api.fs.db.open()

                    fsroot = connection.root()
                    client = zerorpc.Client()
                    client.connect(parts[3])
                    client.hello("tcp://{}:{}".format(platform.node(), self.rpcport))
                    # host = parts[3].split(":")[1].rsplit("/")[-1]
                    parse = urlparse(parts[3])
                    host = parse.hostname
                    port = parse.port

                    if IS_BROKER and host != platform.node():
                        # Get registry from parts[3]
                        node = {"address": parts[3]}
                        self.api.fs.nodes[parts[3]] = node
                        try:
                            self.api.mkdir("/nodes")
                        except:
                            pass

                        file = EmergeFile(id=host)
                        file.type = "node"
                        file.name = host
                        file.path = "/nodes/" + host
                        file.size = 0
                        file.uuid = str(uuid4())
                        file.id = parts[3]
                        file.host = host
                        file.port = port
                        file.node = platform.node()

                        nodes = fsroot.registry["/nodes"]["dir"]
                        if "/nodes/" + host not in nodes:
                            nodes["/nodes/" + host] = json.loads(str(file))

                        fsroot.registry["/nodes/" + host] = json.loads(str(file))
                        fsroot.uuids[file.uuid] = json.loads(str(file))
                        logging.info("STORED /NODES dir %s", json.loads(str(file)))
                        transaction.commit()

                        registry = client.registry()
                        logging.info("REGISTRY[%s] %s", parts[3], registry)

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
