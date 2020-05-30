import json
import os

from appdirs import user_config_dir

from plebnet.controllers import market_controller
from plebnet.settings import plebnet_settings
from plebnet.utilities.btc import satoshi_to_btc
from plebnet.agent.strategies.strategy import Strategy
from datetime import datetime, timedelta
from math import sqrt

MINUTES_IN_DAY = 24 * 60
MAX_ACCUMULATION_TIME = 3 * MINUTES_IN_DAY
ITERATION_TIME_DIFF = 5


class MovingAverage(Strategy):
    """
    Strategy explanation: https://github.com/Tribler/PlebNet/issues/44#issuecomment-446222944
    """

    def __init__(self):
        Strategy.__init__(self)
        self.time_accumulated = 0
        self.bid = None
        self.time_change = 0
        self.parts_sold_today = 0
        self.bid_size = 0
        self.current_hour = datetime.today().hour
        self.transactions = market_controller.transactions()
        self.file_name = None
        self.log_name = None

    def read_last_iteration_info(self):
        config_dir = user_config_dir()
        filename = os.path.join(config_dir, self.file_name)
        if os.path.exists(filename):
            with open(filename, 'r') as json_file:
                data = json.load(json_file)
                self.time_accumulated = data['time_accumulated']
                self.parts_sold_today = data['parts_sold_today']
                self.process_last_bid(data['bid'], data['bid_size'], data['time_change'])
                day = data['date']
                if day != datetime.today().strftime('%Y-%m-%d'):
                    self.parts_sold_today = 0

    def process_last_bid(self, bid, bid_size, bid_time):
        if bid is None:
            return

        fulfilled_part = 0.0
        for transaction in self.transactions:
            if transaction['trader_id'] == bid['trader_id'] and \
                    transaction['order_number'] == bid['order_number']:
                if transaction['transferred']['second']['amount'] > 0:
                    fulfilled_part = float(transaction['transferred']['second']['amount']) / \
                                     transaction['assets']['second']['amount']

        self.parts_sold_today += bid_size * fulfilled_part
        self.time_accumulated += int(bid_time * (1.0 - fulfilled_part))

    def write_iteration_info(self):
        config_dir = user_config_dir()
        filename = os.path.join(config_dir, 'simple_moving_average.json')

        with open(filename, 'w') as json_file:
            json.dump({
                'time_accumulated': self.time_accumulated,
                'time_change': self.time_change,
                'day': datetime.today().strftime('%Y-%m-%d'),
                'bid': self.bid,
                'bid_size': self.bid_size
            }, json_file)

    # TODO: make flexible number of days
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
            variance += (price - moving_average) ** 2
        if variance != 0:
            variance /= (len(closing_transactions) - 1)
        std_deviation = sqrt(variance)

        return moving_average, std_deviation

    def calculate_price(self, transaction):
        """
        Given a transaction on the market, calculates its price BTC/MB
        :param transaction: Transaction to get price
        :return: price in BTC/MB
        """
        if plebnet_settings.get_instance().wallets_testnet():
            result = float(transaction['assets']['second']['amount']) / transaction['assets']['first']['amount']
            return result
        return float(transaction['assets']['first']['amount']) / transaction['assets']['second']['amount']

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

    def get_reputation_gain_rate(self, time_unit_minutes=MINUTES_IN_DAY):
        """
        Calculates how much MB, in average, is produced per unit of time
        :param time_unit_minutes: Unit of time to measure - default check time, 5 minutes
        :return: average of gain of reputation
        """
        return self.get_available_mb() * time_unit_minutes / self.time_accumulated

    def update_accumulated_time(self):
        """
        Updates the time changed by a bid and the time accumulated, based on how many parts of MB are being sold
        A part is the basic unit for our MB sells, it is equivalent to the MB of the reputation gain rate
        :param
        :return:
        """
        self.time_change = min(self.time_accumulated, MINUTES_IN_DAY * self.bid_size)
        self.time_accumulated -= self.time_change

    def create_offer(self, amount_mb, timeout):
        """
        Retrieve the price of the chosen server to buy and make a new offer on the Tribler marketplace.
        :param amount_mb: amount of mb to sell.
        :param timeout: timeout for the offer
        :return: None
        """
        if not self.config.get('chosen_provider'):
            return
        (provider, option, _) = self.config.get('chosen_provider')
        last_price = self.calculate_price(self.transactions[-1])
        btc_price = satoshi_to_btc(last_price * amount_mb)
        return self.place_offer(amount_mb, btc_price, timeout, self.config)

    def apply(self):
        pass

    def sell_reputation(self):
        pass
