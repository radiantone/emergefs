from emerge.core.client import Client

client = Client("0.0.0.0", "5558")

results = client.search(lambda o: o.unit_price < 200)
print(results)
