import requests
from requests.exceptions import ConnectionError
from cloudomate.wallet import Wallet

def is_market_running():
    try:
        requests.get('http://localhost:8085/market')
        return True
    except ConnectionError:
        return False


def get_mc_balance():
    r = requests.get('http://localhost:8085/wallets/MC/balance')
    balance = r.json()
    return balance['balance']['available']


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
