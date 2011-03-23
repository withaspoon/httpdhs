import unittest
from mock import Mock
from httpdhs.backend import KeyValueController

class TestController(unittest.TestCase):
    def given_a_controller_with(self, strategy=Mock(), client=Mock(), database=Mock()):
        return KeyValueController('node1', strategy, client, database)
    
    def test_should_update_the_database_when_setting_directly(self):
        database = Mock()
        controller = self.given_a_controller_with(database=database)
        controller.set_direct('mykey', 'myvalue')
        database.set.assert_called_with('mykey', 'myvalue')
    
    def test_should_use_the_client_to_update_nodes_when_setting_a_value(self):
        strategy = Mock()
        strategy.find_node_addresses_for_key.return_value = ['node1', 'node2']
        client = Mock()
        controller = self.given_a_controller_with(strategy=strategy, client=client)
        
        controller.set('mykey', 'myvalue')

        strategy.find_node_addresses_for_key.assert_called_with('mykey')
        client.set_without_replication.assert_once_called_with('node1', 'mykey', 'myvalue')
        client.set_without_replication.assert_once_called_with('node2', 'mykey', 'myvalue')
    
    def test_should_return_the_value_from_the_database_if_the_node_is_the_current_node(self):
        strategy = Mock()
        strategy.find_node_addresses_for_key.return_value = ['node1', 'node2']
        database = Mock()
        database.get.return_value = 'myvalue'
        controller = self.given_a_controller_with(strategy=strategy, database=database)
        
        self.assertEqual('myvalue', controller.get('mykey'))
    
    def test_should_return_query_another_node_if_the_node_is_not_the_current_node(self):
        strategy = Mock()
        strategy.find_node_addresses_for_key.return_value = ['node2', 'node1']
        client = Mock()
        client.get.return_value = 'myvalue'
        controller = self.given_a_controller_with(strategy=strategy, client=client)
        
        self.assertEqual('myvalue', controller.get('mykey'))
        client.get.assert_once_called_with('node1', 'mykey')
