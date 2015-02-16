from django.test import TestCase

from models import set_message_sentiment
from msgvis.apps.importer.models import create_an_instance_from_json
from msgvis.apps.corpus.models import Dataset, Message

# Create your tests here.
class MessageSentimentTest(TestCase):
    def setUp(self):
        self.dataset = Dataset.objects.create(name="Test Corpus", description="My Dataset")
        test_tweet = r"""{"contributors": null, "truncated": false, "text": "I hate that", "in_reply_to_status_id": null, "id": 562057573302431746, "favorite_count": 0, "source": "<a href=\"http://blackberry.com/twitter\" rel=\"nofollow\">Twitter for BlackBerry\u00ae</a>", "retweeted": false, "coordinates": null, "timestamp_ms": "1422839942657", "entities": {"user_mentions": [], "symbols": [], "trends": [], "hashtags": [{"indices": [93, 107], "text": "OurPriorities"}], "urls": []}, "in_reply_to_screen_name": null, "id_str": "562057573302431746", "retweet_count": 0, "in_reply_to_user_id": null, "favorited": false, "user": {"follow_request_sent": null, "profile_use_background_image": true, "default_profile_image": false, "id": 2223209961, "verified": false, "profile_image_url_https": "https://pbs.twimg.com/profile_images/451825921167994881/8XWideg5_normal.jpeg", "profile_sidebar_fill_color": "DDEEF6", "profile_text_color": "333333", "followers_count": 114, "profile_sidebar_border_color": "C0DEED", "id_str": "2223209961", "profile_background_color": "C0DEED", "listed_count": 4, "profile_background_image_url_https": "https://abs.twimg.com/images/themes/theme1/bg.png", "utc_offset": null, "statuses_count": 4336, "description": "I don't exist. You don't exist. Nothing is real. But enjoy your non-real existence", "friends_count": 274, "location": "", "profile_link_color": "0084B4", "profile_image_url": "http://pbs.twimg.com/profile_images/451825921167994881/8XWideg5_normal.jpeg", "following": null, "geo_enabled": true, "profile_banner_url": "https://pbs.twimg.com/profile_banners/2223209961/1421816307", "profile_background_image_url": "http://abs.twimg.com/images/themes/theme1/bg.png", "name": "Melissa", "lang": "en", "profile_background_tile": false, "favourites_count": 1266, "screen_name": "Brooklyn_Newsie", "notifications": null, "url": "http://www.brunette-the-strange.pinterest.com", "created_at": "Fri Dec 13 10:57:43 +0000 2013", "contributors_enabled": false, "time_zone": null, "protected": false, "default_profile": true, "is_translator": false}, "geo": null, "in_reply_to_user_id_str": null, "possibly_sensitive": false, "lang": "en", "created_at": "Mon Feb 02 01:19:02 +0000 2015", "filter_level": "low", "in_reply_to_status_id_str": null, "place": null}"""
        create_an_instance_from_json(test_tweet, self.dataset)

    def test_sentiment(self):
        """Dataset.created_at should get set automatically."""

        msg = Message.objects.all()[0]
        set_message_sentiment(msg)

        self.assertEquals(msg.sentiment.name, "negative")

