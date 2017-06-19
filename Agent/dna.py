import random


class DNA:
    rate = 0.005

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
        return demutdict

    @staticmethod
    def denormalize(denormdict, length):
        newlength = 0.0
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

    def evolve(self, evoldict):
        evoldict, length = self.normalize(evoldict)
        provider = self.choose_provider(evoldict)
        evoldict = self.mutate(provider, evoldict)
        evoldict = self.denormalize(evoldict, length)
        return evoldict

    def iterate(self, itdict):
        for i in xrange(10000):
            itdict = self.evolve(itdict)
        return itdict

print DNA().create_test_dict()
for i in range(100):
    j = DNA().create_test_dict()
    print DNA().iterate(j)
