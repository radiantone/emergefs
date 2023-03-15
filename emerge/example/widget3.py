from emerge import fs
import emerge.core.objects


@emerge.dataclass
class InventoryItem(emerge.core.objects.EmergeFile):
    """Custom Class for keeping track of an item in inventory."""

    unit_price: float = 0.0
    quantity_on_hand: int = 0
    totalcost: float = 0
    foo: str = "FOO"

    def foobar(self):
        return self.foo + " BAR"

    def total_cost(self) -> float:
        self.totalcost = self.unit_price * self.quantity_on_hand
        return self.totalcost

    def query(self, fs):
        """Runs on server"""
        self.results = []
        for obj in fs.dir("/inventory"):
            if obj.total_cost() < 400:
                self.results.append(obj)


# Create object with state/data
item = InventoryItem(
    id="widget1",
    name="widget1",
    path="/inventory",
    unit_price=3.0,
    quantity_on_hand=10,
    data="A widget{} data with FOO".format(1),
)
fs.store(item)

# Query my new class and return matching objects
widgets = fs.query("/inventory/widget1")
# or just use lambdas without a def query() method
widgets = fs.search(
    lambda o: hasattr(o, "unit_price") and o.total_cost() > 100 and o.unit_price < 3.5
)
