import emerge.core.objects
from emerge import fs


@emerge.dataclass
class AggregationFile(emerge.core.objects.EmergeFile):

    @staticmethod
    def query(fs):
        import pandas as pd
        from dataclasses import asdict

        customers = fs.dir("/customers")

        df = pd.concat([pd.DataFrame([asdict(cust)])[['name', 'customerId', 'value', 'words']] for cust in customers])
        group = df.groupby(['value'])

        return group


agg = AggregationFile(id="agg1", name="agg1", path="/aggregations", data="A query object")

fs.store(agg)

groups = fs.query("/aggregations/agg1")
print(groups.get_group(5).to_json(orient='records'))

series = groups.apply(lambda x: x.to_dict(orient='records'))
sorts = series.to_frame().sort_values(by='value', ascending=False, inplace=False)
print(sorts)


