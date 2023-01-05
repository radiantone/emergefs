from emerge.core.client import Client


results = Client("0.0.0.0", "6558").query("/queries/query1")
print(results)
