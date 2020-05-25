"""
This file is used for logging purposes. The messages send here will be
printed to the log file and when run from a command UI, will be printed
in a color.
"""

# Total imports
import logging

from logging.handlers import WatchedFileHandler
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


def _get_logger(name=settings.logger_filename()):
    logger = logging.getLogger(name)

    if not logger.handlers:

        logger.setLevel(logging.INFO)

        # create formatter and handler
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        path = settings.logger_file()
        handler = WatchedFileHandler(path)
        # combine
        handler.setLevel(logging.INFO)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def put_msg(msg, color=None, origin="", method=_get_logger().info):
    msg = _fill(origin, 15) + " : " + msg
    if settings.active_logger():
        method(msg)
    if settings.active_verbose():
        if color:
            msg = color + msg + bcolors.ENDC
        print(msg)


def log(msg, origin=""): put_msg(str(msg), origin=str(origin))


def success(msg, origin=""): put_msg(str(msg), bcolors.OKGREEN, origin=str(origin))


def warning(msg, origin=""): put_msg(str(msg), bcolors.WARNING, origin=str(origin), method=_get_logger().warning)


def error(msg, origin=""): put_msg(str(msg), bcolors.FAIL, origin=str(origin), method=_get_logger().error)


def _fill(tex, leng):
    if len(tex) > leng:
        tex = tex[:leng-2] + ".."
    else:
        while len(tex) < leng:
            tex = tex + " "
    return tex
