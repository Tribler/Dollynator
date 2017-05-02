import unittest

from RamNodeBuyer import RamNodeBuyer


class TestRamNodeBuyer(unittest.TestCase):
    server = RamNodeBuyer()
    server.buy()


if __name__ == '__main__':
    unittest.main()
