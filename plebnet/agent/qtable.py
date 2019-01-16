import json
import math
import os
import sys
import random

import jsonpickle

from appdirs import user_config_dir

from plebnet.controllers import cloudomate_controller
from plebnet.settings import plebnet_settings
from plebnet.utilities import custom_tree


class QTable:
    learning_rate = 0.005
    environment_lr = 0.4
    discount = 0.05
    INFINITY = 10000000

    def __init__(self):
        self.qtable = {}
        self.environment = {}
        self.providers_offers = []
        self.self_state = VPSState()
        self.name = ""
        self.tree = []
        pass

    def init_qtable_and_environment(self, providers):
        self.init_providers_offers(providers)

        for provider_of in self.providers_offers:
            prov = {}
            environment_arr = {}
            for provider_offer in self.providers_offers:
                prov[self.get_ID(provider_offer)] = self.calculate_measure(provider_offer)
                environment_arr[self.get_ID(provider_offer)] = 0
            self.qtable[self.get_ID(provider_of)] = prov
            self.environment[self.get_ID(provider_of)] = environment_arr

    @staticmethod
    def calculate_measure(provider_offer):
        return 1 / (100 * float(provider_offer.price)) * float(provider_offer.bandwidth)

    def init_providers_offers(self, providers):
        for i, id in enumerate(providers):
            options = cloudomate_controller.options(providers[id])
            for i, option in enumerate(options):
                element = ProviderOffer(provider_name=providers[id].get_metadata()[0], name=str(option.name),
                                        bandwidth=option.bandwidth, price=option.price, memory=option.memory)
                self.providers_offers.append(element)

    def update_values(self, provider_offer_ID, status=False):
        self.update_environment(provider_offer_ID, status)

        for provider_offer in self.providers_offers:
            for provider_of in self.providers_offers:
                learning_compound = self.environment[self.get_ID(provider_offer)][self.get_ID(provider_of)] \
                                    + self.discount * self.max_action_value(provider_offer) \
                                    - self.qtable[self.get_ID(provider_offer)][self.get_ID(provider_of)]

                self.qtable[self.get_ID(provider_offer)][self.get_ID(provider_of)] = \
                    self.qtable[self.get_ID(provider_offer)][self.get_ID(provider_of)] \
                    + self.learning_rate * learning_compound

    def update_environment(self, provider_offer_ID, status):

        for i, actions in enumerate(self.environment):
            if status:
                self.environment[actions][self.get_ID_from_state()] += self.environment_lr

        # Update for offer which was chosen
        if not status:
            self.environment[self.get_ID_from_state()][provider_offer_ID] -= self.environment_lr

    def max_action_value(self, provider):
        max_value = -self.INFINITY
        for i, provider_offer in enumerate(self.qtable):
            if max_value < self.qtable[provider_offer][self.get_ID(provider)]:
                max_value = self.qtable[provider_offer][self.get_ID(provider)]
        return max_value

    def read_dictionary(self, providers=None):

        config_dir = user_config_dir()
        filename = os.path.join(config_dir, 'QTable.json')

        if not os.path.exists(filename):
            # TODO: check if it will not affect anything
            self.self_state = VPSState(provider="blueangelhost", option="Basic Plan")
            self.init_qtable_and_environment(providers)
            self.create_initial_tree()
            self.write_dictionary()
        else:
            with open(filename) as json_file:
                data_encoded = json.load(json_file)
                data = jsonpickle.decode(data_encoded)
                self.environment = data['environment']
                self.qtable = data['qtable']
                self.providers_offers = data['providers_offers']
                self.self_state = data['self_state']
                self.tree = data['tree']
                self.name = data['name']

    def choose_option(self, providers):
        curr_state = custom_tree.get_curr_state(self.tree, self.name)
        lambd = 1 - 1 / (custom_tree.get_no_replications(curr_state) + 3)
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
        to_choose_scores.sort(key=lambda x: x["score"])
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

    def create_child_qtable(self, provider, option, transaction_hash):
        """
        Creates the QTable configuration for the child agent. This is done by copying the own QTable configuration and including the new host provider, the parent name and the transaction hash.
        :param provider: the name the child tree name.
        :param transaction_hash: the transaction hash the child is bought with.
        """
        name = custom_tree.create_child_name(provider, option, transaction_hash)
        self.tree = custom_tree.add_child(self.tree, name, custom_tree.get_curr_state(self.tree, self.name))

        next_state = VPSState(provider=provider, option=option)
        dictionary = {
            "environment": self.environment,
            "qtable": self.qtable,
            "providers_offers": self.providers_offers,
            "self_state": next_state,
            "transaction_hash": transaction_hash,
            "tree": self.tree,
            "name": name

        }
        filename = os.path.join(user_config_dir(), 'Child_QTable.json')
        with open(filename, 'w') as json_file:
            encoded_dictionary = jsonpickle.encode(dictionary)
            json.dump(encoded_dictionary, json_file)

    def create_initial_tree(self):
        self.name = custom_tree.create_child_name(self.self_state.provider, self.self_state.option, "1")
        self.tree = custom_tree.add_child([], self.name)

    def write_dictionary(self):
        """
        Writes the QTABLE configuration to the QTable.json file.
        """
        config_dir = user_config_dir()
        filename = os.path.join(config_dir, 'QTable.json')
        to_save_var = {
            "environment": self.environment,
            "qtable": self.qtable,
            "providers_offers": self.providers_offers,
            "self_state": self.self_state,
            "tree": self.tree,
            "name": self.name
        }
        with open(filename, 'w') as json_file:
            encoded_to_save_var = jsonpickle.encode(to_save_var)
            json.dump(encoded_to_save_var, json_file)


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
