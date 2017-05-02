import unittest

from RamNodeBuyer import RamNodeBuyer
from MockBuyer import MockBuyer


class TestRamNodeBuyer(unittest.TestCase):
    server = RamNodeBuyer()
    server.buy()


if __name__ == '__main__':
    unittest.main()
