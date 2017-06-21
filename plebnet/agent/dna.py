import os
import random
import json

from appdirs import user_config_dir


class DNA:
    rate = 0.005
    length = 0.0
    dictionary = {}

    def __init__(self):
        pass

    @staticmethod
    def create_test_dict():
        testdict = {'blueangelhost': 0.5, 'ccihosting': 0.5, 'crowncloud': 0.5, 'legionbox': 0.5, 'linevast': 0.5,
                    'pulseserver': 0.5, 'rockhoster': 0.5, 'undergroundprivate': 0.5}
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
        dictionary = self.dictionary
        with open(filename, 'w') as json_file:
            json.dump(dictionary, json_file)

    def add_provider(self, provider):
        self.dictionary[provider] = 0.5

    def remove_provider(self, provider):
        self.dictionary.pop(provider)

    def normalize(self):
        length = 0.0
        dictionary = self.dictionary
        for item in dictionary:
            length += dictionary[item]
        for item in dictionary:
            dictionary[item] /= length
        self.dictionary = dictionary
        self.length = length

    def mutate(self, provider):
        dictionary = self.dictionary
        dictionary[provider] += self.rate
        self.dictionary = dictionary

    def demutate(self, provider):
        dictionary = self.dictionary
        dictionary[provider] -= self.rate
        if dictionary[provider] < 0:
            dictionary[provider] += self.rate
        self.dictionary = dictionary

    def denormalize(self):
        newlength = 0.0
        dictionary = self.dictionary
        length = self.length
        for item in dictionary:
            newlength += dictionary[item]
        for item in dictionary:
            dictionary[item] *= (length / newlength)
        self.dictionary = dictionary

    def choose_provider(self, exclude=None):
        dictionary = self.dictionary
        number = random.uniform(0, 1)
        for item in dictionary:
            number -= dictionary[item]
            if number <= 0:
                if item != exclude:
                    return item

    def choose(self):
        self.normalize()
        provider = self.choose_provider()
        provider2 = None
        while not provider2:
            provider2 = self.choose_provider(provider)
        self.denormalize()
        return provider, provider2

    def positive_evolve(self, provider):
        self.normalize()
        self.mutate(provider)
        self.denormalize()

    def negative_evolve(self, provider):
        self.normalize()
        self.demutate(provider)
        self.denormalize()
