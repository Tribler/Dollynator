import unittest

from unittest.mock import MagicMock

from plebnet.agent import core
from plebnet.agent.strategies.constant_sell import ConstantSell

from plebnet.settings import plebnet_settings


class TestConstantSell(unittest.TestCase):

    def test_apply(self):
        self.strategy = ConstantSell()
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

    def test_sell_reputation(self):
        amount_mb = 987
        self.strategy = ConstantSell()
        self.uo = self.strategy.update_offer
        self.available = self.strategy.get_available_mb

        self.strategy.update_offer = MagicMock()
        self.strategy.get_available_mb = MagicMock(return_value=amount_mb)

        self.strategy.sell_reputation()
        self.strategy.update_offer.assert_called_once_with(amount_mb)

        self.strategy.update_offer = self.uo
        self.strategy.get_available_mb = self.available

    def test_sell_reputation_no_mb(self):
        self.strategy = ConstantSell()
        self.uo = self.strategy.update_offer
        self.available = self.strategy.get_available_mb

        self.strategy.update_offer = MagicMock()
        self.strategy.get_available_mb = MagicMock(return_value=0)

        self.strategy.sell_reputation()
        self.strategy.update_offer.assert_not_called()

        self.strategy.update_offer = self.uo
        self.strategy.get_available_mb = self.available

    def test_create_offer_no_provider(self):
        amount_mb = 1
        self.strategy = ConstantSell()
        self.po = self.strategy.place_offer
        self.grp = self.strategy.get_replication_price

        self.strategy.place_offer = MagicMock()
        self.strategy.get_replication_price = MagicMock()
        self.strategy.config.get = MagicMock(return_value=None)

        self.strategy.create_offer(amount_mb, plebnet_settings.TIME_IN_HOUR)
        self.strategy.place_offer.assert_not_called()

        self.strategy.place_offer = self.po
        self.strategy.get_replication_price = self.grp

    def test_create_offer_with_provider(self):
        amount_mb = 1
        self.strategy = ConstantSell()
        self.po = self.strategy.place_offer
        self.grp = self.strategy.get_replication_price

        self.strategy.place_offer = MagicMock()
        self.strategy.get_replication_price = MagicMock(return_value=3)
        self.strategy.config.get = MagicMock(return_value=('prov', 'opt', 'test'))

        self.strategy.create_offer(amount_mb, plebnet_settings.TIME_IN_HOUR)
        self.strategy.place_offer.assert_called_once()

        self.strategy.place_offer = self.po
        self.strategy.get_replication_price = self.grp
