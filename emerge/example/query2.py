from emerge.core.client import Client

results = Client("0.0.0.0", "5558").query("/queries/query1")
print(results)
