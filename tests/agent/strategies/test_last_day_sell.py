import unittest

from mock.mock import MagicMock

from plebnet.agent import core
from plebnet.agent.strategies.last_day_sell import LastDaySell

from plebnet.settings import plebnet_settings


class TestLastDaySell(unittest.TestCase):

    def test_apply(self):
        self.strategy = LastDaySell()
        self.strategy.target_vps_count = 3
        self.sr = self.strategy.sell_reputation
        self.ap = core.attempt_purchase

        self.strategy.sell_reputation = MagicMock()
        core.attempt_purchase = MagicMock()

        self.strategy.apply()

        self.strategy.sell_reputation.assert_called_once()
        self.assertTrue(core.attempt_purchase.call_count == self.strategy.target_vps_count)

        self.strategy.sell_reputation = self.sr
        core.attempt_purchase = self.ap

    def test_sell_reputation_before_last_day(self):
        self.strategy = LastDaySell()
        self.uo = self.strategy.update_offer

        self.strategy.config.time_to_expiration = MagicMock(return_value=plebnet_settings.TIME_IN_DAY + 1)
        self.strategy.update_offer = MagicMock()

        self.strategy.sell_reputation()
        self.strategy.update_offer.assert_not_called()

        self.strategy.update_offer = self.uo

    def test_sell_reputation_on_last_day(self):
        self.strategy = LastDaySell()
        self.uo = self.strategy.update_offer

        self.strategy.config.time_to_expiration = MagicMock(return_value=plebnet_settings.TIME_IN_DAY - 1)
        self.strategy.update_offer = MagicMock()

        self.strategy.sell_reputation()
        self.strategy.update_offer.assert_called_once()

        self.strategy.update_offer = self.uo

    def test_create_offer_no_provider(self):
        self.strategy = LastDaySell()
        self.po = self.strategy.place_offer
        self.grp = self.strategy.get_replication_price

        self.strategy.place_offer = MagicMock()
        self.strategy.get_replication_price = MagicMock()
        self.strategy.config.get = MagicMock(return_value=None)

        self.strategy.create_offer(plebnet_settings.TIME_IN_HOUR)
        self.strategy.place_offer.assert_not_called()

        self.strategy.place_offer = self.po
        self.strategy.get_replication_price = self.grp

    def test_create_offer_with_provider(self):
        self.strategy = LastDaySell()
        self.po = self.strategy.place_offer
        self.grp = self.strategy.get_replication_price

        self.strategy.place_offer = MagicMock()
        self.strategy.get_replication_price = MagicMock(return_value=3)
        self.strategy.config.get = MagicMock(return_value=('prov', 'opt', 'test'))

        self.strategy.create_offer(plebnet_settings.TIME_IN_HOUR)
        self.strategy.place_offer.assert_called_once()

        self.strategy.place_offer = self.po
        self.strategy.get_replication_price = self.grp
