import unittest

from BlueAngelHostBuyer import BlueAngelHostBuyer


class TestBlueAngelHostBuyer(unittest.TestCase):
    server = BlueAngelHostBuyer()
    server.register()


if __name__ == '__main__':
    unittest.main()
