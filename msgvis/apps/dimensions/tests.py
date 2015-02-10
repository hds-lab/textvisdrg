from django.test import TestCase

from msgvis.apps.dimensions.models import Dimension


class DimensionModelTest(TestCase):
    def setUp(self):
        Dimension.objects.create(name='Time', slug='time',
                                 description='Time Dimension',
                                 scope=Dimension.SCOPE_OPEN_ENDED,
                                 type=Dimension.TYPE_QUANTITATIVE)

        Dimension.objects.create(name='Sentiment', slug='sentiment',
                                 description='Sentiment of message',
                                 scope=Dimension.SCOPE_CLOSED_ENDED,
                                 type=Dimension.TYPE_CATEGORICAL)


    def test_can_get_by_slug(self):
        """A stupid model retrieval test"""
        dtime = Dimension.objects.get(slug='time')
        dsentiment = Dimension.objects.get(slug='sentiment')

        self.assertNotEquals(dtime, None)
        self.assertNotEquals(dsentiment, None)
