import random
import json


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

    def read_dictionary(self,json):
        with open('DNA.json') as json_file:
            data = json.loads(json_file)
        self.dictionary = data

    def write_dictionary(self):
        dictionary = self.dictionary
        return json.dumps(dictionary)

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

    def choose_provider(self):
        dictionary = self.dictionary
        number = random.uniform(0, 1)
        for item in dictionary:
            number -= dictionary[item]
            if number <= 0:
                return item

    def choose(self):
        self.normalize()
        provider = self.choose_provider()
        return provider

    def positive_evolve(self, provider):
        self.mutate(provider)
        self.denormalize()

    def negative_evolve(self, provider):
        self.demutate(provider)
        self.denormalize()

    def iterate(self):
        for i in xrange(10000):
            provider = self.choose()
            num = random.uniform(0, 1)
            if num > 0.5:
                self.positive_evolve(provider)
            else:
                self.negative_evolve(provider)


for i in range(100):
    dna = DNA()
    j = dna.create_test_dict()
    dna.dictionary = j
    dna.iterate()
    print dna.dictionary
