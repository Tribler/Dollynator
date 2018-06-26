import unittest
import sys

# from unittest.mock import Mock
from mock.mock import Mock
from argparse import Namespace
from mock.mock import patch

from plebnet import cmdline
from plebnet.agent import core
from plebnet.communication.irc import irc_handler
from plebnet.settings import plebnet_settings

""" HELPER METHODS """


def prep(command): return command.split(" ")


class TestCMDLine(unittest.TestCase):

    """ TESTING cmdline.py """

    """ PREP METHODS """

    def setUp(self):
        self.argv = sys.argv

    def tearDown(self):
        sys.argv = self.argv



    """ THE TEST METHODS """

    def test_setup(self):
        # store originals
        self.setup = core.setup
        # modify
        core.setup = Mock()
        # sys.argv = ['plebnet', 'setup']
        sys.argv = prep('plebnet setup')
        # run
        cmdline.execute()
        # test
        core.setup.assert_called()
        core.setup.assert_called_once_with(Namespace(test_net=False))
        # restore
        core.setup = self.setup

    def test_setup_test(self):
        # store originals
        self.setup = core.setup
        # modify
        core.setup = Mock()
        sys.argv = ['plebnet', 'setup', '-testnet']
        # run
        cmdline.execute()
        # test
        core.setup.assert_called_once_with(Namespace(test_net=True))
        # restore
        core.setup = self.setup

    def test_check(self):
        # store originals
        self.check = core.check
        # modify
        core.check = Mock()
        sys.argv = ['plebnet', 'check']
        # run
        cmdline.execute()
        # test
        core.check.assert_called()
        # restore
        core.check = self.check

    def test_irc_status(self):
        self.original = irc_handler.status_irc_client
        irc_handler.status_irc_client = Mock()
        sys.argv = ['plebnet', 'irc', 'status']
        cmdline.execute()
        irc_handler.status_irc_client.assert_called()
        irc_handler.status_irc_client = self.original

    def test_conf_setup_irc(self):
        self.original_1 = plebnet_settings.Init.irc_channel
        self.original_2 = plebnet_settings.Init.irc_server
        self.original_3 = plebnet_settings.Init.irc_port
        self.original_4 = plebnet_settings.Init.irc_nick
        self.original_5 = plebnet_settings.Init.irc_nick_def
        self.original_6 = plebnet_settings.Init.irc_timeout

        plebnet_settings.Init.irc_channel = Mock()
        plebnet_settings.Init.irc_server = Mock()
        plebnet_settings.Init.irc_port = Mock()
        plebnet_settings.Init.irc_nick = Mock()
        plebnet_settings.Init.irc_nick_def = Mock()
        plebnet_settings.Init.irc_timeout = Mock()

        irc_handler.status_irc_client = Mock()
        content = ('a', 'b', 'c', 'd', 'e', 'f')
        sys.argv = prep('plebnet conf setup -ic %s -is %s -ip %s -in %s -ind %s -it %s' % content)
        cmdline.execute()

        plebnet_settings.Init.irc_channel.assert_called_with(content[0])
        plebnet_settings.Init.irc_server.assert_called_with(content[1])
        plebnet_settings.Init.irc_port.assert_called_with(content[2])
        plebnet_settings.Init.irc_nick.assert_called_with(content[3])
        plebnet_settings.Init.irc_nick_def.assert_called_with(content[4])
        plebnet_settings.Init.irc_timeout.assert_called_with(content[5])

        plebnet_settings.Init.irc_channel = self.original_1
        plebnet_settings.Init.irc_server = self.original_2
        plebnet_settings.Init.irc_port = self.original_3
        plebnet_settings.Init.irc_nick = self.original_4
        plebnet_settings.Init.irc_nick_def = self.original_5
        plebnet_settings.Init.irc_timeout = self.original_5


if __name__ == '__main__':
    unittest.main()
