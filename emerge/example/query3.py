from emerge.core.client import Client

client = Client("0.0.0.0", "6558")

query = client.getobject("/queries/query1", False)

for result in query.results:
    print(round(result.total_cost(), 1), str(result))
