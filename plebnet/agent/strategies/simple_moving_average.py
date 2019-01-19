import json
import os

from appdirs import user_config_dir

from plebnet.agent.strategies.last_day_sell import LastDaySell
from plebnet.controllers import market_controller
from plebnet.utilities import logger
from plebnet.utilities.btc import satoshi_to_btc
from strategy import Strategy
from datetime import datetime, timedelta
from math import sqrt


MAX_ACCUMULATION_TIME = 3*24*60
ITERATION_TIME_DIFF = 5
log_name = "agent.strategies.simple_moving_average"


class SimpleMovingAverage(Strategy):
    """
    Strategy explanation: https://github.com/Tribler/PlebNet/issues/44#issuecomment-446222944
    """
    def __init__(self):
        Strategy.__init__(self)
        self.time_accumulated = 0
        self.bid = None
        self.time_change = 0
        self.transactions = market_controller.transactions()
        self.read_last_iteration_info()

    def read_last_iteration_info(self):
        config_dir = user_config_dir()
        filename = os.path.join(config_dir, 'simple_moving_average.json')
        if os.path.exists(filename):
            with open(filename, 'r') as json_file:
                data = json.load(json_file)
                self.time_accumulated = data['time_accumulated']
                self.process_last_bid(data['bid'], data['time_change'])

    def process_last_bid(self, bid, bid_time):
        if bid is None:
            return

        fulfilled_part = 0.0
        for transaction in self.transactions:
            if transaction['trader_id'] == bid['trader_id'] and \
               transaction['order_number'] == bid['order_number']:
                if transaction['transferred']['second']['amount'] > 0:
                    fulfilled_part = float(transaction['transferred']['second']['amount']) / \
                                     transaction['assets']['second']['amount']

        self.time_accumulated += int(bid_time*(1.0-fulfilled_part))

    def write_iteration_info(self):
        config_dir = user_config_dir()
        filename = os.path.join(config_dir, 'simple_moving_average.json')

        with open(filename, 'w') as json_file:
            json.dump({
                'time_accumulated': self.time_accumulated,
                'time_change': self.time_change,
                'bid': self.bid
            }, json_file)

    def apply(self):
        """
        If there are no transaction history the strategy is useless so it defaults to LastDaySell
        :return:
        """
        if len(self.transactions) == 0:  # Fallback to last_day_sell if can't apply strategy
            logger.log("No transactions saved. Defaulting to Last Day Sell strategy", log_name)
            return LastDaySell().apply()
        self.time_accumulated += ITERATION_TIME_DIFF
        self.bid = self.sell_reputation()
        self.write_iteration_info()
        from plebnet.agent.core import attempt_purchase
        attempt_purchase()

    def get_closing_transactions(self):
        """
        Gets the closing (last) transactions for each period (using a day as a period), max last 30 periods
        :return: dictionary with the transactions with date YYYY-MM-DD as key
        """
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
        """
        Given a transaction on the market, calculates its price BTC/MB
        :param transaction: Transaction to get price
        :return: price in BTC/MB
        """
        return float(transaction['assets']['first']['amount'])/transaction['assets']['second']['amount']

    def calculate_moving_average_data(self):
        """
        Calculates the moving average data: mean and standard deviation from the closing transactions
        :return: moving_average (or mean) and standard_deviation
        """
        closing_transactions = self.get_closing_transactions()

        moving_average = 0.0
        for date, transaction in closing_transactions.items():
            price = self.calculate_price(transaction)
            moving_average += price
        moving_average /= len(closing_transactions)

        variance = 0.0
        for date, transaction in closing_transactions.items():
            price = self.calculate_price(transaction)
            variance += (price - moving_average)**2
        if variance != 0:
            variance /= (len(closing_transactions) - 1)
        std_deviation = sqrt(variance)

        return moving_average, std_deviation

    def get_reputation_gain_rate(self, time_unit_minutes=ITERATION_TIME_DIFF):
        """
        Calculates how much MB, in average, is produced per unit of time
        :param time_unit_minutes: Unit of time to measure - default check time, 5 minutes
        :return: average of gain of reputation
        """
        return self.get_available_mb() * time_unit_minutes / self.time_accumulated

    def update_accumulated_time(self, parts_sold):
        """
        Updates the time changed by a bid and the time accumulated, based on how many parts of MB are being sold
        A part is the basic unit for our MB sells, it is equivalent to the MB of the reputation gain rate
        :param parts_sold: number of parts to be sold on the market
        :return:
        """
        self.time_change = min(self.time_accumulated, ITERATION_TIME_DIFF*parts_sold)
        self.time_accumulated -= self.time_change

    def sell_reputation(self):
        """
        Based on the strategy, calculate if it's accumulation time or how many parts are going to be sold
        Then update the market offer selling the adequate number of MBs
        :return:
        """
        moving_average, std_deviation = self.calculate_moving_average_data()

        available_mb = self.get_available_mb()
        mb_to_sell = self.get_reputation_gain_rate()
        last_price = self.calculate_price(self.transactions[-1])
        if last_price < moving_average:
            if self.time_accumulated <= MAX_ACCUMULATION_TIME:  # Accumulation zone
                return None
            self.update_accumulated_time(1)
        else:
            if last_price >= moving_average + 5 * std_deviation:  # HUGE SPIKE - sell everything
                mb_to_sell = available_mb
                self.update_accumulated_time(self.time_accumulated)
            elif last_price >= moving_average + 3*std_deviation:  # Really Big spike - sell 3 times production rate
                mb_to_sell = min(mb_to_sell * 3, available_mb)
                self.update_accumulated_time(3)
            elif last_price >= moving_average + 2 * std_deviation:  # Big spike - sell 2 times production rate
                mb_to_sell = min(mb_to_sell * 2, available_mb)
                self.update_accumulated_time(2)
            else:
                self.update_accumulated_time(1)

        return self.update_offer(mb_to_sell, ITERATION_TIME_DIFF*60)

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
        btc_price = satoshi_to_btc(last_price * amount_mb)
        return self.place_offer(amount_mb, btc_price, timeout, self.config)
