import unittest
from httpdhs.partitioning import ConsistentHashingPartitioningStrategy

class HashCodeGeneratorMock(object):
    def __init__(self, key_hash_code_pairs):
        self._key_hash_code_pairs = key_hash_code_pairs
    
    def hash(self, key):
        return self._key_hash_code_pairs[key]

class TestWithOneNode(unittest.TestCase):
    def test_should_return_a_single_node_for_any_key(self):
        hash_code_generator = HashCodeGeneratorMock({
            "abc": "50",
            "node1.example:1234#0": "100",
            "def": "200"})
        partitioner = ConsistentHashingPartitioningStrategy(["node1.example:1234"], 1, hash_code_generator)
        self.assertItemsEqual(["node1.example:1234"], partitioner.find_node_addresses_for_key("abc"))
        self.assertItemsEqual(["node1.example:1234"], partitioner.find_node_addresses_for_key("def"))

class TestWithSeveralNodes(unittest.TestCase):
    def given_a_partitioning_strategy_with(self, replicas):
        hash_code_generator = HashCodeGeneratorMock({
            "node1.example:1234#0": "10",
            "node1.example:1234#1": "20",
            "node2.example:1234#0": "30",
            "node2.example:1234#1": "40",
            "node3.example:1234#0": "50",
            "abc": "55",
            "node3.example:1234#1": "60"})
        return ConsistentHashingPartitioningStrategy(
            ["node1.example:1234", "node2.example:1234", "node3.example:1234"],
            replicas, hash_code_generator)
    
    def test_should_return_a_number_of_sequential_nodes_equal_to_the_number_of_replicas(self):
        partitioner = self.given_a_partitioning_strategy_with(replicas=2)
        self.assertEqual(2, len(partitioner.find_node_addresses_for_key("abc")))
    
    def test_should_treat_the_keyspace_as_a_ring(self):
        partitioner = self.given_a_partitioning_strategy_with(replicas=2)
        self.assertItemsEqual(["node3.example:1234", "node1.example:1234"],
                              partitioner.find_node_addresses_for_key("abc"))