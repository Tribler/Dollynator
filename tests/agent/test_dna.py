import unittest
import mock
import os
from appdirs import user_config_dir
from mock.mock import MagicMock
import json

from plebnet.agent import dna
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

    def test_demutate_false(self):
        self.test_dna.add_provider("provider1")
        self.assertFalse(self.test_dna.demutate("provider2"))

    def test_demutate_enough(self):
        self.test_dna.add_provider("provider1")
        self.test_dna.rate = 0.5
        self.test_dna.demutate("provider1")
        self.assertEqual({'provider1': 0.0}, self.test_dna.vps)

    def test_demutate_not_enough(self):
        self.test_dna.add_provider("provider1")
        self.test_dna.rate = 0.2
        self.test_dna.demutate("provider1")
        self.test_dna.rate = 0.4
        self.test_dna.demutate("provider1")
        self.assertEqual({'provider1': 0.3}, self.test_dna.vps)

    def test_denormalize(self):
        self.test_dna.add_provider("provider1")
        self.test_dna.add_provider("provider2")
        self.test_dna.normalize()

        self.test_dna.length = 7
        self.test_dna.denormalize()

        self.assertEqual({'provider1': 3.5, 'provider2': 3.5}, self.test_dna.vps)

    @mock.patch('random.uniform', return_value=0.7)
    def test_choose_provider(self, mock1):
        self.test_dna.add_provider("provider1")
        self.test_dna.add_provider("provider2")
        self.assertEqual(self.test_dna.choose_provider(self.test_dna.vps), 'provider2')

    def test_exclude(self):
        self.test_dna.add_provider("provider1")
        self.test_dna.add_provider("provider2")
        self.test_dna.add_provider("provider3")
        new = self.test_dna.exclude("provider2")

        self.assertEqual({'provider1': 0.5, 'provider3': 0.5}, new)
        self.assertEqual({'provider1': 0.5, 'provider2': 0.5, 'provider3': 0.5}, self.test_dna.vps)

    def test_normalize_excluded(self):
        test_dict = {'provider1': 0.5}
        res_dict = self.test_dna.normalize_excluded(test_dict)
        self.assertEqual({'provider1': 1}, res_dict)

    @mock.patch('plebnet.agent.dna.DNA.write_dictionary', return_value=None)
    def test_positive_evolve(self, mock):
        self.test_dna.add_provider("provider1")
        self.test_dna.add_provider("provider2")
        self.test_dna.rate = 0.25
        self.test_dna.positive_evolve("provider2")

        result = self.test_dna.exclude("provider2")
        self.assertEqual({'provider1': 0.4}, result)

    @mock.patch('plebnet.agent.dna.DNA.write_dictionary', return_value=None)
    def test_negative_evolve(self, mock):
        self.test_dna.add_provider("provider1")
        self.test_dna.add_provider("provider2")
        self.test_dna.rate = 0.5
        self.test_dna.negative_evolve("provider2")
        self.assertEqual({'provider1': 1.0, 'provider2': 0.0}, self.test_dna.vps)

    @mock.patch('plebnet.agent.dna.DNA.write_dictionary', return_value=None)
    def test_set_and_get_own_provider(self, mock):
        self.test_dna.set_own_provider("provider2")
        self.assertEqual("provider2", self.test_dna.get_own_provider())

    @mock.patch('plebnet.agent.dna.DNA.write_dictionary', return_value=None)
    def test_evolve_positive(self, mock):
        self.test_dna.add_provider("provider1")
        self.test_dna.add_provider("provider2")
        self.test_dna.set_own_provider("provider2")

        self.test_dna.evolve(True)
        self.assertEqual({'provider1': 0.25, 'provider2': 0.75}, self.test_dna.vps)

    @mock.patch('plebnet.agent.dna.DNA.write_dictionary', return_value=None)
    def test_evolve_negative(self, mock):
        self.test_dna.add_provider("provider1")
        self.test_dna.add_provider("provider2")
        self.test_dna.set_own_provider("provider2")

        self.test_dna.rate = 0.5
        self.test_dna.evolve(False, "provider1")
        self.assertEqual({'provider1': 0.0, 'provider2': 1.0}, self.test_dna.vps)

    def test_read_dictionary(self):
        initial_dict = {'Self': 'unknown',
                        'parent': 'unknown',
                        'transaction_hash': '',
                        'VPS': 'TEST'}

        self.ex = os.path.exists
        self.ini = DNA.create_initial_dict
        self.wri = DNA.write_dictionary

        os.path.exists = MagicMock(return_value=None)
        DNA.create_initial_dict = MagicMock(return_value=initial_dict)
        DNA.write_dictionary = MagicMock()

        dna = DNA()
        dna.read_dictionary()
        self.assertEqual(dna.vps, 'TEST')

        os.path.exists = self.ex
        DNA.create_initial_dict = self.ini
        DNA.write_dictionary = self.wri


if __name__ == '__main__':
    unittest.main()
