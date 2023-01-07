from dataclasses import dataclass

from emerge.core.client import Client
from emerge.core.objects import EmergeFile


@dataclass
class QueryFile(EmergeFile):
    import persistent.list

    results = persistent.list.PersistentList()

    def query(self, fs):
        """This only runs on the server and receives the filesystem object to traverse"""
        import json

        objs = fs.list("/inventory", True)
        for oid in objs:
            obj = fs.getobject(oid, True)
            if obj.unit_price < 15:
                self.results.append(obj)

        return json.dumps([json.loads(str(result)) for result in self.results])


query = QueryFile(id="query1", name="query1", path="/queries")

client = Client("0.0.0.0", "5558")
client.store(query)

results = client.query("/queries/query1")
print(results)
