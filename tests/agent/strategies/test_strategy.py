import unittest

from mock.mock import MagicMock

from plebnet.agent.config import PlebNetConfig
import plebnet.controllers.market_controller as market

from plebnet.agent.strategies.strategy import Strategy
from plebnet.settings import plebnet_settings
from plebnet.utilities import logger as Logger


class TestStrategy(unittest.TestCase):

    class StrategyWrapper(Strategy):

        def apply(self):
            pass

        def sell_reputation(self):
            pass

        def create_offer(self, timeout):
            pass

    def test_update_offer(self):
        timeout = plebnet_settings.TIME_IN_DAY
        self.strategy = self.StrategyWrapper()
        self.create_offer = self.strategy.create_offer
        self.strategy.create_offer = MagicMock()

        self.strategy.config.time_since_offer = MagicMock(return_value=timeout-1)
        self.strategy.update_offer(timeout)
        self.strategy.create_offer.assert_not_called()

        self.strategy.config.time_since_offer = MagicMock(return_value=timeout+1)
        self.strategy.update_offer(timeout)
        self.strategy.create_offer.assert_called_once()

        self.strategy.create_offer = self.create_offer

    def test_place_offer_zero_mb(self):
        self.strategy = self.StrategyWrapper()
        self.mb = market.get_balance
        self.logger = Logger.log

        Logger.log = MagicMock()
        market.get_balance = MagicMock(return_value=0)
        self.assertFalse(self.strategy.place_offer(5, plebnet_settings.TIME_IN_HOUR, PlebNetConfig()))

        market.get_balance = self.mb
        Logger.log = self.logger

    def test_place_offer(self):
        self.strategy = self.StrategyWrapper()
        self.mb = market.get_balance
        self.logger = Logger.log
        self.put = market.put_bid
        self.true_settings = plebnet_settings.Init.wallets_testnet

        Logger.log = MagicMock()
        market.get_balance = MagicMock(return_value=56)
        market.put_bid = MagicMock()
        plebnet_settings.Init.wallets_testnet = MagicMock(return_value=False)

        self.strategy.place_offer(5, plebnet_settings.TIME_IN_HOUR, PlebNetConfig())
        market.put_bid.assert_called_once()

        market.get_balance = self.mb
        Logger.log = self.logger
        market.put_bid = self.put
