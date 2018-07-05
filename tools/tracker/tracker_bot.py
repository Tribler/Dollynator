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

commands = ["!general",
            "!MB_balance",
            "!BTC_balance",
            "!TBTC_balance",
            "!matchmakers",
            "!uploaded",
            "!downloaded"]

log_file_name = "tracker.log"
log_data_name = "tracker.data"
log_file_path = user_config_dir()


class TrackerBot(object):

    def __init__(self, nickname=None, callback=None):
        self.channel = channel
        self.server = server
        self.timeout = timeout
        self.channel = channel
        self.port = port

        self.nick = nickname or nick
        self.ident = self.nick
        self.gecos = "%s version %s" % (self.nick, version)

        self.on_received_data = callback  

        self.irc = None

        thread_listen = Thread(target=self.run)
        thread_listen.setDaemon(True)
        thread_listen.start()        

    def run(self):
        # start running the IRC server
        try:
            self.init_irc()

            thread_listen = Thread(target=self.listen)
            thread_listen.setDaemon(True)
            thread_listen.start()
            sleep(20)
            thread_asking = Thread(target=self.ask)
            thread_asking.setDaemon(True)
            thread_asking.start()

            while True:
                sleep(1)
            
        except KeyboardInterrupt:
            st = "QUIT :I have to go for now!"
            self.irc.send(st)
            sys.exit()
        except Exception, e:
            self.log("failed to start running an tracker bot  on " + self.server + " " + self.channel)
            self.log(e)

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
        text = msg
        words = msg.split(" ")
        words[0] = words[0].split("!")[0][1:]

        if   "My MB balance"     in msg:            self.log_data(words[0], 'MB_balance', words[7])
        elif "My BTC balance"    in msg:            self.log_data(words[0], 'BTC_balance', words[8])
        elif "My TBTC balance"   in msg:            self.log_data(words[0], 'TBTC_balance', words[7])
        elif "I currently have uploaded:" in msg:   self.log_data(words[0], 'uploaded', words[7])
        elif "I currently have downloaded:" in msg: self.log_data(words[0], 'downloaded', words[7])
        elif "I currently have" in msg:             self.log_data(words[0], 'matchmakers', words[6])
        elif "general:"          in msg:            self.log_data(words[0], 'general', words[4:])
        elif "!trackers" in msg:                    self.send_msg("I am an online tracker!")
        else:                                       self.log("unable to parse: ORIGINAL:%s" % text)


    def log_data(self, bot_nick, key, value):
        logger = self.get_logger(log_data_name)
        logger.info("%s;%s;%s" % (bot_nick, key, value))

        if self.on_received_data:
            self.on_received_data(bot_nick, key, value)


# init the bot when this file is run
if __name__ == '__main__':
    # get custom input
    if len(sys.argv) > 1:
        nick = sys.argv[1]

    TrackerBot()

