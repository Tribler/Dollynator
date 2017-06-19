import random


class DNA:
    rate = 0.005
    length = 0.0
    dictionary = {}

    def __init__(self):
        pass

    def set_length(self, length):
        self.length = length

    def get_length(self):
        return self.length

    def set_dictionary(self, dict):
        self.dictionary = dict

    def get_dictionary(self):
        return self.dictionary

    @staticmethod
    def create_test_dict():
        dict = {'blueangelhost': 0.5, 'ccihosting': 0.5, 'crowncloud': 0.5, 'legionbox': 0.5, 'linevast': 0.5,
                'pulseserver': 0.5, 'rockhoster': 0.5, 'undergroundprivate': 0.5}
        return dict

    def normalize(self):
        length = 0.0
        dictionary = self.dictionary
        for item in dictionary:
            length += dictionary[item]
        for item in dictionary:
            dictionary[item] /= length
        self.set_dictionary(dictionary)
        self.set_length(length)

    def mutate(self, provider):
        dictionary = self.get_dictionary()
        dictionary[provider] += self.rate
        self.set_dictionary(dictionary)

    def demutate(self, provider):
        dictionary = self.get_dictionary()
        dictionary[provider] -= self.rate
        if dictionary[provider] < 0:
            dictionary[provider] += self.rate
        self.set_dictionary(dictionary)

    def denormalize(self):
        newlength = 0.0
        dictionary = self.get_dictionary()
        length = self.get_length()
        for item in dictionary:
            newlength += dictionary[item]
        for item in dictionary:
            dictionary[item] *= (length / newlength)
        self.set_dictionary(dictionary)

    def choose_provider(self):
        dictionary = self.get_dictionary()
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

    def iterate(self, itdict):
        for i in xrange(10000):
            provider = self.choose()
            num = random.uniform(0, 1)
            if num > 0.5:
                self.positive_evolve(provider)
            else:
                self.negative_evolve(provider)


for i in range(100):
    j = DNA().create_test_dict()
    DNA().set_dictionary(j)
    DNA().iterate(j)
    print DNA().get_dictionary()
