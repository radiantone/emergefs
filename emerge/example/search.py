from emerge import fs

results = fs.search(lambda o: hasattr(o, "unit_price") and o.unit_price < 3.5)
print(results)
