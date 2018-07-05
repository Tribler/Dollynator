"""
This file is used to control all dependencies of the Electrum wallet using the Tribler API.

Other files should never have a direct import from Tribler, as this reduces the maintainability of
this code. If Tribler alters its web API, this should be the only file which needs to be updated
in PlebNet.
"""

import market_controller as marketcontroller
import plebnet.settings.plebnet_settings as plebnet_settings
import requests
from requests.exceptions import ConnectionError
from plebnet.utilities import logger

settings = plebnet_settings.get_instance()


def create_wallet(wallet_type):
    """
    Create a BTC or TBTC wallet using the Tribler web API.
    :param wallet_type: BTC or TBTC
    :return: boolean representing success
    """
    if wallet_type == 'TBTC' and settings.wallets_testnet_created():
        logger.log("Testnet wallet already created", "create_wallet")
        return True
    if wallet_type != 'BTC' and wallet_type != 'TBTC':
        logger.log("Called unknown wallet type", "create_wallet")
        return False
    start_market = marketcontroller.is_market_running()
    if not start_market:
        logger.log("The marketplace can't be started", "create_wallet")
        return False
    try:
        data = {'password': settings.wallets_password()}
        r = requests.put('http://localhost:8085/wallets/' + wallet_type, data=data)
        message = r.json()
        if 'created' in message:
            logger.log("Wallet created successfully", "create_wallet")
            return True
        elif message['error'] == 'this wallet already exists':
            logger.log("The wallet was already created", "create_wallet")
            return True
        else:
            logger.log(str(message['error']), "create_wallet")
            return False
    except ConnectionError:
        logger.log("connection error while creating a wallet", "create_wallet")
        return False


class TriblerWallet(object):
    """
    This class expects Tribler to be running and uses the wallet created via Tribler. This object is
    used the send to Cloudomate and has its own get_balance and pay method.
    Either a TBTC or a BTC wallet.
    """

    def __init__(self, testnet=None):
        if testnet:
            self.coin = 'TBTC'
        else:
            self.coin = 'BTC'

    def get_balance(self):
        """
        Returns the balance of the current wallet.
        :return: the balance
        """
        return marketcontroller.get_balance(self.coin)

    def pay(self, address, amount, fee=None):
        """
        Send a post request to the Tribler web API for making a transaction.
        :param address: the address of the receiver
        :param amount: the amount to be sent excluding fee
        :param fee: the fee to be used, 0 if None
        :return: the transaction hash
        """
        if self.get_balance() < amount:
            logger.log('Not enough funds', 'wallet_controller.pay')
            return False

        try:
            data = {'amount': amount*1.1, 'destination': address}
            r = requests.post('http://localhost:8085/wallets/' + self.coin + '/transfer', data=data)
            transaction_hash = r.json()['txid']

            if transaction_hash:
                logger.log('Transaction successful. transaction_hash: %s' % transaction_hash, 'wallet_controller.pay')
            else:
                if self.coin == 'TBTC':
                    # in case the testnet servers are acting funky, but transaction actually
                    # was successful, retrieve the transaction_has from the /transactions route
                    btx = requests.get('http://localhost:8085/wallets/tbtc/transactions')
                    jbtx = btx.json()['transactions'][-1]
                    if address in jbtx['to']:
                        transaction_hash = jbtx['id']
            return transaction_hash
        except ConnectionError:
            logger.log('Transaction unsuccessful', 'pay')
            return False


def get_wallet_address(type):
    try:
        return requests.get('http://localhost:8085/wallets').json()['wallets'][type]['address']
    except:
        return "No %s wallet found" % type


def get_TBTC_wallet(): return get_wallet_address('TBTC')


def get_BTC_wallet(): return get_wallet_address('BTC')


def get_MB_wallet(): return get_wallet_address('MB')


def get_balance(type):
    try:
        return requests.get('http://localhost:8085/wallets').json()['wallets'][type]['balance']['available']
    except:
        return "No %s wallet found" % type


def get_TBTC_balance(): return get_balance('TBTC')


def get_BTC_balance(): return get_balance('BTC')


def get_MB_balance(): return get_balance('MB')


