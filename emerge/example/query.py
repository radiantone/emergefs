import emerge.core.objects
from emerge import fs


@emerge.dataclass
class QueryFile(emerge.core.objects.EmergeFile):
    import persistent.list

    results = persistent.list.PersistentList()

    def query(self, fs):
        """This only runs on the server and receives the filesystem object to traverse"""
        self.results = []
        for obj in fs.dir("/inventory"):
            if obj.unit_price < 20:
                self.results.append(obj)

        return str(self.results)


query = QueryFile(id="query1", name="query1", path="/queries", data="A query object")

fs.store(query)

results = fs.query("/queries/query1")
print(results)
