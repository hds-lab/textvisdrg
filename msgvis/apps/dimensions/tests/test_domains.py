"""Test that the registered dimensions can get their domains"""

from django.test import TestCase

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
        language_codes = [lang.code for lang in languages]
        dimension = registry.get_dimension('language')

        # Generate a distribution where messages increase with each lang id
        language_distribution = self.get_distribution(language_ids)
        dataset = self.generate_messages_for_distribution(
            field_name='language_id',
            distribution=language_distribution,
        )
        result = dimension.get_domain(dataset.message_set.all())
        # results are in descending frequency order
        self.assertEquals(result, list(reversed(language_codes)))

        # Generate another dataset with the distribution going the other way
        language_distribution = self.get_distribution(reversed(language_ids))
        dataset = self.generate_messages_for_distribution(
            field_name='language_id',
            distribution=language_distribution,
        )
        result = dimension.get_domain(dataset.message_set.all())
        self.assertEquals(result, language_codes)

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

        # in descending order by frequency
        self.assertEquals(result, list(reversed(sentiment_values)))

    def test_boolean_domain(self):
        dataset = self.create_empty_dataset()

        dimension = registry.get_dimension('contains_url')
        result = dimension.get_domain(dataset.message_set.all())
        result = list(result)
        result.sort()

        expected = [False, True]
        expected.sort()

        self.assertEquals(result, expected)
