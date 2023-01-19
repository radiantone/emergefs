from dataclasses import dataclass

import dill

from emerge.core.client import Client
from emerge.core.objects import EmergeFile


@dataclass
class Address(EmergeFile):

    street: str = ""
    city: str = ""
    state: str = ""


@dataclass
class Customer(EmergeFile):
    """Class for keeping track of an item in inventory."""

    address: Address = Address()
    name: str = ""


client = Client("0.0.0.0", "5558")

customer = Customer(
    id="customer1",
    name="johndoe",
    path="/customers",
    address=Address(id="address1", street="Park Place", city="Quincy", state="MA"),
)

print(str(customer.address))
print(dill.loads(dill.dumps(customer)))
client.store(customer)
print(customer)
