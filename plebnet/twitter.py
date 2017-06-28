from twython import Twython


def tweet_arrival(name, app_key, app_secret, oauth_token, oauth_token_secret):
    twitter = Twython(app_key, app_secret,
                      oauth_token, oauth_token_secret)
    twitter.update_status(status='Pleb %s has joined the botnet for good.' % name)
