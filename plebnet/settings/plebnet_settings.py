"""
This subclass of settings is used to store the setup configuration.

This configuration should only contain values which are set on initialization
of the first parent, and should not change during the cloning process.

The file it self can be found in the PATH_TO_FILE location.
"""

# Total imports
import os

# Partial imports

# Local imports
from plebnet.settings import setting

# File parameters
PATH_TO_FILE = "plebnet/settings/configuration/setup.cfg"

""" DATE AND TIME VARIABLES """
TIME_IN_HOUR = 60.0 * 60.0
TIME_IN_DAY = TIME_IN_HOUR * 24.0
MAX_DAYS = 5
""" EXIT CODES """
FAILURE = 0
SUCCESS = 1
UNKNOWN = 2

instance = None


def get_instance():
    global instance
    if not instance:
        instance = Init()
    return instance


class Init(object):

    def __init__(self):
        self.filename = os.path.join(os.path.expanduser("~/PlebNet"), PATH_TO_FILE)
        self.settings = setting.Settings(self.filename)
        self.settings.load()

    """THE GETTERS FOR THE PATH SECTION"""

    def get_logger(self): return os.path.join(self.get_logger_path(), self.get_logger_file())

    def get_logger_path(self): return os.path.expanduser(self.settings.get("paths", "LOGGER_PATH"))

    def get_logger_file(self): return self.settings.get("files", "LOGGER_FILE")

    def get_tribler_home(self): return os.path.expanduser(self.settings.get("paths", "TRIBLER_HOME"))

    def get_plebnet_home(self): return os.path.expanduser(self.settings.get("paths", "PLEBNET_HOME"))

    """THE GETTERS FOR THE PID SECTION"""

    def get_tunnelhelper_pid(self): return self.settings.get("pids", "TUNNEL_HELPER_PID")

    def get_tribler_pid(self): return self.settings.get("pids", "TRIBLER_PID")

    """THE GETTERS FOR THE IRC SECTION"""

    def get_irc_channel(self): return self.settings.get("irc", "channel")

    def get_irc_server(self): return self.settings.get("irc", "server")

    def get_irc_port(self): return int(self.settings.get("irc", "port"))

    def get_irc_nick(self): return self.settings.get("irc", "nick")

    def get_irc_timeout(self): return int(self.settings.get("irc", "timeout"))

    """THE SETTERS FOR THE IRC SECTION"""

    def set_irc_channel(self, value): return self.settings.set("irc", "channel", value)

    def set_irc_server(self, value): return self.settings.set("irc", "server", value)

    def set_irc_port(self, value): return self.settings.set("irc", "port", value)

    def set_irc_nick(self, value): return self.settings.set("irc", "nick", value)

    def set_irc_timeout(self, value): return self.settings.set("irc", "timeout", value)

    """THE SETTERS FOR THE VPS SECTION"""

    def get_vps_host(self): return self.settings.get("vps", "host")

    def get_vps_life(self): return self.settings.get("vps", "initdate")

    def get_vps_dead(self): return self.settings.get("vps", "finaldate")
