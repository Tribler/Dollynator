import unittest
from plebnet.agent.dna import DNA


class TestDna(unittest.TestCase):

    test_dna = None

    def setUp(self):
        self.test_dna = DNA()
        self.test_dna.rate = 1
        self.test_dna.length = 0.0
        self.test_dna.dictionary = {}
        self.test_dna.vps = {}

    def tearDown(self):
        pass

    def test_add_provider(self):
        self.test_dna.add_provider("provider1")
        self.assertEqual(self.test_dna.vps, {'provider1': 0.5})

    def test_remove_provider(self):
        self.test_dna.add_provider("provider1")
        self.test_dna.remove_provider("provider1")
        self.assertEqual({}, self.test_dna.vps)

    def test_normalize(self):
        self.test_dna.add_provider("provider1")
        self.test_dna.normalize()
        self.assertEqual({'provider1': 1}, self.test_dna.vps)

    def test_mutate_false(self):
        self.test_dna.add_provider("provider1")
        self.assertFalse(self.test_dna.mutate("provider2"))

    def test_mutate_true(self):
        self.test_dna.add_provider("provider1")
        self.test_dna.mutate("provider1")
        self.assertEqual({'provider1': 1.5}, self.test_dna.vps)


if __name__ == '__main__':
    unittest.main()
