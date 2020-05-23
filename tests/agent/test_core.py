import copy
import unittest
from unittest import skip
import unittest.mock as mock

from CaseInsensitiveDict import CaseInsensitiveDict
from cloudomate.hoster.vps.vps_hoster import VpsOption

from plebnet.agent.qtable import QTable, VPSState

from plebnet.agent.config import PlebNetConfig
from plebnet.clone import server_installer
from plebnet.controllers import tribler_controller, cloudomate_controller, market_controller, wallet_controller
from plebnet.communication.irc import irc_handler
from plebnet.settings import plebnet_settings
from unittest.mock import MagicMock
from plebnet.utilities import logger, fake_generator
import plebnet.agent.core as Core
import subprocess
import os
import cloudomate.hoster.vps.blueangelhost as blueAngel


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
        self.settings = plebnet_settings.Init.wallets_testnet
        self.fake = fake_generator.generate_child_account
        self.irc_nic = plebnet_settings.Init.irc_nick
        self.irc_def = plebnet_settings.Init.irc_nick_def
        self.save = PlebNetConfig.save
        self.init_client = irc_handler.init_irc_client
        self.start_client = irc_handler.start_irc_client
        self.success = logger.success
        self.load = PlebNetConfig.load
        self.exit = plebnet_settings.Init.tribler_exitnode

        args = MagicMock()
        args.testnet = True
        logger.log = MagicMock()
        fake_generator.generate_child_account = MagicMock()
        plebnet_settings.Init.wallets_testnet = MagicMock()
        cloudomate_controller.get_vps_providers = MagicMock()
        plebnet_settings.Init.irc_nick = MagicMock()
        plebnet_settings.Init.irc_nick_def = MagicMock()
        PlebNetConfig.save = MagicMock()
        PlebNetConfig.load = MagicMock()
        irc_handler.init_irc_client = MagicMock()
        irc_handler.start_irc_client = MagicMock()
        logger.success = MagicMock()
        plebnet_settings.Init.tribler_exitnode = MagicMock()

        Core.setup(args)
        logger.success.assert_called_once()

        logger.log = self.logger
        cloudomate_controller.get_vps_providers = self.provider
        plebnet_settings.Init.wallets_testnet = self.settings
        fake_generator.generate_child_account = self.fake
        plebnet_settings.Init.irc_nick = self.irc_nic
        plebnet_settings.Init.irc_nick_def = self.irc_def
        PlebNetConfig.save = self.save
        PlebNetConfig.load = self.load
        irc_handler.init_irc_client = self.init_client
        irc_handler.start_irc_client = self.start_client
        logger.success = self.success
        plebnet_settings.Init.tribler_exitnode = self.exit

    @mock.patch('plebnet.agent.core.attempt_purchase')
    @mock.patch('plebnet.settings.plebnet_settings.Init.wallets_initiate_once', return_value=False)
    @mock.patch('plebnet.settings.plebnet_settings.Init.wallets_testnet_created', return_value=True)
    @mock.patch('plebnet.agent.core.check_tribler', return_value=False)
    @mock.patch('plebnet.agent.core.vpn_is_running', return_value=True)
    @mock.patch('plebnet.agent.core.create_wallet')
    @mock.patch('plebnet.agent.core.select_provider')
    @mock.patch('plebnet.agent.core.strategies')
    @mock.patch('plebnet.agent.core.install_vps')
    @mock.patch('plebnet.controllers.market_controller.has_matchmakers', return_value=True)
    @mock.patch('plebnet.agent.config.PlebNetConfig.load', return_value=False)
    def test_check(self, mock1, mock2, mock3, mock4, mock5, mock6, mock7, mock8, mock9, mock10, mock11):
        self.logger = logger.log

        logger.log = MagicMock()

        Core.strategies['test']().apply = MagicMock()

        Core.check()
        os.environ['TESTNET'] = '0'

        plebnet_settings.Init.wallets_testnet_created = MagicMock(return_value=False)
        Core.check_tribler = MagicMock(return_value=True)

        Core.check()
        Core.install_vps.assert_called_once()
        Core.strategies['test']().apply.assert_called_once()
        Core.create_wallet.assert_called_once()

        logger.log = self.logger

    @mock.patch('plebnet.controllers.cloudomate_controller.get_vps_providers',
                return_value=CaseInsensitiveDict({'blueangelhost': blueAngel.BlueAngelHost}))
    @mock.patch('plebnet.controllers.cloudomate_controller.options', return_value=[VpsOption(name='Advanced',
                                                                                             storage=2,
                                                                                             cores=2,
                                                                                             memory=2,
                                                                                             bandwidth="4.0",
                                                                                             connection="1",
                                                                                             price=100.0,
                                                                                             purchase_url="mock"
                                                                                             ),
                                                                                   VpsOption(name='Basic Plan',
                                                                                             storage=2,
                                                                                             cores=2,
                                                                                             memory=2,
                                                                                             bandwidth="1.0",
                                                                                             connection="1",
                                                                                             price=10.0,
                                                                                             purchase_url="mock"
                                                                                             )])
    @mock.patch('plebnet.agent.core.get_amount_mb_tokens_earned', return_value=88878356)
    def test_attempt_purchase(self, mock1, mock2, mock3):
        self.log = logger.log
        self.testnet = plebnet_settings.Init.wallets_testnet
        self.get = PlebNetConfig.get
        self.get_balance = market_controller.get_balance
        self.calculate_price = cloudomate_controller.calculate_price
        self.purchase_choice = cloudomate_controller.purchase_choice
        self.set = PlebNetConfig.set
        self.save = PlebNetConfig.save
        self.vpn = Core.attempt_purchase_vpn
        self.new = PlebNetConfig.increment_child_index
        self.provider = cloudomate_controller.get_vps_providers
        self.fg = fake_generator.generate_child_account
        self.qtable = QTable()
        self.providers = cloudomate_controller.get_vps_providers()
        providers = cloudomate_controller.get_vps_providers()
        self.qtable.init_qtable_and_environment(providers)
        self.qtable.init_alpha_and_beta()
        self.qtable.set_self_state(VPSState("blueangelhost", "Basic Plan"))

        logger.log = MagicMock()
        plebnet_settings.Init.wallets_testnet = MagicMock(return_value=False)
        PlebNetConfig.get = MagicMock(return_value=['blueangelhost', 'Basic Plan', 0])
        market_controller.get_balance = MagicMock(return_value=100000000)

        Core.qtable = self.qtable
        Core.attempt_purchase_vpn = MagicMock(return_value=False)
        cloudomate_controller.calculate_price = MagicMock(return_value=0.01)
        cloudomate_controller.purchase_choice = MagicMock(return_value=plebnet_settings.SUCCESS)
        PlebNetConfig.set = MagicMock()
        PlebNetConfig.save = MagicMock()
        PlebNetConfig.increment_child_index = MagicMock()
        cloudomate_controller.get_vps_providers = MagicMock()
        fake_generator.generate_child_account = MagicMock()

        Core.config = PlebNetConfig
        qtable_copy = copy.deepcopy(Core.qtable.qtable)

        cur_option = VpsOption(
            name="Basic",
            storage=100,
            cores=2,
            memory=10,
            bandwidth=10000,
            connection=1,
            price=10,
            purchase_url="https://panel.linevast.de"
        )
        cloudomate_controller.get_vps_option = MagicMock(return_value=cur_option)
        PlebNetConfig.time_to_expiration = MagicMock(return_value=1592000)
        Core.get_q_tables_through_gossipping= MagicMock(return_value=[])


        Core.attempt_purchase()

        self.assertLess(qtable_copy['blueangelhost_basic plan']['blueangelhost_basic plan'],
                        Core.qtable.qtable['blueangelhost_basic plan']['blueangelhost_basic plan'])

        qtable_copy = copy.deepcopy(Core.qtable.qtable)
        cloudomate_controller.purchase_choice = MagicMock(return_value=plebnet_settings.FAILURE)
        Core.attempt_purchase()

        self.assertGreater(qtable_copy['blueangelhost_basic plan']['blueangelhost_basic plan'],
                           Core.qtable.qtable['blueangelhost_basic plan']['blueangelhost_basic plan'])

        logger.log = self.log
        plebnet_settings.Init.wallets_testnet = self.testnet
        PlebNetConfig.get = self.get
        market_controller.get_balance = self.get_balance
        cloudomate_controller.calculate_price = self.calculate_price
        cloudomate_controller.purchase_choice = self.purchase_choice
        Core.attempt_purchase_vpn = self.vpn
        PlebNetConfig.set = self.set
        PlebNetConfig.save = self.save
        PlebNetConfig.increment_child_index = self.new
        cloudomate_controller.get_vps_providers = self.provider
        fake_generator.generate_child_account = self.fg

    def test_install_vps(self):
        self.ias = server_installer.install_available_servers

        server_installer.install_available_servers = MagicMock()
        Core.install_vps()
        server_installer.install_available_servers.assert_called_once()

        server_installer.install_available_servers = self.ias

    def test_attempt_purchase_vpn(self):
        self.vpnset = plebnet_settings.Init.vpn_host
        self.vpnpro = cloudomate_controller.get_vpn_providers
        self.wall = plebnet_settings.Init.wallets_testnet
        self.bal = market_controller.get_balance
        self.price = cloudomate_controller.calculate_price_vpn
        self.pur = cloudomate_controller.purchase_choice_vpn
        self.suc = logger.success
        self.log = logger.log
        self.err = logger.error

        cloudomate_controller.purchase_choice_vpn = MagicMock(return_value=plebnet_settings.SUCCESS)
        plebnet_settings.Init.vpn_host = MagicMock()
        cloudomate_controller.get_vpn_providers = MagicMock(return_value='String')
        plebnet_settings.Init.wallets_testnet = MagicMock(return_value=True)
        market_controller.get_balance = MagicMock(return_value=1100000)
        cloudomate_controller.calculate_price_vpn = MagicMock(return_value=0.01)
        logger.success = MagicMock()
        logger.log = MagicMock()
        logger.error = MagicMock()

        Core.attempt_purchase_vpn()
        logger.success.assert_called_once()

        cloudomate_controller.purchase_choice_vpn = MagicMock(return_value=plebnet_settings.FAILURE)
        plebnet_settings.Init.wallets_testnet = MagicMock(return_value=False)
        Core.attempt_purchase_vpn()
        logger.error.assert_called_once()

        plebnet_settings.Init.vpn_host = self.vpnset
        cloudomate_controller.get_vpn_providers = self.vpnpro
        plebnet_settings.Init.wallets_testnet = self.wall
        market_controller.get_balance = self.bal
        cloudomate_controller.calculate_price_vpn = self.price
        cloudomate_controller.purchase_choice_vpn = self.pur
        logger.success = self.suc
        logger.log = self.log
        logger.error = self.err

    def test_vpn_is_running(self):
        self.pid = plebnet_settings.Init.vpn_pid
        self.run = plebnet_settings.Init.vpn_running
        self.call = subprocess.call

        plebnet_settings.Init.vpn_pid = MagicMock(return_value='String')
        plebnet_settings.Init.vpn_running = MagicMock()
        subprocess.call = MagicMock(return_value=0)

        assert Core.vpn_is_running()

        subprocess.call = MagicMock(return_value=1)

        self.assertFalse(Core.vpn_is_running())

        plebnet_settings.Init.vpn_pid = self.pid
        plebnet_settings.Init.vpn_running = self.run
        subprocess.call = self.call

    def test_check_vpn_install(self):
        self.vpn_installed = plebnet_settings.Init.vpn_installed
        self.log = logger.log
        self.ospath = os.path.join
        self.path = plebnet_settings.Init.vpn_config_path
        self.pre = plebnet_settings.Init.vpn_own_prefix
        self.cre = plebnet_settings.Init.vpn_credentials_name
        self.nam = plebnet_settings.Init.vpn_config_name
        self.lis = os.listdir
        self.isf = os.path.isfile
        self.civ = Core.install_vpn
        self.cpr = plebnet_settings.Init.vpn_child_prefix
        self.usr = os.path.expanduser
        self.vpn_running = Core.vpn_is_running

        plebnet_settings.Init.vpn_installed = MagicMock(return_value=True)
        logger.log = MagicMock()
        os.path.join = MagicMock(return_value='String')

        Core.vpn_is_running = MagicMock(return_value=True)
        plebnet_settings.Init.vpn_config_path = MagicMock()
        plebnet_settings.Init.vpn_own_prefix = MagicMock()
        plebnet_settings.Init.vpn_credentials_name = MagicMock(return_value='cred_name')
        plebnet_settings.Init.vpn_config_name = MagicMock(return_value='config_name')
        os.listdir = MagicMock(return_value=[])
        os.path.isfile = MagicMock(return_value=False)
        os.path.expanduser = MagicMock()

        assert Core.check_vpn_install()

        Core.vpn_is_running = MagicMock(return_value=False)
        os.path.isfile = MagicMock(return_value=True)
        Core.install_vpn = MagicMock(return_value=False)
        plebnet_settings.Init.vpn_installed = MagicMock(return_value=False)

        self.assertFalse(Core.check_vpn_install())

        Core.install_vpn = MagicMock(return_value=True)

        assert Core.check_vpn_install()

        os.listdir = MagicMock(return_value=['child_pre0config_name', 'child_pre0cred_name'])
        plebnet_settings.Init.vpn_child_prefix = MagicMock(return_value='child_pre')
        os.path.isfile = MagicMock(return_value=False)
        self.assertFalse(Core.check_vpn_install())

        plebnet_settings.Init.vpn_installed = self.vpn_installed
        logger.log = self.log
        os.path.join = self.ospath
        plebnet_settings.Init.vpn_config_path = self.path
        plebnet_settings.Init.vpn_own_prefix = self.pre
        plebnet_settings.Init.vpn_credentials_name = self.cre
        plebnet_settings.Init.vpn_config_name = self.nam
        os.listdir = self.lis
        os.path.isfile = self.isf
        Core.install_vpn = self.civ
        plebnet_settings.Init.vpn_child_prefix = self.cpr
        os.path.expanduser = self.usr
        Core.vpn_is_running = self.vpn_running

    def test_get_amount_mb_tokens_earned(self):
        self.mb_transactions = wallet_controller.get_MB_transactions
        self.mb_pending = wallet_controller.get_MB_balance_pending
        self.mb_balance = wallet_controller.get_MB_balance
        amount1 = 0.00395598
        amount3 = 0.28483758
        balance_pending = 0.2
        balance_available = 0.4
        transactions = [
            {
                "currency": "MB",
                "to": "17AVS7n3zgBjPq1JT4uVmEXdcX3vgB2wAh",
                "outgoing": True,
                "from": "",
                "description": "",
                "timestamp": "1489673696",
                "fee_amount": 0.0,
                "amount": amount1,
                "id": "6f6c40d034d69c5113ad8cb3710c172955f84787b9313ede1c39cac85eeaaffe"
            },
            {
                "currency": "MB",
                "to": "17AVS7n3zgBjPq1JT4uVmEXdcX3vgB2wAh",
                "outgoing": False,
                "from": "",
                "description": "",
                "timestamp": "1489673696",
                "fee_amount": 0.0,
                "amount": 0.48304839,
                "id": "6f6c40d034d69c5113ad8cb3710c172955f84787b9313ede1c39cac85eeaaffe"
            },
            {
                "currency": "MB",
                "to": "17AVS7n3zgBjPq1JT4uVmEXdcX3vgB2wAh",
                "outgoing": True,
                "from": "",
                "description": "",
                "timestamp": "1489673696",
                "fee_amount": 0.0,
                "amount": amount3,
                "id": "6f6c40d034d69c5113ad8cb3710c172955f84787b9313ede1c39cac85eeaaffe"
            }
        ]
        wallet_controller.get_MB_transactions = MagicMock(return_value=transactions)
        wallet_controller.get_MB_balance_pending = MagicMock(return_value=balance_pending)
        wallet_controller.get_MB_balance = MagicMock(return_value=balance_available)

        mb_tokens_amount = amount1 + amount3 + balance_pending + balance_available
        self.assertEqual(mb_tokens_amount, Core.get_amount_mb_tokens_earned())

        wallet_controller.get_MB_transactions = self.mb_transactions
        wallet_controller.get_MB_balance_pending = self.mb_pending
        wallet_controller.get_MB_balance = self.mb_balance

    def test_get_reward_qlearning(self):
        self.vps_options = cloudomate_controller.get_vps_option
        self.get_mb_earned = Core.get_amount_mb_tokens_earned
        self.config_expiration = PlebNetConfig.time_to_expiration
        self.core_config = Core.config
        self.core_qtable = Core.qtable

        price = 10
        mb_tokens_earned = 88878356
        cur_option = VpsOption(
                name="Basic",
                storage=100,
                cores=2,
                memory=10,
                bandwidth=10000,
                connection=1,
                price=10,
                purchase_url="https://panel.linevast.de"
            )

        Core.config = PlebNetConfig()
        Core.qtable = MagicMock()
        cloudomate_controller.get_vps_option = MagicMock(return_value=cur_option)
        Core.get_amount_mb_tokens_earned = MagicMock(return_value=mb_tokens_earned)
        PlebNetConfig.time_to_expiration = MagicMock(return_value=1592000)

        reward = mb_tokens_earned / (price * (1000000 / plebnet_settings.TIME_IN_DAY) * 10000 * 2)
        self.assertEqual(reward, Core.get_reward_qlearning())

        cloudomate_controller.get_vps_option = self.vps_options
        Core.get_amount_mb_tokens_earned = self.get_mb_earned
        PlebNetConfig.time_to_expiration = self.config_expiration
        Core.config = self.core_config
        Core.qtable = self.core_qtable


if __name__ == '__main__':
    unittest.main()
