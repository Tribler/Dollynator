"""
This file is used for logging purposes. The messages send here will be
printed to the log file and when run from a command UI, will be printed
in a color.
"""

# Total imports
import logging
# Local imports
from plebnet.settings import plebnet_settings

suppress_print = False
settings = plebnet_settings.get_instance()


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def reset():
    if logging.root:
        del logging.root.handlers[:]
        del logging.getLogger().handlers[:]
        del logging.getLogger(settings.get_logger_file()).handlers[:]


def log(msg, method=""):
    # prepare the output
    tex = _fill(method, 15) + " : " + msg
    # output the log details
    _get_logger().info(tex)
    if not suppress_print: print(tex)


def success(msg, method=""):
    # prepare the output
    tex = _fill(method, 15) + " : " + msg
    # output the log details
    _get_logger().info(tex)
    if not suppress_print: print(bcolors.OKGREEN + tex + bcolors.ENDC)


def warning(msg, method=""):
    # prepare the output
    tex = _fill(method, 15) + " : " + msg
    # output the log details
    _get_logger().warning(tex)
    if not suppress_print: print(bcolors.WARNING + tex + bcolors.ENDC)


def error(msg, method=""):
    # prepare the output
    tex = _fill(method, 15) + " : " + msg
    # output the log details
    _get_logger().error(tex)
    if not suppress_print: print(bcolors.FAIL + tex + bcolors.ENDC)


def _get_logger(name=settings.get_logger_file()):
    logger = logging.getLogger(name)

    if not logger.handlers:

        logger.setLevel(logging.INFO)

        # create formatter and handler
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        path = settings.get_logger()
        handler = logging.FileHandler(path)
        # combine
        handler.setLevel(logging.INFO)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def _fill(tex, leng):
    if len(tex) > leng:
        tex = tex[:leng-2] + ".."
    else:
        while len(tex) < leng:
            tex = tex + " "
    return tex
