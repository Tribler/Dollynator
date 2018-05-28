import unittest
import plebnet.controllers.cloudomate_controller as cloudomate
from cloudomate.util.settings import Settings as AccountSettings
from plebnet.agent.config import PlebNetConfig
from mock.mock import MagicMock
from appdirs import user_config_dir
import os
from unittest import skip

class TestCloudomateController(unittest.TestCase):

 @skip("this unittest class is still a work in progress")
 def test_child_account(self):
     self.cloudomate_account = cloudomate.util.settings.settings
     self.cloudomate_read = cloudomate.util.settings.settings.read_settings
     self.os_is_join = os.path.join
     #self.config = user_config_dir()
     self.plebnet_config = PlebNetConfig.get

     cloudomate.util.settings.settings = MagicMock()
     cloudomate.util.settings.settings.read_settings = MagicMock()
     os.path.join = MagicMock()
     PlebNetConfig.get = MagicMock()

     cloudomate.child_account()


     AccountSettings = self.cloudomate_account
     AccountSettings.read_settings = self.cloudomate_read
     os.path.join = self. os_is_join
    # user_config_dir = self.config
     PlebNetConfig.get = self.plebnet_config


 if __name__ == '__main__':
        unittest.main()