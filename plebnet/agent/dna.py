"""
Contains the DNA of the agent, which is used for the genetic decision making. It stores provider-value pairs
which indicate the preference towards each provider. Decisions are made by choosing uniformly between all
preferences. Updating DNA works by normalising all values, increasing/decreasing a value by the rate and
then denormalising all values again.
"""

import copy
import json
import os
import random

from appdirs import user_config_dir

class DNA:
    """
    Class for the DNA of the agent
    """
    rate = 0.005  # the update rate to change the genes
    length = 0.0  # sum of all DNA values
    dictionary = {}  # contains all DNA data
    vps = {}  # contains the probabilities for each option

    def __init__(self):
        pass

    def read_dictionary(self, providers=None):
        """
        Reads DNA configuration from file if the file exists, otherwise creates new DNA configuration with
        the providers given.
        :param providers: dictionary of providers to include in DNA.
        """
        config_dir = user_config_dir()
        filename = os.path.join(config_dir, 'DNA.json')

        if not os.path.exists(filename):
            self.dictionary = self.create_initial_dict(providers)
            self.write_dictionary()
        else:
            with open(filename) as json_file:
                data = json.load(json_file)
                self.dictionary = data
        self.vps = self.dictionary['VPS']

    @staticmethod
    def create_initial_dict(providers):
        """
        Creates the DNA configuration for the first agent, where the host is unknown and the parents do not exist.
        :param providers: dictionary of providers to use in DNA.
        :return: the created DNA configuration.
        """

        initial_dict = {'Self': 'unknown',
                        'tree': '',
                        'transaction_hash': '',
                        'VPS': {provider_class.get_metadata()[0]: 0.5 for
                                provider_class in providers.values()}}
        return initial_dict

    def write_dictionary(self):
        """
        Writes the DNA configuration to the DNA.json file.
        """
        config_dir = user_config_dir()
        filename = os.path.join(config_dir, 'DNA.json')
        with open(filename, 'w') as json_file:
            json.dump(self.dictionary, json_file)

    def create_child_dna(self, provider, tree, transaction_hash):
        """
        Creates the DNA configuration for the child agent. This is done by copying the own DNA configuration
        and including the new host provider, the parent name and the transaction hash.
        :param provider: the name the child tree name.
        :param tree: tree of inheritance
        :param transaction_hash: the transaction hash the child is bought with.
        """
        dictionary = copy.deepcopy(self.dictionary)
        dictionary['Self'] = provider
        dictionary['tree'] = tree
        dictionary['transaction_hash'] = transaction_hash
        filename = os.path.join(user_config_dir(), 'Child_DNA.json')
        with open(filename, 'w') as json_file:
            json.dump(dictionary, json_file)

    def add_provider(self, provider):
        self.vps[provider] = 0.5

    def remove_provider(self, provider):
        self.vps.pop(provider)

    def normalize(self):
        self.length = sum(self.vps.values())
        for item in self.vps:
            self.vps[item] /= self.length

    def mutate(self, provider):
        if provider not in self.vps:
            return False
        self.vps[provider] += self.rate

    def demutate(self, provider):
        if provider not in self.vps:
            return False
        self.vps[provider] -= self.rate
        if self.vps[provider] < 0:
            self.vps[provider] += self.rate

    def denormalize(self):
        newlength = sum(self.vps.values())
        for item in self.vps:
            self.vps[item] *= (self.length / newlength)

    @staticmethod
    def choose_provider(dictionary):
        number = random.uniform(0, 1)
        for item in dictionary:
            number -= dictionary[item]
            if number <= 0:
                return item

    def exclude(self, provider):
        dictionary = copy.deepcopy(self.vps)
        dictionary.pop(provider)
        return dictionary

    @staticmethod
    def normalize_excluded(dictionary):
        length = sum(dictionary.values())
        for item in dictionary:
            dictionary[item] /= length
        return dictionary

    def positive_evolve(self, provider):
        self.normalize()
        self.mutate(provider)
        self.denormalize()
        self.write_dictionary()

    def negative_evolve(self, provider):
        self.normalize()
        self.demutate(provider)
        self.denormalize()
        self.write_dictionary()

    def set_own_provider(self, provider):
        self.dictionary['Self'] = provider
        self.write_dictionary()

    def get_own_provider(self):
        return self.dictionary['Self']

    def set_own_tree(self, tree):
        self.dictionary['tree'] = tree
        self.write_dictionary()

    def get_own_tree(self):
        return self.dictionary['tree']

    def evolve(self, success, provider=None):
        """
        Evolves the DNA of the agent. If successful, increase value of own provider, if not successful
        decrease value of chosen option.
        :param success: boolean if purchase successful.
        :param provider: the provider to change the value of.
        """
        if success:
            self.positive_evolve(self.get_own_provider())
        else:
            self.negative_evolve(provider)


def get_dna():
    dna = DNA()
    dna.read_dictionary()
    return dna.vps

def get_tree():
    dna = DNA()
    dna.read_dictionary()
    return dna.get_own_tree()

def get_host():
    dna = DNA()
    dna.read_dictionary()
    return dna.get_own_provider()
