import oauth2 as oauth
import json
from msgvis.settings.common import TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET, DEBUG
import re
import os
import os.path
from django.db.models import Q
import operator

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
    html = ""
    if content.get('html'):
        html = pattern.match(content['html']).group()
        #html = content.get('html')
    return html

    #return "<p></p>"

def render_hashtag_html(matchobj):
    return "<span class='hashtag'>" + matchobj.group(0) + "</span>"

def render_mention_html(matchobj):
    return "<span class='mention'>" + matchobj.group(0) + "</span>"

def render_link_html(matchobj):
    link = matchobj.group(0)
    return "<span class='link'>" + '<a href="' + link + '" target="_blank">' + link + "</a>" + "</span>"

def render_html_tag(text):
    pattern = r'(?<=\s)#\w+|^#\w+'
    text = re.sub(pattern, render_hashtag_html, text)
    pattern = r'(?<=\s)@\w+|^@\w+'
    text = re.sub(pattern, render_mention_html, text)
    http_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    pattern = r'(?<=\s)' + http_pattern + '|^' + http_pattern
    text = re.sub(pattern, render_link_html, text)
    return text

def quote_query(matchobj):
    return "'" + matchobj.group(0) + "'"

def quote(text):
    pattern = r'(?<== )\d+\-\d+\-\d+ \d+:\d+:\d+|(?<== )[\da-zA-Z_#\-.]+(?=[ )])'
    text = re.sub(pattern, quote_query, text)
    return text

def convert_boolean(query):
    query = query.replace('\'True\'', "1")
    query = query.replace('\'False\'', "0")
    return query

def quote(text):
    pattern = r'(?<== )\d+\-\d+\-\d+ \d+:\d+:\d+|(?<== )[\da-zA-Z_#\-.]+(?=[ )])'
    text = re.sub(pattern, quote_query, text)
    return text

def levels_or(field_name, domain):
    filter_ors = []
    for level in domain:
        if level is None or str(level).strip() == "":
            filter_ors.append((field_name + "__isnull", True))
        else:
            filter_ors.append((field_name, level))

    return reduce(operator.or_, [Q(x) for x in filter_ors])

def get_word_objs(queryset, text_field_name, related_field_name, words):
    word_objs = []
    for word in words:
        obj = queryset.filter(Q((text_field_name, word)))
        if obj.count() > 0:
            word_obj = obj[0]
            or_objs = levels_or(related_field_name, map(lambda x: x.id, word_obj.related_words))
            word_objs.append(or_objs)

    return word_objs