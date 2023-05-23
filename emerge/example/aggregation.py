import emerge.core.objects
from emerge import fs


@emerge.dataclass
class AggregationFile(emerge.core.objects.EmergeFile):
    @staticmethod
    def query(fs):
        from dataclasses import asdict

        import pandas as pd

        customers = fs.dir("/customers")

        df = pd.concat(
            [
                pd.DataFrame([asdict(cust)])[["name", "customerId", "value", "words"]]
                for cust in customers
            ]
        )
        group = df.groupby(["value"])

        return group


agg = AggregationFile(
    id="agg1", name="agg1", path="/aggregations", data="A query object"
)

# Put the new object on the server
fs.store(agg)

# Query my new object from the server (as a service)
# Perform dataframe aggregations on the server
# Return the results locally here as a dataframe
groups = fs.query("/aggregations/agg1")

# Compute size of each group and add it to count col
counts = groups.size().reset_index(name="count")
print(counts)

# Just get the group where value=5 and print it
print(groups.get_group(2).to_json(orient="records"))

# Sort the group+count dataframe and print it
sorts = counts.sort_values(by="value", ascending=False, inplace=False)
print(sorts)
print("---------------------------------")
# Query the sorted dataframe with an expression
print(sorts.query("value > 0 and count < 100"))
