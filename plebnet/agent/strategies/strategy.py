from abc import ABCMeta, abstractmethod

from plebnet.agent.config import PlebNetConfig
from plebnet.settings import plebnet_settings
from plebnet.utilities import logger

log_name = "agent.strategies.strategy"
BTC_FLUCTUATION_MARGIN = 1.15


class Strategy(metaclass=ABCMeta):

    def __init__(self):
        self.config = PlebNetConfig()

    @abstractmethod
    def apply(self):
        """
        Performs the whole strategy step for one plebnet check iteration
        :return:
        """
        pass

    @abstractmethod
    def sell_reputation(self):
        """
        Sells or holds current reputation (MB) depending on the implementing strategy
        :return:
        """
        pass

    @abstractmethod
    def create_offer(self, timeout):
        """
        Creates a new order in the market, with parameters depending on the implementing strategy
        :return:
        """
        pass

    def update_offer(self, timeout=plebnet_settings.TIME_IN_HOUR):
        """
        Check if an hour as passed since the last offer made, if passed create a new offer.
        """
        if self.config.time_since_offer() > timeout:
            logger.log("Calculating new offer", log_name)
            self.create_offer(timeout)
            self.config.save()
