from plebnet.agent.strategies.last_day_sell import LastDaySell

from plebnet.agent.strategies.moving_average_template import MovingAverage
from plebnet.utilities import logger

short_term = 3
long_term = 10
MINUTES_IN_DAY = 24 * 60
MAX_ACCUMULATION_TIME = 3 * MINUTES_IN_DAY
ITERATION_TIME_DIFF = 5


class CrossoversMovingAverages(MovingAverage):
    """
    strategy explanation https://www.investopedia.com/articles/active-trading/052014/how-use-moving-average-buy-stocks.asp
    In short: takes 2 moving averages, one on the short and one on the long term, and in base of the crossover it
    identifies shifting up and shifting down trends in the market.
    """

    def __init__(self):
        MovingAverage.__init__(self)
        self.log_name = "agent.strategies.crossovers_moving_averages"
        self.file_name = 'crossovers_moving_averages.json'
        self.read_last_iteration_info()

    def apply(self):
        """
        If there are no transaction history the strategy is useless so it defaults to LastDaySell
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
        moving_average_short, std_average_short = self.calculate_moving_average_data(short_term)
        moving_average_long, std_average_long = self.calculate_moving_average_data(long_term)

        if moving_average_short >= moving_average_long:
            # golden cross: indication of a growth in the market. Wait to sell.
            if self.time_accumulated <= MAX_ACCUMULATION_TIME:
                return None
            self.bid_size = 1 - self.parts_sold_today
        else:  # death cross: market is shifting down. sell now.
            if moving_average_short < moving_average_long - 3 * std_average_long:
                # the trend is downwards but still close to average, sell more parts to avoid losing money in next sell
                self.bid_size = 3 - self.parts_sold_today
            if moving_average_short < moving_average_long - 2 * std_average_long:
                self.bid_size = 3 - self.parts_sold_today
            else:
                # price is not convenient, sell only one part.
                self.bid_size = 1 - self.parts_sold_today

        if self.bid_size <= 0:
            return None

        mb_to_sell = min(self.get_available_mb(), self.get_reputation_gain_rate() * self.bid_size)
        self.update_accumulated_time()

        return self.update_offer(mb_to_sell, ITERATION_TIME_DIFF * 60)
