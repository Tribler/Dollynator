import unittest

from CCIHostingBuyer import CCIHostingBuyer


class TestCCIHostingBuyer(unittest.TestCase):
    server = CCIHostingBuyer()
    server.register()


if __name__ == '__main__':
    unittest.main()
