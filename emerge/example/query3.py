from emerge import fs

query = fs.getobject("/queries/query1", False)

for result in query.results:
    print(round(result.total_cost(), 1))
