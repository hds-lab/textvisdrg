import sys, six
from django.db import IntegrityError
from django.utils.timezone import utc
from urlparse import urlparse

import json
from datetime import datetime
from email.utils import parsedate
from msgvis.apps.questions.models import Article, Question
from msgvis.apps.corpus.models import *
from msgvis.apps.enhance.models import set_message_sentiment


def create_an_user_from_json_obj(user_data, dataset_obj):
    sender, created = Person.objects.get_or_create(dataset=dataset_obj,
                                                   original_id=user_data['id'])
    if user_data.get('screen_name'):
        sender.username = user_data['screen_name']
    if user_data.get('name'):
        sender.full_name = user_data['name']
    if user_data.get('lang'):
        sender.language = Language.objects.get_or_create(code=user_data['lang'])[0]
    if user_data.get('friends_count'):
        sender.friend_count = user_data['friends_count']
    if user_data.get('followers_count'):
        sender.follower_count = user_data['followers_count']
    if user_data.get('statuses_count'):
        sender.message_count = user_data['statuses_count']
    sender.save()

    return sender


def create_an_instance_from_json(json_str, dataset_obj):
    """
    Given a dataset object, imports a tweet from json string into
    the dataset.
    """
    tweet_data = json.loads(json_str)
    return get_or_create_a_tweet_from_json_obj(tweet_data, dataset_obj)


def get_or_create_language(code):
    lang, created = Language.objects.get_or_create(code=code)
    return lang


def get_or_create_timezone(name):
    zone, created = Timezone.objects.get_or_create(name=name)
    return zone


def get_or_create_messagetype(name):
    mtype, created = MessageType.objects.get_or_create(name=name)
    return mtype


def get_or_create_hashtag(hashtagblob):
    ht, created = Hashtag.objects.get_or_create(text=hashtagblob['text'])
    return ht


def get_or_create_url(urlblob):
    urlparse_results = urlparse(urlblob['expanded_url'])
    domain = urlparse_results.netloc
    url, created = Url.objects.get_or_create(full_url=urlblob['expanded_url'],
                                             domain=domain,
                                             short_url=urlblob['url'])
    return url


def get_or_create_media(mediablob):
    media, created = Media.objects.get_or_create(type=mediablob['type'],
                                                 media_url=mediablob['media_url'])
    return media


def handle_reply_to(status_id, user_id, screen_name, dataset_obj):
    # update original tweet shared_count
    tmp_tweet = {
        'id': status_id,
        'user': {
            'id': user_id,
            'screen_name': screen_name,
        },
        'in_reply_to_status_id': None
    }

    original_tweet = get_or_create_a_tweet_from_json_obj(tmp_tweet, dataset_obj)
    if original_tweet is not None:
        original_tweet.replied_to_count += 1
        original_tweet.save()

        original_tweet.sender.replied_to_count += 1
        original_tweet.sender.save()


def handle_retweet(retweeted_status, dataset_obj):
    # update original tweet shared_count
    original_tweet = get_or_create_a_tweet_from_json_obj(retweeted_status, dataset_obj)
    if original_tweet is not None:
        original_tweet.shared_count += 1
        original_tweet.save()

        original_tweet.sender.shared_count += 1
        original_tweet.sender.save()


def handle_entities(tweet, entities, dataset_obj):
    # hashtags
    if entities.get('hashtags') and len(entities['hashtags']) > 0:
        tweet.contains_hashtag = True
        for hashtag in entities['hashtags']:
            tweet.hashtags.add(get_or_create_hashtag(hashtag))

    # urls
    if entities.get('urls') and len(entities['urls']) > 0:
        tweet.contains_url = True
        for url in entities['urls']:
            tweet.urls.add(get_or_create_url(url))

    # media
    if entities.get('media') and len(entities['media']) > 0:
        tweet.contains_media = True
        for me in entities['media']:
            tweet.media.add(get_or_create_media(me))

    # user_mentions
    if entities.get('user_mentions') and len(entities['user_mentions']) > 0:
        tweet.contains_mention = True
        for mention in entities['user_mentions']:
            mention_obj = create_an_user_from_json_obj(mention, dataset_obj)
            mention_obj.mentioned_count += 1
            mention_obj.save()
            tweet.mentions.add(mention_obj)


def get_or_create_a_tweet_from_json_obj(tweet_data, dataset_obj):
    """
    Given a dataset object, imports a tweet from json object into
    the dataset.
    """
    if 'in_reply_to_status_id' not in tweet_data:
        return None

    if tweet_data.get('lang') != 'en':
        return None

    tweet, created = Message.objects.get_or_create(dataset=dataset_obj,
                                                   original_id=tweet_data['id'])

    # text
    if tweet_data.get('text'):
        tweet.text = tweet_data['text']

    # created_at
    if tweet_data.get('created_at'):
        tweet.time = datetime(*(parsedate(tweet_data['created_at']))[:6], tzinfo=utc)

    # language
    if tweet_data.get('lang'):
        tweet.language = get_or_create_language(tweet_data['lang'])

    if tweet_data.get('user'):
        # sender
        tweet.sender = create_an_user_from_json_obj(tweet_data['user'], dataset_obj)

        # time_zone
        if tweet_data['user'].get('time_zone'):
            tweet.timezone = get_or_create_timezone(tweet_data['user']['time_zone'])


    # type
    if tweet_data.get('retweeted_status') is not None:
        tweet.type = get_or_create_messagetype("retweet")

        handle_retweet(tweet_data['retweeted_status'], dataset_obj)

    elif tweet_data.get('in_reply_to_status_id') is not None:
        tweet.type = get_or_create_messagetype("reply")

        handle_reply_to(status_id=tweet_data['in_reply_to_status_id'],
                        user_id=tweet_data['in_reply_to_user_id'],
                        screen_name=tweet_data['in_reply_to_screen_name'],
                        dataset_obj=dataset_obj)

    else:
        tweet.type = get_or_create_messagetype('tweet')

    if tweet_data.get('entities'):
        handle_entities(tweet, tweet_data.get('entities'), dataset_obj)

    # sentiment
    set_message_sentiment(tweet, save=False)

    tweet.save()

    return tweet


def load_research_questions_from_json(json_str):
    """
    Load research questions from json string
    """

    questions = json.loads(json_str)
    for q in questions:
        source = q['source']
        article, created = Article.objects.get_or_create(title=source['title'],
                                                         defaults={'authors': source['authors'],
                                                                   'year': source['year'],
                                                                   'venue': source['venue'],
                                                                   'link': source['link']})
        question = Question(source=article, text=q['text'])
        question.save()
        for dim in q['dimensions']:
            question.add_dimension(dim)
        question.save()

    return True
