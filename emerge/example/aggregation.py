import json
from dataclasses import dataclass

from emerge.core.client import Client
from emerge.core.objects import EmergeFile


@dataclass
class QueryFile(EmergeFile):
    import persistent.list

    results = persistent.list.PersistentList()

    @staticmethod
    def query(fs):
        import pandas as pd
        from dataclasses import asdict

        customers = fs.dir("/customers")

        df = pd.concat([pd.DataFrame([asdict(cust)]) for cust in customers])
        group = df.groupby(['value'])

        return group.apply(lambda x: x.to_dict(orient='records')).to_json()


query = QueryFile(id="agg1", name="agg1", path="/aggregations", data="A query object")

client = Client("0.0.0.0", "5558")
client.store(query)

results = client.query("/aggregations/agg1")

for key, value in results.items():
    print(key, value)
