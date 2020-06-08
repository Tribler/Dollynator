from plebnet.messaging import Message, Contact, MessageConsumer, generate_contact_key_pair
from plebnet.address_book import AddressBook
import random
import threading
import time
from cloudomate.hoster.vps.vps_hoster import VpsOption
from plebnet.agent.qtable import ProviderOffer, VPSState
import math
import os
import jsonpickle
import copy

from typing import Tuple

class QTableDemo:
    learning_rate = 0.005
    environment_lr = 0.4
    discount = 0.05
    INFINITY = 10000000
    start_alpha = 0.8  # between 0.5 and 1.
    start_beta = 0.2  # between 0 and 0.5

    def __init__(self, replications = 0):
        self.qtable = {}
        self.environment = {}
        self.alphatable = {}
        self.betatable = {}
        self.number_of_updates = {}
        self.providers_offers = []
        self.self_state = VPSState()

        self.replications = replications

        pass

    def init_qtable_and_environment(self, providers):
        """
        Initializes the qtable and environment with their respective starting values.
        """
        self.init_providers_offers(providers)

        for provider_of in self.providers_offers:
            prov = {}
            environment_arr = {}
            for provider_offer in self.providers_offers:
                prov[self.get_ID(provider_offer)] = 0
                environment_arr[self.get_ID(provider_offer)] = 0
            self.qtable[self.get_ID(provider_of)] = prov
            self.environment[self.get_ID(provider_of)] = environment_arr

    def init_alpha_and_beta(self):
        """
        Initialize the alpha and beta arrays with their respective starting values.
        Arrays and not table because every column of the QTable is going to have the same
        alpha and beta values since we never update only one cell but the whole column.
        """
        # self.alphatable = {i: self.start_alpha for i in self.providers_offers}
        # self.betatable = {i: self.start_beta for i in self.providers_offers}
        for provider_of in self.providers_offers:
            alph = {}
            bet = {}
            num = {}
            for provider_offer in self.providers_offers:
                alph[self.get_ID(provider_offer)] = self.start_alpha
                bet[self.get_ID(provider_offer)] = self.start_beta
                num[self.get_ID(provider_offer)] = 0
            self.alphatable[self.get_ID(provider_of)] = alph
            self.betatable[self.get_ID(provider_of)] = bet
            self.number_of_updates[self.get_ID(provider_of)] = num

    def init_providers_offers(self, providers):
        """
        Gets all the available provider offers to choose from.
        """
        for i, id in enumerate(providers):
            options = cloudomate_controller.options(providers[id])
            for i, option in enumerate(options):
                element = ProviderOffer(provider_name=providers[id].get_metadata()[0], name=str(option.name),
                                        bandwidth=option.bandwidth, price=option.price, memory=option.memory)
                self.providers_offers.append(element)

    def update_alpha_and_beta(self, provider_offer_ID):
        """
        every time we merge local QTable with remote one we want to update alpha and beta first in order to give the
        appropriate weight to local and remote information.
        """
        # TODO: Switch to a mathematical model update? I.e.: a modified sigmoid
        update_current_state = self.number_of_updates[self.get_ID_from_state()][self.get_ID_from_state()] + 1

        if update_current_state <= 50:
            for provider_of in self.providers_offers:
                self.alphatable[self.get_ID(provider_of)][self.get_ID_from_state()] = \
                    self.start_alpha - update_current_state * 0.012  # chosen constant
                self.betatable[self.get_ID(provider_of)][self.get_ID_from_state()] = \
                    self.start_beta + update_current_state * 0.012  # chosen constant
                self.number_of_updates[self.get_ID(provider_of)][self.get_ID_from_state()] += 1

        else:
            for provider_of in self.providers_offers:
                self.alphatable[self.get_ID(provider_of)][provider_offer_ID] = 0.2
                self.betatable[self.get_ID(provider_of)][provider_offer_ID] = 0.8

    def max_action_value(self, provider):
        max_value = -self.INFINITY
        for i, provider_offer in enumerate(self.qtable):
            if max_value < self.qtable[provider_offer][self.get_ID(provider)]:
                max_value = self.qtable[provider_offer][self.get_ID(provider)]
        return max_value

    def choose_option(self, providers):
        """
        Selects the next action (VPS provider to buy) to choose from the qtable.
        """
        lambd = 1 - 1 / (self.replications + 3)
        num = random.expovariate(lambd)
        num = int(math.floor(num))

        if num > len(self.qtable[self.get_ID_from_state()]) - 1:
            num = len(self.qtable[self.get_ID_from_state()]) - 1

        return self.choose_k_option(providers, num)

    def choose_k_option(self, providers, num):
        candidate = {"option": {}, "option_name": "", "provider_name": "", "score": -self.INFINITY,
                     "price": self.INFINITY,
                     "currency": "USD"}

        score = self.get_kth_score(providers, num)

        for i, offer_name in enumerate(self.qtable):
            if self.qtable[self.get_ID_from_state()][offer_name] == score and self.find_provider(
                    offer_name) in providers:
                candidate["score"] = self.qtable[self.get_ID_from_state()][offer_name]
                provider = self.find_provider(offer_name)
                candidate["provider_name"] = provider
                candidate["option_name"] = self.find_offer(offer_name, provider)
        options = cloudomate_controller.options(providers[candidate["provider_name"]])

        for i, option in enumerate(options):
            if option.name == candidate["option_name"]:
                candidate["option"] = option
                candidate["price"] = option.price

        return candidate

    def get_kth_score(self, providers, num):
        to_choose_scores = []
        for i, offername in enumerate(self.qtable):
            if self.find_provider(offername) in providers:
                elem = {"score": self.qtable[self.get_ID_from_state()][offername], "id": offername}
                to_choose_scores.append(elem)
        to_choose_scores.sort(key=lambda x: x["score"], reverse=True)
        return to_choose_scores[num]["score"]

    def find_provider(self, offer_name):
        for offer in self.providers_offers:
            if self.get_ID(offer) == offer_name:
                return offer.provider_name.lower()
        raise ValueError("Can't find provider for " + offer_name)

    def find_offer(self, offer_name, provider):
        for offer in self.providers_offers:
            if self.get_ID(offer) == offer_name and provider.lower() == offer.provider_name.lower():
                return offer.name
        raise ValueError("Can't find offer for " + offer_name)

    def set_self_state(self, self_state):
        self.self_state = self_state

    def get_ID(self, provider_offer):
        return str(provider_offer.provider_name).lower() + "_" + str(provider_offer.name).lower()

    def get_ID_from_state(self):
        return str(self.self_state.provider).lower() + "_" + str(self.self_state.option).lower()

    def update_qtable(self, received_qtables, provider_offer_ID, status=False, MBtokens=0):
        """
        Updates an agent's QTable by considering the QTables received from other nodes through gossiping
        and its own informations, according to an adapted version of the QD-Learning algorithm.
        It uses two submethods - update_remote_qtable and update_self_qtable - to execute the two part of the algorithm.
        :param received_qtables: an array containing the QTables received from other agents
        :param provider_offer_ID: the ID of the VPS option attempted to purchase.
        :param status: a boolean indicating whether the purchase was successfully executed or not.
        """

        to_add = copy.deepcopy(self.qtable)
        for i in to_add:
            for j in to_add:
                to_add[i][j] = 0

        for remote_qtable in received_qtables:
            self.update_remote_qtable(remote_qtable, provider_offer_ID, to_add)

        self.update_self_qtable(provider_offer_ID, status, MBtokens, to_add)

        for i in self.qtable:
            for j in self.qtable:
                self.qtable[i][j] += to_add[i][j]

        self.update_alpha_and_beta(provider_offer_ID)


    def update_remote_qtable(self, remote_qtable, provider_offer_ID, to_add):
        """
        Method that gets a remote QTable and updates the local one following the
        algorithm (10) found in the following paper 'link'
        :param remote_qtable: remote QTable shared by random agent.
        :param provider_offer_ID: the ID of the VPS option attempted to purchase.
        :param to_add: a matrix having the same dimensions of a qtable to store intermediate results.
        """

        for state in to_add:
            to_add[state][provider_offer_ID] -= self.betatable[state][provider_offer_ID] * self.qtable[state][
                provider_offer_ID] - remote_qtable[state][provider_offer_ID]
            to_add[state][self.get_ID_from_state()] -= self.betatable[state][self.get_ID_from_state()] \
                                                       * self.qtable[state][self.get_ID_from_state()] \
                                                       - remote_qtable[state][self.get_ID_from_state()]

    def update_self_qtable(self, provider_offer_ID, status, MBtokens, to_add):
        """
        Method that gets updates an agent's QTable according to its purchase attempt of a new VPS service
        :param provider_offer_ID: the ID of the VPS option attempted to purchase.
        :param status: a boolean indicating whether the purchase was successfully executed or not.
        :param to_add: a matrix having the same dimensions of a qtable to store intermediate results.
        """

        self.update_environment(provider_offer_ID, status, MBtokens)

        for provider_offer in self.providers_offers:
            learning_compound_purchase = self.environment[self.get_ID(provider_offer)][provider_offer_ID] \
                                         + self.discount * self.max_action_value(provider_offer) \
                                         - self.qtable[self.get_ID(provider_offer)][provider_offer_ID]
            learning_compound_current = self.environment[self.get_ID(provider_offer)][self.get_ID_from_state()] \
                                        + self.discount * self.max_action_value(provider_offer) \
                                        - self.qtable[self.get_ID(provider_offer)][self.get_ID_from_state()]

            to_add[self.get_ID(provider_offer)][provider_offer_ID] += self.alphatable[self.get_ID(provider_offer)][
                                                                          provider_offer_ID] * learning_compound_purchase
            to_add[self.get_ID(provider_offer)][self.get_ID_from_state()] += \
                self.alphatable[self.get_ID(provider_offer)][
                    self.get_ID_from_state()] * learning_compound_current

    def update_environment(self, provider_offer_ID, status, MBtokens):
        """
        Method that updates an agent's environment according to its purchase attempt of a new VPS service
        :param provider_offer_ID: the ID of the VPS option attempted to purchase.
        :param status: a boolean indicating whether the purchase was successfully executed or not.
        """

        if status:
            for i, actions in enumerate(self.environment):
                self.environment[actions][provider_offer_ID] += self.environment_lr
                self.environment[actions][self.get_ID_from_state()] += MBtokens
        else:
            for i, actions in enumerate(self.environment):
                self.environment[actions][provider_offer_ID] -= self.environment_lr
                self.environment[actions][self.get_ID_from_state()] += MBtokens


def log(node, message):

    print("Node " + node.self_contact.id + ": " + message)


vps_options = [
    VpsOption(
        name='Advanced',
        storage=2,
        cores=2,
        memory=2,
        bandwidth="mock",
        connection="1",
        price=100.0,
        purchase_url="mock"
    ),
    VpsOption(
        name='Basic Plan',
        storage=2,
        cores=2,
        memory=2,
        bandwidth="mock",
        connection="1",
        price=10.0,
        purchase_url="mock"
    )
]


def generate_new_node(
        replicating_node: Tuple[AddressBook, QTableDemo],
        port: int,
        id: str
    ):

    replicating_ab, replicating_qt = replicating_node

    replicating_option = replicating_qt.choose_option()

    pub, priv = generate_contact_key_pair()

    new_node_contact = Contact(
        id=str(id),
        host='127.0.0.1',
        port=port,
        public_key=pub
    )

    new_node_ab = AddressBook(
        self_contact=new_node_contact,
        private_key=priv
    )

    replicating_ab.create_new_distributed_contact(new_node_contact)
    
    new_node_qt = copy.deepcopy(replicating_qt)

    new_node_qt.replications += 1

    new_node_qt.self_state = VPSState(replicating_option.provider_name, replicating_option.option_name)
    
    return new_node_ab, new_node_qt


def demo():
    
    global nodes
    nodes = []

    def start_replicating(
        ports_range = 8000,
        replicating_interval = 1,
        ping_interval = 1,
        restore_timeout = 2,
        receiver_notify_interval = 0.001
    ):

        id_counter = 1

        root_pub, root_priv = generate_contact_key_pair()
        root_contact = Contact(
            id=str(id_counter),
            host="127.0.0.1",
            port=ports_range,
            public_key=root_pub
        )

        root = AddressBook(
            self_contact=root_contact,
            private_key=root_priv,
            contact_restore_timeout=restore_timeout,
            inactive_nodes_ping_interval=ping_interval,
            receiver_notify_interval=receiver_notify_interval
        )

        global nodes
        nodes.append(root)

        while True:

            ports_range += 1
            id_counter += 1

            replicating_node = random.choice(nodes)

            log(replicating_node, "Replicating")

            new_node_contact_list = replicating_node.contacts.copy()
            new_node_contact_list.append(replicating_node.self_contact)

            pub, priv = generate_contact_key_pair()

            new_node_contact = Contact(
                id=str(id_counter),
                host='127.0.0.1',
                port=ports_range,
                public_key=pub
            )

            new_node = AddressBook(
                self_contact=new_node_contact,
                private_key=priv,
                contacts=new_node_contact_list,
                contact_restore_timeout=restore_timeout,
                inactive_nodes_ping_interval=ping_interval,
                receiver_notify_interval=receiver_notify_interval
            )

            nodes.append(new_node)

            replicating_node.create_new_distributed_contact(new_node_contact)

            time.sleep(replicating_interval)

    def start_killing(
        nodes_threshold = 5,
        killing_interval = 2
    ):
        global nodes

        while True:

            time.sleep(killing_interval)

            if (len(nodes) < nodes_threshold):

                continue

            kill_probability = 1 / 6

            for node in nodes:

                if random.uniform(0, 1) <= kill_probability:

                    log(node, "dying")

                    node.kill()
                    nodes.remove(node)

    def print_snapshots(
        print_interval = 3
    ):

        global nodes

        while True:
            
            time.sleep(print_interval)

            print("\n=====================================================")

            for node in nodes:
                
                contacts_list = ""

                for contact in node.contacts:

                    contacts_list += str(contact.id) + ", "

                print("Node " + node.self_contact.id + " has " + str(len(node.contacts)) + " contacts: " + contacts_list)

            print("=====================================================\n")



    threading.Thread(target=start_replicating).start()
    threading.Thread(target=start_killing).start()
    threading.Thread(target=print_snapshots).start()


if __name__ == "__main__":
    demo()
