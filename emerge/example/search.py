from emerge.core.client import Client

client = Client("0.0.0.0", "5558")

results = client.search(lambda o: hasattr(o, "unit_price") and o.unit_price < 3.5)
print(results)
