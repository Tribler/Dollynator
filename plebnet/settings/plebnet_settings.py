"""
This subclass of settings is used to store the setup configuration.

This configuration should only contain values which are set on initialization
of the first parent, and should not change during the cloning process.

The file it self can be found in the PATH_TO_FILE location.
"""

# Total imports
import os

# Partial imports
from appdirs import user_config_dir, user_data_dir
from shutil import copy2 as copy

# Local imports
from plebnet.settings import setting

# File parameters
file_name = 'plebnet_setup.cfg'

conf_path = user_config_dir()
data_path = user_data_dir()
init_path = os.path.join(os.path.expanduser("~/PlebNet"), 'plebnet/settings/configuration')

init_file = os.path.join(init_path, file_name)
conf_file = os.path.join(conf_path, file_name)

""" DATE AND TIME VARIABLES """
TIME_IN_HOUR = 60.0 * 60.0
TIME_IN_DAY = TIME_IN_HOUR * 24.0
MAX_DAYS = 5
""" EXIT CODES """
FAILURE = 0
SUCCESS = 1
UNKNOWN = 2

instance = None


class Init(object):

    def __init__(self):
        # file does not exist --> copy the initial file
        if not os.path.isfile(conf_file):
            copy(init_file, conf_path)

        self.settings = setting.Settings(conf_file)

    """ THE ATTRIBUTE METHODS FOR THE PATH SECTION """

    def logger_file(self): return os.path.join(self.logger_path(), self.logger_filename())

    def logger_path(self, value=None): return conf_path

    def logger_filename(self, value=None): return self.settings.handle("filenames", "LOGGER_FILE", value)

    def tribler_home(self, value=None):
        str = self.settings.handle("paths", "TRIBLER_HOME", value)
        if not value: return os.path.expanduser(str)

    def plebnet_home(self, value=None):
        str = self.settings.handle("paths", "PLEBNET_HOME", value)
        if not value: return os.path.expanduser(str)

    def vpn_config_path(self, value=None): 
        str = self.settings.handle("paths", "VPN_CONFIG_PATH", value)
        if not value: return os.path.expanduser(str)

    """ THE ATTRIBUTE METHODS FOR THE PID SECTION """

    def tunnelhelper_pid(self, value=None): return self.settings.handle("pids", "TUNNEL_HELPER_PID", value)

    def tribler_pid(self, value=None): return self.settings.handle("pids", "TRIBLER_PID", value)

    """ THE ATTRIBUTE METHODS FOR THE IRC SECTION """

    def irc_channel(self, value=None): return self.settings.handle("irc", "channel", value)

    def irc_server(self, value=None): return self.settings.handle("irc", "server", value)

    def irc_port(self, value=None):
        str = self.settings.handle("irc", "port", value)
        if not value: return int(os.path.expanduser(str))

    def irc_nick(self, value=None): return self.settings.handle("irc", "nick", value)

    def irc_nick_def(self, value=None): return self.settings.handle("irc", "nick_def", value)

    def irc_timeout(self, value=None):
        str = self.settings.handle("irc", "timeout", value)
        if not value: return int(os.path.expanduser(str))

    """ THE ATTRIBUTE METHODS FOR THE VPS SECTION """

    def vps_host(self, value=None): return self.settings.handle("vps", "host", value)

    def vps_life(self, value=None): return self.settings.handle("vps", "initdate", value)

    def vps_dead(self, value=None): return self.settings.handle("vps", "finaldate", value)

    def github_username(self, value=None): return self.settings.handle("github", "username", value)

    def github_password(self, value=None): return self.settings.handle("github", "password", value)

    def github_owner(self, value=None): return self.settings.handle("github", "owner", value)

    def github_repo(self, value=None): return self.settings.handle("github", "repo", value)

    def github_active(self, value=None): return self.settings.handle("github", "active", value) == "1"

    """"THE ATTRIBUTE METHODS FOR THE WALLETS SECTION"""
    
    def wallets_testnet_created(self, value=None): return self.settings.handle("wallets", "testnet_created", value) == "1"

    def wallets_testnet(self, value=None): return self.settings.handle("wallets", "testnet", value) == "1"

    def wallets_initiate_once(self, value=None): return self.settings.handle("wallets", "initiate_once", value) == "1"

    def wallets_password(self, value=None): return self.settings.handle("wallets", "password", value)

    """THE ATTRIBUTE METHODS FOR THE ACTIVE SECTION"""

    def active_verbose(self, value=None): return self.settings.handle("active", "verbose", value) == "1"

    def active_logger(self, value=None): return self.settings.handle("active", "logger", value) == "1"

    """THE ATTRIBUTE METHODS FOR THE VPN SECTION"""

    def vpn_installed(self, value=None): return self.settings.handle("vpn", "installed", value) == "1"

    def vpn_running(self, value=None):
        return self.settings.handle("vpn", "running", value) == "1"

    def vpn_pid(self, value=None):
        return self.settings.handle("vpn", "pid", value)

    def vpn_host(self, value=None): return self.settings.handle("vpn", "host", value)

    def vpn_child_prefix(self, value=None): return self.settings.handle("vpn", "child_prefix", value)

    def vpn_own_prefix(self, value=None): return self.settings.handle("vpn", "own_prefix", value)

    def vpn_config_name(self, value=None): return self.settings.handle("vpn", "config_name", value)

    def vpn_credentials_name(self, value=None): return self.settings.handle("vpn", "credentials_name", value)

    """THE ATTRIBUTE METHODS FOR THE TRIBLER SECTION"""
    def tribler_exitnode(self, value=None): return self.settings.handle("tribler", "exitnode", value)  == '1'


def write():
    get_instance()
    instance.settings.write()


def store(args):
    get_instance()
    for arg in vars(args):
        if (arg in dir(instance)) and getattr(args, arg):
            getattr(instance, arg)(str(getattr(args, arg)))
    instance.settings.write()


def get_instance():
    global instance
    if not instance:
        instance = Init()
    return instance
