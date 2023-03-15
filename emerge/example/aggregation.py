import emerge.core.objects
from emerge import fs


@emerge.dataclass
class AggregationFile(emerge.core.objects.EmergeFile):

    @staticmethod
    def query(fs):
        import pandas as pd
        from dataclasses import asdict

        customers = fs.dir("/customers")

        df = pd.concat([pd.DataFrame([asdict(cust)])[['name', 'customerId', 'value']] for cust in customers])
        group = df.groupby(['value', 'name'])

        return group.apply(lambda x: x.to_dict(orient='records'))


agg = AggregationFile(id="agg1", name="agg1", path="/aggregations", data="A query object")

fs.store(agg)

results = fs.query("/aggregations/agg1")

df = results.to_frame()

sorts = df.sort_values(by='name', ascending=True, inplace=False)
print(sorts)

