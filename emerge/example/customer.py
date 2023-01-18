from dataclasses import dataclass
from emerge.core.client import Client
from emerge.core.objects import EmergeFile


@dataclass
class Address(EmergeFile):

    street: str = ''
    city: str = ''
    state: str = ''


@dataclass
class Customer(EmergeFile):
    """Class for keeping track of an item in inventory."""

    address: Address = None
    name: str = ''


client = Client("0.0.0.0", "5558")

customer = Customer(
    id="customer1",
    name="johndoe",
    path="/customers",
    address=Address(id="address1", street="Park Place", city="Quincy", state="MA")
)
client.store(customer)
print(customer)
