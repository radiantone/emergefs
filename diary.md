## Aug 27, 2022
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

- 
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


