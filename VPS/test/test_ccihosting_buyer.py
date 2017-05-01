import unittest

from CCIHostingBuyer import CCIHostingBuyer
from MockBuyer import MockBuyer


class TestCCIHostingBuyer(unittest.TestCase):
    server = CCIHostingBuyer()
    server.buy()


if __name__ == '__main__':
    unittest.main()
