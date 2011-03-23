from node import NodeDownError

class KeyValueDatabase(object):
    def __init__(self):
        self._table = {}
    
    def set(self, key, value):
        self._table[key] = value
    
    def get(self, key):
        if key in self._table:
            return self._table[key]

class KeyValueController(object):
    def __init__(self, node_name, partitioning_strategy, client, database):
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
