# -*- coding: utf-8 -*-
from django.test import TestCase
from msgvis.apps.corpus.models import Dataset, Message
from msgvis.apps.questions.models import Article, Question

from models import create_an_instance_from_json, load_research_questions_from_json


# Create your tests here.
class ImportTest(TestCase):

    def test_import_tweets(self):
        """Dataset.created_at should get set automatically."""
        dset = Dataset.objects.create(name="Test Corpus", description="My Dataset")

        test_tweet = r"""{u'contributors': None, u'truncated': False, u'text': u'#martinwattenberg uses translation to Traditional Chinese in Google Translate for a demonstration in his talk!!!!', u'in_reply_to_status_id': None, u'id': 570735009314656256, u'favorite_count': 0, u'source': u'<a href="http://twitter.com" rel="nofollow">Twitter Web Client</a>', u'retweeted': False, u'coordinates': None, u'entities': {u'symbols': [], u'user_mentions': [], u'hashtags': [{u'indices': [0, 17], u'text': u'martinwattenberg'}], u'urls': []}, u'in_reply_to_screen_name': None, u'id_str': u'570735009314656256', u'retweet_count': 0, u'in_reply_to_user_id': None, u'favorited': False, u'user': {u'follow_request_sent': None, u'profile_use_background_image': True, u'profile_text_color': u'333333', u'default_profile_image': False, u'id': 1858716428, u'profile_background_image_url_https': u'https://abs.twimg.com/images/themes/theme1/bg.png', u'verified': False, u'profile_location': None, u'profile_image_url_https': u'https://pbs.twimg.com/profile_images/570735134517637120/mHZ-5Pmq_normal.jpeg', u'profile_sidebar_fill_color': u'DDEEF6', u'entities': {u'description': {u'urls': []}}, u'followers_count': 15, u'profile_sidebar_border_color': u'C0DEED', u'id_str': u'1858716428', u'profile_background_color': u'C0DEED', u'listed_count': 0, u'is_translation_enabled': False, u'utc_offset': 28800, u'statuses_count': 1, u'description': u'', u'friends_count': 24, u'location': u'', u'profile_link_color': u'0084B4', u'profile_image_url': u'http://pbs.twimg.com/profile_images/570735134517637120/mHZ-5Pmq_normal.jpeg', u'following': None, u'geo_enabled': False, u'profile_background_image_url': u'http://abs.twimg.com/images/themes/theme1/bg.png', u'name': u'Nan-Chen Chen', u'lang': u'en', u'profile_background_tile': False, u'favourites_count': 0, u'screen_name': u'nanchenchen', u'notifications': None, u'url': None, u'created_at': u'Thu Sep 12 22:14:04 +0000 2013', u'contributors_enabled': False, u'time_zone': u'Taipei', u'protected': False, u'default_profile': True, u'is_translator': False}, u'geo': None, u'in_reply_to_user_id_str': None, u'lang': u'en', u'created_at': u'Thu Feb 26 00:00:04 +0000 2015', u'in_reply_to_status_id_str': None, u'place': None}"""
        result = create_an_instance_from_json(test_tweet, dset)
        self.assertTrue(result)

        msg = dset.message_set.filter(original_id="562057573306609665")
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