import unittest
from httpdhs.backend import KeyValueDatabase

class TestDatabase(unittest.TestCase):
    def test_should_return_none_when_no_value_exists_for_key(self):
        database = KeyValueDatabase()
        self.assertIsNone(database.get("abc"))

    def test_should_return_a_value_if_a_value_exists_for_key(self):
        database = KeyValueDatabase()
        database.set("abc", "123")
        self.assertEqual("123", database.get("abc"))