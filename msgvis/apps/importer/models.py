from django.db import models
from django.utils.timezone import utc
from urlparse import urlparse

import json
from datetime import datetime
from email.utils import parsedate
from msgvis.apps.questions.models import Article, Question
from msgvis.apps.corpus.models import *
from msgvis.apps.enhance.models import set_message_sentiment

# Create your models here.

def create_an_user_from_json_obj(user_data, dataset_obj):
    sender, created = Person.objects.get_or_create(dataset=dataset_obj,
                                                         original_id=user_data['id'])
    if user_data.get('screen_name'):
        sender.username = user_data['screen_name']
    if user_data.get('name'):
        sender.full_name = user_data['name']
    if user_data.get('lang'):
        sender.language =  Language.objects.get_or_create(code=user_data['lang'])[0]
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
    if get_or_create_a_tweet_from_json_obj(tweet_data, dataset_obj) is not None:
        return True
    else:
        return False

def get_or_create_a_tweet_from_json_obj(tweet_data, dataset_obj):
    """
    Given a dataset object, imports a tweet from json object into
    the dataset.
    """
    if 'in_reply_to_status_id' not in tweet_data:
        return None

    tweet, created = Message.objects.get_or_create(dataset=dataset_obj, original_id = tweet_data['id'])

    # text
    if tweet_data.get('text'):
        tweet.text = tweet_data['text']

    # created_at
    if tweet_data.get('created_at'):
        tweet.time = datetime(*(parsedate(tweet_data['created_at']))[:6], tzinfo=utc)

    # language
    if tweet_data.get('lang'):
        tweet.language, created = Language.objects.get_or_create(code=tweet_data['lang'])

    if tweet_data.get('user'):
        # sender
        tweet.sender = create_an_user_from_json_obj(tweet_data['user'], dataset_obj)

        # time_zone
        if tweet_data['user'].get('time_zone'):
            tweet.timezone, created = Timezone.objects.get_or_create(name=tweet_data['user']['time_zone'])



    # type
    if tweet_data.get('retweeted_status') is not None:
        tweet.type, created = MessageType.objects.get_or_create(name="retweet")

        # update original tweet shared_count
        original_tweet = get_or_create_a_tweet_from_json_obj(tweet_data['retweeted_status'], dataset_obj)
        original_tweet.shared_count += 1
        original_tweet.save()

        original_tweet.sender.shared_count += 1
        original_tweet.sender.save()

    elif tweet_data.get('in_reply_to_status_id') is not None:
        tweet.type, created = MessageType.objects.get_or_create(name="reply")

        # update original tweet shared_count
        tmp_tweet = {
                        'id': tweet_data['in_reply_to_status_id'],
                        'user': {
                                    'id': tweet_data['in_reply_to_user_id'],
                                    'screen_name': tweet_data['in_reply_to_screen_name'],
                                },
                        'in_reply_to_status_id': None
                    }
        original_tweet = get_or_create_a_tweet_from_json_obj(tmp_tweet, dataset_obj)
        original_tweet.replied_to_count += 1
        original_tweet.save()

        original_tweet.sender.replied_to_count += 1
        original_tweet.sender.save()

    else:
        tweet.type, created = MessageType.objects.get_or_create(name="tweet")


    # hashtags
    if tweet_data.get('entities') and tweet_data['entities'].get('hashtags') and len(tweet_data['entities']['hashtags']) > 0:
        tweet.contains_hashtag = True
        for hashtag in tweet_data['entities']['hashtags']:
            hashtag_obj, created = Hashtag.objects.get_or_create(text=hashtag['text'])
            tweet.hashtags.add(hashtag_obj)

    # urls
    if tweet_data.get('entities') and tweet_data['entities'].get('entities') and len(tweet_data['entities']['urls']) > 0:
        tweet.contains_url = True
        for url in tweet_data['entities']['urls']:
            urlparse_results = urlparse(url['expanded_url'])
            domain = urlparse_results.netloc
            url_obj, created = Url.objects.get_or_create(full_url=url['expanded_url'], domain=domain,
                                                         short_url=url['url'])
            tweet.urls.add(url_obj)

    # media
    if tweet_data.get('entities') and tweet_data['entities'].get('media') and len(tweet_data['entities']['media']) > 0:
        tweet.contains_media = True
        for me in tweet_data['entities']['media']:
            media_obj, created = Media.objects.get_or_create(type=me['type'], media_url=me['media_url'])
            tweet.media.add(media_obj)

    # user_mentions
    if tweet_data.get('entities') and tweet_data['entities'].get('user_mentions') and len(tweet_data['entities']['user_mentions']) > 0:
        tweet.contains_mention = True
        for mention in tweet_data['entities']['user_mentions']:
            mention_obj = create_an_user_from_json_obj(mention, dataset_obj)
            mention_obj.mentioned_count += 1
            mention_obj.save()
            tweet.mentions.add(mention_obj)

    tweet.save()

    # sentiment
    set_message_sentiment(tweet)

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