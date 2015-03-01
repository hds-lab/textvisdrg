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
def create_an_instance_from_json(json_str, dataset_obj):
    """
    Given a dataset object, imports a tweet from json string into
    the dataset.
    """

    tweet_data = json.loads(json_str)
    tweet = Message(dataset=dataset_obj)
    if 'in_reply_to_status_id' not in tweet_data:
        return False
    tweet.text = tweet_data['text']
    tweet.time = datetime(*(parsedate(tweet_data['created_at']))[:6], tzinfo=utc)

    tweet.language, created = Language.objects.get_or_create(code=tweet_data['lang'])
    tweet.original_id = tweet_data['id']
    if tweet_data['user'].get('time_zone'):
        tweet.timezone, created = Timezone.objects.get_or_create(name=tweet_data['user']['time_zone'])

    tweet.sender, created = Person.objects.get_or_create(dataset=dataset_obj,
                                                         original_id=tweet_data['user']['id'],
                                                         defaults={'username': tweet_data['user']['screen_name'],
                                                                   'full_name': tweet_data['user']['name'],
                                                                   'language': Language.objects.get_or_create(
                                                                       code=tweet_data['user']['lang'])[0],
                                                                   'replied_to_count': 0,
                                                                   'shared_count': 0,
                                                                   'mentioned_count': 0,
                                                                   'friend_count': tweet_data['user']['friends_count'],
                                                                   'follower_count': tweet_data['user']['followers_count'],
                                                                   'message_count': tweet_data['user']['statuses_count']}
    )

    if tweet_data.get('retweeted_status') is not None:
        tweet.type, created = MessageType.objects.get_or_create(name="retweet")
    elif tweet_data.get('in_reply_to_status_id') is not None:
        tweet.type, created = MessageType.objects.get_or_create(name="reply")
    else:
        tweet.type, created = MessageType.objects.get_or_create(name="tweet")

    tweet.save()

    if len(tweet_data['entities']['hashtags']) > 0:
        tweet.contains_hashtag = True
        for hashtag in tweet_data['entities']['hashtags']:
            hashtag_obj, created = Hashtag.objects.get_or_create(text=hashtag['text'])
            tweet.hashtags.add(hashtag_obj)

    if len(tweet_data['entities']['urls']) > 0:
        tweet.contains_url = True
        for url in tweet_data['entities']['urls']:
            urlparse_results = urlparse(url['expanded_url'])
            domain = urlparse_results.netloc
            url_obj, created = Url.objects.get_or_create(full_url=url['expanded_url'], domain=domain,
                                                         short_url=url['url'])
            tweet.urls.add(url_obj)

    if tweet_data['entities'].get('media') is not None and len(tweet_data['entities']['media']) > 0:
        tweet.contains_media = True
        for me in tweet_data['entities']['media']:
            media_obj, created = Media.objects.get_or_create(type=me['type'], media_url=me['media_url'])
            tweet.media.add(media_obj)

    if len(tweet_data['entities']['user_mentions']) > 0:
        tweet.contains_mention = True
        for mention in tweet_data['entities']['user_mentions']:
            mention_obj, created = Person.objects.get_or_create(dataset=dataset_obj,
                                                                original_id=mention['id'],
                                                                defaults={'username': mention['screen_name'],
                                                                          'full_name': mention['name']})
            tweet.mentions.add(mention_obj)
    tweet.save()

    set_message_sentiment(tweet)

    return True

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