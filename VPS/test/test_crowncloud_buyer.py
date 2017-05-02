import unittest

from CrowncloudBuyer import CrowncloudBuyer


class TestCrowncloudBuyer(unittest.TestCase):
    server = CrowncloudBuyer()
    server.buy()


if __name__ == '__main__':
    unittest.main()
