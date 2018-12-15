from abc import ABCMeta, abstractmethod

from plebnet.agent.config import PlebNetConfig
from plebnet.controllers import market_controller
from plebnet.controllers.cloudomate_controller import calculate_price, calculate_price_vpn
from plebnet.settings import plebnet_settings
from plebnet.utilities import logger


log_name = "agent.strategies.strategy"
BTC_FLUCTUATION_MARGIN = 1.15


class Strategy():
    __metaclass__ = ABCMeta

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

    @staticmethod
    def get_replication_price(vps_provider, option, vpn_provider='azirevpn'):
        return (calculate_price(vps_provider, option) + calculate_price_vpn(vpn_provider)) * BTC_FLUCTUATION_MARGIN

    def update_offer(self, timeout=plebnet_settings.TIME_IN_HOUR):
        """
        Check if an hour as passed since the last offer made, if passed create a new offer.
        """
        if self.config.time_since_offer() > timeout:
            logger.log("Calculating new offer", log_name)
            self.create_offer(timeout)
            self.config.save()

    def btc_to_satoshi(self, btc_amount):
        return int(btc_amount * 100000000)

    def place_offer(self, chosen_est_price, timeout, config):
        """
        Sell all available MB for the chosen estimated price on the Tribler market.
        :param config: config
        :param timeout: timeout of the offer to place
        :param chosen_est_price: Target amount of BTC to receive
        :return: success of offer placement
        """
        available_mb = market_controller.get_balance('MB')
        if available_mb == 0:
            logger.log("No MB available", log_name)
            return False
        config.bump_offer_date()

        coin = 'TBTC' if plebnet_settings.get_instance().wallets_testnet() else 'BTC'

        config.set('last_offer', {coin: chosen_est_price, 'MB': available_mb})
        return market_controller.put_bid(first_asset_amount=self.btc_to_satoshi(chosen_est_price),
                                         first_asset_type=coin,
                                         second_asset_amount=available_mb,
                                         second_asset_type='MB',
                                         timeout=timeout)
