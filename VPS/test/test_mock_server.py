import unittest

from MockBuyer import MockBuyer


class TestMockServer(unittest.TestCase):
    server = MockBuyer()
    server.buy()


if __name__ == '__main__':
    unittest.main()
