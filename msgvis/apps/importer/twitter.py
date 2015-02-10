
def get_tweepy_auth():
    import tweepy
    from django.conf import settings

    consumer_key = settings.TWITTER_CONSUMER_KEY
    consumer_secret = settings.TWITTER_CONSUMER_SECRET

    if consumer_key and consumer_secret:
        print "Using Twitter consumer key/secret from settings."
    else:
        print "Twitter consumer key/secret not in settings."
        consumer_key = raw_input("Consumer key: ")
        consumer_secret = raw_input("Consumer secret: ")

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret, callback='oob')

    access_token = settings.TWITTER_ACCESS_TOKEN
    access_token_secret = settings.TWITTER_ACCESS_TOKEN_SECRET

    if access_token and access_token_secret:
        print "Using Twitter consumer key/secret from settings."
        auth.set_access_token(access_token, access_token_secret)
    else:
        try:
            redirect_url = auth.get_authorization_url()
            print "------"
            print "Visit this url: %s" % redirect_url
        except tweepy.TweepError:
            print 'Error! Failed to get request token.'

        # Example w/o callback (desktop)
        verifier = raw_input('Paste the verifier here: ')
        print "------"

        # Convert the verifier into an access token
        try:
            auth.get_access_token(verifier)

            print "Successfully obtained access token."
            print "Add these environment variables to skip this step in the future:"
            print "  TWITTER_CONSUMER_KEY: %s" % auth.consumer_key
            print "  TWITTER_CONSUMER_SECRET: %s" % auth.consumer_secret
            print "  TWITTER_ACCESS_TOKEN=%s" % auth.access_token
            print "  TWITTER_ACCESS_TOKEN_SECRET=%s" % auth.access_token_secret

        except tweepy.TweepError:
            print 'Error! Failed to get access token.'

    return auth
