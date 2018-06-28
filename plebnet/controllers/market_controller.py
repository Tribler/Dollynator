"""
This file is used to control all dependencies with the Tribler marketplace.

Other files should never have a direct import from the Tribler marketplace, as this
reduces the maintainability of this code. If Tribler Market alters its call methods,
this should be the only file which needs to be updated in PlebNet.
"""

import requests

from requests.exceptions import ConnectionError
from plebnet.utilities import logger


def is_market_running():
    """
    Check if the Tribler market is running.
    :return: boolean
    """
    try:
        askslive = requests.head('http://localhost:8085/market/asks')
        bidslive = requests.head('http://localhost:8085/market/bids')
        if askslive.status_code & bidslive.status_code == 200:
            return True
        else:
            return False
    except ConnectionError:
        return False


def get_balance(domain):
    """
    Get the balance of the current wallet.
    :param domain: the wallet type BTC, TBTC or MB
    :return: the balance
    """
    logger.log('The market is running' + str(is_market_running()), "get " + domain + " balance")
    try:
        r = requests.get('http://localhost:8085/wallets/' + domain + '/balance')
        balance = r.json()
        return balance['balance']['available']
    except ConnectionError:
        return False


def put_ask(price, price_type, quantity, quantity_type, timeout):
    return _put_request(price, price_type, quantity, quantity_type, timeout, 'asks')


def put_bid(price, price_type, quantity, quantity_type, timeout):
    return _put_request(price, price_type, quantity, quantity_type, timeout, 'bids')


def _put_request(price, price_type, quantity, quantity_type, timeout, domain):
    """
    Put an ask or a bid on the Tribler marketplace.
    :param price: the price
    :param price_type: the price type
    :param quantity: the quantity
    :param quantity_type: the quantity type
    :param timeout: the time the ask or bid should exist
    :param domain: ask or bid
    :return: confirmation of the creation
    """
    url = 'http://localhost:8085/market/' + domain
    data = {'price': price,
            'quantity': quantity,
            'price_type': price_type,
            'quantity_type': quantity_type,
            'timeout': timeout}
    json = requests.put(url, data=data).json()
    if 'created' in json:
        return json['created']
    else:
        print json['error']['message']
        return False


def match_makers():
    """
    Returns the number of matchmakers the agent has.
    :return: the number of matchmakers
    """
    try:
        return len(requests.get('http://localhost:8085/market/matchmakers').json()['matchmakers'])
    except ConnectionError:
        return "Unable to retrieve amount of "


def asks():
    url = 'http://localhost:8085/market/asks'
    r = requests.get(url)
    return r.json()['asks']


def bids():
    url = 'http://localhost:8085/market/bids'
    r = requests.get(url)
    return r.json()['bids']


def has_matchmakers():
    """
    Checks if there are any matchmakers.
    :return: boolean
    """
    url = 'http://localhost:8085/market/matchmakers'
    r = requests.get(url)
    return r.json()['matchmakers'] != []
