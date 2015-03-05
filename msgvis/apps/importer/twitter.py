"""
Utilities for working with Twitter.
"""

try:
    import tweepy
except ImportError:
    tweepy = None


def tweepy_installed():
    """Return True if tweepy is installed"""
    return tweepy is not None

def get_tweepy_auth():
    """
    Interactive commands for getting Twitter API authorization.
    Returns a tweepy.OAuthHandler.
    """

    from django.conf import settings

    consumer_key = settings.TWITTER_CONSUMER_KEY
    consumer_secret = settings.TWITTER_CONSUMER_SECRET

    if consumer_key and consumer_secret:
        print "Using consumer key/secret from settings."
    else:
        print "Twitter consumer key/secret not in settings."
        print "You will need to use keys from a Twitter app (https://apps.twitter.com/)"
        consumer_key = raw_input("Consumer key: ")
        consumer_secret = raw_input("Consumer secret: ")

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret, callback='oob')

    access_token = settings.TWITTER_ACCESS_TOKEN
    access_token_secret = settings.TWITTER_ACCESS_TOKEN_SECRET

    if access_token and access_token_secret:
        print "Using access token/secret from settings."
        auth.set_access_token(access_token, access_token_secret)
    else:
        try:
            redirect_url = auth.get_authorization_url()
            print "------"
            print ""
            print "Visit this url:  %s" % redirect_url
            print ""
            print "------"
        except tweepy.TweepError:
            print 'Error! Failed to get request token.'

        # Example w/o callback (desktop)
        verifier = raw_input('Paste the verifier here: ')

        # Convert the verifier into an access token
        try:
            auth.get_access_token(verifier)

            print "Successfully obtained access token."
            print "Copy these variables to your environment to skip this step in the future:"
            print "  TWITTER_CONSUMER_KEY=%s" % auth.consumer_key
            print "  TWITTER_CONSUMER_SECRET=%s" % auth.consumer_secret
            print "  TWITTER_ACCESS_TOKEN=%s" % auth.access_token
            print "  TWITTER_ACCESS_TOKEN_SECRET=%s" % auth.access_token_secret

        except tweepy.TweepError:
            print 'Error! Failed to get access token.'

    return auth

def get_languages():
    """Get a list of languages supported by Twitter."""
    auth = get_tweepy_auth()
    api = tweepy.API(auth_handler=auth)
    return api.supported_languages()

def get_timezones(time_zones_mapping_file):
    """Get a list of twitter-supported timezones as name/Olson code pairs."""

    print "Reading time zones from %s" % time_zones_mapping_file

    with open(time_zones_mapping_file, 'rb') as infile:
        mapping = infile.read()
        mapping = mapping.replace(' => ', ':')

        import json
        mapping = json.loads(mapping)
        return mapping.items()
