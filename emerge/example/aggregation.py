import json
from dataclasses import dataclass

from emerge.core.client import Client
from emerge.core.objects import EmergeFile


@dataclass
class QueryFile(EmergeFile):
    import persistent.list

    results = persistent.list.PersistentList()

    def query(self, fs):
        """This only runs on the server and receives the filesystem object to traverse"""
        import pandas as pd

        from dataclasses import asdict

        old_list = fs.dir("/customers")

        df = pd.DataFrame()

        for o in old_list:
            d = pd.DataFrame([asdict(o)])
            d = d[['name', 'customerId', 'value']]
            df = df.append(d, ignore_index=True)

        group = df.groupby(['value'])

        return group.apply(lambda x: x.to_json(orient='records')).to_json()


query = QueryFile(id="agg1", name="agg1", path="/aggregations", data="A query object")

client = Client("0.0.0.0", "5558")
client.store(query)

results = client.query("/aggregations/agg1")
_r = json.loads(results)
for key, value in _r.items():
    print(key, json.dumps(json.loads(value), indent=4))
