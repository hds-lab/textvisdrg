from django.test import TestCase, TransactionTestCase

from msgvis.apps.corpus import models as corpus_models
from msgvis.apps.dimensions import models, distributions, registry

import random



class DimensionRegistryTest(TestCase):
    def test_registry_contains_dimension(self):
        """The registry should have some dimensions"""
        time = registry.get_dimension('time')
        self.assertIsNotNone(time)
        self.assertIsInstance(time, models.TimeDimension)

    def test_registry_size(self):
        """The number of dimensions registered should be 20"""
        self.assertEquals(len(registry.get_dimension_ids()), 20)


class DimensionDistributionTest(TransactionTestCase):
    fixtures = ['dimensions_test_corpus', ]


    def test_can_get_distribution(self):
        """Just check that the Dimension.get_distribution method runs"""

        sentiment = registry.get_dimension('sentiment')

        dset = corpus_models.Dataset.objects.get(pk=1)
        result = sentiment.get_distribution(dataset=dset)
        self.assertNotEquals(result, None)
        self.assertTrue(len(result) > 0)
        self.assertIsInstance(result[0], dict)


def generate_message_distribution(field_name, distribution):
    """
    Generates a bunch of messages for testing.
    On each message, the given field will be set to some value,
    according to the distribution indicating how often
    each value should occur. Returns a dataset
    containing the messages.
    """

    dataset = corpus_models.Dataset.objects.create(
        name="Test %s distribution" % field_name,
        description="Created by generate_message_distribution",
    )

    num = 0
    for value, count in distribution.iteritems():
        for i in range(count):
            dataset.message_set.create(**{
                field_name: value,
                'text': "Message %d: %s = '%s'" % (num, field_name, value),
            })
            num += 1

    return dataset


class CategoricalDistributionTest(TransactionTestCase):
    fixtures = ['sentiments']

    def get_random_distribution(self, values, min=5, max=10):
        """Get a dictionary containing a random distribution over the values"""

        distrib = {}
        for value in values:
            distrib[value] = random.randrange(min, max)
        return distrib

    def assertMessagesMatchDistribution(self, dataset, field_name, distribution):
        """Confirms the messages in the dataset match the distribution for the given field."""

        # Calculate the categorical distribution over the field name
        calc = distributions.CategoricalDistribution()
        result = calc.group_by(dataset.message_set.all(), field_name=field_name)

        # Should match the length of the distribution
        self.assertEquals(len(result), len(distribution))

        for row in result:
            # check the result row value is in the distribution
            self.assertIn(row['value'], distribution)

            # check the count is correct
            self.assertEquals(row['count'], distribution[row['value']])

    def test_related_model_distribution(self):
        """
        Checks that the distribution of a categorical related model field,
        in this case Sentiment, can be calculated correctly.
        """

        sentiment_ids = corpus_models.Sentiment.objects.values_list('id', flat=True).distinct()

        distribution = self.get_random_distribution(sentiment_ids)
        field_name = 'sentiment_id'

        dataset = generate_message_distribution(
            field_name=field_name,
            distribution=distribution,
        )

        self.assertMessagesMatchDistribution(dataset, field_name, distribution)

    def test_boolean_distribution(self):
        """
        Checks that the distribution of a boolean field, in this case
        'contains_hashtag', can be calculated correctly.
        """

        values = [True, False]
        distribution = self.get_random_distribution(values)
        field_name = 'contains_url'

        dataset = generate_message_distribution(
            field_name=field_name,
            distribution=distribution,
        )

        self.assertMessagesMatchDistribution(dataset, field_name, distribution)
