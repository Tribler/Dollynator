import json
import os
import time

from appdirs import user_config_dir

CONFIG_NAME = "plebnet.json"


class PlebNetConfig(object):
    def load(self):
        config_dir = user_config_dir()
        filename = os.path.join(config_dir, CONFIG_NAME)
        if not os.path.isfile(filename):
            self.save()
        with open(filename, 'r') as json_file:
            self.config = json.load(json_file)

    def __init__(self):
        self.config = {'expiration_date': 0,
                       'last_offer_date': 0,
                       'last_offer': {'MC': 0,
                                      'BTC:': 0.0},
                       'excluded_providers': [],
                       'chosen_provider': None,
                       'bought': [],
                       'installed': [],
                       'transactions': []}
        self.load()

    def save(self):
        config_dir = user_config_dir()
        filename = os.path.join(config_dir, CONFIG_NAME)
        with open(filename, 'w') as f:
            json.dump(self.config, f, indent=3)

    def get(self, option):
        return self.config[option]

    def time_to_expiration(self):
        current_time = time.time()
        expiration = float(self.config['expiration_date'])
        return expiration - current_time

    def time_since_offer(self):
        current_time = time.time()
        offer_time = float(self.config['last_offer_date'])
        return current_time - offer_time

    def bump_offer_date(self):
        self.config['last_offer_date'] = time.time()

    def set(self, option, value):
        self.config[option] = value
