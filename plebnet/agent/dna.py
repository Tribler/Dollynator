"""
Contains the DNA of the agent, which is used for the genetic decision making
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
    length = 0.0  # total length of DNA values
    dictionary = {}  # contains all DNA data
    vps = {}  # contains the probabilities for each option

    def __init__(self):
        pass

    def read_dictionary(self, providers=None):
        config_dir = user_config_dir()
        filename = os.path.join(config_dir, 'DNA.json')

        if not os.path.exists(filename):
            self.dictionary = self.create_initial_dict(providers)
        else:
            with open(filename) as json_file:
                data = json.load(json_file)
                self.dictionary = data
        self.vps = self.dictionary['VPS']

    @staticmethod
    def create_initial_dict(providers):
        initial_dict = {'Self': '',
                        'parent': '',
                        'transaction_hash': '',
                        'VPS': {provider_class.get_metadata()[0]: 0.5 for
                                provider_class in providers.values()}}
        return initial_dict

    def write_dictionary(self):
        config_dir = user_config_dir()
        filename = os.path.join(config_dir, 'DNA.json')
        with open(filename, 'w') as json_file:
            json.dump(self.dictionary, json_file)

    def create_child_dna(self, provider, parent_name, transaction_hash):
        dictionary = copy.deepcopy(self.dictionary)
        dictionary['Self'] = provider
        dictionary['parent'] = parent_name
        dictionary['transaction_hash'] = transaction_hash
        # TODO
        # raise NotImplementedError('RESET ALL VARIABLES EXCEPT VPS')
        # TODO
        config_dir = user_config_dir()
        filename = os.path.join(config_dir, 'Child_DNA.json')
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
            print("{0} not in dna".format(provider))
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

    def choose(self):
        self.normalize()
        provider = self.choose_provider(self.vps)
        self.denormalize()
        dictionary = self.exclude(provider)
        dictionary = self.normalize_excluded(dictionary)
        provider2 = None
        while not provider2:
            provider2 = self.choose_provider(dictionary)
        return provider, provider2

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


# TODO: Move to DNA, this is not a static method....
def get_own_provider(dna):
    return dna.dictionary['Self']


# TODO: Move to DNA, this is not a static method....
def evolve(provider, dna, success):
    if success:
        dna.positive_evolve(provider)
    else:
        dna.negative_evolve(provider)
