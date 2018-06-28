import unittest
import mock
from appdirs import user_config_dir
import os
from cloudomate.util.settings import Settings
from plebnet.utilities import fake_generator


test_file = os.path.join(user_config_dir(), 'test_child_config.cfg')


class TestFakeGenerator(unittest.TestCase):

    def setUp(self):
        if os.path.isfile(test_file):
            os.remove(test_file)

    def tearDown(self):
        if os.path.isfile(test_file):
            os.remove(test_file)

    @mock.patch('plebnet.utilities.fake_generator._child_file', return_value=test_file)
    def test_generate_child_account_file_created(self, mock):
        fake_generator.generate_child_account()
        self.assertTrue(os.path.isfile(test_file))

    @mock.patch('plebnet.utilities.fake_generator._child_file', return_value=test_file)
    def test_generate_child_has_content(self, mock):
        fake_generator.generate_child_account()
        account = Settings()
        account.read_settings(test_file)

        self.assertIsNotNone(account.get('user', 'email'))
        self.assertIsNotNone(account.get('user', 'firstname'))
        self.assertIsNotNone(account.get('user', 'lastname'))
        self.assertIsNotNone(account.get('user', 'companyname'))
        self.assertIsNotNone(account.get('user', 'phonenumber'))
        self.assertIsNotNone(account.get('user', 'password'))

        self.assertIsNotNone(account.get('address', 'address'))
        self.assertIsNotNone(account.get('address', 'city'))
        self.assertIsNotNone(account.get('address', 'state'))
        self.assertIsNotNone(account.get('address', 'countrycode'))
        self.assertIsNotNone(account.get('address', 'zipcode'))

        self.assertIsNotNone(account.get('server', 'root_password'))
        self.assertEqual(account.get('server', 'ns1'), 'ns1')
        self.assertEqual(account.get('server', 'ns2'), 'ns2')
        self.assertIsNotNone(account.get('server', 'hostname'))


if __name__ == '__main__':
    unittest.main()
