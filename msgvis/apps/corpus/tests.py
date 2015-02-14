from datetime import datetime

from django.test import TestCase

from models import Dataset, Message, get_example_messages


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
        Message.objects.create(dataset=self.dataset, text="Some text", time="2015-02-02T01:19:02Z")

    def test_get_example_message(self):
        """Dataset.created_at should get set automatically."""
        settings = {}
        msgs = get_example_messages(settings=settings)
        self.assertEquals(msgs.count(), 1)

        settings = {
            "dimensions": ["time", "hashtag"],
            "filters": [
                {
                  "dimension": "time",
                  "min": "2015-02-02T01:19:02Z",
                  "max": "2015-02-02T01:19:03Z"
                }
              ],
            "focus": {
                "time": "2015-02-02T01:19:02Z"
            }
        }
        msgs = get_example_messages(settings=settings)
        self.assertEquals(msgs.count(), 1)

        settings = {
            "dimensions": ["time", "hashtag"],
            "filters": [
                {
                  "dimension": "time",
                  "min": "2015-02-02T01:19:03Z",
                  "max": "2015-02-02T01:19:03Z"
                }
              ],
            "focus": {
                "time": "2015-02-02T01:19:03Z"
            }
        }
        msgs = get_example_messages(settings=settings)
        self.assertEquals(msgs.count(), 0)

