from plebnet.address_book import AddressBook
from plebnet.demo.qtable_demo import QTableDemo

import json
import random
import time

class Node:

    def __init__(
        self,
        address_book: AddressBook,
        qtable: QTableDemo,
        age: int = 0,
        btc_balance: int = 0,
        mb_tokens: int = 0
    ):

        self.address_book = address_book
        self.qtable = qtable
        self.age = age
        self.btc_balance = btc_balance
        self.mb_tokens = mb_tokens

    def print_node(self):

        contacts_list = ""

        for contact in self.address_book.contacts:

            contacts_list += contact.id + ", "

        print("Node " + self.address_book.self_contact.id)
        print("\tage: " + str(self.age))
        print("\tbtc balance: " + str(self.btc_balance))
        # print("\tmb balance: " + str(self.mb_tokens))
        print("\tcontacts (" + str(len(self.address_book.contacts)) + "): " + contacts_list)

    def earn_bitcoins(self, print_format, output):

        sell_rate = random.uniform(0.4, 0.8)
        sell_price = random.uniform(0.9, 1.1)

        sold_mb_tokens = self.mb_tokens * sell_rate
        self.mb_tokens -= sold_mb_tokens

        earned_btc = sell_price * sold_mb_tokens
        self.btc_balance += earned_btc

        if print_format == 'json':

            log = json.dumps({
                'event_type': 'sold_mb_tokens',
                'timestamp': time.time(),
                'node': self.address_book.self_contact.id,
                'amount_sold': sold_mb_tokens,
                'btc_earned': earned_btc,
                'new_mb_tokens_balance': self.mb_tokens,
                'new_btc_balance': self.btc_balance
            })

            print(log)

            if output is not None:

                output.write(log + "\n")


    def earn_mb_tokens(self, print_format, output):

        earned_mb_tokens = random.uniform(1.0, 2.0)
        self.mb_tokens += earned_mb_tokens

        if print_format == 'json':

            log = json.dumps({
                'event_type': 'earn_mb_tokens',
                'timestamp': time.time(),
                'node': self.address_book.self_contact.id,
                'amount': earned_mb_tokens,
                'new_mb_tokens_balance': self.mb_tokens
            })

            print(log)

            if output is not None:

                output.write(log + "\n")
