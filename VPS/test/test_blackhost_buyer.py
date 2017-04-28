import unittest

from BlackhostBuyer import BlackhostBuyer
from MockBuyer import MockBuyer


class TestBlackhostBuyer(unittest.TestCase):
    server = BlackhostBuyer()
    server.buy()


if __name__ == '__main__':
    unittest.main()
