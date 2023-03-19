<img src="./images/logo.png" width="200">

*Serverless, object-oriented, computational file system for python*


> emerge combines the notion of an object persistent store and service API mesh into one design as a distributed filesystem with computational features.


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

## Usage

```bash
$ emerge
Usage: emerge [OPTIONS] COMMAND [ARGS]...

Options:
  --debug  Debug switch
  --help   Show this message and exit.

Commands:
  call     Call an object method
  cat      Display contents of an object
  code     List source code of an object
  cp       Copy object command
  help     Display details of an objects class
  ls       List files in a directory
  methods  Display available methods for an object
  mkdir    Make directory command
  node     Emerge node commands
  query    Execute query method of an object
  rm       Remove object command
```
## Examples

```python
from emerge.core.client import Client
from emerge.core.objects import EmergeFile

@dataclass
class InventoryItem(EmergeFile):
    """ Create your own classes on-the-fly """
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

client = Client("0.0.0.0", "5558")  # Connect to any node

# Stores item under path /inventory/widget
client.store(item)
```
Execute object methods as-a-service
> NOTE: Method runs on the host containing the object
```python
client.run("/inventory/widget", "total_cost")
```
Retrieve object and run methods on it locally
```python
widget = client.get("/inventory/widget")
total_cost = widget.total_cost()
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

NOTE: Method executes on the server, only results are returned
```bash
$ emerge call /inventory/widget total_cost
30.0
```
> Important to understand that the custom class `InventoryItem` with its methods was created in the client, on-the-fly and stored in emerge.
> No code update, recompile, redeploy of the emerge network is needed.

### Execute Local Methods
NOTE: Object (including its state/data) is retrieved from the server and the method invoked in the local process
```bash
$ emerge call --local /inventory/widget total_cost
30.0
```

### Execute A Method on All Objects in a Directory
NOTE: Execution occurs on the server
```bash
$ emerge call /inventory total_cost
[30.0, 434.10034997376107, 137.4442513978148, 907.5910237092307, 129.6896355950612, 705.798940493996, 589.6721640143035, 1408.5984146794274, 1722.7589088095774]
```

### Getting Help on an Object
```bash
$ emerge help /inventory/widget1
Help on InventoryItem in module __main__ object:

class InventoryItem(emerge.core.objects.EmergeFile)
 |  InventoryItem(id: str, data: str = '', name: str = '', path: str = '/', perms: str = 'rwxrwxrwx', type: str = 'file', unit_price: float = 0.0, quantity_on_hand: int = 0) -> None
 |  
 |  Class for keeping track of an item in inventory.
 |  
 |  Method resolution order:
 |      InventoryItem
 |      emerge.core.objects.EmergeFile
 |      emerge.core.objects.EmergeObject
 |      emerge.data.EmergeData
 |      persistent.Persistent
 |      builtins.object
 |  
 |  Methods defined here:
 |  
 |  __eq__(self, other)
 |  
 |  __init__(self, id: str, data: str = '', name: str = '', path: str = '/', perms: str = 'rwxrwxrwx', type: str = 'file', unit_price: float = 0.0, quantity_on_hand: int = 0) -> None
:
```

### Getting Methods of an Object 
```bash
$ emerge methods /inventory/widget7
run ()
total_cost () -> float
```

### Showing the Source Code of an Object
```bash
$ emerge code /inventory/widget1
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


```
### Getting Objects
`emerge` is a distributed and federated namespace platform serving python objects like a filesystem.
When requesting an object by path, you can connect to any node in the filesystem to make this request.
If that node does not host the object, it will consult the broker which will have a reference to where the file path is being held and retrieve it from that node.

In the example output below, let's assume we have stored the object `/inventory/widget1` on the broker node.
The node at `localhost:5559` does not have knowledge of that object.

When we attempt to ask `localhost:5559` for `/inventory/widget` it first checks its own registry for that path, if it doesn't have it, it passes the request to the broker and you get the expected result.

The second call `emerge cat /inventory/widget1` defaults to requesting the object from the broker.

```bash
$ emerge -h localhost:5559 cat /inventory/widget1
{"data": "A widget1 data", "date": "Jan 15 2023 03:00:31", "id": "widget1", "name": "widget1", "node": "", "path": "/inventory", "perms": "rwxrwxrwx", "quantity_on_hand": 10, "totalcost": 30.0, "type": "file", "unit_price": 3.0, "uuid": "af9720c3-01f8-43bd-b0a4-6988b0061997"}
$ emerge cat /inventory/widget1
{"data": "A widget1 data", "date": "Jan 15 2023 03:00:31", "id": "widget1", "name": "widget1", "node": "", "path": "/inventory", "perms": "rwxrwxrwx", "quantity_on_hand": 10, "totalcost": 30.0, "type": "file", "unit_price": 3.0, "uuid": "af9720c3-01f8-43bd-b0a4-6988b0061997"}


```

### Querying the Filesystem


#### Query With a Lambda
`emerge` doesn't have a DSL query language, it uses `plain-old-python`! This removes a lot of layers, mappings, serializers and other complexities used between traditional SQL databases, ORMs, objects etc.
Simpler is better!
```python
from emerge.core.client import Client

client = Client("0.0.0.0", "5558")

results = client.search(lambda o: hasattr(o, 'unit_price') and o.unit_price < 3.5)
print(results)
```
```bash
['{"data": "A widget1 data", "id": "widget1", "name": "widget1", "path": "/inventory", "perms": "rwxrwxrwx", "quantity_on_hand": 10, "totalcost": 0.0, "type": "file", "unit_price": 3.0, "uuid": "c959c600-9404-4d94-b8d4-135b8e631da1"}', 
'{"data": "A widget1 data", "id": "widget1", "name": "widget1", "path": "/inventory", "perms": "rwxrwxrwx", "quantity_on_hand": 10, "totalcost": 0.0, "type": "file", "unit_price": 3.0, "uuid": "ec7a3450-c02e-4405-a522-55f56c48106f"}', 
'{"data": "A widget2 data", "id": "widget2", "name": "widget2", "path": "/inventory", "perms": "rwxrwxrwx", "quantity_on_hand": 11, "totalcost": 0.0, "type": "file", "unit_price": 3.4092252235237934, "uuid": "86b6802a-5fad-4305-95ec-ae56c7e1d1ee"}', 
'{"data": "A widget3 data", "id": "widget3", "name": "widget3", "path": "/inventory", "perms": "rwxrwxrwx", "quantity_on_hand": 26, "totalcost": 0.0, "type": "file", "unit_price": 3.2701771680050653, "uuid": "157676d2-80fc-4737-a895-a3ed69809fa6"}', 
'{"data": "A widget1 data", "id": "widget1", "name": "widget1", "path": "/inventory", "perms": "rwxrwxrwx", "quantity_on_hand": 10, "totalcost": 0.0, "type": "file", "unit_price": 3.0, "uuid": "57c2dc38-beef-461e-b77b-a736656a2a61"}']

```
#### Using a QueryObject

Given the following object with a defined `query` method, using the `query` command will invoke the query method passing in a reference to the filesystem for the method to query.

```python
@dataclass
class QueryFile(EmergeFile):
    import persistent.list

    results = persistent.list.PersistentList()

    def query(self, fs):
        """This only runs on the server and receives the filesystem object to traverse"""

        self.results = []
        for obj in fs.dir("/inventory"):
            if obj.unit_price < 15:
                self.results.append(obj)

        return [str(result) for result in self.results]
```
Invoke the query object
```bash
$ emerge query /queries/query1
[{"name": "widget1", "path": "/inventory", "id": "widget1", "unit_price": 3.0, "quantity_on_hand": 10, "perms": "rwxrwxrwx", "type": "file", "data": "A widget1 data"}, {"name": "widget2", "path": "/inventory", "id": "widget2", "unit_price": 14.470011665792036, "quantity_on_hand": 30, "perms": "rwxrwxrwx", "type": "file", "data": "A widget2 data"}, {"name": "widget3", "path": "/inventory", "id": "widget3", "unit_price": 10.57263472290883, "quantity_on_hand": 13, "perms": "rwxrwxrwx", "type": "file", "data": "A widget3 data"}, {"name": "widget1", "path": "/inventory", "id": "widget1", "unit_price": 3.0, "quantity_on_hand": 10, "perms": "rwxrwxrwx", "type": "file", "data": "A widget1 data"}, {"name": "widget2", "path": "/inventory", "id": "widget2", "unit_price": 14.470011665792036, "quantity_on_hand": 30, "perms": "rwxrwxrwx", "type": "file", "data": "A widget2 data"}, {"name": "widget3", "path": "/inventory", "id": "widget3", "unit_price": 10.57263472290883, "quantity_on_hand": 13, "perms": "rwxrwxrwx", "type": "file", "data": "A widget3 data"}, {"name": "widget1", "path": "/inventory", "id": "widget1", "unit_price": 3.0, "quantity_on_hand": 10, "perms": "rwxrwxrwx", "type": "file", "data": "A widget1 data"}, {"name": "widget2", "path": "/inventory", "id": "widget2", "unit_price": 14.470011665792036, "quantity_on_hand": 30, "perms": "rwxrwxrwx", "type": "file", "data": "A widget2 data"}, {"name": "widget3", "path": "/inventory", "id": "widget3", "unit_price": 10.57263472290883, "quantity_on_hand": 13, "perms": "rwxrwxrwx", "type": "file", "data": "A widget3 data"}, {"name": "widget1", "path": "/inventory", "id": "widget1", "unit_price": 3.0, "quantity_on_hand": 10, "perms": "rwxrwxrwx", "type": "file", "data": "A widget1 data"}, {"name": "widget2", "path": "/inventory", "id": "widget2", "unit_price": 14.470011665792036, "quantity_on_hand": 30, "perms": "rwxrwxrwx", "type": "file", "data": "A widget2 data"}, {"name": "widget3", "path": "/inventory", "id": "widget3", "unit_price": 10.57263472290883, "quantity_on_hand": 13, "perms": "rwxrwxrwx", "type": "file", "data": "A widget3 data"}]
```

#### Retrieving Stored Results Later

The query class may retain the results as in the example above. This way, another client can simply request the currently stored results without re-executing the query

```python
from emerge.core.client import Client

client = Client("0.0.0.0", "5558")

# Just retrieve the stored query object
query = client.getobject("/queries/query1", False)

# And access its data like a regular python object
for result in query.results:
    print(round(result.total_cost(), 1))
```
Output
```python
30.0
434.1
137.4
30.0
434.1
137.4
30.0
434.1
137.4
30.0
434.1
137.4
```
### Using Object Proxies
Emerge can proxy an object you created on-the-fly and stored in the filesystem so you can invoke methods on it directly, rather than using the `client` object to execute methods.
```python
from emerge.core.client import Client

client = Client("0.0.0.0", "5558")

widget1 = client.proxy("/inventory/widget1")
# Invoke method on server
print(widget1.total_cost())

widgets = client.list("/inventory")
print(widgets)

proxies = [client.proxy(widget) for widget in widgets]

# Executes each method on the server
print([proxy.total_cost() for proxy in proxies])

query = client.proxy("/queries/query1")

# Access member as if local. results is lazy loaded from the server
for result in query.results:
    print(result)
    print(round(result.total_cost(), 1))
```

### GraphQL queries
`emerge` will automatically create the required GraphQL schemas and resolvers for your objects!

Given the following class you create an object and insert into the filesystem.
```python
from dataclasses import dataclass

from emerge.core.client import Client
from emerge.core.objects import EmergeFile


@dataclass
class InventoryItem(EmergeFile):
    """Class for keeping track of an item in inventory."""

    unit_price: float = 0.0
    quantity_on_hand: int = 0
    totalcost: float = 0
    foo: str = "FOO"

    def run(self):
        return "total cost:{}".format(self.total_cost())

    def total_cost(self) -> float:
        import logging

        logging.debug("InventoryItem: total_cost executing")
        self.totalcost = self.unit_price * self.quantity_on_hand
        return self.totalcost


client = Client("0.0.0.0", "5558")

item = InventoryItem(
    id="widget1",
    name="widget1",
    path="/inventory",
    unit_price=3.0,
    quantity_on_hand=10,
    data="A widget{} data".format(1),
)
client.store(item)
```
Once `emerge` as received and stored your custom object/class it will generate the GraphQL artifacts needed to query it.
Internally, `emerge` creates and maintains optimize indicies over your custom object fields dynamically, making it super-fast to execute queries in memory.
Then issue a GraphQL query to find it
```bash

$ cat query1.json 
query {
  InventoryItem(name: "widget1") {
    name
    id
    path
  }
}
$ emerge graphql "$(cat query1.json)"
{'InventoryItem': {'name': 'widget1', 'id': 'widget1', 'path': '/inventory'}}
$ cat query3.json 
query {
  InventoryItemList {
    name
    id
    path
    uuid
    totalcost
  }
}
$ emerge graphql "$(cat query3.json)"
{'InventoryItemList': [{'name': 'widget8', 'id': 'widget8', 'path': '/inventory', 'uuid': '3fd460a1-07a7-4a3a-8804-87ef0c4cee4f', 'totalcost': 0.0}, 
{'name': 'widget3', 'id': 'widget3', 'path': '/inventory', 'uuid': '4d7d8d2d-2811-4444-a098-ac1c652073f7', 'totalcost': 0.0}, 
{'name': 'widget9', 'id': 'widget9', 'path': '/inventory', 'uuid': '8b8c4a11-1e01-4a9f-9070-9ea31e18240d', 'totalcost': 0.0}, 
{'name': 'widget4', 'id': 'widget4', 'path': '/inventory', 'uuid': '8ba02fc6-5d59-4b03-ae2a-2f4807acb879', 'totalcost': 0.0}, 
{'name': 'query1', 'id': 'query1', 'path': '/queries', 'uuid': 'b2e188fe-e693-4338-a619-71e8d9fa6690', 'totalcost': None}, 
{'name': 'widget1', 'id': 'widget1', 'path': '/inventory', 'uuid': 'c959c600-9404-4d94-b8d4-135b8e631da1', 'totalcost': 0.0}, 
{'name': 'query1', 'id': 'query1', 'path': '/queries', 'uuid': 'd7ab0d1f-7bf7-4962-9d34-d92bb3ff7069', 'totalcost': None}

```

## Running a Node

```bash
$ emerge --debug node start
2022-08-31 10:48:34,261 : root DEBUG : Debug ON
2022-08-31 10:48:34,322 : root INFO : Starting NodeServer on port: 5558
2022-08-31 10:48:34,322 : root DEBUG : [NodeServer] Setup...
2022-08-31 10:48:34,322 : root DEBUG : [NodeServer] start...
2022-08-31 10:48:34,323 : root DEBUG : Subscribed to NODE on tcp://0.0.0.0:5557
2022-08-31 10:48:34,323 : root DEBUG : get_messages
2022-08-31 10:48:34,323 : root DEBUG : Waiting on message
2022-08-31 10:48:34,324 : root INFO : Z0DBFileSystem setup
2022-08-31 10:48:34,324 : ZODB.BaseStorage DEBUG : create storage emerge.fs
2022-08-31 10:48:34,324 : txn.139737146840640 DEBUG : new transaction
2022-08-31 10:48:34,324 : txn.139737146840640 DEBUG : commit
2022-08-31 10:48:34,325 : root INFO : Z0DBFileSystem start
2022-08-31 10:48:34,325 : zerorpc.events DEBUG : bound to tcp://0.0.0.0:5558 (status=<SocketContext(bind='tcp://0.0.0.0:5558')>)

```

### Using Docker Compose
`emerge` comes with a docker compose file to run a broker node and a secondary node.
```bash
$ make up
$ make down
$ make clean
```
