import os
import random
import json
import copy

from appdirs import user_config_dir


class DNA:
    rate = 0.005
    length = 0.0
    dictionary = {}

    def __init__(self):
        pass

    @staticmethod
    def create_test_dict():
        testdict = {'blueangelhost': 0.5, 'ccihosting': 0.5, 'crowncloud': 0, 'legionbox': 0, 'linevast': 0.5,
                    'pulseserver': 0.5, 'rockhoster': 0.5, 'undergroundprivate': 0}
        return testdict

    def read_dictionary(self):
        config_dir = user_config_dir()
        filename = os.path.join(config_dir, 'DNA.json')

        if not os.path.exists(filename):
            self.dictionary = self.create_test_dict()
        else:
            with open(filename) as json_file:
                data = json.load(json_file)
                self.dictionary = data

    def write_dictionary(self):
        config_dir = user_config_dir()
        filename = os.path.join(config_dir, 'DNA.json')
        with open(filename, 'w') as json_file:
            json.dump(self.dictionary, json_file)

    def add_provider(self, provider):
        self.dictionary[provider] = 0.5

    def remove_provider(self, provider):
        self.dictionary.pop(provider)

    def normalize(self):
        self.length = sum(self.dictionary.values())
        for item in self.dictionary:
            self.dictionary[item] /= self.length

    def mutate(self, provider):
        self.dictionary[provider] += self.rate

    def demutate(self, provider):
        self.dictionary[provider] -= self.rate
        if self.dictionary[provider] < 0:
            self.dictionary[provider] += self.rate

    def denormalize(self):
        newlength = sum(self.dictionary.values())
        for item in self.dictionary:
            self.dictionary[item] *= (self.length / newlength)

    @staticmethod
    def choose_provider(dictionary):
        number = random.uniform(0, 1)
        for item in dictionary:
            number -= dictionary[item]
            if number <= 0:
                return item

    def exclude(self, provider):
        dictionary = copy.deepcopy(self.dictionary)
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
        provider = self.choose_provider(self.dictionary)
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

    def negative_evolve(self, provider):
        self.normalize()
        self.demutate(provider)
        self.denormalize()
