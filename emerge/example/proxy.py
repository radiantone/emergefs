from emerge import fs


widget1 = fs.proxy("/inventory/widget1")
# Invoke method on server
print(widget1.total_cost())
print(widget1.name)

widgets = fs.list("/inventory")
print(widgets)

proxies = [fs.proxy(widget) for widget in widgets]

# Executes each method on the server
print([proxy.total_cost() for proxy in proxies])

query = fs.proxy("/queries/query1")

for result in query.results:
    print(result)
    print(round(result.total_cost(), 1))
