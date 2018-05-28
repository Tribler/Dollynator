"""
This file is used to handle the commandline input regarding the IRC connection. It tells the IRC-deamon what to do.
"""

import os
import subprocess

from plebnet.utilities import logger

#TODO alle bestandspaden in 1 file, vanuit daar vervolgens inladen --> improved maintainability
PLEBNET_HOME = os.path.expanduser("~/PlebNet")
DEAMON = "plebnet/communication/irc/initIRC.sh"
CLIENT = "plebnet/communication/irc/ircbot.py"
PATH_TO_DEAMON = os.path.join(PLEBNET_HOME, DEAMON)
PATH_TO_CLIENT = os.path.join(PLEBNET_HOME, CLIENT)


# TODO: implement send_heartbeat


# TODO: implement send_msg(args)


def init_irc_client(args=None):
    """
    This method initializes the IRC client by setting up the proper rights to run the files
    :param args: The remaining commands from the commandline, can be neglected.
    :type args: String
    :return: None
    :rtype: None
    """

    logger.log("the IRC client is initializing", "init_irc_client")

    subprocess.call('sudo chmod +x %s' % PATH_TO_CLIENT, shell=True)
    subprocess.call('sudo chmod +x %s' % PATH_TO_DEAMON, shell=True)

    logger.log("the IRC client is initialized", "init_irc_client")


def start_irc_client(args=None):
    """
    This method starts the IRC client deamon
    :param args: The remaining commands from the commandline, can be neglected.
    :type args: String
    :return: None
    :rtype: None
    """
    logger.log("the IRC client is starting", "start_irc_client")

    # run the init file
    success = subprocess.call('sudo %s start' % PATH_TO_DEAMON, shell=True)
    if success:
        logger.log("the IRC client is started", "start_irc_client")
    else:
        logger.error("the IRC client failed to start", "start_irc_client")
    return success


def stop_irc_client(args=None):
    """
    This method stops the IRC client deamon
    :param args: The remaining commands from the commandline, can be neglected.
    :type args: String
    :return: None
    :rtype: None
    """
    logger.log("the IRC client is stopping", "stop_irc_client")

    # run the init file
    success = subprocess.call('sudo %s stop' % PATH_TO_DEAMON, shell=True)
    if success:
        logger.log("the IRC client is stopped", "stop_irc_client")
    else:
        logger.error("the IRC client is not stopped", "stop_irc_client")
    return success


def restart_irc_client(args=None):
    """
    This method restarts the IRC client deamon
    :param args: The remaining commands from the commandline, can be neglected.
    :type args: String
    :return: None
    :rtype: None
    """
    stop_irc_client()
    success = start_irc_client()
    return success


def status_irc_client(args=None):
    """
    This method can be used to check if the IRC client is still running.
    :param args: The remaining commands from the commandline, can be neglected.
    :type args: String
    :return: None
    :rtype: None
    """

    subprocess.call('sudo %s status' % PATH_TO_DEAMON, shell=True)
