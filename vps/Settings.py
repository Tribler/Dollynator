import json


class Settings(object):
    """
    This class uses a private settings.json to infer some variable to be used in development that either need to be 
    globally defined or should not leak for security reasons. 
    """

    def __init__(self):
        self.json = self._load()

    def enable_global_ssh_logging(self):
        try:
            return self.json['enable_global_ssh_logging']
        except:
            return False

    def get_test_server_ip(self):
        try:
            return self.json['testserver']['sship']
        except:
            return None

    def get_test_server_ssh_port(self):
        try:
            return self.json['testserver']['sshport']
        except:
            return None

    def get_test_server_ssh_password(self):
        try:
            return self.json['testserver']['sshpassword']
        except:
            return None

    def get_test_server_ssh_username(self):
        try:
            return self.json['testserver']['sshusername']
        except:
            return None

    def get_test_server_vps_buyer(self):
        try:
            return self.json['testserver']['VPSBuyer']
        except:
            return None

    @staticmethod
    def _load():
        try:
            f = open("settings.json", "r")
            fc = f.read()
            return json.loads(fc)
        except:
            print("failed to load settings.json, do not expect this program to run properly without it")
            return {}
