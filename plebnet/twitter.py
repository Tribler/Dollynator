from twython import Twython


def tweet_arrival(name):
    twitter = Twython(APP_KEY, APP_SECRET,
                      OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    twitter.update_status(status='Pleb %s has joined the botnet for good.' % name)
