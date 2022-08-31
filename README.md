<img src="./img/logo.png" width="200">

Distributed, computational, object-based file system in pure python


> emerge combines the notion of an object persistent store and service API mesh into one design as a distributed filesystem.


Whereas with current REST/API type architectural patterns, you would do the following:

- Create database schemas representing your data objects (data modeling)
- Retrieve data from databases using separate query language (e.g. SQL) 
- Map data query results back into objects
- Write separate code that operates on the re-hydrated objects (business logic)
- Write separate code still that exposes said operations over a network (API)
- Write separate code still that translates from incoming requests to said operations and said objects (HTTP)
- And keeping everything in sync, probably writing more code to make this maintenance headache easier
- All these transformations are slow, difficult to manage and get in the way of actual work

With emerge, you simply:

- Create a custom python class that encapsulates your data and methods that operate on that data.
- Store the objects in the emerge filesystem
- Request those objects by their path (same as a file)
- Run methods on retrieved objects (locally or remotely: implicit servicing)
- Celebrate!

## Benefits

- No Database schemas or query languages
- No `Impedence Mismatches` between layers
- No visible middleware
- No protocol hassles
- No API scaffolding
- Ultra fast
- Ultra simple
- Plain Old Python end-to-end
- Scriptable CLI for interacting with filesystem

## Examples

```python
from emerge.core.client import Client
from emerge.core.objects import EmergeFile

@dataclass
class InventoryItem(EmergeFile):
    
    unit_price: float = 0.0
    quantity_on_hand: int = 0

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

client = Client("0.0.0.0", "6558")  # Connect to any node

client.store(item)
```
### Browse Filesystem
Browse the emerge object filesystem from command line:
```bash
$ emerge ls
inventory
$ emerge ls -l 
rwxrwxrwx 1        Aug 31 2022 14:08:37  inventory 
$ emerge ls -l /inventory
rwxrwxrwx 5.6K     Aug 31 2022 14:08:37  widget    
$ emerge cat /inventory/widget
{"name": "widget", "path": "/inventory", "id": "widget1", "price": 3.0, "quantity": 10, "perms": "rwxrwxrwx", "type": "file", "data": "A widget1 data"}
$ 

```
Listing the directory, shows the directory contents length in the size column. In this case "1".
For the widget object, the object size is shown 5.6K

### Execute Remote Methods

```bash
$ emerge remote /inventory/widget total_cost
30.0
```
> Important to understand that the custom class `InventoryItem` with its methods was created in the client, on-the-fly and stored in emerge.
> No code update, recompile, redeploy of the emerge network is needed.

### Execute Local Methods

```bash
$ emerge local /inventory/widget total_cost
30.0
```