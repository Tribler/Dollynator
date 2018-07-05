import unittest

from plebnet.communication.irc import ircbot
from plebnet.settings import plebnet_settings
from mock.mock import MagicMock
from plebnet.agent import dna


line_join = "376 " + plebnet_settings.get_instance().irc_nick()
line_ping = "PING 1234"
line_host = "a b c :!host"
line_alive = "a b c :!alive"
line_error = "a b c :!error"

reply_join = "JOIN"
reply_host = "My host is : "
reply_ping = "PONG 1234"
reply_alive = "I am alive, for"
reply_error = "A error occurred in IRCbot"
reply_error_created = "Let me create an error ..."
reply_heart = "IRC is still running - alive for"


class TestIRCbot(unittest.TestCase):

    msgs = None
    #plebnet_settings.get_instance().active_logger("0")
    #plebnet_settings.get_instance().active_verbose("0")
    #plebnet_settings.get_instance().github_active("0")

    def setUp(self):
        global msgs
        # store originals
        self.original_run = ircbot.Create.run
        self.original_init_irc = ircbot.Create.init_irc
        self.active_logger = plebnet_settings.Init.active_logger
        self.active_verbose = plebnet_settings.Init.active_verbose
        self.github_active = plebnet_settings.Init.github_active
        # modify
        plebnet_settings.Init.active_logger = MagicMock(return_value=False)
        plebnet_settings.Init.active_verbose = MagicMock(return_value=False)
        plebnet_settings.Init.github_active = MagicMock(return_value=False)
        ircbot.Create.run = self.skip
        ircbot.Create.init_irc = self.skip
        # create instance with modified properties
        self.instance = ircbot.Create()
        self.instance.irc = self.irc_server()
        # empty the send messages
        msgs = []

    def tearDown(self):
        # restore originals
        ircbot.Create.send_run = self.original_run
        ircbot.Create.init_irc = self.original_init_irc
        plebnet_settings.Init.active_logger = self.active_logger
        plebnet_settings.Init.active_verbose = self.active_verbose
        plebnet_settings.Init.github_active = self.github_active

    """ USED FOR REPLACEMENTS """

    def append_msg(self, msg): msgs.append(msg)

    def skip(self): pass

    class irc_server(object):
        def __init__(self):
            pass

        def recv(self, x=None):
            return ""

        def send(self, msg):
            msgs.append(msg)

    """ THE ACTUAL TESTS """

    def test_handle_lines_ping(self):
        self.instance.handle_line(line_ping)
        self.assertIn(reply_ping, msgs[0])

    def test_keep_running(self):
        msg = "%s\r\n%s\r\n%s\r\n%s\r\n" % (line_join, line_ping, line_host, line_error)
        self.true_dna = dna.get_host

        dna.get_host = MagicMock(return_value="Linevast")
        self.instance.keep_running(str(msg))

        self.assertIn(reply_join, msgs[0])
        self.assertIn(reply_ping, msgs[1])
        self.assertIn(reply_error_created, msgs[2])
        self.assertIn(reply_error, msgs[3])
        msg = "%s\r\n" % (line_alive)
        self.instance.keep_running(str(msg))
        self.assertIn(reply_alive, msgs[4])



        dna.get_host = self.true_dna

    def test_heartbeat(self):
        self.instance.last_beat = 0
        self.instance.timeout = 1000 # large enough for no second heartbeat
        self.instance.heartbeat()
        self.assertIn(reply_heart, msgs[0])
        self.assertEqual(len(msgs), 1)
        # only send once
        self.assertNotEqual(self.instance.last_beat, 0)
        self.instance.heartbeat()
        self.assertEqual(len(msgs), 1)

    # def test_error(self):


if __name__ == '__main__':
    unittest.main()