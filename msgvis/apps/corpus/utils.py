import oauth2 as oauth
import json
from msgvis.settings.common import TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET
import re


def get_embedded_html(tweet_original_id):
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
    html = ""
    if content.get('html'):
        html = pattern.match(content['html']).group()
        #html = content.get('html')
    return html

    #return "<p></p>"


