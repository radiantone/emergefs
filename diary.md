## May 2023

- Added pluggable Server client classes (e.g. Z0RPCClient, HTTPClient - future) 
- Initial planning for running emerge from within pyodide
- Code housekeeping
- Design slides
- Added geometry example
- Added Abstractions for FileSystem that allows various implementations to be used:
  - SQLFileSystem
  - S3FileSystem
  - DynamoDBFileSystem
- Added Abstractions for NodeServer to allow various implementations
  - Z0DBNodeServer
  - RESTNodeServer
- Added Abstractions for IClient to allow various implementations
  - Z0RPCClient
  - RESTClient
  

## March 2023

- Added object versions
- Added aggregation support/examples
- Added transaction managers in server
- Misc fixes, enhancements and optimizations

## Jan 12, 2023

- Added GraphQL support, fixes, etc

## Jan 5, 2023

- Added query objects with persistent results
- Cleaned up command names/usage
- Added methods/help for an object

## Aug 29, 2022

- Paths are broken into directories and subtrees are created to store objects
- root["/registry"] stores ids for all objects but not visible in root.objects listings
- Added properties to stored objects: type, perms, owner

## Aug 28, 2022

- Return directory objects from get, list

- Run a node
  - Host a RPC API that allows for storing, getting and executing object behavior
- Run a client
  - Create a custom class with methods and data
  - Create instance of class
  - Store instance in remote object store
  - Retrieve instance from remote object store
  - Print state and execute methods
  - Instruct remote node to execute method on stored object, return result i.e."a service"

## Aug 27, 2022

- lambdaflow will use emerge file system to store and retrieve state
  - Each worker node will also spawn an emerge filesystem node
  - lambda code can read/write objects from the local worker object store
  - or retrieve known object state from a known object node during a flow execution

- zeromq for pub/sub
  - reliable pub/sub through external repo
- zerodb for object persistence
- zerorpc
  - expose node API to other nodes
  - invoke methods directly
  - store and get objects
- Use pub sub to broadcast requests to the network
  - e.g. who has oids 1,2 and 3?
    - nodes reply directly to requesting who's address was in the message
  - show me your stored oids
    - a registry or scheduler node will do this and store it as an object
      - then when it starts again, it reads that object to get best known state
      - of the network. re-issues the ping request and updates the object
      - other nodes can broadcast a request for the "registry" oid and get
      - a reply from the owning node, then store it locally itself

- Server click cli
  - Start the server, listen on emerge pub/sub channel
  - Observe join and departure events in the local cluster
- Create a File object, store data in it, or use a reader object
  - emerge will read that file into Block objects and yield those
  - each block is sent to n number of nodes depending on the raid level of the File
- Requesting a file
  - When a node requests a file, it sends out a pub sub for other nodes to notify it of the blocks they have
  - the requesting node then orders the block id's to reassemble the file map and requests the blocks from the host nodes
  - if a block transfer fails midstream, the requesting node falls back to the next node who owns that block id


