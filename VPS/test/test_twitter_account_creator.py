import unittest

from TwitterAccountCreator import TwitterAccountCreator


class TestTwitterAccountCreator(unittest.TestCase):
    twitter = TwitterAccountCreator()
    username = 'ginasmythpleb@heijligers.me'
    password = 'UFrhhuebduH7#'
    twitter.login(username, password)
    # twitter.create()


if __name__ == '__main__':
    unittest.main()
