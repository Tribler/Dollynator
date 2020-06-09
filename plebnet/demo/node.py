from plebnet.address_book import AddressBook
from plebnet.demo.qtable_demo import QTableDemo

import random

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
        # print("\tcontacts (" + str(len(self.address_book.contacts)) + "): " + contacts_list)

    def earn_bitcoins(self):

        sell_rate = random.uniform(0.4, 0.8)

        self.btc_balance += self.mb_tokens * sell_rate
        self.mb_tokens *= sell_rate

    def earn_mb_tokens(self):

        self.mb_tokens = random.uniform(1.0, 2.0)
