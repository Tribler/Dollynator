#!/usr/bin/python2
#coding=utf8

import time
import logging
import os
import requests
import sys

from plebnet.utilities.btc import satoshi_to_btc

__offer_check_time__ = 10

coin = None


def check_bids(limit):
    '''
    Periodically checks for bids in the market, and places an ask against it.
    Currently, accepts all bids regardless of bidder.
    '''
    
    logging.info('Coin type is: %s' % coin)
    logging.info('Limit price is: %s BTC/MB' % limit)
        
    r = requests.get('http://localhost:8085/market/bids')

    # evaluate each
    asks = r.json()['bids']

    # we focus only on MB-for-BTC bids
    for ask in asks:
        if ask['asset1'] == coin and ask['asset2'] == 'MB':
            ticks = sorted(ask['ticks'], key=tick_price)

            for tick in ticks:
                first_amount = tick['assets']['first']['amount']  # should be in BTC
                first_type = tick['assets']['first']['type']
                second_amount = tick['assets']['second']['amount']  # should be in MB
                second_type = tick['assets']['second']['type']
                price = tick_price(tick)

                logging.info('[Bid]: %s %s / %s %s (%s)' % (satoshi_to_btc(first_amount), first_type, second_amount,
                                                            second_type, price))

                if price < limit:
                    make_ask(first_amount, first_type, second_amount, second_type)
                    time.sleep(10)


def tick_price(tick):
    return satoshi_to_btc(tick['assets']['first']['amount']) / tick['assets']['second']['amount']


def make_ask(first_amount, first_type, second_amount, second_type):
    '''
    Makes an ask with the same arguments as a bid.
    '''
    logging.info("[Making an ask]:  %s %s / %s %s" % (str(satoshi_to_btc(first_amount)), first_type, str(second_amount),
                                                      second_type))

    # make a bid
    data = {
        'first_asset_amount': first_amount,
        'first_asset_type': first_type,
        'second_asset_amount': second_amount,
        'second_asset_type': second_type
    }
    r = requests.put('http://localhost:8085/market/asks', data=data)
    logging.info(r.json())


if __name__ == "__main__":
    '''
    Initializes check bids.
    '''
    logging.basicConfig(format="%(asctime)s:%(message)s", level='NOTSET', datefmt='%d/%m/%Y %H:%M:%S')

    tribler_wallet_path = os.path.expanduser('~/.Tribler/wallet')
    if os.path.isfile(os.path.join(tribler_wallet_path, 'tbtc_wallet')):
        coin = 'TBTC'
    else:
        coin = 'BTC'

    limit = 0
    if len(sys.argv) == 2:
        limit = float(sys.argv[1])
    else:
        print("Usage: python buybot.py <limit price>")
        exit(0)

    while True:
        check_bids(limit)
        time.sleep(300)
