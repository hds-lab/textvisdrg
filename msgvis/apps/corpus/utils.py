import oauth2 as oauth
import json
from msgvis.settings.common import TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET, DEBUG
import re
import os


def get_embedded_html(tweet_original_id):

    if DEBUG or os.environ["DJANGO_SETTINGS_MODULE"] == "msgvis.settings.test":
        fake = r'<blockquote class="twitter-tweet" data-cards="hidden" > <p lang="en" dir="ltr">Sunsets don&#39;t get much better than this one over <a href="https://twitter.com/GrandTetonNPS">@GrandTetonNPS</a>. <a href="https://twitter.com/hashtag/nature?src=hash">#nature</a> <a href="https://twitter.com/hashtag/sunset?src=hash">#sunset</a> <a href="http://t.co/YuKy2rcjyU">pic.twitter.com/YuKy2rcjyU</a></p>&mdash; US Dept of Interior (@Interior) <a href="https://twitter.com/Interior/status/463440424141459456">May 5, 2014</a></blockquote>'
        return fake


    # Create your consumer with the proper key/secret.

    consumer = oauth.Consumer(key=TWITTER_ACCESS_TOKEN, secret=TWITTER_ACCESS_TOKEN_SECRET)

    # Request token URL for Twitter.
    request_token_url = "https://api.twitter.com/1.1/statuses/oembed.json?url=https://twitter.com/x/status/" + str(tweet_original_id)

    # Create our client.
    client = oauth.Client(consumer)

    # The OAuth Client request works just like httplib2 for the most part.
    resp, content = client.request(request_token_url, "GET")

    content = json.loads(content)

    pattern = re.compile("<blockquote.*</blockquote>")
    #html = ""
    if content.get('html'):
        html = pattern.match(content['html']).group()
        #html = content.get('html')
    return html

    #return "<p></p>"


