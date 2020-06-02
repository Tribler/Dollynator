from math import sqrt

from plebnet.agent.strategies.last_day_sell import LastDaySell
from plebnet.utilities import logger
from plebnet.agent.strategies.moving_average_template import MovingAverage

MINUTES_IN_DAY = 24 * 60
MAX_ACCUMULATION_TIME = 3 * MINUTES_IN_DAY
ITERATION_TIME_DIFF = 5

number_days = 3


class SimpleMovingAverage(MovingAverage):
    """
    Strategy explanation: https://github.com/Tribler/PlebNet/issues/44#issuecomment-446222944
    """

    def __init__(self, exp=False):
        MovingAverage.__init__(self)
        self.file_name = 'simple_moving_average.json'
        self.log_name = "agent.strategies.simple_moving_average"
        self.read_last_iteration_info()
        self.exp = exp  # boolean that decides if use linear moving average or exponential one. The exp gives more
        # weight to recent values and therefore is more sensible to changes. Implemented description at following link
        # https://www.investopedia.com/terms/e/ema.asp

    def apply(self):
        """
        If there are no transaction history the strategy is useless so it defaults to LastDaySell
        :return:
        """
        if len(self.transactions) == 0:  # Fallback to last_day_sell if can't apply strategy
            logger.log("No transactions saved. Defaulting to Last Day Sell strategy", self.log_name)
            return LastDaySell().apply()
        self.time_accumulated += ITERATION_TIME_DIFF
        self.bid = self.sell_reputation()
        self.write_iteration_info()
        from plebnet.agent.core import attempt_purchase
        attempt_purchase()

    def sell_reputation(self):
        """
        Based on the strategy, calculate if it's accumulation time or how many parts are going to be sold
        Then update the market offer selling the adequate number of MBs
        :return:
        """
        if self.exp:
            moving_average, std_deviation = self.calculate_exp_moving_average_data(12)  # common value for exp average
        moving_average, std_deviation = self.calculate_moving_average_data(number_days)

        last_price = self.calculate_price(self.transactions[-1])
        if last_price < moving_average:
            # Accumulation zone. If it has been passed, wait until the last hour of the day to make a bid
            if self.time_accumulated <= MAX_ACCUMULATION_TIME or self.current_hour < 23:
                return None
            self.bid_size = 1 - self.parts_sold_today
        else:
            if last_price >= moving_average + 3 * std_deviation:  # Really Big spike - sell 3 times production rate
                self.bid_size = 3 - self.parts_sold_today
            elif last_price >= moving_average + 2 * std_deviation:  # Big spike - sell 2 times production rate
                self.bid_size = 2 - self.parts_sold_today
            else:
                self.bid_size = 1 - self.parts_sold_today

        if self.bid_size <= 0:
            return None

        mb_to_sell = min(self.get_available_mb(), self.get_reputation_gain_rate() * self.bid_size)
        self.update_accumulated_time()

        return self.update_offer(mb_to_sell, ITERATION_TIME_DIFF * 60)

    def calculate_exp_moving_average_data(self):
        """
        Calculate moving_average and std_deviation for the exponential moving average.
        """
        closing_transactions = self.get_closing_transactions(12)
        moving_average_yesterday, std_deviation_yesterday = self.calculate_moving_average_data(12)
        price_today = self.calculate_price(self.transactions[-1])
        smoothing = 2  # standard value for exp moving average

        moving_average = (price_today * (smoothing / (1 + 12))
                          + moving_average_yesterday * (1 - (smoothing / (1 + 12))))

        variance = 0.0
        for date, transaction in closing_transactions.items():
            price = self.calculate_price(transaction)
            variance += (price - moving_average) ** 2
        if variance != 0:
            variance /= (len(closing_transactions) - 1)
        std_deviation = sqrt(variance)

        return moving_average, std_deviation

