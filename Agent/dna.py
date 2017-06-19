import random


class DNA:
    rate = 0.005
    length = 0.0

    def __init__(self):
        pass

    @staticmethod
    def create_test_dict():
        dict = {'blueangelhost': 0.5, 'ccihosting': 0.5, 'crowncloud': 0.5, 'legionbox': 0.5, 'linevast': 0.5,
                'pulseserver': 0.5, 'rockhoster': 0.5, 'undergroundprivate': 0.5}
        return dict

    @staticmethod
    def normalize(normdict):
        length = 0.0
        for item in normdict:
            length += normdict[item]
        for item in normdict:
            normdict[item] /= length
        return normdict, length

    def mutate(self, provider, mutdict):
        mutdict[provider] += self.rate
        return mutdict

    def demutate(self, provider, demutdict):
        demutdict[provider] -= self.rate
        if demutdict[provider] < 0:
            demutdict[provider] += self.rate
        return demutdict

    def denormalize(self, denormdict):
        newlength = 0.0
        length = self.get_length()
        for item in denormdict:
            newlength += denormdict[item]
        for item in denormdict:
            denormdict[item] *= (length / newlength)
        check = 0.0
        for item in denormdict:
            check += denormdict[item]
        return denormdict

    @staticmethod
    def choose_provider(provdict):
        number = random.uniform(0, 1)
        for item in provdict:
            number -= provdict[item]
            if number <= 0:
                return item

    def choose(self, dictionary):
        dictionary, l = self.normalize(dictionary)
        self.set_length(l)
        provider = self.choose_provider(dictionary)
        return provider

    def positive_evolve(self, posdict, provider):
        posdict = self.mutate(provider, posdict)
        posdict = self.denormalize(posdict)
        return posdict

    def negative_evolve(self, negdict, provider):
        negdict = self.demutate(provider, negdict)
        negdict = self.denormalize(negdict)
        return negdict

    def iterate(self, itdict):
        for i in xrange(10000):
            provider = self.choose(itdict)
            num = random.uniform(0, 1)
            if num > 0.5:
                itdict = self.positive_evolve(itdict, provider)
            else:
                itdict = self.negative_evolve(itdict, provider)
        return itdict

    def set_length(self, length):
        self.length = length

    def get_length(self):
        return self.length


print DNA().create_test_dict()
for i in range(100):
    j = DNA().create_test_dict()
    print DNA().iterate(j)
