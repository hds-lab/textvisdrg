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

        mtype = registry.get_dimension('type')

        dset = corpus_models.Dataset.objects.get(pk=1)
        result = mtype.get_distribution(dataset=dset)

        # We got something back
        self.assertNotEquals(result, None)
        self.assertTrue(len(result) > 0)

        # It is the right type
        self.assertIsInstance(result[0], corpus_models.MessageType)

        # It counted something
        self.assertTrue(result[0].count > 0)


class DistributionTestCase(TransactionTestCase):
    def get_random_distribution(self, values, min=5, max=10):
        """Get a dictionary containing a random distribution over the values"""

        distrib = {}
        for value in values:
            distrib[value] = random.randrange(min, max)
        return distrib

    def generate_message_distribution(self, field_name, distribution, many=False):
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
                create_params = {
                    'text': "Message %d: %s = '%s'" % (num, field_name, value),
                    }

                if not many:
                    # If it's a flat field, we just send the value at this point
                    create_params[field_name] = value

                msg = dataset.message_set.create(**create_params)

                if many:
                    # Otherwise we need to add it after the fact
                    getattr(msg, field_name).add(value)

                num += 1

        return dataset


    def assertDistributionsEqual(self, result, desired_distribution):
        """Confirms the messages in the dataset match the distribution for the given field."""

        # Should match the length of the distribution
        self.assertEquals(len(result), len(desired_distribution))

        for row in result:
            # check the result row value is in the distribution

            # If the distribution is on a ForeignKey field we get back
            # model objects augmented with a count field.
            # Otherwise, it's just a dict with value/count keys.
            if hasattr(row, 'id'):
                value = row.id
                count = row.count
            else:
                value = row['value']
                count = row['count']

            self.assertIn(value, desired_distribution)

            # check the count is correct
            self.assertEquals(count, desired_distribution[value])

class CategoricalDistributionsTest(DistributionTestCase):
    fixtures = ['sentiments']

    def test_related_model_distribution(self):
        """
        Checks that the distribution of a categorical related model field,
        in this case Sentiment, can be calculated correctly.
        """

        sentiment_ids = corpus_models.Sentiment.objects.values_list('id', flat=True).distinct()

        sentiment_distribution = self.get_random_distribution(sentiment_ids)

        dataset = self.generate_message_distribution(
            field_name='sentiment_id',
            distribution=sentiment_distribution,
        )

        calculator = distributions.ForeignKeyDistribution()

        # Calculate the categorical distribution over the field name
        result = calculator.group_by(dataset, field_name='sentiment')

        self.assertDistributionsEqual(result, sentiment_distribution)

    def test_many_related_model_distribution(self):
        """
        Checks that the distribution of a categorical many-to-many related model field,
        in this case Hashtags, can be calculated correctly.
        """

        # Create some hashtags
        for ht in range(5):
            corpus_models.Hashtag.objects.create(
                text="#ht%d" % ht
            )

        hashtag_ids = corpus_models.Hashtag.objects.values_list('id', flat=True).distinct()
        hashtag_distribution = self.get_random_distribution(hashtag_ids)

        dataset = self.generate_message_distribution(
            field_name='hashtags',
            distribution=hashtag_distribution,
            many=True,
        )

        calculator = distributions.ForeignKeyDistribution()

        # Calculate the categorical distribution over the field name
        result = calculator.group_by(dataset, field_name='hashtags')
        self.assertDistributionsEqual(result, hashtag_distribution)

    def test_boolean_distribution(self):
        """
        Checks that the distribution of a boolean field, in this case
        'contains_hashtag', can be calculated correctly.
        """

        values = [True, False]
        bool_distribution = self.get_random_distribution(values)

        dataset = self.generate_message_distribution(
            field_name='contains_url',
            distribution=bool_distribution,
        )

        calculator = distributions.CategoricalDistribution()
        result = calculator.group_by(dataset, field_name='contains_url')
        self.assertDistributionsEqual(result, bool_distribution)

class QuantitativeDistributionsTest(DistributionTestCase):

    def test_count_distribution(self):
        """
        Checks that the distribution of a count field,
        in this case shared_count, can be calculated correctly.
        """

        shared_counts = range(0, 12)
        shared_count_distribution = self.get_random_distribution(shared_counts)
        dataset = self.generate_message_distribution(
            field_name='shared_count',
            distribution=shared_count_distribution,
        )

        calculator = distributions.QuantitativeDistribution()
        result = calculator.group_by(dataset, field_name='shared_count')
        self.assertDistributionsEqual(result, shared_count_distribution)
