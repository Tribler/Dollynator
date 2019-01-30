from plebnet.controllers import wallet_controller
from plebnet.utilities import logger
from plebnet.utilities.btc import satoshi_to_btc
from strategy import Strategy

from plebnet.settings import plebnet_settings

log_name = "agent.strategies.last_day_sell"


class LastDaySell(Strategy):
    def __init__(self):
        Strategy.__init__(self)
        self.target_vps_count = int(plebnet_settings.get_instance().strategy_vps_count())

    def apply(self):
        from plebnet.agent.core import attempt_purchase
        self.sell_reputation()
        for i in range(0, self.target_vps_count):
            attempt_purchase()

    def sell_reputation(self):
        if self.config.time_to_expiration() <= plebnet_settings.TIME_IN_DAY:
            available_mb = self.get_available_mb()
            if available_mb == 0:
                logger.log("No MB available", log_name)
                return
            self.update_offer(available_mb)

    def create_offer(self, amount_mb, timeout):
        """
        Retrieve the price of the chosen server to buy and make a new offer on the Tribler marketplace.
        :param amount_mb: Amount of reputation to sell
        :param timeout: offer to
        :return: None
        """
        if not self.config.get('chosen_provider'):
            return
        wallet = wallet_controller.TriblerWallet(plebnet_settings.get_instance().wallets_testnet_created())
        (provider, option, _) = self.config.get('chosen_provider')
        btc_balance = satoshi_to_btc(wallet.get_balance())
        btc_price = max(self.get_replication_price(provider, option) * self.target_vps_count - btc_balance, 0)
        self.place_offer(amount_mb, btc_price, timeout, self.config)
