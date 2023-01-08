from emerge.core.client import Client

client = Client("0.0.0.0", "5558")

widget1 = client.proxy("/inventory/widget1")
# Invoke method on server
print(widget1.total_cost())

widgets = client.list("/inventory")
print(widgets)

proxies = [client.proxy(widget) for widget in widgets]

# Executes each method on the server
print([proxy.total_cost() for proxy in proxies])

query = client.proxy("/queries/query1")

for result in query.results:
    print(result)
    print(round(result.total_cost(), 1))
