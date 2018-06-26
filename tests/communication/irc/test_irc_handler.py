import unittest
import subprocess

from mock.mock import MagicMock
from plebnet.communication.irc import irc_handler
from plebnet.settings import plebnet_settings


#plebnet_settings.get_instance().active_logger("0")
#plebnet_settings.get_instance().active_verbose("0")
#plebnet_settings.get_instance().github_active("0")


class TestIRCbot(unittest.TestCase):

    def setUp(self):
        self.original_call = subprocess.call
        self.active_logger = plebnet_settings.Init.active_logger
        self.active_verbose = plebnet_settings.Init.active_verbose
        self.github_active = plebnet_settings.Init.github_active
        plebnet_settings.Init.active_logger = MagicMock(return_value=False)
        plebnet_settings.Init.active_verbose = MagicMock(return_value=False)
        plebnet_settings.Init.github_active = MagicMock(return_value=False)

    def tearDown(self):
        subprocess.call == self.original_call
        plebnet_settings.Init.active_logger = self.active_logger
        plebnet_settings.Init.active_verbose = self.active_verbose
        plebnet_settings.Init.github_active = self.github_active

    """ USED FOR REPLACEMENTS """

    def call_true(self, args, shell=True): return True

    def call_false(self, args, shell=True): return False

    """ THE ACTUAL TESTS """

    def test_init(self):
        subprocess.call = self.call_true
        irc_handler.init_irc_client()

    def test_succes(self):
        subprocess.call = self.call_true

        success = irc_handler.start_irc_client()
        self.assertTrue(success)

        success = irc_handler.stop_irc_client()
        self.assertTrue(success)

        success = irc_handler.restart_irc_client()
        self.assertTrue(success)

        success = irc_handler.status_irc_client()
        self.assertTrue(success)

    def test_failure(self):
        subprocess.call = self.call_false

        success = irc_handler.start_irc_client()
        self.assertFalse(success)

        success = irc_handler.stop_irc_client()
        self.assertFalse(success)

        success = irc_handler.restart_irc_client()
        self.assertFalse(success)

        # success = irc_handler.status_irc_client()
        # self.assertFalse(success)


if __name__ == '__main__':
    unittest.main()
