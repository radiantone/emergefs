import emerge.core.objects
from emerge import fs


@emerge.dataclass
class InventoryItem(emerge.core.objects.EmergeFile):
    """Class for keeping track of an item in inventory."""

    unit_price: float = 0.0
    quantity_on_hand: int = 0
    totalcost: float = 0
    foo: str = "FOO"

    def combine(self):
        return "COMBINED"

    def total_cost(self) -> float:
        import logging

        logging.debug("InventoryItem: total_cost executing")
        self.totalcost = self.unit_price * self.quantity_on_hand
        return self.totalcost


item = InventoryItem(
    id="widget1",
    name="widget1",
    path="/inventory",
    unit_price=3.0,
    quantity_on_hand=10,
    data="A widget{} data with FOO".format(1),
)
fs.store(item)
print(item)
