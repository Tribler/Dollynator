import unittest

from CrowncloudBuyer import CrowncloudBuyer


class TestCrowncloudBuyer(unittest.TestCase):
    server = CrowncloudBuyer()
    server.register()


if __name__ == '__main__':
    unittest.main()
