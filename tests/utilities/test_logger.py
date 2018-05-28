import unittest
import mock
from appdirs import user_config_dir
import os
import sys
from plebnet.utilities import logger
from plebnet.settings import plebnet_settings

# test_file = os.path.join(user_config_dir(), 'test.log')
test_path = user_config_dir()
test_name = plebnet_settings.get_instance().get_logger_file()
test_file = os.path.join(test_path, test_name)
msg1 = "this is a log"
msg2 = "this is another log"
msg3 = "this is a nice line"
msg4 = "this is a beautiful line of text"


class TestLogger(unittest.TestCase):

    def setUp(self):
        logger.reset()
        logger.suppress_print = True
        if os.path.isfile(test_file):
            os.remove(test_file)

    def tearDown(self):
        if os.path.isfile(test_file):
            os.remove(test_file)

    @mock.patch('plebnet.settings.plebnet_settings.Init.get_logger_path', return_value=test_path)
    def test_generate_file(self, mock):
        self.assertFalse(os.path.isfile(test_file))
        logger.log(msg1)
        self.assertTrue(os.path.isfile(test_file))

    @mock.patch('plebnet.settings.plebnet_settings.Init.get_logger_path', return_value=test_path)
    def test_add_logs(self, mock):
        logger.log(msg1)
        logger.log(msg2)
        self.assertTrue(msg1 in open(test_file).read())
        self.assertTrue(msg2 in open(test_file).read())

    @mock.patch('plebnet.settings.plebnet_settings.Init.get_logger_path', return_value=test_path)
    def test_add_multiple_logs(self, mock):
        logger.log(msg1)
        logger.warning(msg2)
        logger.success(msg3)
        logger.error(msg4)

        f = open(test_file)
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
