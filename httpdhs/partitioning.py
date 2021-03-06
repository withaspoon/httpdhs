import sha
import bisect

class Sha1HashCodeGenerator(object):
    """Class that generates SHA1 hashes"""
    
    def hash(self, what):
        return sha.new(what).hexdigest()

class ConsistentHashingPartitioningStrategy(object):
    """Paritioning strategy that uses consistent hashing.
    
    Keeps a sorted list of nodes spread out over a ring representing the
    keyspace. More information on wikipedia:
    http://en.wikipedia.org/wiki/Consistent_hashing"""
    
    def __init__(self, node_addresses, replicas, hash_code_generator=Sha1HashCodeGenerator()):
        self._replicas = replicas
        self._hash_code_generator = hash_code_generator
        self._keyspace_ring = []
        for address in node_addresses:
            self._add_node_address(address)
    
    def _add_node_address(self, address):
        for n in xrange(self._replicas):
            hash_code = self._hash_code_generator.hash(address + "#" + str(n))
            self._keyspace_ring.append([hash_code, address])
        self._keyspace_ring = sorted(self._keyspace_ring)

    def find_node_addresses_for_key(self, key):
        index = self._find_index_for_key_in_ring(key)
        
        addresses = []
        for n in xrange(self._replicas):
            if index >= len(self._keyspace_ring):
                index = 0
            addresses.append(self._keyspace_ring[index][1])
            index += 1
        
        return set(addresses)

    def _find_index_for_key_in_ring(self, key):
        hash_code = self._hash_code_generator.hash(key)
        return bisect.bisect_right(self._keyspace_ring, [hash_code, key])