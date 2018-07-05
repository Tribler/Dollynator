import unittest
import responses
import plebnet.controllers.market_controller as Market
import requests
from mock.mock import MagicMock
from plebnet.utilities import logger


class TestMarketController(unittest.TestCase):

 @responses.activate
 def test_market_running_true(self):
    responses.add(responses.HEAD, 'http://localhost:8085/market/asks', status=200)
    responses.add(responses.HEAD, 'http://localhost:8085/market/bids', status=200)
    assert(Market.is_market_running())

 @responses.activate
 def test_market_running_false(self):
    responses.add(responses.HEAD, 'http://localhost:8085/market/asks', status=200)
    responses.add(responses.HEAD, 'http://localhost:8085/market/bids', status=400)
    self.assertFalse(Market.is_market_running())

 def test_market_running_error(self):
    self.assertFalse(Market.is_market_running())

 @responses.activate
 def test_get_asks(self):
    responses.add(responses.GET, 'http://localhost:8085/market/asks', json={'asks': [{'test': 'true'}]})
    self.assertEqual(Market.asks(), [{'test': 'true'}])

 @responses.activate
 def test_get_bids(self):
     responses.add(responses.GET, 'http://localhost:8085/market/bids', json={'bids': [{'test': 'true'}]})
     self.assertEqual(Market.bids(), [{'test': 'true'}])

 @responses.activate
 def test_get_balance(self):
    self.true_logger = logger.log
    logger.log = MagicMock(return_value='Test')
    responses.add(responses.GET, 'http://localhost:8085/wallets/MB/balance',
              json={'balance': {'available': 0.02, 'pending': 0.0, 'currency': 'MB'}})
    r = Market.get_balance('MB')
    self.assertEqual(r, 0.02)
    logger.log = self.true_logger

 def test_get_balance_no_connection(self):
     self.true_logger = logger.log
     self.true_requests = requests.get

     logger.log = MagicMock(return_value='Test')
     requests.get = MagicMock(side_effect=requests.ConnectionError)
     self.assertFalse(Market.get_balance('MB'))
     logger.log = self.true_logger
     requests.get = self.true_requests

 def test_put_ask(self):
     self.true_put = Market._put_request
     Market._put_request = MagicMock(return_value=True)
     assert(Market.put_ask(10, 'MB', 10, 'BTC', 100))
     Market._put_request = self.true_put

 def test_put_bid(self):
     self.true_put = Market._put_request
     Market._put_request = MagicMock(return_value=True)
     assert(Market.put_bid(10, 'MB', 10, 'BTC', 100))
     Market._put_request = self.true_put

 @responses.activate
 def test_put_request(self):
     responses.add(responses.PUT, 'http://localhost:8085/market/bids', json={'created': True})
     assert(Market._put_request(10, 'MB', 10, 'BTC', 1000, 'bids'))

 @responses.activate
 def test_put_request_False(self):
     responses.add(responses.PUT, 'http://localhost:8085/market/bids', json={'error': {'message': 'test'}})
     self.assertFalse(Market._put_request(10, 'MB', 10, 'BTC', 1000, 'bids'))

 @responses.activate
 def test_matchmakers(self):
     responses.add(responses.GET, 'http://localhost:8085/market/matchmakers',
                   json={'matchmakers': ['test1', 'test2', 'test3']})
     self.assertEqual(Market.match_makers(), 3)

 def test_matchmakers_error(self):
     self.requests = requests.get
     requests.get = MagicMock(side_effect=requests.ConnectionError)
     self.assertEquals(Market.match_makers(), "Unable to retrieve amount of ")
     requests.get = self.requests

 @responses.activate
 def test_has_matchmakers(self):
     responses.add(responses.GET, 'http://localhost:8085/market/matchmakers',
                   json={'matchmakers': ['test1', 'test2', 'test3']})
     assert Market.has_matchmakers()


if __name__ == '__main__':
    unittest.main()