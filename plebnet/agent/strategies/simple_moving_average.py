import json
import os

from appdirs import user_config_dir

from plebnet.agent.strategies.last_day_sell import LastDaySell
from plebnet.controllers import market_controller
from strategy import Strategy
from datetime import datetime, timedelta
from math import sqrt


MAX_ACCUMULATION_TIME = 3*24*60
ITERATION_TIME_DIFF = 5


class SimpleMovingAverage(Strategy):
    def __init__(self):
        Strategy.__init__(self)
        self.time_accumulated = 0
        self.transactions = []

    def read_last_iteration_info(self):
        config_dir = user_config_dir()
        filename = os.path.join(config_dir, 'simple_moving_average.json')
        if os.path.exists(filename):
            with open(filename, 'r') as json_file:
                data = json.load(json_file)
                self.time_accumulated = data['time_accumulated']

    def write_iteration_info(self):
        config_dir = user_config_dir()
        filename = os.path.join(config_dir, 'simple_moving_average.json')

        with open(filename, 'w') as json_file:
            json.dump({
                'time_accumulated': self.time_accumulated,
            }, json_file)

    def apply(self):
        self.transactions = market_controller.transactions()
        if len(self.transactions) == 0:  # Fallback to last_day_sell if can't apply strategy
            return LastDaySell().apply()
        self.time_accumulated += ITERATION_TIME_DIFF
        from plebnet.agent.core import attempt_purchase
        self.sell_reputation()
        self.write_iteration_info()
        attempt_purchase()

    def get_closing_transactions(self):
        closing_transactions = {}

        for transaction in self.transactions:
            date = datetime.fromtimestamp(transaction['timestamp'])
            date_str = date.strftime('%Y-%m-%d')
            if date_str in closing_transactions:
                existing_date = datetime.fromtimestamp(closing_transactions[date_str]['timestamp'])
                if date > existing_date:
                    closing_transactions[date_str] = transaction
            else:
                today = datetime.today().date()
                thirty_days_ago = (datetime.today() - timedelta(days=30)).date()
                if today > date.date() > thirty_days_ago:
                    closing_transactions[date_str] = transaction

        return closing_transactions

    def calculate_price(self, transaction):
        return float(transaction['assets']['first']['amount'])/transaction['assets']['second']['amount']

    def calculate_moving_average_data(self):
        closing_transactions = self.get_closing_transactions()

        moving_average = 0.0
        for date, transaction in closing_transactions.items():
            price = self.calculate_price(transaction)
            moving_average += price / len(closing_transactions)

        variance = 0.0
        for date, transaction in closing_transactions.items():
            price = self.calculate_price(transaction)
            variance += (price - moving_average)**2 / len(closing_transactions)
        std_deviation = sqrt(variance)

        return moving_average, std_deviation

    def get_reputation_gain_rate(self, time_unit_minutes=ITERATION_TIME_DIFF):
        return self.get_available_mb()/self.time_accumulated * time_unit_minutes

    def sell_reputation(self):
        moving_average, std_deviation = self.calculate_moving_average_data()

        available_mb = self.get_available_mb()
        mb_to_sell = self.get_reputation_gain_rate()
        last_price = self.calculate_price(self.transactions[-1])
        if last_price < moving_average:
            if self.time_accumulated <= MAX_ACCUMULATION_TIME:  # Accumulation zone
                return
            self.time_accumulated = max(self.time_accumulated - ITERATION_TIME_DIFF, 0)
        else:
            if last_price >= moving_average + 5 * std_deviation:  # HUGE SPIKE - sell everything
                mb_to_sell = available_mb
                self.time_accumulated = 0
            elif last_price >= moving_average + 3*std_deviation:  # Really Big spike - sell 3 times production rate
                mb_to_sell = min(self.get_reputation_gain_rate() * 3, available_mb)
                self.time_accumulated = max(self.time_accumulated - ITERATION_TIME_DIFF * 3, 0)
            elif last_price >= moving_average + 2 * std_deviation:  # Big spike - sell 2 times production rate
                mb_to_sell = min(self.get_reputation_gain_rate() * 2, available_mb)
                self.time_accumulated = max(self.time_accumulated - ITERATION_TIME_DIFF * 2, 0)
            else:
                self.time_accumulated = max(self.time_accumulated - ITERATION_TIME_DIFF, 0)

        self.update_offer(mb_to_sell, ITERATION_TIME_DIFF*60)

    def create_offer(self, amount_mb, timeout):
        """
        Retrieve the price of the chosen server to buy and make a new offer on the Tribler marketplace.
        :param amount_mb:
        :param timeout: offer to
        :return: None
        """
        if not self.config.get('chosen_provider'):
            return
        (provider, option, _) = self.config.get('chosen_provider')
        last_price = self.calculate_price(self.transactions[-1])
        btc_price = int(last_price * amount_mb)
        self.place_offer(amount_mb, btc_price, timeout, self.config)
