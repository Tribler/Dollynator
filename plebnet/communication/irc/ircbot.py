#! /usr/bin/env python3

"""
This file is used to setup and maintain a connection with an IRC server.
"""

import traceback
import socket
import random
import time
import sys

# as the file is loaded separately, the imports have to be adjusted.

sys.path.append('./PlebNet')
from plebnet.agent.qtable import QTable
from plebnet.agent.core import vpn_is_running
from plebnet.communication import git_issuer
from plebnet.controllers import wallet_controller, market_controller, tribler_controller
from plebnet.utilities import logger
from plebnet.settings import plebnet_settings


class Create(object):
    """
    The object which maintains the server connection
    """
    def __init__(self):
        logger.log("preparing an IRC connection")

        # load required settings once
        settings = plebnet_settings.get_instance()
        self.server = settings.irc_server()
        self.timeout = settings.irc_timeout()
        self.channel = settings.irc_channel()
        self.port = settings.irc_port()

        self.nick = settings.irc_nick()
        nick_number = self.nick[len(settings.irc_nick_def()):]
        self.ident = "plebber"
        self.gecos = "Plebbot version 2.15"

        self.irc = None
        self.init_time = time.time()
        self.last_beat = time.time()

        # prep reply functions
        self.responses = {}
        self.add_response("alive",                      self.msg_alive)
        self.add_response("error",                      self.msg_error)
        self.add_response("init",                       self.msg_init)
        self.add_response("joke",                       self.msg_joke)
        self.add_response("MB_wallet",                  self.msg_MB_wallet)
        self.add_response("BTC_wallet",                 self.msg_BTC_wallet)
        self.add_response("TBTC_wallet",                self.msg_TBTC_wallet)
        self.add_response("MB_balance",                 self.msg_MB_balance)
        self.add_response("BTC_balance",                self.msg_BTC_balance)
        self.add_response("TBTC_balance",               self.msg_TBTC_balance)
        self.add_response("matchmakers",                self.msg_match_makers)
        self.add_response("uploaded",                   self.msg_uploaded)
        self.add_response("downloaded",                 self.msg_downloaded)
        self.add_response("general",                    self.msg_general)
        self.add_response("helped",                     self.msg_helped)
        self.add_response("helped_by",                  self.msg_helped_by)
        self.add_response("qtables" + str(nick_number), self.msg_qtable)

        # start running the IRC server
        self.init_irc()
        self.run()

    def add_response(self, command, response):
        """
        This method is used to add new commands to the IRC-bot.
        :param command: the command (after !) which should trigger the provided method
        :type command: String
        :param response: The method to call as the command is received
        :type response: a method
        """
        self.responses[":!" + command] = response

    def init_irc(self):
        try:
            logger.log("start running an IRC connection on " + self.server + " " + self.channel)
            self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.irc.connect((self.server, self.port))
        except:
            title = "A error occurred in IRCbot init_irc %s" % sys.exc_info()[0]
            body = traceback.format_exc()
            logger.error(title)
            logger.error(body)
            git_issuer.handle_error(title, body)
            git_issuer.handle_error("A error occurred in IRCbot", sys.exc_info()[0], ['crash'])

    def run(self):
        """
        This method keeps listening to the server for incoming messages and processes them.
        """
        self.send("NICK %s" % self.nick)
        self.send("USER %s %s %s : %s" % (self.nick, self.nick, self.nick, self.gecos))
        self.heartbeat()

        buffer = ""
        while True:
            buffer = self.keep_running(buffer)

    def keep_running(self, buffer):
        try:
            buffer += self.irc.recv(2048).decode()
            lines = str.split(buffer, "\r\n")
            buffer = lines.pop()

            for line in lines:
                logger.log("Received IRC message: " + line)

            for line in lines:
                self.handle_line(line)

        except KeyboardInterrupt:
            st = "QUIT :I have to go for now!"
            self.irc.send(st)
            raise
        except:
            title = "A error occurred in IRCbot %s" % sys.exc_info()[0]
            body = traceback.format_exc()
            logger.error(title)
            logger.error(body)
            git_issuer.handle_error(title, body)
            self.send_msg(title)

        return buffer

    def heartbeat(self):
        """
        This method sends a heartbeat to the IRC server when it is called.

        """
        timer = time.time()
        elapsed_time = timer - self.last_beat

        if elapsed_time > self.timeout:
            self.last_beat = timer
            time_str = time.strftime("%H:%M:%S", time.gmtime(timer - self.init_time))
            logger.log("IRC is still running - alive for " + time_str)
            self.send_msg("IRC is still running - alive for %s" % time_str)

    def handle_line(self, line):
        """
        This method handles a line received from the IRC server.
        :param line: The line to process
        :type line: String
        """

        line = str.rstrip(line)
        words = str.split(line)

        # playing ping-pong with a key (words[1])
        if words[0] == "PING":
            st = "PONG %s" % words[1]
            self.send(st)

        # server status 433 --> nickname is already in use, so we chose a new one
        elif line.find("433 * " + self.nick) != -1:
            settings = plebnet_settings.get_instance()
            settings.irc_nick(settings.irc_nick_def() + str(random.randint(1000, 10000)))
            self.nick = settings.irc_nick()

            self.send("NICK %s" % self.nick)
            self.send("USER %s %s %s : %s" % (self.nick, self.nick, self.nick, self.gecos))

        # server status 376 and 422 means ready to join a channel
        elif line.find("376 " + self.nick) != -1 or line.find("422 " + self.nick) != -1:
            st = "JOIN " + self.channel
            self.send(st)

        # handle incoming messages
        elif len(words) > 3 and words[3] in self.responses:
            self.responses[words[3]]()

    """
    THE SENDER METHODS
    These handle the outgoing messages
    """
    def send(self, msg):
        logger.log("Sending  IRC message: %s" % msg)
        msg2 = "%s\r\n" % msg
        self.irc.send(msg2.encode())

    def send_msg(self, msg):
        self.send("PRIVMSG %s :%s" % (self.channel,  msg))

    """
    THE RESPONSES (don't forget to add them to the self.responses in the init method)
    These methods are used to determine the response to received commands
    """
    def msg_alive(self):
        time_str = time.strftime("%j days + %H:%M:%S", time.gmtime(time.time() - self.init_time))
        self.send_msg("I am alive, for %s" % time_str)

    def msg_error(self):
        self.send_msg("Let me create an error ...")
        raise Exception('This is an error for testing purposes')


    def msg_init(self):         self.send_msg("My init date is: %s" % plebnet_settings.get_instance().vps_life())

    def msg_joke(self):         self.send_msg("Q: Why did the hipster burn his tongue? A: He ate the pizza before it was cool.")

    def msg_MB_wallet(self):    self.send_msg("My MB wallet is: %s" % wallet_controller.get_MB_wallet())

    def msg_BTC_wallet(self):   self.send_msg("My BTC wallet is: %s" % wallet_controller.get_BTC_wallet())

    def msg_TBTC_wallet(self):  self.send_msg("My TBTC wallet is: %s" % wallet_controller.get_TBTC_wallet())

    def msg_MB_balance(self):   self.send_msg("My MB balance is: %s" % wallet_controller.get_MB_balance())

    def msg_BTC_balance(self):  self.send_msg("My BTC balance is:  %s" % wallet_controller.get_BTC_balance())

    def msg_TBTC_balance(self): self.send_msg("My TBTC balance is: %s" % wallet_controller.get_TBTC_balance())

    def msg_match_makers(self): self.send_msg("I currently have: %s matchmakers" % market_controller.match_makers())

    def msg_uploaded(self):     self.send_msg("I currently have uploaded: %s MB" % tribler_controller.get_uploaded())

    def msg_downloaded(self):   self.send_msg("I currently have downloaded: %s MB" % tribler_controller.get_downloaded())

    def msg_helped(self):       self.send_msg("I currently have helped: %s peers" % tribler_controller.get_helped())

    def msg_helped_by(self):    self.send_msg("I am currently helped by: %s peers" % tribler_controller.get_helped_by())

    def msg_general(self):
        qtable = QTable()
        qtable.read_dictionary()
        data = {
            'host': qtable.self_state.provider,
            'option': qtable.self_state.option,
            'vpn': vpn_is_running(),
            'tree': qtable.tree,
            'exitnode': plebnet_settings.get_instance().tribler_exitnode()
        }
        self.send_msg("general: %s" % data)

    def msg_qtable(self):
        qtable = QTable()
        qtable.read_dictionary()
        headers = ["-"]
        table = []
        header_dict = {}
        # get all the available vps options
        for k, v in qtable.qtable.items():
            shorter_item = k.split(" ")[0].split("_")[0] + "1"
            num = 1
            while shorter_item in headers:
                num += 1
                shorter_item = shorter_item.replace(shorter_item[-1], str(num))
            headers.append(shorter_item)
            header_dict[k] = shorter_item

        # get the rest of the table
        index = 0
        for k, v in qtable.qtable.items():
            table.append([header_dict[k]])
            for k2, v2 in v.items():
                table[index].append(str(v2))
            index += 1

        # get the format string used for each line in the table
        formatt = "{:<%i} "
        max_len = 20
        for vps_service in headers[1:]:
            max_len = max(len(vps_service) + 2, max_len)
            formatt += "{:<%i} " % max(20, (len(vps_service) + 2))
        formatt = formatt % max_len
        formatt = formatt[:-1]
        headers[0] *= (max_len - 2)

        # send individual messages for each line of the qtable
        # , because IRC only supports up until 512 characters per message
        self.send_msg(formatt.format(*headers))
        # message = formatt.format(*headers)
        time.sleep(3)
        for line in table:
            time.sleep(3)
            # message += formatt.format(*line)
            self.send_msg(formatt.format(*line))
        # self.send_msg(message)


if __name__ == '__main__':
    Create()
