import unittest
import mock
import os
import subprocess

from appdirs import user_config_dir

from plebnet.clone import server_installer
from plebnet.agent.config import PlebNetConfig
from plebnet.agent.dna import DNA
from plebnet.utilities import fake_generator
from cloudomate.util.settings import Settings
from plebnet.settings import plebnet_settings as setup
from mock.mock import MagicMock
from plebnet.utilities import logger as Logger

test_log_path = os.path.join(user_config_dir(), 'tests_logs')
test_log_file = os.path.join(user_config_dir(), 'tests_logs/plebnet.logs')
test_child_file = os.path.join(user_config_dir(), 'test_child_config.cfg')
test_child_DNA_file = os.path.join(user_config_dir(), 'Child_DNA.json')
test_bought = ('linevast', 666, 0)
plebnet_file = os.path.join(user_config_dir(), 'plebnet.json')

test_account = Settings()


class TestServerInstaller(unittest.TestCase):

    # test_account = None
    test_dna = None

    @mock.patch('plebnet.utilities.fake_generator._child_file', return_value=test_child_file)
    def setUp(self, mock):

        if os.path.isfile(test_log_file):
            os.remove(test_log_file)
        if os.path.isfile(test_child_file):
            os.remove(test_child_file)
        self.test_dna = DNA()

        fake_generator.generate_child_account()

        global test_account
        test_account.read_settings(test_child_file)

    def tearDown(self):
        if os.path.isfile(test_log_file):
            os.remove(test_log_file)
        if os.path.isfile(test_child_file):
            os.remove(test_child_file)
        if os.path.isfile(test_child_DNA_file):
            os.remove(test_child_DNA_file)
        if os.path.isfile(plebnet_file):
            os.remove(plebnet_file)

    def test_is_valid_ip_false(self):
        self.assertFalse(server_installer.is_valid_ip('20.0.110'))
        self.assertFalse(server_installer.is_valid_ip('300.300.300.300'))

    def test_is_valid_ip_true(self):
        self.assertTrue(server_installer.is_valid_ip('120.30.0.11'))

    def test_is_valid_ip_no_number(self):
        self.assertFalse(server_installer.is_valid_ip('120.0.1.a'))

    @mock.patch('plebnet.clone.server_installer._install_server', return_value=False)
    @mock.patch('plebnet.controllers.cloudomate_controller.get_ip', return_value='120.21.0.12')
    @mock.patch('plebnet.controllers.cloudomate_controller.child_account', return_value=test_account)
    @mock.patch('cloudomate.hoster.vps.linevast.LineVast.enable_tun_tap', return_value=False)
    @mock.patch('cloudomate.hoster.vps.linevast.LineVast.change_root_password', return_value=True)
    @mock.patch('plebnet.controllers.cloudomate_controller.save_info_vpn', return_value=True)
    @mock.patch('plebnet.clone.server_installer.check_access', return_value=True)
    @mock.patch('cloudomate.util.settings.Settings.get', return_value='Henri')
    @mock.patch('plebnet.settings.plebnet_settings.Init.active_logger', return_value=False)
    @mock.patch('plebnet.settings.plebnet_settings.Init.active_verbose', return_value=False)
    @mock.patch('cloudomate.hoster.vps.linevast.LineVast.change_root_password', return_value=True)
    @mock.patch('plebnet.agent.dna.DNA.get_own_tree', return_value='tree')
    def test_install_available_servers(self, mock1, mock2, mock3, mock4, mock5, mock6, mock7, mock8, mock9, mock10, mock11, mock12):
        config = PlebNetConfig()
        config.get('bought').append(test_bought)
        config.save()

        server_installer.install_available_servers(config, self.test_dna)

        self.assertEqual(config.get('installed'), [{'linevast': False}])
        self.assertEqual(config.get('bought'), [])

    def test_install_server(self):
        self.logger = Logger.log
        self.instance = setup.get_instance
        self.home = setup.Init.plebnet_home
        self.subprocess = subprocess.call

        Logger.log = MagicMock()
        setup.Init.plebnet_home = MagicMock(return_value='test\path')
        subprocess.call = MagicMock(return_value=0)

        assert server_installer._install_server('IPFakeAddress', 'ROOTPWD')

        self.vpnpre = setup.Init.vpn_child_prefix
        self.vpncon = setup.Init.vpn_config_path
        self.osex = os.path.expanduser
        self.cred = setup.Init.vpn_credentials_name
        self.name = setup.Init.vpn_config_name

        setup.Init.vpn_child_prefix = MagicMock(return_value='String')
        setup.Init.vpn_config_path = MagicMock(return_value='String')
        os.path.expanduser = MagicMock(return_value='String')
        setup.Init.vpn_credentials_name = MagicMock(return_value='String')
        setup.Init.vpn_config_name = MagicMock(return_value='String')
        subprocess.call = MagicMock(return_value=1)

        self.assertFalse(server_installer._install_server('IPFakeAddress', 'ROOTPWD', 'testVPN', True))

        Logger.log = self.logger
        setup.get_instance = self.instance
        setup.Init.plebnet_home = self.home
        subprocess.call = self.subprocess

        setup.Init.vpn_child_prefix = self.vpnpre
        setup.Init.vpn_config_path = self.vpncon
        os.path.expanduser = self.osex
        setup.Init.vpn_credentials_name = self.cred
        setup.Init.vpn_config_name = self.name


if __name__ == '__main__':
    unittest.main()
