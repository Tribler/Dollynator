import unittest

from BlackhostBuyer import BlackhostBuyer


class TestBlackhostBuyer(unittest.TestCase):
    server = BlackhostBuyer()
    server.buy()


if __name__ == '__main__':
    unittest.main()
