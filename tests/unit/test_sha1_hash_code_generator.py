import unittest
from httpdhs.partitioning import Sha1HashCodeGenerator

class TestWhenHashing(unittest.TestCase):
    def test_should_return_a_sha1_hash(self):
        hash_code_generator = Sha1HashCodeGenerator()
        self.assertEqual("aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d", hash_code_generator.hash("hello"))
