import random

import emerge.core.objects
from emerge import fs


@emerge.dataclass
class InventoryItem(emerge.core.objects.EmergeFile):
    """Class for keeping track of an item in inventory."""

    unit_price: float = 0.0
    quantity_on_hand: int = 0
    totalcost: float = 0.0

    def total_cost(self) -> float:
        import logging

        logging.debug("InventoryItem: total_cost executing")
        self.totalcost = self.unit_price * self.quantity_on_hand
        return self.totalcost


for i in range(1, 10):
    item = InventoryItem(
        id="widget" + str(i),
        name="widget" + str(i),
        perms="rwxrwxrwx",
        type="file",
        path="/inventory",
        data="A widget{} data".format(i),
        unit_price=random.uniform(1.5, 75.5),
        quantity_on_hand=random.randrange(0, 50),
    )
    print(item)
    fs.store(item)
