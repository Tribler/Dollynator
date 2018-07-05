import unittest
import subprocess
import responses
import requests
import plebnet.controllers.tribler_controller as Tribler
from mock.mock import MagicMock
from plebnet.utilities import logger
import plebnet.settings.plebnet_settings as Settings


class TestTriblerController(unittest.TestCase):

    def test_start(self):
        self.true_logger_log = logger.log
        self.true_logger_success = logger.success
        self.true_subprocess_call = subprocess.call
        self.true_setup = Settings.Init.wallets_testnet

        logger.log = MagicMock()
        logger.success = MagicMock()
        Settings.Init.wallets_testnet = MagicMock(return_value=True)
        subprocess.call = MagicMock(return_value=0)
        assert(Tribler.start())

        Settings.Init.wallets_testnet = self.true_setup
        subprocess.call = self.true_subprocess_call
        logger.log = self.true_logger_log
        logger.success = self.true_logger_success

    def test_start_False(self):
        self.true_subprocess_call = subprocess.call
        self.true_logger_error = logger.error
        self.true_setup = Settings.Init.wallets_testnet

        subprocess.call = MagicMock(return_value=1)
        Settings.Init.wallets_testnet = MagicMock(return_value=False)
        logger.error = MagicMock()
        self.assertFalse(Tribler.start())

        subprocess.call = self.true_subprocess_call
        logger.error = self.true_logger_error
        Settings.Init.wallets_testnet = self.true_setup


    def test_start_exception(self):
        self.true_subprocess_call = subprocess.call
        self.true_logger_error = logger.error
        self.true_setup = Settings.Init.wallets_testnet

        subprocess.call = MagicMock(side_effect=subprocess.CalledProcessError(returncode=2, cmd=['bad']))
        Settings.Init.wallets_testnet = MagicMock(return_value=True)
        logger.error = MagicMock()
        self.assertFalse(Tribler.start())

        logger.error = self.true_logger_error
        subprocess.call = self.true_subprocess_call
        Settings.Init.wallets_testnet = self.true_setup

    @responses.activate
    def test_get_uploaded(self):
        responses.add(responses.GET, 'http://localhost:8085/trustchain/statistics',
                      json={'statistics': {'total_up': 400}})
        self.assertEquals(Tribler.get_uploaded(), 0.0003814697265625)

    def test_get_uploaded_error(self):
        self.requests = requests.get
        requests.get = MagicMock(side_effect=requests.ConnectionError)
        self.assertEquals(Tribler.get_uploaded(), "Unable to retrieve amount of uploaded data")
        requests.get = self.requests

    @responses.activate
    def test_get_downloaded(self):
        responses.add(responses.GET, 'http://localhost:8085/trustchain/statistics',
                      json={'statistics': {'total_down': 400}})
        self.assertEquals(Tribler.get_downloaded(), 0.0003814697265625)

    def test_get_downloaded_error(self):
        self.requests = requests.get
        requests.get = MagicMock(side_effect=requests.ConnectionError)
        self.assertEquals(Tribler.get_downloaded(), "Unable to retrieve amount of downloaded data")
        requests.get = self.requests

    @responses.activate
    def test_get_helped_by(self):
        responses.add(responses.GET, 'http://localhost:8085/trustchain/statistics',
                      json={'statistics': {'peers_that_helped_pk': 400}})
        self.assertEquals(Tribler.get_helped_by(), 400)

    def test_get_helped_by_error(self):
        self.requests = requests.get
        requests.get = MagicMock(side_effect=requests.ConnectionError)
        self.assertEquals(Tribler.get_helped_by(), "Unable to retrieve amount of peers that helped this agent")
        requests.get = self.requests

    @responses.activate
    def test_get_helped(self):
        responses.add(responses.GET, 'http://localhost:8085/trustchain/statistics',
                      json={'statistics': {'peers_that_pk_helped': 400}})
        self.assertEquals(Tribler.get_helped(), 400)

    def test_get_helped_error(self):
        self.requests = requests.get
        requests.get = MagicMock(side_effect=requests.ConnectionError)
        self.assertEquals(Tribler.get_helped(), "Unable to retrieve amount of peers helped by this agent")
        requests.get = self.requests


if __name__ == '__main__':
    unittest.main()