import unittest

from CCIHostingBuyer import CCIHostingBuyer


class TestCCIHostingBuyer(unittest.TestCase):
    server = CCIHostingBuyer()
    server.buy()


if __name__ == '__main__':
    unittest.main()
