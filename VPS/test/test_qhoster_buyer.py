import unittest

from QHosterBuyer import QHosterBuyer


class TestQHosterBuyer(unittest.TestCase):
    server = QHosterBuyer()
    server.buy()


if __name__ == '__main__':
    unittest.main()
