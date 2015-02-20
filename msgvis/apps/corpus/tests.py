from datetime import datetime

from django.test import TestCase

from msgvis.apps.corpus import models as corpus_models


class DatasetModelTest(TestCase):
    def test_created_at_set(self):
        """Dataset.created_at should get set automatically."""
        dset = corpus_models.Dataset.objects.create(name="Test Corpus", description="My Dataset")
        self.assertIsInstance(dset.created_at, datetime)


class MessageModelTest(TestCase):
    def setUp(self):
        self.dataset = corpus_models.Dataset.objects.create(name="Test Corpus", description="My Dataset")

    def test_can_get_message(self):
        """Should be able to get messages from a dataset."""

        corpus_models.Message.objects.create(dataset=self.dataset, text="Some text")
        msgs = self.dataset.message_set.all()

        self.assertEquals(msgs.count(), 1)
        self.assertEquals(msgs.first().text, "Some text")


class GetExampleMessageTest(TestCase):
    def setUp(self):
        self.dataset = corpus_models.Dataset.objects.create(name="Test Corpus", description="My Dataset")

        corpus_models.Message.objects.create(
            dataset=self.dataset,
            text="blah blah blah",
            time="2015-02-02T01:19:02Z",
        )

        hashtag = corpus_models.Hashtag.objects.create(text="OurPriorities")
        msg = corpus_models.Message.objects.create(
            dataset=self.dataset,
            text="blah blah blah #%s" % hashtag.text,
            time="2015-02-02T01:19:02Z"
        )
        msg.hashtags.add(hashtag)

    def test_with_no_filters(self):
        """Empty filter settings should return all messages"""
        settings = {}
        msgs = self.dataset.get_example_messages(settings=settings)
        self.assertEquals(msgs.count(), 2)

    def test_with_inclusive_filters(self):
        """Filters that include all the messages."""
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

        msgs = self.dataset.get_example_messages(settings=settings)
        self.assertEquals(msgs.count(), 2)

    def test_with_exclusive_filters(self):
        """Filters that exclude all the messages"""
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
        msgs = self.dataset.get_example_messages(settings=settings)
        self.assertEquals(msgs.count(), 0)

    def test_partial_match(self):
        """Filters that match just one message"""

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
        msgs = self.dataset.get_example_messages(settings=settings)
        self.assertEquals(msgs.count(), 1)



