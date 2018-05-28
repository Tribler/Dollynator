import unittest
import mock
import os

from appdirs import user_config_dir

from plebnet.clone import server_installer
from plebnet.agent.config import PlebNetConfig


# file1 = os.path.join(user_config_dir(), 'plebnet.json')


class TestServerInstaller(unittest.TestCase):

    def setUp(self):
        pass
    #    if os.path.isfile(file1):
    #        os.remove(file1)

    def tearDown(self):
        pass
    #    if os.path.isfile(file1):
    #        os.remove(file1)

    def test_is_valid_ip_false(self):
        self.assertFalse(server_installer.is_valid_ip('20.0.110'))
        self.assertFalse(server_installer.is_valid_ip('300.300.300.300'))

    def test_is_valid_ip_true(self):
        self.assertTrue(server_installer.is_valid_ip('120.30.0.11'))




    # @mock.patch('plebnet.clone.server_installer._install_server', return_value=1)
    # def test_install_available_servers(self, mock_install):
    #    self.assertEqual(1, server_installer.install_available_servers(PlebNetConfig(), "sds"))


if __name__ == '__main__':
    unittest.main()
