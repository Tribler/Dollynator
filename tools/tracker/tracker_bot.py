#! /usr/bin/env python

"""
This file is used to setup and maintain a connection with an IRC server.
"""

import socket
import logging
import random
import sys
import os

from threading import Thread
from time import sleep
from logging.handlers import WatchedFileHandler
from appdirs import user_config_dir

# load defaults
version = "0.1"
timeout = 60*10
patience = 2 # waiting time between asks, for order, prevent flooding

channel = "#plebnet123"
nick = "trackerbot"
server = "irc.undernet.org"
port = 6669
ask = True

commands = ["!MB_balance", "!BTC_balance", "!TBTC_balance", "!matchmakers", "!uploaded", "!downloaded"]

log_file_name = "tracker.log"
log_data_name = "tracker.data"
log_file_path = user_config_dir()


class TrackerBot(object):

    def __init__(self):
        self.channel = channel
        self.server = server
        self.timeout = timeout
        self.channel = channel
        self.port = port

        self.nick = nick
        self.ident = nick
        self.gecos = "%s version %s" % (nick, version)

        self.irc = None

        # start running the IRC server
        try:
            self.init_irc()
        except KeyboardInterrupt:
            st = "QUIT :I have to go for now!"
            self.irc.send(st)
        except Exception, e:
            self.log("failed to start running an tracker bot  on " + self.server + " " + self.channel)
            self.log(e)

        thread_listen = Thread(target=self.listen)
        thread_listen.start()
        sleep(20)
        thread_asking = Thread(target=self.ask)
        thread_asking.start()

    def init_irc(self):
        self.log("start running an tracker bot  on " + self.server + " " + self.channel)
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.irc.connect((self.server, self.port))

        self.send("NICK %s" % self.nick)
        self.send("USER %s %s %s : %s" % (self.nick, self.nick, self.nick, self.gecos))

    def listen(self):
        try:
            buffer = ""
            while 1:
                buffer = self.keep_listening(buffer)
        except KeyboardInterrupt:
            st = "QUIT :I have to go for now!"
            self.irc.send(st)
        except Exception, e:
            self.log("failed to start running an tracker bot  on " + self.server + " " + self.channel)
            self.log(e)

    def keep_listening(self, buffer):
        buffer = buffer + self.irc.recv(2048)
        lines = str.split(buffer, "\r\n")
        buffer = lines.pop()

        for line in lines:
            self.log("Received IRC message: " + line)

        for line in lines:
            self.handle_line(line)

        return buffer

    def handle_line(self, line):

        line = str.rstrip(line)
        words = str.split(line)

        # playing ping-pong with a key (words[1])
        if words[0] == "PING":
            st = "PONG %s" % words[1]
            self.send(st)

        # server status 433 --> nickname is already in use, so we chose a new one
        elif line.find("433 * " + self.nick) != -1:
            self.nick = self.nick + str(random.randint(1000, 10000))
            self.send("NICK %s" % self.nick)
            self.send("USER %s %s %s : %s" % (self.nick, self.nick, self.nick, self.gecos))

        # server status 376 and 422 means ready to join a channel
        elif line.find("376 " + self.nick) != -1 or line.find("422 " + self.nick) != -1:
            st = "JOIN " + self.channel
            self.send(st)

        # handle incoming messages
        else:
            self.store(line)

    def ask(self):
        while 1:
            try:
                for command in commands:
                    self.send_msg(command)
                    sleep(patience)
                sleep(self.timeout-len(commands)*patience)
            except KeyboardInterrupt:
                st = "QUIT :I have to go for now!"
                self.irc.send(st)
            except Exception, e:
                self.log("failed to ask tracker bot  on " + self.server + " " + self.channel)
                self.log(e)

    """
    THE SENDER METHODS
    These handle the outgoing messages
    """
    def send(self, msg):
        self.log("Sending  IRC message: %s" % msg)
        self.irc.send("%s\r\n" % msg)

    def send_msg(self, msg):
        self.send("PRIVMSG %s :%s" % (self.channel,  msg))


    """
    Handle logging of data and messages
    """
    def get_logger(self, name):
        logger = logging.getLogger(name)

        if not logger.handlers:
            logger.setLevel(logging.INFO)

            # create formatter and handler
            formatter = logging.Formatter('%(asctime)s;%(message)s')
            handler = WatchedFileHandler(os.path.join(log_file_path, name))
            # combine
            handler.setLevel(logging.INFO)
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def log(self, msg):
        logger = self.get_logger(log_file_name)
        logger.info(msg)

    def store(self, msg):
        logger = self.get_logger(log_data_name)

        text = msg
        words = msg.split(" ")
        words[0] = words[0].split("!")[0][1:]
        if   "My MB balance"     in msg:            logger.info("%s;MB_balance;%s"   % (words[0], words[7]))
        elif "My BTC balance"    in msg:            logger.info("%s;BTC_balance;%s"  % (words[0], words[8]))
        elif "My TBTC balance"   in msg:            logger.info("%s;TBTC_balance;%s" % (words[0], words[7]))
        elif "I currently have uploaded:" in msg:   logger.info("%s;uploaded;%s"     % (words[0], words[7]))
        elif "I currently have downloaded:" in msg: logger.info("%s;downloaded;%s"   % (words[0], words[7]))
        elif "I currently have:" in msg:            logger.info("%s;matchmakers;%s"  % (words[0], words[6]))
        elif "!trackers" in msg:                    self.send_msg("I am an online tracker!")
        else:                                       self.log("unable to parse: ORIGINAL:%s" % text)


# init the bot when this file is run
if __name__ == '__main__':
    # get custom input
    if len(sys.argv) > 1:
        nick = sys.argv[1]

    TrackerBot()

