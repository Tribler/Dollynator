# import unittest
#
# import irc.client
#
# from plebnet.communication import ircbot
# from plebnet.settings import setup_settings
#
#
# class TestIRCbot(unittest.TestCase):
#
#     def get_irc_channel(self): return self.settings.get("irc", "channel")
#
#     def get_irc_server(self): return self.settings.get("irc", "server")
#
#     def get_irc_port(self): return int(self.settings.get("irc", "port"))
#
#     def get_irc_nick(self): return self.settings.get("irc", "nick")
#
#     def get_irc_timeout(self): return int(self.settings.get("irc", "timeout"))
#
#     def setUp(self):
#         self.irc_settings = setup_settings.Init()
#         self.temp_server = self.irc_settings.get_irc_server()
#         self.irc_settings.set_irc_server()
#
#     def tearDown(self):
#         self.irc_settings = setup_settings.Init()
#
#
#     @unittest.mock.patch('irc.connection.socket')
#     def test_init(self):
#         DNA().add_provider("provider1")
#         self.assertEqual(DNA().vps, {'provider1': 0.5})
#
#
#
# if __name__ == '__main__':
#     unittest.main()