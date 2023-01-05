from dataclasses import dataclass

from emerge.core.client import Client
from emerge.core.objects import EmergeFile


@dataclass
class QueryFile(EmergeFile):
    import persistent.list

    results = persistent.list.PersistentList()

    def query(self, fs):
        import json
        import logging

        objs = fs.list("/inventory", True)
        for oid in objs:
            obj = fs.getobject(oid, True)
            logging.info("OBJ %s %s", type(obj), obj)
            if hasattr(obj, "unit_price") and obj.unit_price < 15:
                self.results.append(obj)

        logging.info("self.RESULTS %s", self.results)
        return json.dumps([json.loads(str(result)) for result in self.results])


query = QueryFile(id="query1", name="query1", path="/queries")

client = Client("0.0.0.0", "6558")
client.store(query)

results = client.query("/queries/query1")
print(results)
