import unittest
import os
import subprocess
import plebnet.controllers.tribler_controller as Tribler
from mock.mock import MagicMock
from plebnet.utilities import logger

class TestTriblerController(unittest.TestCase):

    def test_running(self):
        self.true_os_path = os.path.isfile
        os.path.isfile = MagicMock(return_value=True)
        assert(Tribler.running())
        os.path.isfile = self.true_os_path

    def test_start(self):
        self.true_logger_log = logger.log
        self.true_logger_success = logger.success
        self.true_subprocess_call = subprocess.call

        logger.log = MagicMock()
        logger.success = MagicMock()
        subprocess.call = MagicMock(return_value=True)
        assert(Tribler.start())

        subprocess.call = self.true_subprocess_call
        logger.log = self.true_logger_log
        logger.success = self.true_logger_success

    def test_start_False(self):
        self.true_subprocess_call = subprocess.call
        self.true_logger_error = logger.error

        subprocess.call = MagicMock(return_value=False)
        logger.error = MagicMock()
        self.assertFalse(Tribler.start())

        subprocess.call = self.true_subprocess_call
        logger.error = self.true_logger_error

    def test_start_exception(self):
        self.true_subprocess_call = subprocess.call
        self.true_logger_error = logger.error

        subprocess.call = MagicMock(side_effect=subprocess.CalledProcessError(returncode=2,cmd=['bad']))
        logger.error = MagicMock()
        self.assertFalse(Tribler.start())

        logger.error = self.true_logger_error
        subprocess.call = self.true_subprocess_call

    if __name__ == '__main__':
        unittest.main()