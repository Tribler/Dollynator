import os
import unittest

import cloudomate.hoster.vps.blueangelhost as blueAngel
import cloudomate.hoster.vps.linevast as linevast
import cloudomate.gateway.coinbase as Coinbase
import cloudomate.hoster.vpn.azirevpn as azirevpn
from cloudomate import wallet as wallet_util
from cloudomate.hoster.vps.clientarea import ClientArea
from cloudomate.util.settings import Settings
from cloudomate.cmdline import providers as cloudomate_providers
from mock.mock import MagicMock
from plebnet.communication import git_issuer


import plebnet.controllers.cloudomate_controller as cloudomate
import plebnet.controllers.market_controller as market
from plebnet.controllers.wallet_controller import TriblerWallet
import plebnet.agent.dna as DNA
from plebnet.agent.config import PlebNetConfig
from plebnet.settings import plebnet_settings
from plebnet.utilities import logger as Logger


class TestCloudomateController(unittest.TestCase):

    class Price(object):
        def __init__(self, me):
            self.price = me

        price = 0

    def test_child_account(self):
        self.cloudomate_settings = Settings.__init__
        self.cloudomate_read = Settings.read_settings
        self.os_is_join = os.path.join
        self.PlebNetConfig = PlebNetConfig.__init__
        self.PlebNetConfig_get = PlebNetConfig.get

        os.path.join = MagicMock()
        Settings.read_settings = MagicMock()
        Settings.__init__ = MagicMock(return_value=None)
        PlebNetConfig.__init__ = MagicMock(return_value=None)
        PlebNetConfig.get = MagicMock(return_value="test")

        # Test child_account with index
        cloudomate.child_account("1")
        os.path.join.assert_called_once()
        Settings.read_settings.assert_called_once()
        Settings.__init__.assert_called_once()
        PlebNetConfig.get.assert_not_called()

        # Test child_account without index
        cloudomate.child_account()
        PlebNetConfig.get.assert_called_once()

        os.path.join = self.os_is_join
        Settings.read_settings = self.cloudomate_read
        Settings.__init__ = self.cloudomate_settings
        PlebNetConfig.__init__ = self.PlebNetConfig
        PlebNetConfig.get = self.PlebNetConfig_get

    def test_vps_providers(self):
        r = cloudomate.get_vps_providers()
        assert len(r) > 0

    def test_status(self):
        self.child_account = cloudomate.child_account
        self.provider = blueAngel.BlueAngelHost.get_status

        cloudomate.child_account = MagicMock()
        blueAngel.BlueAngelHost.get_status = MagicMock()
        assert cloudomate.status(blueAngel.BlueAngelHost)

        cloudomate.child_account = self.child_account
        blueAngel.BlueAngelHost.get_status = self.provider

    def test_get_ip(self):
        self.clientarea = ClientArea.__init__
        self.clientarea_service = ClientArea.get_services
        self.clientarea_ip = ClientArea.get_ip
        self.logger_log = Logger.log

        ClientArea.__init__ = MagicMock(return_value=None)
        Logger.log = MagicMock()
        ClientArea.get_services = MagicMock()
        ClientArea.get_ip = MagicMock()

        cloudomate.get_ip(blueAngel.BlueAngelHost, 'testaccount')
        ClientArea.get_ip.assert_called_once()

        ClientArea.__init__ = self.clientarea
        Logger.log = self.logger_log
        ClientArea.get_services = self.clientarea_service
        ClientArea.get_ip = self.clientarea_ip

    def test_options(self):
        self.provider = blueAngel.BlueAngelHost.get_options

        blueAngel.BlueAngelHost.get_options = MagicMock()
        cloudomate.options(blueAngel.BlueAngelHost)
        blueAngel.BlueAngelHost.get_options.assert_called_once()

        blueAngel.BlueAngelHost.get_options = self.provider

    def test_get_network_fee(self):
        self.wallet_util = wallet_util.get_network_fee

        wallet_util.get_network_fee = MagicMock()
        cloudomate.get_network_fee()
        wallet_util.get_network_fee.assert_called_once()

        wallet_util.get_network_fee = self.wallet_util

    def test_pick_providers(self):
        self.DNA = DNA.DNA.choose_provider
        self.vps = cloudomate.get_vps_providers
        self.get_gateway = blueAngel.BlueAngelHost.get_gateway
        self.estimate_price = Coinbase.Coinbase.estimate_price
        self.pick_options = cloudomate.pick_option
        self.get_price = wallet_util.get_price
        self.get_fee = wallet_util.get_network_fee

        DNA.DNA.choose_provider = MagicMock()
        cloudomate.get_vps_providers = MagicMock(return_value=[blueAngel.BlueAngelHost, blueAngel.BlueAngelHost])
        blueAngel.BlueAngelHost.get_gateway = MagicMock()
        Coinbase.Coinbase.estimate_price = MagicMock()
        cloudomate.pick_option = MagicMock(return_value=[1, 2, 3])
        wallet_util.get_price = MagicMock()
        wallet_util.get_network_fee = MagicMock()

        cloudomate.pick_provider(list)
        blueAngel.BlueAngelHost.get_gateway.assert_called_once()

        DNA.DNA.choose_provider = self.DNA
        cloudomate.get_vps_providers = self.vps
        blueAngel.BlueAngelHost.get_gateway = self.get_gateway
        Coinbase.Coinbase.estimate_price = self.estimate_price
        cloudomate.pick_option = self.pick_options
        wallet_util.get_price = self.get_price
        wallet_util.get_network_fee = self.get_fee

    def test_pick_otpions_zero(self):
        self.options = cloudomate.options
        self.providers = cloudomate_providers.__init__

        cloudomate.options = MagicMock()
        cloudomate_providers.__init__= MagicMock()
        cloudomate.pick_option('BlueAngelHost')
        cloudomate.options.assert_called_once()

        cloudomate.options = self.options
        cloudomate_providers.__init__ = self.providers

    def test_pick_options(self):
        self.options = cloudomate.options
        self.providers_true = cloudomate_providers.__init__
        self.linevast = linevast.LineVast
        self.logger = Logger.log

        cloudomate.options = MagicMock(return_value=[self.Price(2), self.Price(5), self.Price(1)])
        cloudomate_providers.__init__ = MagicMock()
        Logger.log = MagicMock()

        cloudomate.pick_option('BlueAngelHost')
        Logger.log.assert_called_once()

        cloudomate_providers.__init__ = self.providers_true
        cloudomate.options = self.options
        linevast.LineVast = self.linevast
        Logger.log = self.logger

    def test_update_offer(self):
        self.config = PlebNetConfig.get
        self.calculate_price = cloudomate.calculate_price
        self.placeoffer = cloudomate.place_offer

        PlebNetConfig.get = MagicMock(return_value=False)
        cloudomate.place_offer = MagicMock(return_value=True)

        cloudomate.update_offer(PlebNetConfig())
        cloudomate.place_offer.assert_not_called()

        cloudomate.calculate_price = MagicMock(return_value=9)
        PlebNetConfig.get = MagicMock(return_value=(blueAngel.BlueAngelHost, 'test', 'test'))
        cloudomate.update_offer(PlebNetConfig())
        cloudomate.place_offer.assert_called_once()

        PlebNetConfig.get = self.config
        cloudomate.calculate_price = self.calculate_price
        cloudomate.place_offer = self.placeoffer

    def test_calculate_price(self):
        self.options = cloudomate.options
        self.logger = Logger.log
        self.providers = cloudomate_providers.__init__

        cloudomate.options = MagicMock()
        Logger.log = MagicMock()
        cloudomate_providers.__init__ = MagicMock()

        cloudomate.calculate_price('BlueAngelHost', 0)
        cloudomate.options.assert_called_once()

        self.options = cloudomate.options = self.options
        Logger.log = self.logger
        cloudomate_providers.__init__ = self.providers


    def test_calculate_price_vpn(self):
        self.options = cloudomate.options
        self.logger = Logger.log
        self.providers = cloudomate_providers.__init__

        cloudomate.options = MagicMock()
        Logger.log = MagicMock()
        cloudomate_providers.__init__ = MagicMock()

        cloudomate.calculate_price_vpn('azirevpn')
        cloudomate.options.assert_called_once()

        self.options = cloudomate.options = self.options
        Logger.log = self.logger
        cloudomate_providers.__init__ = self.providers

    def test_place_offer_zero_mb(self):
        self.mb = market.get_balance
        self.logger = Logger.log

        Logger.log = MagicMock()
        market.get_balance = MagicMock(return_value=0)
        self.assertFalse(cloudomate.place_offer(5, PlebNetConfig()))

        market.get_balance = self.mb
        Logger.log = self.logger

    def test_place_offer(self):
        self.mb = market.get_balance
        self.logger = Logger.log
        self.put = market.put_ask
        self.true_settings = plebnet_settings.Init.wallets_testnet

        Logger.log = MagicMock()
        market.get_balance = MagicMock(return_value=56)
        market.put_ask = MagicMock()
        plebnet_settings.Init.wallets_testnet = MagicMock(return_value=False)

        cloudomate.place_offer(5, PlebNetConfig())
        market.put_ask.assert_called_once()

        market.get_balance = self.mb
        Logger.log = self.logger
        market.put_ask = self.put

    def test_purchase_choice_failure(self):
        self.config = PlebNetConfig.get
        self.triblerwallet = TriblerWallet.__init__
        self.settings = plebnet_settings.Init.wallets_testnet_created
        self.purchase = blueAngel.BlueAngelHost.purchase
        self.logger = Logger.warning

        PlebNetConfig.get = MagicMock(side_effect=self.side_effect)
        plebnet_settings.Init.wallets_testnet_created = MagicMock(return_value=None)
        TriblerWallet.__init__ = MagicMock(return_value=None)
        blueAngel.BlueAngelHost.purchase = MagicMock(return_value=None)
        Logger.warning = MagicMock()

        self.assertEquals(cloudomate.purchase_choice(PlebNetConfig()), plebnet_settings.FAILURE)

        PlebNetConfig.get = self.config
        TriblerWallet.__init__ = self.triblerwallet
        plebnet_settings.Init.wallets_testnet_created = self.settings
        blueAngel.BlueAngelHost.purchase = self.purchase
        Logger.warning = self.logger

    def test_purchase_choice(self):
        self.config = PlebNetConfig.get
        self.triblerwallet = TriblerWallet.__init__
        self.settings = plebnet_settings.Init.wallets_testnet_created
        self.purchase = blueAngel.BlueAngelHost.purchase
        self.logger = Logger.warning

        PlebNetConfig.get = MagicMock(side_effect=self.side_effect)
        plebnet_settings.Init.wallets_testnet_created = MagicMock(return_value=None)
        TriblerWallet.__init__ = MagicMock(return_value=None)
        blueAngel.BlueAngelHost.purchase = MagicMock(return_value=('Hash', 0))
        Logger.warning = MagicMock()

        self.assertEquals(cloudomate.purchase_choice(PlebNetConfig()), plebnet_settings.SUCCESS)

        PlebNetConfig.get = self.config
        TriblerWallet.__init__ = self.triblerwallet
        plebnet_settings.Init.wallets_testnet_created = self.settings
        blueAngel.BlueAngelHost.purchase = self.purchase
        Logger.warning = self.logger

    def test_purchase_choice_error(self):
        self.config = PlebNetConfig.get
        self.triblerwallet = TriblerWallet.__init__
        self.settings = plebnet_settings.Init.wallets_testnet_created
        self.purchase = blueAngel.BlueAngelHost.purchase
        self.logger = Logger.warning

        self.error = Logger.error
        self.issue = git_issuer.handle_error

        PlebNetConfig.get = MagicMock(side_effect=self.side_effect)
        plebnet_settings.Init.wallets_testnet_created = MagicMock(return_value=None)
        TriblerWallet.__init__ = MagicMock(return_value=None)
        blueAngel.BlueAngelHost.purchase = MagicMock(side_effect=Exception)
        Logger.warning = MagicMock()
        Logger.error = MagicMock()
        git_issuer.handle_error = MagicMock()

        self.assertEquals(cloudomate.purchase_choice(PlebNetConfig()), plebnet_settings.FAILURE)

        PlebNetConfig.get = self.config
        TriblerWallet.__init__ = self.triblerwallet
        plebnet_settings.Init.wallets_testnet_created = self.settings
        blueAngel.BlueAngelHost.purchase = self.purchase
        Logger.warning = self.logger
        Logger.error = self.error
        git_issuer.handle_error = self.issue

    def test_purchase_choice_vpn(self):
        self.config = PlebNetConfig.get
        self.triblerwallet = TriblerWallet.__init__
        self.settings = plebnet_settings.Init.wallets_testnet_created
        self.purchase = azirevpn.AzireVpn.purchase
        self.logger = Logger.warning

        PlebNetConfig.get = MagicMock(side_effect=self.side_effect)
        plebnet_settings.Init.wallets_testnet_created = MagicMock(return_value=None)
        TriblerWallet.__init__ = MagicMock(return_value=None)
        azirevpn.AzireVpn.purchase = MagicMock(return_value=('Hash', 0))
        Logger.warning = MagicMock()

        self.assertEquals(cloudomate.purchase_choice_vpn(PlebNetConfig()), plebnet_settings.SUCCESS)

        PlebNetConfig.get = self.config
        TriblerWallet.__init__ = self.triblerwallet
        plebnet_settings.Init.wallets_testnet_created = self.settings
        azirevpn.AzireVpn.purchase = self.purchase
        Logger.warning = self.logger

    # def test_save_info_vpn(self):
    #     self.config = PlebNetConfig.get
    #     self.settings = plebnet_settings.Init
    #
    #     PlebNetConfig.get = MagicMock(side_effect=self.side_effect)
    #
    #     self.assertTrue(cloudomate.save_info_vpn(PlebNetConfig()))
    #
    #     PlebNetConfig.get = self.config
    #     plebnet_settings.init = self.settings
    #
    def side_effect(type, value):
        if value == 'child_index':
            return 2
        else:
            return ['BlueAngelHost', 0, 'test']

if __name__ == '__main__':
    unittest.main()
