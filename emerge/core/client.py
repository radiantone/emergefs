import dill
import zerorpc


class Client:
    def __init__(self, host, port):
        self.client = zerorpc.Client()
        self.client.connect("tcp://{}:{}".format(host, port))

    def store(self, obj):
        self.client.store(obj.id, obj.path, obj.name, dill.dumps(obj))

    def get(self, oid):
        return dill.loads(self.client.get(oid))

    def run(self, oid, method):
        return self.client.execute(oid, method)
