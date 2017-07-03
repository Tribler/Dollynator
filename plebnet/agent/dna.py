import copy
import json
import os
import random

from appdirs import user_config_dir


class DNA:
    rate = 0.005
    length = 0.0
    dictionary = {}
    vps = {}

    def __init__(self):
        pass

    @staticmethod
    def create_test_dict():
        testdict = {'Self': '',
                    'parent': '',
                    'transaction_hash': '',
                    'VPS': {'ccihosting': 0.5, 'linevast': 0.5, 'pulseservers': 0.5, 'rockhoster': 0.5}}
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
        self.vps = self.dictionary['VPS']

    def write_dictionary(self):
        config_dir = user_config_dir()
        filename = os.path.join(config_dir, 'DNA.json')
        with open(filename, 'w') as json_file:
            json.dump(self.dictionary, json_file)

    def create_child_dna(self, provider, parentname, transaction_hash):
        dictionary = copy.deepcopy(self.dictionary)
        dictionary['Self'] = provider
        dictionary['parent'] = parentname
        dictionary['transaction_hash'] = transaction_hash
        #TODO
        #raise NotImlementedError('RESET ALL VARIABLES EXCEPT VPS')
        #TODO
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
            print("{0} not in dna".format(provider))
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


if __name__ == "__main__":
    dna = DNA()
    dna.read_dictionary()
    print(dna.dictionary)
    dictionary = dna.exclude('linevast')
    print(dictionary)
    for i in range(100):
        dna.positive_evolve('rockhoster')
    print(dna.dictionary)
    print(dna.choose_provider(dictionary))
