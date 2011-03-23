from node import NodeDownError
from http import HttpClient

class KeyValueDatabase(object):
    """Simple transient key value database class."""
    
    def __init__(self):
        self._table = {}
    
    def set(self, key, value):
        self._table[key] = value
    
    def get(self, key):
        if key in self._table:
            return self._table[key]

class KeyValueController(object):
    """Controller for node and database querying.
    
    KeyValueController is the controlling class for a single node and is
    dependent on a partitioning strategy to find which node to set or get
    a key value pair from. Inter-node communication is done using the passed
    in client."""
    
    def __init__(self, node_name, partitioning_strategy, client=HttpClient(), database=KeyValueDatabase()):
        self._node_name = node_name
        self._partitioning_strategy = partitioning_strategy
        self._client = client
        self._database = database
    
    def _addresses_for_key(self, key):
        return self._partitioning_strategy.find_node_addresses_for_key(key)
    
    def set(self, key, value):
        for address in self._addresses_for_key(key):
            try:
                self._client.set_without_replication(address, key, value)
            except NodeDownError:
                pass
    
    def set_direct(self, key, value):
        self._database.set(key, value)
        
    def get(self, key):
        for address in self._addresses_for_key(key):
            if address == self._node_name:
                return self._database.get(key)
            else:
                try:
                    return self._client.get(address, key)
                except NodeDownError:
                    pass
