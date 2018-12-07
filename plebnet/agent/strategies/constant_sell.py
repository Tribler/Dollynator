from strategy import Strategy, BTC_FLUCTUATION_MARGIN

from plebnet.controllers import cloudomate_controller
from plebnet.settings import plebnet_settings
from plebnet.agent.core import place_offer, attempt_purchase


# TODO: THIS WAS IMPLEMENTED ASSUMING TRIBLER MARKET ORDERS ARENT PARTIALLY MATCHED.


class LastDaySell(Strategy):
    def __init__(self):
        Strategy.__init__(self)
        self.target_no_vps = int(plebnet_settings.get_instance().strategy_no_vps())

    def apply(self):
        self.sell_reputation()
        for i in range(0, self.target_no_vps):
            attempt_purchase()

    def sell_reputation(self):
        self.update_offer()

    def create_offer(self, timeout):
        """
        Retrieve the price of the chosen server to buy and make a new offer on the Tribler marketplace.
        :param timeout: offer to
        :return: None
        """
        if not self.config.get('chosen_provider'):
            return
        (provider, option, _) = self.config.get('chosen_provider')
        btc_price = cloudomate_controller.calculate_price(provider, option) * self.target_no_vps \
            * BTC_FLUCTUATION_MARGIN
        place_offer(btc_price, timeout, self.config)
