from emerge.core.client import Client

client = Client("0.0.0.0", "6558")

query = client.getobject("/queries/query1", False)

print(type(query), query.results)
