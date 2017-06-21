import os
import time
from ConfigParser import SafeConfigParser

from appdirs import user_config_dir

CONFIG_NAME = "plebnet.cfg"


class PlebNetConfig(object):
    @staticmethod
    def load():
        config_dir = user_config_dir()
        filename = os.path.join(config_dir, CONFIG_NAME)
        cfg = PlebNetConfig()
        cfg.config.read(filename)
        return cfg

    def __init__(self):
        self.config = SafeConfigParser()
        config = self.config
        config.add_section('main')
        config.set('main', 'expiration_date', 0)
        config.set('main', 'last_offer_date', 0)
        config.set('main', 'last_offer', {'MC': 0, 'BTC:': 0.0})
        config.set('main', 'excluded_providers', [])
        config.set('main', 'chosen_providers', [])
        config.set('main', 'bought', [])

    def save(self):
        config_dir = user_config_dir()
        filename = os.path.join(config_dir, CONFIG_NAME)
        with open(filename, 'w') as f:
            self.config.write(f)

    def get(self, option):
        return self.config.get('main', option)

    def time_to_expiration(self):
        current_time = time.time()
        expiration = self.config.getfloat('main', 'expiration_date')
        return expiration - current_time

    def time_since_offer(self):
        current_time = time.time()
        offer_time = self.config.getfloat('main', 'last_offer_date')
        return current_time - offer_time

    def set(self, option, value):
        self.config.set('main', option, value)
