import unittest
import mock
from anytree import Node
from mock.mock import MagicMock
from appdirs import user_config_dir
import os
import sys
from plebnet.utilities import logger
from plebnet.settings import plebnet_settings
from plebnet.utilities.custom_tree import get_curr_state, create_child_name, get_no_replications

logfile = plebnet_settings.get_instance().logger_file()

msg1 = "this is a log"
msg2 = "this is another log"
msg3 = "this is a nice line"
msg4 = "this is a beautiful line of text"


class TestCustomTree(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_curr_state(self):
        a = Node("a")
        b = Node("b", parent=a)
        tree = [a, b]
        curr_state = get_curr_state(tree, "a")
        assert (curr_state == a)
        assert (curr_state != b)

    def test_create_child_name(self):
        name = create_child_name("1", "2", "3")
        assert (name == "1|2|3")

    def test_get_no_replications(self):
        a = Node("a")
        b = Node("b", parent=a)
        c = Node("c", parent=a)
        tree = [a, b, c]
        no_replications = get_no_replications(b)
        assert (no_replications == 1)


if __name__ == '__main__':
    unittest.main()
