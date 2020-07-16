import json
import subprocess
import requests
import unittest
import responses

import plebnet.controllers.wallet_controller as walletcontroller
import plebnet.controllers.market_controller as marketcontroller
import plebnet.settings.plebnet_settings as plebnet_settings

from unittest.mock import MagicMock
from plebnet.utilities import logger


class TestWalletController(unittest.TestCase):

    def setUp(self):
        self.settings_true = plebnet_settings.Init.wallets_testnet_created
        self.true_logger = logger.log
        self.true_market = marketcontroller.is_market_running
        self.settings_password = plebnet_settings.Init.wallets_password
        logger.log = MagicMock()
        plebnet_settings.Init.wallets_testnet_created = MagicMock(return_value=False)
        marketcontroller.is_market_running = MagicMock(return_value=True)
        plebnet_settings.Init.wallets_password = MagicMock(return_value="plebnet")

    def tearDown(self):
        logger.log = self.true_logger
        plebnet_settings.Init.wallets_testnet_created = self.settings_true
        marketcontroller.is_market_running = self.true_market
        plebnet_settings.Init.wallets_password = self.settings_password

    def test_create_wallet_testnet_created(self):
        plebnet_settings.Init.wallets_testnet_created = MagicMock(return_value=True)
        assert walletcontroller.create_wallet('TBTC')

    def test_create_wallet_wrong_type(self):
        self.assertFalse(walletcontroller.create_wallet('nonesense'))

    def test_create_wallet_no_market(self):
        marketcontroller.is_market_running = MagicMock(return_value=False)
        self.assertFalse(walletcontroller.create_wallet('TBTC'))

    @responses.activate
    def test_create_wallet(self):
        responses.add(responses.PUT, 'http://localhost:8085/wallets/BTC',
                      json={'created': 'true'})
        assert walletcontroller.create_wallet('BTC')

    @responses.activate
    def test_create_wallet_already_created(self):
        responses.add(responses.PUT, 'http://localhost:8085/wallets/BTC',
                      json={'error': 'this wallet already exists'})
        assert walletcontroller.create_wallet('BTC')

    @responses.activate
    def test_create_wallet_unknown_error(self):
        responses.add(responses.PUT, 'http://localhost:8085/wallets/BTC',
                      json={'error': 'unknown error'})
        self.assertFalse(walletcontroller.create_wallet('BTC'))

    @responses.activate
    def test_get_wallet_address(self):
        responses.add(responses.GET, 'http://localhost:8085/wallets',
                      json={'wallets': {'BTC': {'address': 5000}}})
        self.assertEqual(walletcontroller.get_wallet_address('BTC'), 5000)

    def test_get_wallet_address_error(self):
        self.requests = requests.get
        requests.get = MagicMock(side_effect=requests.ConnectionError)
        self.assertEquals(walletcontroller.get_wallet_address('BTC'), "No %s wallet found" % 'BTC')

        requests.get = self.requests

    @responses.activate
    def test_get_balance(self):
        responses.add(responses.GET, 'http://localhost:8085/wallets',
                      json={'wallets': {'BTC': {'balance': {'available': 5000}}}})
        self.assertEqual(walletcontroller.get_balance('BTC'), 5000)

    def test_get_balance_error(self):
        self.requests = requests.get
        requests.get = MagicMock(side_effect=requests.ConnectionError)
        self.assertEquals(walletcontroller.get_balance('BTC'), "No %s wallet found" % 'BTC')

        requests.get = self.requests

    def test_create_wallet_different_error(self):
        self.popen = subprocess.Popen.communicate
        self.json = json.loads
        json.loads = MagicMock(return_value={'error': 'unspecified error'})

        self.assertFalse(walletcontroller.create_wallet('TBTC'))

        json.loads = self.json
        subprocess.Popen.communicate = self.popen

    def test_create_wallet_error(self):
        self.popen = subprocess.Popen.communicate
        subprocess.Popen.communicate = MagicMock(side_effect=requests.ConnectionError)

        self.assertFalse(walletcontroller.create_wallet('TBTC'))

        subprocess.Popen.communicate = self.popen

    def test_tribler_wallet_constructor(self):
        r = walletcontroller.TriblerWallet()
        r.__init__()
        assert r.coin == 'BTC'
        o = walletcontroller.TriblerWallet(True)
        o.__init__(True)
        assert o.coin == 'TBTC'

    def test_get_balance2(self):
        self.market = marketcontroller.get_balance
        marketcontroller.get_balance = MagicMock(return_value=5)

        r = walletcontroller.TriblerWallet()
        r.__init__()

        self.assertEquals(r.get_balance(), 5)

        marketcontroller.get_balance = self.market

    def test_pay_not_enough_balance(self):
        self.balance = walletcontroller.TriblerWallet.get_balance
        self.popen = subprocess.Popen.communicate
        walletcontroller.TriblerWallet.get_balance = MagicMock(return_value=0)
        subprocess.Popen.communicate = MagicMock()

        r = walletcontroller.TriblerWallet()
        r.__init__()
        r.pay('address', 30)
        walletcontroller.TriblerWallet.get_balance.assert_called_once()
        subprocess.Popen.communicate.assert_not_called()

        walletcontroller.TriblerWallet.get_balance = self.balance
        subprocess.Popen.communicate = self.popen

    def test_pay_error(self):
        self.balance = walletcontroller.TriblerWallet.get_balance
        walletcontroller.TriblerWallet.get_balance = MagicMock(return_value=50)

        r = walletcontroller.TriblerWallet()
        r.__init__()

        self.assertEquals(r.pay('address', 30), False)
        walletcontroller.TriblerWallet.get_balance = self.balance

    @responses.activate
    def test_pay(self):
        self.true_balance = walletcontroller.TriblerWallet.get_balance
        walletcontroller.TriblerWallet.get_balance = MagicMock(return_value=300)

        r = walletcontroller.TriblerWallet()
        r.__init__()

        responses.add(responses.POST, 'http://localhost:8085/wallets/' + r.coin + '/transfer', json={'txid': 'testID'})
        self.assertEquals(r.pay('address', 0.000003), 'testID')
        walletcontroller.TriblerWallet.get_balance = self.true_balance

    @responses.activate
    def test_pay_transactions(self):
        self.true_balance = walletcontroller.TriblerWallet.get_balance
        walletcontroller.TriblerWallet.get_balance = MagicMock(return_value=300)

        r = walletcontroller.TriblerWallet(True)
        r.__init__(True)
        print(r.coin)

        responses.add(responses.POST, 'http://localhost:8085/wallets/' + r.coin + '/transfer', json={'txid': None})
        responses.add(responses.GET, 'http://localhost:8085/wallets/tbtc/transactions', json={"transactions": [{
            "id": "testID",
            "to": 'address'}]})

        self.assertEquals(r.pay('address', 0.000003), 'testID')
        walletcontroller.TriblerWallet.get_balance = self.true_balance

    @responses.activate
    def test_get_balance_pending(self):
        pending = 2.4
        responses.add(responses.GET, 'http://localhost:8085/wallets/MB/balance',
                      json={'balance': {'available': 0.02, 'pending': pending, 'currency': 'MB'}})
        self.assertEqual(pending, walletcontroller.get_MB_balance_pending())

    def test_get_balance_pending_no_connection(self):
        self.requests = requests.get
        requests.get = MagicMock(side_effect=requests.ConnectionError)
        self.assertEquals(walletcontroller.get_MB_balance_pending(), "No %s wallet found" % 'MB')

        requests.get = self.requests

    @responses.activate
    def test_get_transactions(self):
        transactions = [{
            "currency": "BTC",
            "to": "17AVS7n3zgBjPq1JT4uVmEXdcX3vgB2wAh",
            "outgoing": False,
            "from": "",
            "description": "",
            "timestamp": "1489673696",
            "fee_amount": 0.0,
            "amount": 0.00395598,
            "id": "6f6c40d034d69c5113ad8cb3710c172955f84787b9313ede1c39cac85eeaaffe"
        }]
        responses.add(responses.GET, 'http://localhost:8085/wallets/MB/transactions',
                      json={"transactions": transactions})
        self.assertEqual(transactions, walletcontroller.get_MB_transactions())

    def test_get_transactions_no_connection(self):
        self.requests = requests.get
        requests.get = MagicMock(side_effect=requests.ConnectionError)
        self.assertEquals(walletcontroller.get_MB_transactions(), "No %s wallet found" % 'MB')

        requests.get = self.requests


if __name__ == '__main__':
    unittest.main()
