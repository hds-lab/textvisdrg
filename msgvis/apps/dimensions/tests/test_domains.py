"""Test that the registered dimensions can get their domains"""

from django.test import TestCase

from datetime import timedelta
from django.utils import timezone as tz

from django.conf import settings

from msgvis.apps.dimensions import registry
from msgvis.apps.base.tests import DistributionTestCaseMixins
from msgvis.apps.corpus import models as corpus_models


class CategoricalDomainTest(DistributionTestCaseMixins, TestCase):
    def test_related_categorical_domain(self):
        """
        Checks that the domain of a categorical related model field,
        in this case Language, can be calculated correctly.
        """

        # Create some language labels
        languages = self.create_test_languages(model=True)
        language_ids = [lang.id for lang in languages]
        language_names = [lang.name for lang in languages]
        dimension = registry.get_dimension('language')

        # Generate a distribution where messages increase with each lang id
        language_distribution = self.get_distribution(language_ids)
        dataset = self.generate_messages_for_distribution(
            field_name='language_id',
            distribution=language_distribution,
        )
        result = dimension.get_domain(dataset.message_set.all())
        # results are in descending frequency order
        self.assertEquals(result, list(reversed(language_names)))

        # Generate another dataset with the distribution going the other way
        language_distribution = self.get_distribution(reversed(language_ids))
        dataset = self.generate_messages_for_distribution(
            field_name='language_id',
            distribution=language_distribution,
        )
        result = dimension.get_domain(dataset.message_set.all())
        self.assertEquals(result, language_names)

    def test_categorical_domain(self):
        """
        Checks that the domain of a categorical model field,
        in this case Sentiment, can be calculated correctly.
        """

        # Create some language labels
        sentiment_values, sentiment_labels = zip(*corpus_models.Message.SENTIMENT_CHOICES)

        sentiment_distribution = self.get_distribution(sentiment_values)

        dataset = self.generate_messages_for_distribution(
            field_name='sentiment',
            distribution=sentiment_distribution,
        )

        dimension = registry.get_dimension('sentiment')

        # Calculate the categorical distribution over the field name
        result = dimension.get_domain(dataset.message_set.all())

        # in order of CHOICES
        self.assertEquals(result, sentiment_values)

    def test_boolean_domain(self):
        dataset = self.create_empty_dataset()

        dimension = registry.get_dimension('contains_url')
        result = dimension.get_domain(dataset.message_set.all())
        result = list(result)
        self.assertEquals(len(result), 2)
        self.assertEquals(result, dimension.domain)

    def test_quantitative_domain(self):

        reply_values = [1, 2001]
        distribution = self.get_distribution(reply_values)
        dataset = self.generate_messages_for_distribution('replied_to_count', distribution)
        
        dimension = registry.get_dimension('replies')
        result = dimension.get_domain(dataset.message_set.all(), bins=10)
        result = list(result)
        
        self.assertEquals(result, [0, 200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000, 2200])
        
    def test_time_domain(self):
        base_time = tz.datetime(2012, 5, 2, 20, 10, 2, 0)
        if settings.USE_TZ:
            base_time = base_time.replace(tzinfo=tz.utc)

        time_values = [base_time, base_time + timedelta(days=1)]
        distribution = self.get_distribution(time_values)
        dataset = self.generate_messages_for_distribution('time', distribution)
        dimension = registry.get_dimension('time')
        result = dimension.get_domain(dataset.message_set.all(), bins=24)
        
        self.assertEquals(len(result), 26)
        self.assertEquals(result[0], base_time.replace(minute=0, second=0))
        self.assertEquals(result[24], time_values[1].replace(minute=0, second=0))
        self.assertEquals(result[25], time_values[1].replace(minute=0, second=0) + timedelta(hours=1))
