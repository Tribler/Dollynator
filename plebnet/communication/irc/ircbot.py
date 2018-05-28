#! /usr/bin/env python

"""
This file is used to setup and maintain a connection with an IRC server.
"""

import traceback
import random
import socket
import time
import sys

# as the file is loaded separately, the imports have to be fixed
sys.path.append('./PlebNet')
from plebnet.utilities import logger
from plebnet.settings import plebnet_settings


class Create(object):
    """
    The object which maintains the server connection
    """
    def __init__(self):
        logger.log("preparing an IRC connection")

        # load required settings once
        irc_settings = plebnet_settings.get_instance()
        self.server = irc_settings.irc_server()
        self.timeout = irc_settings.irc_timeout()
        self.channel = irc_settings.irc_channel()
        self.port = irc_settings.irc_port()

        self.nick = "plebbot" + str(random.randint(1000, 10000))
        self.ident = "plebber"
        self.gecos = "Plebbot version 2.14"

        self.irc = None
        self.init_time = time.time()
        self.last_beat = time.time()

        # prep reply functions
        self.responses = {}
        self.add_response("alive", self.msg_alive)
        self.add_response("host", self.msg_host)
        self.add_response("init", self.msg_init)
        self.add_response("joke", self.msg_joke)

        # start running the IRC server
        logger.log("start running an IRC connection on " + self.server + " " + self.channel)
        self.run()

    def add_response(self, command, response):
        """
        This method is used to add new commands to the IRC-bot.
        :param command: the command (after !) which should trigger the provided method
        :type command: String
        :param response: The method to call as the command is received
        :type response: a method
        :return: None
        :rtype: None
        """
        self.responses[":!" + command] = response

    def run(self):
        """
        This method keeps listening to the server for incomming messages and processes them.
        :return:
        :rtype:
        """
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.irc.connect((self.server, self.port))

        try:
            buffer = ""

            # init the contact
            self.send("NICK %s" % self.nick)
            self.send("USER %s %s %s : %s" % (self.nick, self.nick,  self.nick, self.gecos))

            while 1:

                self.heartbeat()

                buffer = buffer + self.irc.recv(2048)
                lines = str.split(buffer, "\r\n")
                buffer = lines.pop()

                for line in lines:
                    logger.log("Received IRC message: " + line)

                for line in lines:
                    self.handle_line(line)

        except KeyboardInterrupt:
            st = "QUIT :I have to go for now!"
            self.irc.send(st)
        except:
            logger.log("An error occurred at the IRC")
            logger.log(traceback.format_exc())
            st = "QUIT :I have to go for now!"
            self.send(st)

    def heartbeat(self):
        """
        This method sends a heartbeat to the IRC server when it is called
        :return: None
        :rtype: None
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
        This method handles a line received from the IRC server
        :param line: The line to process
        :type line: String
        :return: None
        :rtype: None
        """

        line = str.rstrip(line)
        words = str.split(line)

        # playing ping-pong with a key (words[1])
        # TODO: reply to private pings: <user> PRIVMSG <botnick> :_PING 12345667_
        if words[0] == "PING":
            st = "PONG %s" % words[1]
            self.send(st)

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
        self.irc.send("%s\r\n" % msg)

    def send_msg(self, msg):
        self.send("PRIVMSG %s :%s" % (self.channel,  msg))

    """
    THE RESPONSES (don't forget to add them to the self.responses in the init method)
    These methods are used to determine the response to received commands
    """
    def msg_alive(self):
        time_str = time.strftime("%H:%M:%S", time.gmtime(time.time() - self.init_time))
        self.send_msg("I am alive, for %s" % time_str)

    def msg_host(self):
        self.send_msg("My host is : %s" % setup_settings.Init().get_vps_host())

    def msg_init(self):
        self.send_msg("My init date is : %s" % setup_settings.Init().get_vps_life())

    def msg_joke(self):
        self.send_msg("Q: Why did the hipster burn his tongue? A: he ate the pizza before it was cool")


# init the bot when this file is run
bot = Create()
