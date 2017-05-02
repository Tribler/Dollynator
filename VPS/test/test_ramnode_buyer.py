import unittest

from RamNodeBuyer import RamNodeBuyer


class TestRamNodeBuyer(unittest.TestCase):
    server = RamNodeBuyer()
    server.register()


if __name__ == '__main__':
    unittest.main()
