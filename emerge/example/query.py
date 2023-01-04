
from dataclasses import dataclass

from emerge.core.client import Client
from emerge.core.objects import EmergeFile


@dataclass
class QueryFile(EmergeFile):

    def query(self, server):
        import logging
        import json

        results = []

        objs = server.list("/inventory", True)
        logging.info("RESULTS %s", results)
        for oid in objs:
            obj = server.getobject(oid, True)
            logging.info("OBJ %s", obj)
            if hasattr(obj, 'unit_price') and obj.unit_price < 15:
                results += [json.loads(str(obj))]

        return results

    def __str__(self):
        import json

        return json.dumps(
            {
                "name": self.name,
                "path": self.path,
                "id": self.id,
                "perms": self.perms,
                "type": self.type,
                "data": self.data,
            }
        )


query = QueryFile(
    id="query1",
    name="query1",
    path="/queries")

client = Client("0.0.0.0", "6558")
client.store(query)

files = client.list("/queries", offset=0, size=0)
print(files)

results = client.query("/queries/query1")
print(results)
