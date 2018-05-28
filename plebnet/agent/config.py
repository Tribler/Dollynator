"""
Store and retrieve the configuration of the agent
"""

import json
import os
import time

from appdirs import user_config_dir


CONFIG_NAME = "plebnet.json"


class PlebNetConfig(object):
    """
    Store and retrieve the configuration of the agent
    """
    def __init__(self):
        """
        The initiator for a PlebNetConfig object
        """
        self.config = {"child_index": 0,
                       "expiration_date": 0,
                       "last_offer_date": 0,
                       "last_offer": {"MC": 0,
                                      "BTC:": 0.0},
                       "excluded_providers": [],
                       "chosen_provider": None,
                       "bought": [],
                       "installed": [],
                       "transactions": []}
        self.load()

    def load(self):
        """
        A method to read the config content from a file
        :return:
        """
        config_dir = user_config_dir()
        filename = os.path.join(config_dir, CONFIG_NAME)
        if not os.path.isfile(filename):
            self.save()
        with open(filename, 'r') as json_file:
            self.config = json.load(json_file)

    def save(self):
        """
        A method to write the config content to a file
        :return: nothing
        """
        config_dir = user_config_dir()
        filename = os.path.join(config_dir, CONFIG_NAME)
        with open(filename, 'w') as f:
            json.dump(self.config, f, indent=3)

    def get(self, option):
        """
        A method to retrieve the content of the configurations options
        :param option: the option which should be returned
        :type option: String
        :return: the content of the input
        :rtype: Generic
        """
        #TODO: check if option exists, otherwise raise error and return None
        return self.config[option]

    def time_to_expiration(self):
        """
        Retrieve the amount of time left before the VPS is ended
        :return: The amount of seconds left to live
        :rtype: double
        """
        current_time = time.time()
        expiration = float(self.config['expiration_date'])
        return expiration - current_time

    def time_since_offer(self):
        """
        Retrieve the amount of seconds since the last offer on the Tribler market was made
        :return: The amount of seconds since the last offer
        :rtype: double
        """
        current_time = time.time()
        offer_time = float(self.config['last_offer_date'])
        return current_time - offer_time

    def bump_offer_date(self):
        """
        Reset the last offer time to the current time
        :return: None
        :rtype: None
        """
        self.config['last_offer_date'] = time.time()

    def set(self, option, value):
        """
        A function to set the value of the configuration
        :param option: which config value should be updated
        :type option: String
        :param value: The value to put in place of the option
        :type value: Generic
        :return: None
        :rtype: None
        """
        self.config[option] = value

    def increment_child_index(self):
        """
        Increment the child index number after a new server is created
        :return: None
        :rtype: None
        """
        self.config['child_index'] = self.config['child_index'] + 1
        self.save()
