from emerge import fs
import emerge.core.objects

import dill


@emerge.dataclass
class Address(emerge.core.objects.EmergeFile):

    street: str = ""
    city: str = ""
    state: str = ""


@emerge.dataclass
class Customer(emerge.core.objects.EmergeFile):
    """Class for keeping track of an item in inventory."""

    address: Address = Address()
    name: str = ""


customer = Customer(
    id="customer1",
    name="johndoe",
    path="/customers",
    address=Address(id="address1", street="Park Place", city="Quincy", state="MA"),
)

print(str(customer.address))
print(dill.loads(dill.dumps(customer)))
fs.store(customer)
print(customer)