"""
This file is used to control all dependencies with Tribler Market.

Other files should never have a direct import from Tribler Market, as the reduces the maintainability of this code.
If Tribler Market alters its call methods, this should be the only file which needs to be updated in PlebNet.
"""

import requests

from requests.exceptions import ConnectionError
# TODO: deze moet hier ook weg, en is deze wallet anders dan de Electurm wallet?
from cloudomate.wallet import Wallet

from plebnet.utilities import logger

def is_market_running():
    try:
        requests.get('http://localhost:8085/market')
        return True
    except ConnectionError:
        return False


def get_mc_balance():
    logger.log('The market is running: ' + str(is_market_running()), "get balance")
    try:
        r = requests.get('http://localhost:8085/wallets/MC/balance')
        balance = r.json()
        return balance['balance']['available']
    except ConnectionError:
        return False


def get_btc_balance():
    w = Wallet()
    return w.get_balance_confirmed()


def put_ask(price, price_type, quantity, quantity_type, timeout):
    return _put_request(price, price_type, quantity, quantity_type, timeout, 'asks')


def put_bid(price, price_type, quantity, quantity_type, timeout):
    return _put_request(price, price_type, quantity, quantity_type, timeout, 'bids')


def _put_request(price, price_type, quantity, quantity_type, timeout, domain):
    url = 'http://localhost:8085/market/' + domain
    data = {'price': price,
            'price_type': price_type,
            'quantity': quantity,
            'quantity_type': quantity_type,
            'timeout': timeout}
    json = requests.put(url, data=data).json()
    if 'created' in json:
        return json['created']
    else:
        print json['error']['message']
        return False


def asks():
    url = 'http://localhost:8085/market/asks'
    r = requests.get(url)
    return r.json()['asks']


def bids():
    url = 'http://localhost:8085/market/bids'
    r = requests.get(url)
    return r.json()['bids']


if __name__ == '__main__':
    if not is_market_running():
        print "Market isn't running"
        exit(0)
    print get_mc_balance()
    print put_bid(1, 'MC', 1, 'BTC', 120)
    print put_ask(1, 'MC', 1, 'BTC', 120)
    print asks()
    print bids()
    print is_market_running()
