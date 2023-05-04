from typing import List

from persistent import Persistent

import emerge.core.objects
from emerge import fs


class MyClass(emerge.core.objects.EmergeFile):
    """Custom class"""

    text = None

    def data(self):
        """Return some data"""
        return self.text

    def run(self):
        return "wordsA:" + str(self.word_count())

    def word_count(self):
        return len(self.text.split(" "))


class Collection(Persistent):
    list: List = []


@emerge.dataclass
class InventoryItem(emerge.core.objects.EmergeFile):
    """Class for keeping track of an item in inventory."""

    unit_price: float = 0.0
    quantity_on_hand: int = 0

    def run(self):
        return "total cost:{}".format(self.total_cost())

    def total_cost(self) -> float:
        return self.unit_price * self.quantity_on_hand


item = InventoryItem(
    id="widget1",
    name="widget",
    path="/inventory",
    unit_price=3.0,
    quantity_on_hand=10,
    data="A widget{} data".format(1),
)