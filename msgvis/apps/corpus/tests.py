from datetime import datetime

from django.test import TestCase

from models import Dataset, Message, get_example_messages
from msgvis.apps.importer.models import create_an_instance_from_json


class DatasetModelTest(TestCase):
    def test_created_at_set(self):
        """Dataset.created_at should get set automatically."""
        dset = Dataset.objects.create(name="Test Corpus", description="My Dataset")
        self.assertIsInstance(dset.created_at, datetime)


class MessageModelTest(TestCase):
    def setUp(self):
        self.dataset = Dataset.objects.create(name="Test Corpus", description="My Dataset")

    def test_can_get_message(self):
        """Should be able to get messages from a dataset."""

        Message.objects.create(dataset=self.dataset, text="Some text")
        msgs = self.dataset.message_set.all()

        self.assertEquals(msgs.count(), 1)
        self.assertEquals(msgs.first().text, "Some text")

class GetExampleMessageTest(TestCase):
    def setUp(self):
        self.dataset = Dataset.objects.create(name="Test Corpus", description="My Dataset")
        test_tweet = r"""{"contributors": null, "truncated": false, "text": "RT @vifubutojiwa: \uff13\u6708\u30fb\u30fb\u30fb\u5225\u308c\u306e\u5b63\u7bc0\u307e\u3067\u306b\u3001\n\u304d\u308c\u3044\u306b\u306a\u308a\u305f\u3044\u5973\u5b50\u96c6\u5408\u301c\uff01\uff01\n\u3084\u3063\u305f\u3089\u5f7c\u6c0f\u3067\u6765\u3061\u3083\u3063\u305f\u2661\n\n\u30b3\u30ec\u21d2http://t.co/ZOjvtpicy3\n\n\u544a\u767d\u3001\u5927\u6210\u529f\u3057\u305f\u3044\u4eba\uff01\n\u6025\u3052\u301c\u301c\u301c\u301c\uff01\uff01\uff01\nhttp://t.co/ZIXytozeHN", "in_reply_to_status_id": null, "id": 562057573306609665, "favorite_count": 0, "source": "<a href=\"http://yahoo.co.jp\" rel=\"nofollow\">\u3010\u753b\u50cf\u3011\u6e21\u8fba\u9ebb\u53cb\u306e\u904e\u6fc0\u3067\u30b8\u30e7\u30ea\u30b8\u30e7\u30ea\u306a\u30ef\u30ad\uff57\uff57\uff57\uff57\uff57\uff57</a>", "retweeted": false, "coordinates": null, "timestamp_ms": "1422839942658", "entities": {"symbols": [], "media": [{"source_status_id_str": "562042011570540544", "expanded_url": "http://twitter.com/vifubutojiwa/status/562042011570540544/photo/1", "display_url": "pic.twitter.com/ZIXytozeHN", "url": "http://t.co/ZIXytozeHN", "media_url_https": "https://pbs.twimg.com/media/B8zGOoFCUAAbIsM.jpg", "source_status_id": 562042011570540544, "id_str": "562042008093478912", "sizes": {"small": {"h": 232, "resize": "fit", "w": 340}, "large": {"h": 438, "resize": "fit", "w": 640}, "medium": {"h": 410, "resize": "fit", "w": 600}, "thumb": {"h": 150, "resize": "crop", "w": 150}}, "indices": [113, 135], "type": "photo", "id": 562042008093478912, "media_url": "http://pbs.twimg.com/media/B8zGOoFCUAAbIsM.jpg"}], "hashtags": [], "user_mentions": [{"id": 2537819460, "indices": [3, 16], "id_str": "2537819460", "screen_name": "vifubutojiwa", "name": "\u30e2\u30c6\u5973\u306b\u306a\u308b\u65b9\u6cd5"}], "trends": [], "urls": [{"url": "http://t.co/ZOjvtpicy3", "indices": [67, 89], "expanded_url": "http://bit.ly/15rFGhE", "display_url": "bit.ly/15rFGhE"}]}, "in_reply_to_screen_name": null, "id_str": "562057573306609665", "retweet_count": 0, "in_reply_to_user_id": null, "favorited": false, "retweeted_status": {"contributors": null, "truncated": false, "text": "\uff13\u6708\u30fb\u30fb\u30fb\u5225\u308c\u306e\u5b63\u7bc0\u307e\u3067\u306b\u3001\n\u304d\u308c\u3044\u306b\u306a\u308a\u305f\u3044\u5973\u5b50\u96c6\u5408\u301c\uff01\uff01\n\u3084\u3063\u305f\u3089\u5f7c\u6c0f\u3067\u6765\u3061\u3083\u3063\u305f\u2661\n\n\u30b3\u30ec\u21d2http://t.co/ZOjvtpicy3\n\n\u544a\u767d\u3001\u5927\u6210\u529f\u3057\u305f\u3044\u4eba\uff01\n\u6025\u3052\u301c\u301c\u301c\u301c\uff01\uff01\uff01\nhttp://t.co/ZIXytozeHN", "in_reply_to_status_id": null, "id": 562042067321241601, "favorite_count": 39, "source": "<a href=\"https://about.twitter.com/products/tweetdeck\" rel=\"nofollow\">TweetDeck</a>", "retweeted": false, "coordinates": null, "entities": {"symbols": [], "media": [{"source_status_id_str": "562042011570540544", "expanded_url": "http://twitter.com/vifubutojiwa/status/562042011570540544/photo/1", "display_url": "pic.twitter.com/ZIXytozeHN", "url": "http://t.co/ZIXytozeHN", "media_url_https": "https://pbs.twimg.com/media/B8zGOoFCUAAbIsM.jpg", "source_status_id": 562042011570540544, "id_str": "562042008093478912", "sizes": {"small": {"h": 232, "resize": "fit", "w": 340}, "large": {"h": 438, "resize": "fit", "w": 640}, "medium": {"h": 410, "resize": "fit", "w": 600}, "thumb": {"h": 150, "resize": "crop", "w": 150}}, "indices": [95, 117], "type": "photo", "id": 562042008093478912, "media_url": "http://pbs.twimg.com/media/B8zGOoFCUAAbIsM.jpg"}], "hashtags": [], "user_mentions": [], "trends": [], "urls": [{"url": "http://t.co/ZOjvtpicy3", "indices": [49, 71], "expanded_url": "http://bit.ly/15rFGhE", "display_url": "bit.ly/15rFGhE"}]}, "in_reply_to_screen_name": null, "id_str": "562042067321241601", "retweet_count": 17805, "in_reply_to_user_id": null, "favorited": false, "user": {"follow_request_sent": null, "profile_use_background_image": true, "default_profile_image": false, "id": 2537819460, "verified": false, "profile_image_url_https": "https://pbs.twimg.com/profile_images/549131945985056768/pJRlrXA4_normal.png", "profile_sidebar_fill_color": "DDEEF6", "profile_text_color": "333333", "followers_count": 417, "profile_sidebar_border_color": "C0DEED", "id_str": "2537819460", "profile_background_color": "C0DEED", "listed_count": 2, "profile_background_image_url_https": "https://abs.twimg.com/images/themes/theme1/bg.png", "utc_offset": 32400, "statuses_count": 3, "description": null, "friends_count": 8, "location": "", "profile_link_color": "0084B4", "profile_image_url": "http://pbs.twimg.com/profile_images/549131945985056768/pJRlrXA4_normal.png", "following": null, "geo_enabled": false, "profile_background_image_url": "http://abs.twimg.com/images/themes/theme1/bg.png", "name": "\u30e2\u30c6\u5973\u306b\u306a\u308b\u65b9\u6cd5", "lang": "ja", "profile_background_tile": false, "favourites_count": 0, "screen_name": "vifubutojiwa", "notifications": null, "url": null, "created_at": "Sat May 31 16:44:10 +0000 2014", "contributors_enabled": false, "time_zone": "Seoul", "protected": false, "default_profile": true, "is_translator": false}, "geo": null, "in_reply_to_user_id_str": null, "possibly_sensitive": false, "lang": "ja", "created_at": "Mon Feb 02 00:17:25 +0000 2015", "filter_level": "low", "in_reply_to_status_id_str": null, "place": null, "extended_entities": {"media": [{"source_status_id_str": "562042011570540544", "expanded_url": "http://twitter.com/vifubutojiwa/status/562042011570540544/photo/1", "display_url": "pic.twitter.com/ZIXytozeHN", "url": "http://t.co/ZIXytozeHN", "media_url_https": "https://pbs.twimg.com/media/B8zGOoFCUAAbIsM.jpg", "source_status_id": 562042011570540544, "id_str": "562042008093478912", "sizes": {"small": {"h": 232, "resize": "fit", "w": 340}, "large": {"h": 438, "resize": "fit", "w": 640}, "medium": {"h": 410, "resize": "fit", "w": 600}, "thumb": {"h": 150, "resize": "crop", "w": 150}}, "indices": [95, 117], "type": "photo", "id": 562042008093478912, "media_url": "http://pbs.twimg.com/media/B8zGOoFCUAAbIsM.jpg"}]}}, "user": {"follow_request_sent": null, "profile_use_background_image": true, "default_profile_image": false, "id": 2451370675, "verified": false, "profile_image_url_https": "https://pbs.twimg.com/profile_images/503810863896080385/JY4ZNhjq_normal.jpeg", "profile_sidebar_fill_color": "DDEEF6", "profile_text_color": "333333", "followers_count": 157, "profile_sidebar_border_color": "C0DEED", "id_str": "2451370675", "profile_background_color": "C0DEED", "listed_count": 5, "profile_background_image_url_https": "https://abs.twimg.com/images/themes/theme1/bg.png", "utc_offset": null, "statuses_count": 3521, "description": null, "friends_count": 76, "location": "", "profile_link_color": "0084B4", "profile_image_url": "http://pbs.twimg.com/profile_images/503810863896080385/JY4ZNhjq_normal.jpeg", "following": null, "geo_enabled": false, "profile_banner_url": "https://pbs.twimg.com/profile_banners/2451370675/1408952925", "profile_background_image_url": "http://abs.twimg.com/images/themes/theme1/bg.png", "name": "\uff78\uff7f\uff88\uff90\u307e\u3055\u3068\u3045\u30fc", "lang": "ja", "profile_background_tile": false, "favourites_count": 1568, "screen_name": "masanagi31", "notifications": null, "url": null, "created_at": "Fri Apr 18 13:25:16 +0000 2014", "contributors_enabled": false, "time_zone": null, "protected": false, "default_profile": true, "is_translator": false}, "geo": null, "in_reply_to_user_id_str": null, "possibly_sensitive": false, "lang": "ja", "created_at": "Mon Feb 02 01:19:02 +0000 2015", "filter_level": "low", "in_reply_to_status_id_str": null, "place": null, "extended_entities": {"media": [{"source_status_id_str": "562042011570540544", "expanded_url": "http://twitter.com/vifubutojiwa/status/562042011570540544/photo/1", "display_url": "pic.twitter.com/ZIXytozeHN", "url": "http://t.co/ZIXytozeHN", "media_url_https": "https://pbs.twimg.com/media/B8zGOoFCUAAbIsM.jpg", "source_status_id": 562042011570540544, "id_str": "562042008093478912", "sizes": {"small": {"h": 232, "resize": "fit", "w": 340}, "large": {"h": 438, "resize": "fit", "w": 640}, "medium": {"h": 410, "resize": "fit", "w": 600}, "thumb": {"h": 150, "resize": "crop", "w": 150}}, "indices": [113, 135], "type": "photo", "id": 562042008093478912, "media_url": "http://pbs.twimg.com/media/B8zGOoFCUAAbIsM.jpg"}]}}"""
        create_an_instance_from_json(test_tweet, self.dataset)
        test_tweet = r"""{"contributors": null, "truncated": false, "text": "The amount of money America puts into the SuperBowl could probably pay off out National Debt #OurPriorities", "in_reply_to_status_id": null, "id": 562057573302431746, "favorite_count": 0, "source": "<a href=\"http://blackberry.com/twitter\" rel=\"nofollow\">Twitter for BlackBerry\u00ae</a>", "retweeted": false, "coordinates": null, "timestamp_ms": "1422839942657", "entities": {"user_mentions": [], "symbols": [], "trends": [], "hashtags": [{"indices": [93, 107], "text": "OurPriorities"}], "urls": []}, "in_reply_to_screen_name": null, "id_str": "562057573302431746", "retweet_count": 0, "in_reply_to_user_id": null, "favorited": false, "user": {"follow_request_sent": null, "profile_use_background_image": true, "default_profile_image": false, "id": 2223209961, "verified": false, "profile_image_url_https": "https://pbs.twimg.com/profile_images/451825921167994881/8XWideg5_normal.jpeg", "profile_sidebar_fill_color": "DDEEF6", "profile_text_color": "333333", "followers_count": 114, "profile_sidebar_border_color": "C0DEED", "id_str": "2223209961", "profile_background_color": "C0DEED", "listed_count": 4, "profile_background_image_url_https": "https://abs.twimg.com/images/themes/theme1/bg.png", "utc_offset": null, "statuses_count": 4336, "description": "I don't exist. You don't exist. Nothing is real. But enjoy your non-real existence", "friends_count": 274, "location": "", "profile_link_color": "0084B4", "profile_image_url": "http://pbs.twimg.com/profile_images/451825921167994881/8XWideg5_normal.jpeg", "following": null, "geo_enabled": true, "profile_banner_url": "https://pbs.twimg.com/profile_banners/2223209961/1421816307", "profile_background_image_url": "http://abs.twimg.com/images/themes/theme1/bg.png", "name": "Melissa", "lang": "en", "profile_background_tile": false, "favourites_count": 1266, "screen_name": "Brooklyn_Newsie", "notifications": null, "url": "http://www.brunette-the-strange.pinterest.com", "created_at": "Fri Dec 13 10:57:43 +0000 2013", "contributors_enabled": false, "time_zone": null, "protected": false, "default_profile": true, "is_translator": false}, "geo": null, "in_reply_to_user_id_str": null, "possibly_sensitive": false, "lang": "en", "created_at": "Mon Feb 02 01:19:02 +0000 2015", "filter_level": "low", "in_reply_to_status_id_str": null, "place": null}"""
        create_an_instance_from_json(test_tweet, self.dataset)
        #Message.objects.create(dataset=self.dataset, text="Some text", time="2015-02-02T01:19:02Z")

    def test_get_example_message(self):
        """Dataset.created_at should get set automatically."""
        settings = {}
        msgs = get_example_messages(settings=settings)
        self.assertEquals(msgs.count(), 2)

        settings = {
            "dimensions": ["time", "hashtags"],
            "filters": [
                {
                  "dimension": "time",
                  "min": "2015-02-02T01:19:02Z",
                  "max": "2015-02-02T01:19:03Z"
                }
              ],
            "focus": [
                {
                  "dimension": "time",
                  "value": "2015-02-02T01:19:02Z",
                }
            ],
        }
        msgs = get_example_messages(settings=settings)
        self.assertEquals(msgs.count(), 2)

        settings = {
            "dimensions": ["time", "hashtags"],
            "filters": [
                {
                  "dimension": "time",
                  "min": "2015-02-02T01:19:03Z",
                  "max": "2015-02-02T01:19:03Z"
                }
              ],
            "focus": [
                {
                  "dimension": "time",
                  "value": "2015-02-02T01:19:03Z",
                }
            ],
        }
        msgs = get_example_messages(settings=settings)
        self.assertEquals(msgs.count(), 0)
        settings = {
            "dimensions": ["time", "hashtags"],
            "filters": [
                {
                  "dimension": "time",
                  "min": "2015-02-02T01:19:03Z",
                  "max": "2015-02-02T01:19:03Z"
                }
              ],
            "focus": [
                {
                  "dimension": "hashtags",
                  "value": "OurPriorities",
                }
            ],
        }
        msgs = get_example_messages(settings=settings)
        self.assertEquals(msgs.count(), 1)

