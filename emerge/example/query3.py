from emerge.core.client import Client

client = Client("0.0.0.0", "5558")

query = client.getobject("/queries/query1", False)

for result in query.results:
    print(round(result.total_cost(), 1))
