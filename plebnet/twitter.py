import os
from ConfigParser import ConfigParser

from appdirs import user_config_dir
from cloudomate.util.config import UserOptions
from twython import Twython


def tweet_arrival():
    options = UserOptions()
    options.read_settings()
    name = options.get('firstname') + ' ' + options.get('lastname')

    path = os.path.join(user_config_dir(), 'twitter.cfg')
    if not os.path.exists(path):
        print("Can't Tweet: {0} doesn't exist".format(path))
        return False
    cp = ConfigParser()
    cp.read(path)

    try:
        twitter = Twython(cp.get('twitter', 'app_key'),
                          cp.get('twitter', 'app_secret'),
                          cp.get('twitter', 'oauth_token'),
                          cp.get('twitter', 'oauth_token_secret'))
        twitter.update_status(
            status='Pleb %s has joined the botnet for good. #PlebNet #Cloudomate #Tribler #Bitcoin' % name)
        print("Tweeted arrival")
    except Exception, e:
        print e
        return False
    return True
