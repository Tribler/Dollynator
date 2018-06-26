import unittest
from plebnet.agent.dna import DNA
from plebnet.agent.config import PlebNetConfig
from plebnet.clone import server_installer
from plebnet.controllers import tribler_controller, cloudomate_controller, market_controller, wallet_controller
from plebnet.communication.irc import irc_handler
from plebnet.settings import plebnet_settings
from mock.mock import MagicMock
from plebnet.utilities import logger, fake_generator
import plebnet.agent.core as Core
import mock
import os
from appdirs import user_config_dir

from plebnet.agent.dna import DNA


class TestCore(unittest.TestCase):

    def test_create_wallet_testnet(self):
        self.settings = plebnet_settings.Init.wallets_testnet
        self.logger = logger.log
        self.wallet = wallet_controller.create_wallet
        self.wallet_created = plebnet_settings.Init.wallets_testnet_created
        self.initiated = plebnet_settings.Init.wallets_initiate_once
        self.write = plebnet_settings.write

        plebnet_settings.Init.wallets_testnet = MagicMock(return_value=True)
        logger.log = MagicMock()
        wallet_controller.create_wallet = MagicMock(return_value=True)
        plebnet_settings.Init.wallets_testnet_created = MagicMock()
        plebnet_settings.Init.wallets_initiate_once = MagicMock()
        plebnet_settings.write = MagicMock()

        Core.create_wallet()
        self.assertEqual(os.environ.get('TESTNET'), '1')
        os.environ['TESTNET'] = '0'

        plebnet_settings.Init.wallets_testnet = self.settings
        logger.log = self.logger
        wallet_controller.create_wallet = self.wallet
        plebnet_settings.Init.wallets_testnet_created = self.wallet_created
        plebnet_settings.Init.wallets_initiate_once = self.initiated
        plebnet_settings.write = self.write

    def test_create_wallet_bitcoin(self):
        self.settings = plebnet_settings.Init.wallets_testnet
        self.logger = logger.log
        self.wallet = wallet_controller.create_wallet
        self.initiated = plebnet_settings.Init.wallets_initiate_once
        self.write = plebnet_settings.setting.Settings.write

        plebnet_settings.Init.wallets_testnet = MagicMock(return_value=False)
        logger.log = MagicMock()
        wallet_controller.create_wallet = MagicMock(return_value=True)
        plebnet_settings.Init.wallets_initiate_once = MagicMock()
        plebnet_settings.setting.Settings.write = MagicMock()

        Core.create_wallet()
        plebnet_settings.Init.wallets_initiate_once.assert_called_once()
        plebnet_settings.setting.Settings.write.assert_called_once()

        plebnet_settings.Init.wallets_testnet = self.settings
        logger.log = self.logger
        wallet_controller.create_wallet = self.wallet
        plebnet_settings.Init.wallets_initiate_once = self.initiated
        plebnet_settings.setting.Settings.write = self.write

    def test_check_tribler_true(self):
        self.running = tribler_controller.running
        self.logger = logger.log

        tribler_controller.running = MagicMock(return_value=True)
        logger.log = MagicMock()
        assert Core.check_tribler()

        tribler_controller.running = self.running
        logger.log = self.logger

    def test_check_tribler_false(self):
        self.running = tribler_controller.running
        self.start = tribler_controller.start
        self.logger = logger.log

        tribler_controller.start = MagicMock()
        tribler_controller.running = MagicMock(return_value=False)
        logger.log = MagicMock()
        self.assertFalse(Core.check_tribler())

        tribler_controller.running = self.running
        logger.log = self.logger
        tribler_controller.start = self.start

    def test_setup(self):
        self.logger = logger.log
        self.provider = cloudomate_controller.get_vps_providers
        self.DNA = DNA.read_dictionary
        self.settings = plebnet_settings.Init.wallets_testnet
        self.fake = fake_generator.generate_child_account
        self.irc_nic = plebnet_settings.Init.irc_nick
        self.irc_def = plebnet_settings.Init.irc_nick_def
        self.save = PlebNetConfig.save
        self.init_client = irc_handler.init_irc_client
        self.start_client = irc_handler.start_irc_client
        self.success = logger.success
        self.dna_remove = DNA.remove_provider
        self.load = PlebNetConfig.load

        args = MagicMock()
        DNA.remove_provider = MagicMock()
        args.testnet = True
        logger.log = MagicMock()
        fake_generator.generate_child_account = MagicMock()
        plebnet_settings.Init.wallets_testnet = MagicMock()
        cloudomate_controller.get_vps_providers = MagicMock()
        DNA.read_dictionary = MagicMock()
        plebnet_settings.Init.irc_nick = MagicMock()
        plebnet_settings.Init.irc_nick_def = MagicMock()
        PlebNetConfig.save = MagicMock()
        PlebNetConfig.load = MagicMock()
        irc_handler.init_irc_client = MagicMock()
        irc_handler.start_irc_client = MagicMock()
        logger.success = MagicMock()

        Core.setup(args)
        logger.success.assert_called_once()

        logger.log = self.logger
        DNA.remove_provider = self.dna_remove
        cloudomate_controller.get_vps_providers = self.provider
        DNA.read_dictionary = self.DNA
        plebnet_settings.Init.wallets_testnet = self.settings
        fake_generator.generate_child_account = self.fake
        plebnet_settings.Init.irc_nick = self.irc_nic
        plebnet_settings.Init.irc_nick_def = self.irc_def
        PlebNetConfig.save = self.save
        PlebNetConfig.load = self.load
        irc_handler.init_irc_client = self.init_client
        irc_handler.start_irc_client = self.start_client
        logger.success = self.success

    def test_check(self):
        self.logger = logger.log
        self.wallet_created = plebnet_settings.Init.wallets_testnet_created
        self.tribler = Core.check_tribler
        self.DNA = DNA.read_dictionary
        self.initiated = plebnet_settings.Init.wallets_initiate_once
        self.cw = Core.create_wallet
        self.sp = Core.select_provider
        self.hm = market_controller.has_matchmakers
        self.uo = Core.update_offer
        self.ap = Core.attempt_purchase
        self.iv = Core.install_vps
        self.load = PlebNetConfig.load
        self.vpn_running = Core.vpn_is_running

        logger.log = MagicMock()
        plebnet_settings.Init.wallets_testnet_created = MagicMock(return_value=True)

        PlebNetConfig.load = MagicMock(return_value=False)
        Core.check_tribler = MagicMock(return_value=False)
        Core.vpn_is_running = MagicMock(return_value=True)
        DNA.read_dictionary = MagicMock()
        plebnet_settings.Init.wallets_initiate_once = MagicMock(return_value=False)
        Core.create_wallet = MagicMock()
        Core.select_provider = MagicMock()
        market_controller.has_matchmakers = MagicMock(return_value=True)
        Core.update_offer = MagicMock()
        Core.attempt_purchase = MagicMock()
        Core.install_vps = MagicMock()

        Core.check()
        os.environ['TESTNET'] = '0'

        plebnet_settings.Init.wallets_testnet_created = MagicMock(return_value=False)
        Core.check_tribler = MagicMock(return_value=True)

        Core.check()
        Core.install_vps.assert_called_once()
        Core.attempt_purchase.assert_called_once()
        Core.create_wallet.assert_called_once()

        logger.log = self.logger
        Core.vpn_is_running = self.vpn_running
        plebnet_settings.Init.wallets_testnet_created = self.wallet_created
        Core.check_tribler = self.tribler
        DNA.read_dictionary = self.DNA
        plebnet_settings.Init.wallets_initiate_once = self.initiated
        Core.create_wallet = self.cw
        Core.select_provider = self.sp
        market_controller.has_matchmakers = self.hm
        Core.update_offer = self.uo
        Core.attempt_purchase = self.ap
        Core.install_vps = self.iv
        PlebNetConfig.load = self.load

    def test_update_offer(self):
        self.time = PlebNetConfig.time_since_offer
        self.timep = plebnet_settings.TIME_IN_HOUR
        self.logger = logger.log
        self.uo = cloudomate_controller.update_offer
        self.save = PlebNetConfig.save

        PlebNetConfig.time_since_offer = MagicMock(return_value=300)
        plebnet_settings.TIME_IN_HOUR = 200
        logger.log = MagicMock()
        cloudomate_controller.update_offer = MagicMock()
        PlebNetConfig.save = MagicMock()

        Core.config = PlebNetConfig
        Core.update_offer()
        PlebNetConfig.save.assert_called_once()

        PlebNetConfig.time_since_offer = self.time
        plebnet_settings.TIME_IN_HOUR = self.timep
        logger.log = self.logger
        cloudomate_controller.update_offer = self.uo
        PlebNetConfig.save = self.save

    def test_attempt_purchase(self):
        self.log = logger.log
        self.testnet = plebnet_settings.Init.wallets_testnet
        self.get = PlebNetConfig.get
        self.get_balance = market_controller.get_balance
        self.calculate_price = cloudomate_controller.calculate_price
        self.purchase_choice = cloudomate_controller.purchase_choice
        self.evolve = DNA.evolve
        self.set = PlebNetConfig.set
        self.save = PlebNetConfig.save
        self.vpn = Core.attempt_purchase_vpn

        logger.log = MagicMock()
        plebnet_settings.Init.wallets_testnet = MagicMock(return_value=True)
        PlebNetConfig.get = MagicMock(return_value=['ccihosting', 'test', 0])
        market_controller.get_balance = MagicMock(return_value=300)

        Core.attempt_purchase_vpn = MagicMock(return_value=False)
        cloudomate_controller.calculate_price = MagicMock(return_value=500)
        cloudomate_controller.purchase_choice = MagicMock(return_value=plebnet_settings.SUCCESS)
        DNA.evolve = MagicMock()
        PlebNetConfig.set = MagicMock()
        PlebNetConfig.save = MagicMock()

        Core.config = PlebNetConfig
        Core.dna = DNA
        Core.attempt_purchase()

        plebnet_settings.Init.wallets_testnet = MagicMock(return_value=False)
        market_controller.get_balance = MagicMock(return_value=700)
        Core.attempt_purchase()
        DNA.evolve.assert_called_with(True)

        cloudomate_controller.purchase_choice = MagicMock(return_value=plebnet_settings.FAILURE)
        Core.attempt_purchase()
        DNA.evolve.assert_called_with(False, 'ccihosting')

        logger.log = self.log
        plebnet_settings.Init.wallets_testnet = self.testnet
        PlebNetConfig.get = self.get
        market_controller.get_balance = self.get_balance
        cloudomate_controller.calculate_price = self.calculate_price
        cloudomate_controller.purchase_choice = self.purchase_choice
        DNA.evolve = self.evolve
        Core.attempt_purchase_vpn = self.vpn
        PlebNetConfig.set = self.set
        PlebNetConfig.save = self.save

    def test_install_vps(self):
        self.ias = server_installer.install_available_servers

        server_installer.install_available_servers = MagicMock()
        Core.install_vps()
        server_installer.install_available_servers.assert_called_once()

        server_installer.install_available_servers = self.ias













if __name__ == '__main__':
    unittest.main()