import unittest
import mock
from mock.mock import MagicMock
from appdirs import user_config_dir
import os
import sys
from plebnet.utilities import logger
from plebnet.settings import plebnet_settings

logfile = plebnet_settings.get_instance().logger_file()

msg1 = "this is a log"
msg2 = "this is another log"
msg3 = "this is a nice line"
msg4 = "this is a beautiful line of text"


class TestLogger(unittest.TestCase):

    def setUp(self):
        # logger.reset()
        logger.suppress_print = True
        if os.path.isfile(logfile):
            print(logfile)
            os.remove(logfile)
        #ensure logging is allowed
        plebnet_settings.get_instance().active_logger("1")

    def tearDown(self):
        if os.path.isfile(logfile):
            os.remove(logfile)
        # disable logging for further tests
        plebnet_settings.get_instance().active_logger("0")

    def test_generate_file(self):
        self.assertFalse(os.path.isfile(logfile))
        logger.log(msg1)
        self.assertTrue(os.path.isfile(logfile))

    def test_add_logs(self):
        logger.log(msg1)
        logger.log(msg2)
        self.assertTrue(msg1 in open(logfile).read())
        self.assertTrue(msg2 in open(logfile).read())

    def test_add_multiple_logs(self):
        logger.log(msg1)
        logger.warning(msg2)
        logger.success(msg3)
        logger.error(msg4)

        f = open(logfile)
        for line in f:
            if msg1 in line:
                self.assertTrue("INFO" in line)
            if msg2 in line:
                self.assertTrue("WARNING" in line)
            if msg3 in line:
                self.assertTrue("INFO" in line)
            if msg4 in line:
                self.assertTrue("ERROR" in line)


if __name__ == '__main__':
    unittest.main()
