import dill
import zerorpc


class Client:
    def __init__(self, host, port):
        self.client = zerorpc.Client()
        self.client.connect("tcp://{}:{}".format(host, port))

    def store(self, obj):
        self.client.store(obj.id, obj.path, obj.name, dill.dumps(obj))

    def list(self, path, offset=0, size=0):
        return dill.loads(self.client.list(path, offset, size))

    def get(self, oid, offset=0, size=0):
        file = self.client.get(oid, offset=offset, size=size)

        _files = []
        if type(file) is list:
            for f in file:
                _f = dill.loads(f)
                if "obj" in _f:
                    _f["obj"] = dill.loads(_f["obj"])
                _files += [_f]
        else:
            if "obj" in file:
                file["obj"] = dill.loads(file["obj"])
            _files = file

        return _files

    def run(self, oid, method):
        return self.client.execute(oid, method)
