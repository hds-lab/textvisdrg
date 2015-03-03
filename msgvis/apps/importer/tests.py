# -*- coding: utf-8 -*-
from django.test import TestCase
from msgvis.apps.corpus.models import Dataset, Message
from msgvis.apps.questions.models import Article, Question

from models import create_an_instance_from_json, load_research_questions_from_json, get_or_create_a_tweet_from_json_obj


# Create your tests here.
class ImportTest(TestCase):

    def test_mini_tweet(self):
        dset = Dataset.objects.create(name="Test Corpus", description="My Dataset")
        tmp_tweet = {
                        'id': 1234,
                        'user': {
                                    'id': 5678,
                                    'screen_name': 'test',
                                },
                        'in_reply_to_status_id': None
                    }
        msg = get_or_create_a_tweet_from_json_obj(tmp_tweet, dset)
        self.assertNotEquals(msg, None)

    def test_import_tweets(self):
        """Dataset.created_at should get set automatically."""
        dset = Dataset.objects.create(name="Test Corpus", description="My Dataset")

        test_tweet = r"""{"contributors": null, "truncated": false, "text": "#martinwattenberg uses translation to Traditional Chinese in Google Translate for a demonstration in his talk!!!!", "in_reply_to_status_id": null, "id": 570735009314656256, "favorite_count": 0, "source": "<a href=\"http://twitter.com\" rel=\"nofollow\">Twitter Web Client</a>", "retweeted": false, "coordinates": null, "entities": {"symbols": [], "user_mentions": [], "hashtags": [{"indices": [0, 17], "text": "martinwattenberg"}], "urls": []}, "in_reply_to_screen_name": null, "id_str": "570735009314656256", "retweet_count": 0, "in_reply_to_user_id": null, "favorited": false, "user": {"follow_request_sent": null, "profile_use_background_image": true, "profile_text_color": "333333", "default_profile_image": false, "id": 1858716428, "profile_background_image_url_https": "https://abs.twimg.com/images/themes/theme1/bg.png", "verified": false, "profile_location": null, "profile_image_url_https": "https://pbs.twimg.com/profile_images/570735134517637120/mHZ-5Pmq_normal.jpeg", "profile_sidebar_fill_color": "DDEEF6", "entities": {"description": {"urls": []}}, "followers_count": 15, "profile_sidebar_border_color": "C0DEED", "id_str": "1858716428", "profile_background_color": "C0DEED", "listed_count": 0, "is_translation_enabled": false, "utc_offset": 28800, "statuses_count": 1, "description": "", "friends_count": 24, "location": "", "profile_link_color": "0084B4", "profile_image_url": "http://pbs.twimg.com/profile_images/570735134517637120/mHZ-5Pmq_normal.jpeg", "following": null, "geo_enabled": false, "profile_background_image_url": "http://abs.twimg.com/images/themes/theme1/bg.png", "name": "Nan-Chen Chen", "lang": "en", "profile_background_tile": false, "favourites_count": 0, "screen_name": "nanchenchen", "notifications": null, "url": null, "created_at": "Thu Sep 12 22:14:04 +0000 2013", "contributors_enabled": false, "time_zone": "Taipei", "protected": false, "default_profile": true, "is_translator": false}, "geo": null, "in_reply_to_user_id_str": null, "lang": "en", "created_at": "Thu Feb 26 00:00:04 +0000 2015", "in_reply_to_status_id_str": null, "place": null}"""
        result = create_an_instance_from_json(test_tweet, dset)
        self.assertTrue(result)

        msg = dset.message_set.filter(original_id="570735009314656256")
        self.assertEquals(msg.count(), 1)


    def test_import_questions(self):
        json_str = r"""[{
                            "source":{
                                "authors":"Shaomei Wu\nJake M. Hofman\nWinter A. Mason\nDuncan J. Watts",
                                "link":"http:\/\/nanro.org\/~nanchen\/social_science_papers\/pdfs\/Wu et al_2011_Who says what to whom on twitter.pdf",
                                "title":"Who says what to whom on twitter",
                                "year":"2011",
                                "venue":"Proceedings of the 20th international conference on World wide web"
                            },
                            "dimensions":[
                                "urls",
                                "media",
                                "age",
                                "gender",
                                "sender_message_count",
                                "sender_reply_count",
                                "sender_mention_count",
                                "sender_friend_count",
                                "sender_follower_count"
                            ],
                            "text":"What 12\\types of content\\ are emphasized by 3456789\\different categories of users\\?"
                        }]"""


        result = load_research_questions_from_json(json_str)
        self.assertTrue(result)

        question = Question.objects.get(text="""What 12\\types of content\\ are emphasized by 3456789\\different categories of users\\?""")
        self.assertEquals(len(question.dimensions.all()), 9)

        article = question.source
        self.assertEquals(article.year, 2011)