from emerge.core.client import Client


client = Client("0.0.0.0", "6558")


results = client.query("/queries/query1")
print(results)
