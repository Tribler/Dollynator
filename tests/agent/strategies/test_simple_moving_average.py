from datetime import datetime, timedelta
import time
import unittest

from unittest.mock import MagicMock
import unittest.mock as mock

from plebnet.agent import core
from plebnet.agent.strategies.last_day_sell import LastDaySell
from plebnet.agent.strategies.simple_moving_average import SimpleMovingAverage, MAX_ACCUMULATION_TIME, \
                                                            ITERATION_TIME_DIFF, MINUTES_IN_DAY
from plebnet.controllers import market_controller

from plebnet.settings import plebnet_settings


class TestSimpleMovingAverage(unittest.TestCase):

    def setUp(self):
        self.read = SimpleMovingAverage.read_last_iteration_info
        self.tra = market_controller.transactions
        SimpleMovingAverage.read_last_iteration_info = MagicMock()
        market_controller.transactions = MagicMock()
        self.strategy = SimpleMovingAverage()

        self.strategy.transactions = [
            {
                'trader_id': 1,
                'order_number': 1,
                'assets': {
                    'first': {
                        'amount': 10,
                        'type': 'BTC'
                    },
                    'second': {
                        'amount': 10,
                        'type': 'MB'
                    }
                },
                'transferred': {
                    'first': {
                        'amount': 10,
                        'type': 'BTC'
                    },
                    'second': {
                        'amount': 10,
                        'type': 'MB'
                    }
                }
            }
        ]

    def tearDown(self):
        del self.strategy
        SimpleMovingAverage.read_last_iteration_info = self.read
        market_controller.transactions = self.tra

    def test_process_last_bid_fulfilled(self):
        bid_time = 10
        initial_time = 7
        bid_size = 1.0
        self.strategy.time_accumulated = initial_time

        self.strategy.process_last_bid(self.strategy.transactions[0], bid_size, bid_time)
        self.assertEqual(self.strategy.time_accumulated, initial_time)
        self.assertEqual(self.strategy.parts_sold_today, bid_size)

        self.strategy.transactions[0]['transferred']['first']['amount'] /= 2
        self.strategy.transactions[0]['transferred']['second']['amount'] /= 2
        self.strategy.parts_sold_today = 0

        self.strategy.process_last_bid(self.strategy.transactions[0], bid_size, bid_time)
        self.assertEqual(self.strategy.time_accumulated, initial_time + bid_time/2)
        self.assertEqual(self.strategy.parts_sold_today, bid_size/2)

    def test_process_last_bid_not_fulfilled(self):
        bid_time = 10
        initial_time = 5
        bid_size = 1.0
        self.strategy.time_accumulated = initial_time
        self.strategy.process_last_bid({'trader_id': 0, 'order_number': 0}, bid_size, bid_time)
        self.assertEqual(self.strategy.time_accumulated, initial_time + bid_time)
        self.assertEqual(self.strategy.parts_sold_today, 0)

    def test_fallback_to_last_day(self):
        self.strategy.transactions = []

        LastDaySell.apply = MagicMock()
        self.strategy.apply()
        LastDaySell.apply.assert_called_once()

    @mock.patch("plebnet.agent.core.attempt_purchase")
    def test_apply(self, attempt_purchase):
        initial_time = 10
        self.strategy.time_accumulated = initial_time
        self.strategy.sell_reputation = MagicMock()
        self.strategy.write_iteration_info = MagicMock()

        self.strategy.apply()

        self.assertEqual(self.strategy.time_accumulated, initial_time + ITERATION_TIME_DIFF)
        self.strategy.sell_reputation.assert_called_once()
        self.strategy.write_iteration_info.assert_called_once()
        attempt_purchase.assert_called_once()

    def create_transaction(self, timestamp, price=1):
        return {
                'trader_id': 1,
                'order_number': 1,
                'timestamp': timestamp,
                'assets': {
                    'first': {
                        'amount': 10*price,
                        'type': 'BTC'
                    },
                    'second': {
                        'amount': 10,
                        'type': 'MB'
                    }
                },
                'transferred': {
                    'first': {
                        'amount': 10*price,
                        'type': 'BTC'
                    },
                    'second': {
                        'amount': 10,
                        'type': 'MB'
                    }
                }
            }

    def test_closing_transactions(self):
        closing_timestamps = []
        self.strategy.transactions = []
        num_days = 3
        start_date = datetime.today() - timedelta(days=num_days)
        for i in range(0, num_days):
            t1 = time.mktime((start_date.year, start_date.month, start_date.day+i, 15, 0, 0, 0, 0, -1))
            t2 = time.mktime((start_date.year, start_date.month, start_date.day+i, 20, 0, 0, 0, 0, -1))
            closing_timestamps.append(t2)
            self.strategy.transactions.append(self.create_transaction(t1))
            self.strategy.transactions.append(self.create_transaction(t2))

        closing_transactions = self.strategy.get_closing_transactions()

        self.assertEqual(len(closing_transactions), num_days)
        for closing_transaction in closing_transactions.values():
            self.assertTrue(closing_transaction['timestamp'] in closing_timestamps)

    def test_calculate_price(self):
        price = 5
        self.assertEqual(price, self.strategy.calculate_price(self.create_transaction(0, price)))

    def test_moving_average(self):
        self.strategy.get_closing_transactions = MagicMock(return_value={
            'a': self.create_transaction(time.mktime((2019, 1, 1, 15, 0, 0, 0, 0, -1)), 1),
            'b': self.create_transaction(time.mktime((2019, 1, 2, 15, 0, 0, 0, 0, -1)), 2),
            'c': self.create_transaction(time.mktime((2019, 1, 3, 15, 0, 0, 0, 0, -1)), 3)
        })

        mean, std_dev = self.strategy.calculate_moving_average_data()

        self.assertEqual(mean, 2)
        self.assertEqual(std_dev, 1)

    def test_get_reputation_gain_rate(self):
        self.strategy.get_available_mb = MagicMock(return_value=1)
        self.strategy.time_accumulated = MINUTES_IN_DAY
        self.assertEqual(self.strategy.get_reputation_gain_rate(), 1)

    def test_sell_reputation_below_mean_in_accumulation_zone(self):
        mean = 5
        std_dev = 2
        self.strategy.calculate_moving_average_data = MagicMock(return_value=(mean, std_dev))
        self.strategy.get_available_mb = MagicMock(return_value=100)
        self.strategy.get_reputation_gain_rate = MagicMock(return_value=5)
        self.strategy.calculate_price = MagicMock(return_value=2)
        self.strategy.update_accumulated_time = MagicMock()
        self.strategy.update_offer = MagicMock()
        self.strategy.time_accumulated = MAX_ACCUMULATION_TIME - 1

        self.strategy.sell_reputation()

        self.strategy.calculate_moving_average_data.assert_called_once()
        self.strategy.calculate_price.assert_called_once()
        self.strategy.update_accumulated_time.assert_not_called()
        self.strategy.get_available_mb.assert_not_called()
        self.strategy.get_reputation_gain_rate.assert_not_called()
        self.strategy.update_offer.assert_not_called()

    def test_sell_reputation_below_mean_outside_accumulation_zone(self):
        mean = 5
        std_dev = 2
        self.strategy.calculate_moving_average_data = MagicMock(return_value=(mean, std_dev))
        self.strategy.get_available_mb = MagicMock(return_value=100)
        self.strategy.get_reputation_gain_rate = MagicMock(return_value=5)
        self.strategy.calculate_price = MagicMock(return_value=2)
        self.strategy.update_accumulated_time = MagicMock()
        self.strategy.update_offer = MagicMock()
        self.strategy.time_accumulated = MAX_ACCUMULATION_TIME + 1
        self.strategy.current_hour = 23

        self.strategy.sell_reputation()

        self.strategy.calculate_moving_average_data.assert_called_once()
        self.strategy.calculate_price.assert_called_once()
        self.strategy.get_available_mb.assert_called_once()
        self.strategy.get_reputation_gain_rate.assert_called_once()
        self.strategy.update_accumulated_time.assert_called_once()
        self.strategy.update_offer.assert_called_with(self.strategy.get_reputation_gain_rate(),
                                                      ITERATION_TIME_DIFF * 60)
        self.assertEqual(self.strategy.bid_size, 1)

    def test_sell_reputation_once_above_mean(self):
        mean = 5
        std_dev = 2
        times_above_mean = 1
        self.strategy.calculate_moving_average_data = MagicMock(return_value=(mean, std_dev))
        self.strategy.get_available_mb = MagicMock(return_value=100)
        self.strategy.get_reputation_gain_rate = MagicMock(return_value=5)
        self.strategy.calculate_price = MagicMock(return_value=mean+std_dev*times_above_mean)
        self.strategy.update_accumulated_time = MagicMock()
        self.strategy.update_offer = MagicMock()
        self.strategy.time_accumulated = MAX_ACCUMULATION_TIME - 1

        self.strategy.sell_reputation()

        self.strategy.calculate_moving_average_data.assert_called_once()
        self.strategy.calculate_price.assert_called_once()
        self.strategy.get_available_mb.assert_called_once()
        self.strategy.get_reputation_gain_rate.assert_called_once()
        self.strategy.update_accumulated_time.assert_called_once()
        self.strategy.update_offer.assert_called_with(self.strategy.get_reputation_gain_rate(),
                                                      ITERATION_TIME_DIFF * 60)
        self.assertEqual(self.strategy.bid_size, times_above_mean)

    def test_sell_reputation_spike(self):
        mean = 5
        std_dev = 2
        times_above_mean = 2
        self.strategy.calculate_moving_average_data = MagicMock(return_value=(mean, std_dev))
        self.strategy.get_available_mb = MagicMock(return_value=100)
        self.strategy.get_reputation_gain_rate = MagicMock(return_value=5)
        self.strategy.calculate_price = MagicMock(return_value=mean+std_dev*times_above_mean)
        self.strategy.update_accumulated_time = MagicMock()
        self.strategy.update_offer = MagicMock()
        self.strategy.time_accumulated = MAX_ACCUMULATION_TIME - 1

        self.strategy.sell_reputation()

        self.strategy.calculate_moving_average_data.assert_called_once()
        self.strategy.calculate_price.assert_called_once()
        self.strategy.get_available_mb.assert_called_once()
        self.strategy.get_reputation_gain_rate.assert_called_once()
        self.strategy.update_accumulated_time.assert_called_once()
        self.strategy.update_offer.assert_called_with(self.strategy.get_reputation_gain_rate()*times_above_mean,
                                                      ITERATION_TIME_DIFF * 60)
        self.assertEqual(self.strategy.bid_size, times_above_mean)

    def test_sell_reputation_big_spike(self):
        mean = 5
        std_dev = 2
        times_above_mean = 3
        self.strategy.calculate_moving_average_data = MagicMock(return_value=(mean, std_dev))
        self.strategy.get_available_mb = MagicMock(return_value=100)
        self.strategy.get_reputation_gain_rate = MagicMock(return_value=5)
        self.strategy.calculate_price = MagicMock(return_value=mean+std_dev*times_above_mean)
        self.strategy.update_accumulated_time = MagicMock()
        self.strategy.update_offer = MagicMock()
        self.strategy.time_accumulated = MAX_ACCUMULATION_TIME - 1

        self.strategy.sell_reputation()

        self.strategy.calculate_moving_average_data.assert_called_once()
        self.strategy.calculate_price.assert_called_once()
        self.strategy.get_available_mb.assert_called_once()
        self.strategy.get_reputation_gain_rate.assert_called_once()
        self.strategy.update_accumulated_time.assert_called_once()
        self.strategy.update_offer.assert_called_with(self.strategy.get_reputation_gain_rate() * times_above_mean,
                                                      ITERATION_TIME_DIFF * 60)
        self.assertEqual(self.strategy.bid_size, times_above_mean)

    def test_create_offer_no_provider(self):
        amount_mb = 1
        self.strategy = SimpleMovingAverage()
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
        self.strategy.place_offer = MagicMock()
        self.strategy.config.get = MagicMock(return_value=('prov', 'opt', 'test'))

        self.strategy.create_offer(amount_mb, plebnet_settings.TIME_IN_HOUR)
        self.strategy.place_offer.assert_called_once()