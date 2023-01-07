<img src="./img/logo.png" width="200">

*Serverless, object-oriented, computational file system for python*


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

### Querying the Filesystem

Given the following object with a defined `query` method, using the `query` command will invoke the query method passing in a reference to the filesystem for the method to query.

```python
@dataclass
class QueryFile(EmergeFile):
    import persistent.list

    results = persistent.list.PersistentList()

    def query(self, fs):
        """This only runs on the server and receives the filesystem object to traverse"""
        import json

        objs = fs.list("/inventory", True)
        for oid in objs:
            obj = fs.getobject(oid, True)
            if obj.unit_price < 15:
                self.results.append(obj)

        return json.dumps([json.loads(str(result)) for result in self.results])
```
Invoke the query object
```bash
$ emerge query /queries/query1
[{"name": "widget1", "path": "/inventory", "id": "widget1", "unit_price": 3.0, "quantity_on_hand": 10, "perms": "rwxrwxrwx", "type": "file", "data": "A widget1 data"}, {"name": "widget2", "path": "/inventory", "id": "widget2", "unit_price": 14.470011665792036, "quantity_on_hand": 30, "perms": "rwxrwxrwx", "type": "file", "data": "A widget2 data"}, {"name": "widget3", "path": "/inventory", "id": "widget3", "unit_price": 10.57263472290883, "quantity_on_hand": 13, "perms": "rwxrwxrwx", "type": "file", "data": "A widget3 data"}, {"name": "widget1", "path": "/inventory", "id": "widget1", "unit_price": 3.0, "quantity_on_hand": 10, "perms": "rwxrwxrwx", "type": "file", "data": "A widget1 data"}, {"name": "widget2", "path": "/inventory", "id": "widget2", "unit_price": 14.470011665792036, "quantity_on_hand": 30, "perms": "rwxrwxrwx", "type": "file", "data": "A widget2 data"}, {"name": "widget3", "path": "/inventory", "id": "widget3", "unit_price": 10.57263472290883, "quantity_on_hand": 13, "perms": "rwxrwxrwx", "type": "file", "data": "A widget3 data"}, {"name": "widget1", "path": "/inventory", "id": "widget1", "unit_price": 3.0, "quantity_on_hand": 10, "perms": "rwxrwxrwx", "type": "file", "data": "A widget1 data"}, {"name": "widget2", "path": "/inventory", "id": "widget2", "unit_price": 14.470011665792036, "quantity_on_hand": 30, "perms": "rwxrwxrwx", "type": "file", "data": "A widget2 data"}, {"name": "widget3", "path": "/inventory", "id": "widget3", "unit_price": 10.57263472290883, "quantity_on_hand": 13, "perms": "rwxrwxrwx", "type": "file", "data": "A widget3 data"}, {"name": "widget1", "path": "/inventory", "id": "widget1", "unit_price": 3.0, "quantity_on_hand": 10, "perms": "rwxrwxrwx", "type": "file", "data": "A widget1 data"}, {"name": "widget2", "path": "/inventory", "id": "widget2", "unit_price": 14.470011665792036, "quantity_on_hand": 30, "perms": "rwxrwxrwx", "type": "file", "data": "A widget2 data"}, {"name": "widget3", "path": "/inventory", "id": "widget3", "unit_price": 10.57263472290883, "quantity_on_hand": 13, "perms": "rwxrwxrwx", "type": "file", "data": "A widget3 data"}]
```

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