import unittest

from QHosterBuyer import QHosterBuyer


class TestQHosterBuyer(unittest.TestCase):
    server = QHosterBuyer()
    server.register()


if __name__ == '__main__':
    unittest.main()
