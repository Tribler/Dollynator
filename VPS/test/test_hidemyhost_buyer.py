import unittest

from HideMyHostBuyer import HideMyHostBuyer


class TestHideMyHostBuyer(unittest.TestCase):
    server = HideMyHostBuyer()
    server.register()


if __name__ == '__main__':
    unittest.main()
