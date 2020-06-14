import copy
import json
import math
import os
import sys
import random

import jsonpickle

from appdirs import user_config_dir
from plebnet.agent.config import PlebNetConfig
from requests import get

from plebnet import address_book, messaging
from plebnet.controllers import cloudomate_controller
from plebnet.settings import plebnet_settings


class QTable:
    learning_rate = 0.005
    environment_lr = 0.4
    discount = 0.05
    INFINITY = 10000000
    start_alpha = 0.8  # between 0.5 and 1
    start_beta = 0.2  # between 0 and 0.5
    node_pub, node_priv = messaging.generate_contact_key_pair()
    port = 8000

    def __init__(self):
        self.qtable = {}
        self.environment = {}
        self.alphatable = {}
        self.betatable = {}
        self.number_of_updates = {}
        self.providers_offers = []
        self.self_state = VPSState()
        self.tree = ""
        self.address_book = None
        pass

    # TODO : share QTable when reproducing
    # TODO : update local qtable through remote qtables when reproducing

    def init_qtable_and_environment(self, providers):
        """
        Initializes the qtable and environment with their respective starting values.
        """
        self.init_providers_offers(providers)

        for provider_of in self.providers_offers:
            prov = {}
            environment_arr = {}
            for provider_offer in self.providers_offers:
                prov[self.get_ID(provider_offer)] = 0  # self.calculate_measure(provider_offer)
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

    def init_address_book(self, parent_id: str = ""):
        node_id = messaging.generate_contact_id(parent_id)
        config = PlebNetConfig()
        index = config.get("child_index")
        ip = get('https://api.ipify.org').text
        self_contact = messaging.Contact(node_id, ip, self.port, self.node_pub)
        self.address_book = address_book.AddressBook(self_contact, self.node_priv)

    @staticmethod
    def calculate_measure(provider_offer):
        """
        Estimates the starting value of the qtable.
        """
        return 1 / (math.pow(float(provider_offer.price), 3)) * float(provider_offer.bandwidth)

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
                # update alpha and beta
                self.alphatable[self.get_ID(provider_of)][self.get_ID_from_state()] = \
                    self.start_alpha - update_current_state * 0.012  # chosen constant
                self.betatable[self.get_ID(provider_of)][self.get_ID_from_state()] = \
                    self.start_beta + update_current_state * 0.012  # chosen constant
                # update number_of_updates table
                self.number_of_updates[self.get_ID(provider_of)][self.get_ID_from_state()] += 1

        # Is this really needed?
        else:
            for provider_of in self.providers_offers:
                # set alpha and beta to maximum values
                self.alphatable[self.get_ID(provider_of)][provider_offer_ID] = 0.2
                self.betatable[self.get_ID(provider_of)][provider_offer_ID] = 0.8

    def max_action_value(self, provider):
        max_value = -self.INFINITY
        for i, provider_offer in enumerate(self.qtable):
            if max_value < self.qtable[provider_offer][self.get_ID(provider)]:
                max_value = self.qtable[provider_offer][self.get_ID(provider)]
        return max_value

    def read_dictionary(self, providers=None):
        """
        Read the QTable object from file, if there isn't any make one.
        """
        config_dir = user_config_dir()
        filename = os.path.join(config_dir, 'QTable.json')

        if not os.path.exists(filename):
            # TODO: check if it will not affect anything
            self.self_state = VPSState(provider="linevast", option="Basic")
            self.init_qtable_and_environment(providers)
            self.init_alpha_and_beta()
            self.create_initial_tree()
            self.init_address_book()
            self.write_dictionary()
        else:
            with open(filename) as json_file:
                data_encoded = json.load(json_file)
                data = jsonpickle.decode(data_encoded)
                self.environment = data['environment']
                self.qtable = data['qtable']
                self.alphatable = data['alphatable']
                self.betatable = data['betatable']
                self.number_of_updates = data['number_of_updates']
                self.providers_offers = data['providers_offers']
                self.self_state = data['self_state']
                self.tree = data['tree']
                self.address_book = data['address_book']

    def choose_option(self, providers):
        """
        Selects the next action (VPS provider to buy) to choose from the qtable.
        """
        lambd = 1 - 1 / (self.get_no_replications() + 3)
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

        # TODO: Handle an edge case when cloudomate fails and options returns an empty array
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
        self.write_dictionary()

    def get_ID(self, provider_offer):
        return str(provider_offer.provider_name).lower() + "_" + str(provider_offer.name).lower()

    def get_ID_from_state(self):
        return str(self.self_state.provider).lower() + "_" + str(self.self_state.option).lower()

    def create_new_address_book(self, provider, child_index):
        """
        This method creates a new AddressBook to pass to the child. It sets the child's contact as self_contact
        and adds the parent's contact in the contacts list.
        """
        child_pub, child_priv = messaging.generate_contact_key_pair()
        child_id = messaging.generate_contact_id(self.address_book.self_contact.id)
        ip = self.get_node_ip(provider, child_index)
        child_contact = messaging.Contact(child_id, ip, self.port, child_pub)
        new_address_book = address_book.AddressBook(self_contact=child_contact,
                                                    private_key=child_priv,
                                                    contacts=self.address_book.contacts)
        new_address_book.contacts.append(self.address_book.self_contact)
        # TODO : Add child's contact to parent's addressbook?
        return new_address_book

    def get_node_ip(self, provider, index):
        account = cloudomate_controller.child_account(index)
        return cloudomate_controller.get_ip(provider, account)

    def create_child_qtable(self, provider, option, transaction_hash, child_index):
        """
        Creates the QTable configuration for the child agent. This is done by copying the own QTable configuration and
        including the new host provider, the parent name and the transaction hash.
        Moreover it passes an updated AddressBook to the child.
        :param provider: the name the child tree name.
        :param transaction_hash: the transaction hash the child is bought with.
        """

        next_state = VPSState(provider=provider, option=option)
        tree = self.tree + "." + str(child_index)
        new_address_book = self.create_new_address_book(provider, child_index)
        dictionary = {
            "environment": self.environment,
            "qtable": self.qtable,
            "alphatable": self.alphatable,
            "betatable": self.betatable,
            "number_of_updates": self.number_of_updates,
            "providers_offers": self.providers_offers,
            "self_state": next_state,
            "transaction_hash": transaction_hash,
            "tree": tree,
            "address_book": new_address_book
        }

        filename = os.path.join(user_config_dir(), 'Child_QTable.json')
        with open(filename, 'w') as json_file:
            encoded_dictionary = jsonpickle.encode(dictionary)
            json.dump(encoded_dictionary, json_file)

    def create_initial_tree(self):
        self.tree = plebnet_settings.get_instance().irc_nick()

    def get_no_replications(self):
        return len(self.tree.split("."))

    def write_dictionary(self):
        """
        Writes the QTABLE configuration to the QTable.json file.
        """
        config_dir = user_config_dir()
        filename = os.path.join(config_dir, 'QTable.json')
        to_save_var = {
            "environment": self.environment,
            "qtable": self.qtable,
            "alphatable": self.alphatable,
            "betatable": self.betatable,
            "number_of_updates": self.number_of_updates,
            "providers_offers": self.providers_offers,
            "self_state": self.self_state,
            "tree": self.tree,
            "address_book": self.address_book
        }
        with open(filename, 'w') as json_file:
            encoded_to_save_var = jsonpickle.encode(to_save_var)
            json.dump(encoded_to_save_var, json_file)

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

    # TODO: check if formula is correct
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

    # TODO : decide how many nodes to share qtable with
    def share_qtable(self):
        """
        Method that share local QTable with n nodes when the agent tries to reproduce.
        """
        msg = messaging.Message('qtable', 'qtable', self.qtable)
        for contact in self.address_book.contacts:
            self.address_book.send_message_to_contact(contact, msg)


class ProviderOffer:
    UNLIMITED_BANDWIDTH = 10

    def __init__(self, provider_name="", name="", bandwidth="", price=0, memory=0):
        self.provider_name = provider_name
        self.name = name
        self.price = price
        self.memory = memory
        try:
            bandwidth = float(bandwidth)
            if bandwidth < sys.maxsize:
                self.bandwidth = bandwidth
            else:
                self.bandwidth = self.UNLIMITED_BANDWIDTH
        except:
            self.bandwidth = self.UNLIMITED_BANDWIDTH


class VPSState:
    def __init__(self, provider="", option=""):
        self.provider = provider
        self.option = option
