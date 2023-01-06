import random
from dataclasses import dataclass

from emerge.core.client import Client
from emerge.core.objects import EmergeFile


@dataclass
class InventoryItem(EmergeFile):
    """Class for keeping track of an item in inventory."""

    unit_price: float = 0.0
    quantity_on_hand: int = 0

    def run(self):
        return "total cost:{}".format(self.total_cost())

    def total_cost(self) -> float:
        import logging

        logging.debug("InventoryItem: total_cost executing")
        return self.unit_price * self.quantity_on_hand

    def __str__(self):
        import json

        return json.dumps(
            {
                "name": self.name,
                "path": self.path,
                "id": self.id,
                "unit_price": self.unit_price,
                "quantity_on_hand": self.quantity_on_hand,
                "perms": self.perms,
                "type": self.type,
                "data": self.data,
            }
        )


client = Client("0.0.0.0", "6558")

item = InventoryItem(
    id="widget1",
    name="widget1",
    path="/inventory",
    unit_price=3.0,
    quantity_on_hand=10,
    data="A widget{} data".format(1),
)
client.store(item)
print(item)

print(client.run("/inventory/widget1", "total_cost"))


for i in range(2, 10):
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
    client.store(item)
