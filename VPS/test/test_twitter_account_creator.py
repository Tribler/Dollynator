import unittest

from TwitterAccountCreator import TwitterAccountCreator


class TestTwitterAccountCreator(unittest.TestCase):
    server = TwitterAccountCreator()
    server.create()


if __name__ == '__main__':
    unittest.main()
