# Simple DHT over HTTP

Feedback is welcome at [johan@withaspoon.se](mailto:johan@withaspoon.se).

## Description

A simple non-persistent distributed hash table with pluggable partitioners that communicates over RESTful HTTP.

The database can be queried by accessing any of the nodes in the cluster and inter-node communication is done "behind the scenes". The currently implemented partitioner uses a consistent hashing algorithm to distribute the keys over the available nodes. The consistent hashing algorithm uses a ring based representation and replication is done by reading and writing the key to the next configurable N nodes in the ring.

## Installation

    # For the application
    pip install cherrypy
    pip install routes
    
    # For running the tests
    pip install nosetests
    

## Usage

Start the application by running:

    ./server --port=1234 --replicas=2 --conf=httpdhs.conf

The configuration file must contain a list of all nodes that is part of the cluster.

To run the example cluster, run the following commands in separate terminals:

    ./server --port=1234 --replicas=2 --conf=httpdhs.conf
    ./server --port=1235 --replicas=2 --conf=httpdhs.conf
    ./server --port=1236 --replicas=2 --conf=httpdhs.conf

To set and get values using curl run:

    # Setting mykey=myvalue
    curl -XPUT -dvalue=myvalue http://localhost:1234/db/mykey
    
    # Getting mykey
    curl http://localhost:1234/db/mykey

To load the cluster with all the postal codes in Sweden (beware, this takes a long time!). Run:

    ./load-data
    # Wait 10 minutes, then...
    curl http://localhost:1234/db/74121 # 74121=Knivsta
    curl http://localhost:1234/db/12139	# 12139=Johanneshov
    # etc.

## Running the tests

Simply use nosetests from the root directory.

## Architectural Notes

Some of the key components have been modularized to support changes in requirements.

### Partitioning

The partitioner can easily be changed to a more or less sophisticated variant. To support simple sharding one could simply implement a partitioner that only returns one node based on the modulus of the hash.

### Server and client protocols

Server and client communication is kept in the module "http" and all backend logic is kept separate from this. To support multiple protocols one could  inject the backend logic into yet another server implementation running in the same application.

### Database

The database implementation is currently transient and a persistent version could "easily" be implemented and injected when the server starts.

## Performance

Loading up a set of roughly 14000 key value pairs on 3 nodes with a replication of 2 takes around 10 minutes on my MacBook Pro. This corresponds to around 25 inserts per second.

## Current Limitations

- The cluster can't really be distributed since it relies on the node name being called localhost
- If a node goes down this is only noticed by the inter-communication client and should be handled by a supervisor that preferably marks them as dead
- The ring could be heavily unbalanced and there is no support for rebalancing
- Keys value pairs are not redistributed when a node comes back up
- The replication is not optimal and should preferably be done using a protocol other than HTTP for performance reasons
- All nodes must be known at startup and there is no way of adding nodes when the cluster is running
- The replicas could end up on the same node more than once depending on the node positions in the key space ring
- Some partitioning logic could be moved to the client to make finding the right node faster
- There is no way of inspecting the keys
- Deletion is unsupported
- No logging whatsoever

etc. etc.