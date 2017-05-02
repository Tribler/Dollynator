import unittest

from AbeloHostBuyer import AbeloHostBuyer


class TestAbeloHostBuyer(unittest.TestCase):
    server = AbeloHostBuyer()
    server.register()


if __name__ == '__main__':
    unittest.main()
