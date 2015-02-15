"""Test the distributions"""

from django.test import TestCase

from msgvis.apps.dimensions import distributions
from msgvis.apps.corpus import models as corpus_models

from django.conf import settings
from django.utils import timezone as tz
from django.utils import dateparse


class DistributionTestCaseMixins(object):
    """Some utilities for working with distributions"""

    def get_distribution(self, values, min_count=5):
        """Get a dictionary containing a (deterministic) distribution over the values"""
        distrib = {}
        for idx, value in enumerate(values):
            distrib[value] = min_count + idx
        return distrib

    def generate_messages_for_distribution(self, field_name, distribution, many=False, dataset=None):
        """
        Generates a bunch of messages for testing.
        On each message, the given field will be set to some value,
        according to the distribution indicating how often
        each value should occur. Returns a dataset
        containing the messages.
        """

        if dataset is None:
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
        """
        Confirms the messages in the dataset match the distribution for the given field.
        Allows for missing entries in the result due to zeros.
        """

        # It's alright if it is missing zero-count values.
        zeros = {}
        for value, count in desired_distribution.iteritems():
            if count == 0:
                zeros[value] = count

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

            # check the count is correct
            self.assertIn(value, desired_distribution)
            self.assertEquals(count, desired_distribution[value])

            if count == 0:
                del zeros[value]

        # Should match the length of the distribution
        self.assertEquals(len(result), len(desired_distribution) - len(zeros))


class CategoricalDistributionsTest(DistributionTestCaseMixins, TestCase):
    def test_related_model_distribution(self):
        """
        Checks that the distribution of a categorical related model field,
        in this case Sentiment, can be calculated correctly.
        """

        # Create some sentiment labels
        for val in range(-1, 1):
            corpus_models.Sentiment.objects.create(
                value=val,
                name=str(val)
            )

        sentiment_ids = corpus_models.Sentiment.objects.values_list('id', flat=True).distinct()
        sentiment_distribution = self.get_distribution(sentiment_ids)

        dataset = self.generate_messages_for_distribution(
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
        hashtag_distribution = self.get_distribution(hashtag_ids)

        dataset = self.generate_messages_for_distribution(
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
        bool_distribution = self.get_distribution(values)

        dataset = self.generate_messages_for_distribution(
            field_name='contains_url',
            distribution=bool_distribution,
        )

        calculator = distributions.CategoricalDistribution()
        result = calculator.group_by(dataset, field_name='contains_url')
        self.assertDistributionsEqual(result, bool_distribution)

    def test_boolean_distribution_with_zeros(self):
        """
        Checks that the tests work if there are zeros in the
        expected distribution.
        """

        values = [True, False]
        bool_distribution = self.get_distribution(values, min_count=0)
        self.assertEquals(bool_distribution[True], 0)

        dataset = self.generate_messages_for_distribution(
            field_name='contains_url',
            distribution=bool_distribution,
        )

        calculator = distributions.CategoricalDistribution()
        result = calculator.group_by(dataset, field_name='contains_url')
        self.assertDistributionsEqual(result, bool_distribution)

    def test_empty_boolean_distribution(self):
        """
        Checks that we can calculate a distribution with no messages.
        """

        values = [True, False]
        bool_distribution = {True: 0, False: 0}

        dataset = self.generate_messages_for_distribution(
            field_name='contains_url',
            distribution=bool_distribution,
        )

        calculator = distributions.CategoricalDistribution()
        result = calculator.group_by(dataset, field_name='contains_url')
        self.assertDistributionsEqual(result, bool_distribution)


class QuantitativeDistributionsTest(DistributionTestCaseMixins, TestCase):
    def test_count_distribution(self):
        """
        Checks that the distribution of a count field,
        in this case shared_count, can be calculated correctly.
        """

        shared_counts = range(0, 12)
        shared_count_distribution = self.get_distribution(shared_counts)
        dataset = self.generate_messages_for_distribution(
            field_name='shared_count',
            distribution=shared_count_distribution,
        )

        calculator = distributions.QuantitativeDistribution()
        result = calculator.group_by(dataset, field_name='shared_count')
        self.assertDistributionsEqual(result, shared_count_distribution)

    def test_wide_count_distribution(self):
        """
        If the range of the counts is very large,
        they should come out binned.
        """
        shared_counts = [1, 2, 100, 101]
        shared_count_distribution = self.get_distribution(shared_counts)
        dataset = self.generate_messages_for_distribution(
            field_name='shared_count',
            distribution=shared_count_distribution,
        )

        binned_distribution = {
            0: shared_count_distribution[1] + shared_count_distribution[2],
            100: shared_count_distribution[100] + shared_count_distribution[101],
        }

        calculator = distributions.QuantitativeDistribution(desired_bins=5)
        result = calculator.group_by(dataset, field_name='shared_count')
        self.assertEquals(result.bin_size, 20)
        self.assertEquals(result.min_val, 1)
        self.assertEquals(result.max_val, 101)
        self.assertDistributionsEqual(result, binned_distribution)


    def test_narrow_count_distribution(self):
        """
        If the range is very small but we ask for a lot of bins,
        we should get a bin size of 1.
        """
        shared_counts = [1, 2, 1, 2, 3]
        shared_count_distribution = self.get_distribution(shared_counts)
        dataset = self.generate_messages_for_distribution(
            field_name='shared_count',
            distribution=shared_count_distribution,
        )

        calculator = distributions.QuantitativeDistribution(desired_bins=50)
        result = calculator.group_by(dataset, field_name='shared_count')
        self.assertEquals(result.bin_size, 1)
        self.assertEquals(result.min_val, 1)
        self.assertEquals(result.max_val, 3)
        self.assertDistributionsEqual(result, shared_count_distribution)


class TimeDistributionsTest(DistributionTestCaseMixins, TestCase):
    def setUp(self):
        # Get an arbitrary time to work with
        self.base_time = tz.datetime(2012, 5, 2, 20, 10, 2, 42)

        if settings.USE_TZ:
            self.base_time = self.base_time.replace(tzinfo=tz.utc)

    def generate_times(self, start_time, offset_type, offsets):
        """
        Generate a list of datetimes starting with start.
        The offset type is a property for timedelta.
        The offsets is an array of numbers.
        """

        yield start_time
        for offset in offsets:
            start_time += tz.timedelta(**{offset_type: offset})
            yield start_time

    def fix_datetimes(self, results):
        """
        Given a list of value/count dictionaries, makes
        sure that all the values are datetimes, not strings.
        """
        for row in results:
            value = row['value']
            count = row['count']

            if isinstance(value, basestring):

                value = dateparse.parse_datetime(value)
                if settings.USE_TZ:
                    value = value.replace(tzinfo=tz.utc)
                row['value'] = value


    def test_narrow_time_distribution(self):
        """
        Checks that the distribution of a time field can be calculated correctly.
        """

        times = self.generate_times(self.base_time, 'minutes', [2, 5, 10, 12, 1])
        time_distribution = self.get_distribution(times)

        dataset = self.generate_messages_for_distribution(
            field_name='time',
            distribution=time_distribution,
        )

        calculator = distributions.TimeDistribution(desired_bins=2000)
        result = calculator.group_by(dataset, field_name='time')

        self.fix_datetimes(result)

        self.assertDistributionsEqual(result, time_distribution)

    def test_wide_time_distribution(self):
        """
        If the range of the counts is very large,
        they should come out binned.
        """

        # base_time plus 4 days later
        times = list(self.generate_times(self.base_time, 'days', [4]))
        time_distribution = self.get_distribution(times)

        dataset = self.generate_messages_for_distribution(
            field_name='time',
            distribution=time_distribution,
        )

        # Remove the time parts
        day1 = times[0].replace(hour=0, minute=0, second=0, microsecond=0)
        day2 = times[1].replace(hour=0, minute=0, second=0, microsecond=0)

        binned_distribution = {
            day1: time_distribution[times[0]],
            day2: time_distribution[times[1]]
        }

        calculator = distributions.TimeDistribution(desired_bins=4)
        result = calculator.group_by(dataset, field_name='time')

        self.fix_datetimes(result)

        self.assertEquals(result.bin_size, 24 * 60 * 60)  # 24 hour bins
        self.assertEquals(result.min_val, times[0])
        self.assertEquals(result.max_val, times[1])
        self.assertDistributionsEqual(result, binned_distribution)

    def run_time_bin_test(self, delta, desired_bins, expected_bin_size):
        """Run a generic time bin test."""
        t0 = self.base_time
        t1 = t0 + delta
        calculator = distributions.TimeDistribution(desired_bins=desired_bins)
        self.assertEquals(calculator._get_bin_size(t0, t1), expected_bin_size)

    def test_time_bin_min_size(self):
        """Returns minimum bin size of 1 second."""
        self.run_time_bin_test(
            delta=tz.timedelta(seconds=4),
            desired_bins=10,
            expected_bin_size=1)

    def test_time_bin_even_split(self):
        """Split evenly when the desired bins is perfect"""
        self.run_time_bin_test(
            delta=tz.timedelta(minutes=4),
            desired_bins=8,
            expected_bin_size=30,
        )

    def test_time_bin_at_least_desired(self):
        """Continues to deliver at least the desired bins"""
        self.run_time_bin_test(
            delta=tz.timedelta(minutes=4),
            desired_bins=7,
            expected_bin_size=30,
        )

    def test_time_bin_bumps_up(self):
        """If you ask for more bins, increases granularity"""
        self.run_time_bin_test(
            delta=tz.timedelta(minutes=4),
            desired_bins=9,
            expected_bin_size=15,
            )

class AuthorFieldDistributionsTest(DistributionTestCaseMixins, TestCase):
    def generate_authors(self, field_name, values):
        """Generate a dataset and a set of authors with fields set to the given values."""
        dataset = corpus_models.Dataset.objects.create(
            name="Test author name distribution",
            description="Created by test_author_name_distribution",
        )

        # Create some authors
        for value in values:
            corpus_models.Person.objects.create(**{'dataset': dataset, field_name: value})

        return dataset

    def distibute_messages_to_authors(self, dataset):
        """Create messages for each author, and return a dict of author id to message count."""
        author_ids = dataset.person_set.values_list('id', flat=True).distinct()
        author_distribution = self.get_distribution(author_ids)

        self.generate_messages_for_distribution(
            field_name='sender_id',
            distribution=author_distribution,
            dataset=dataset,
        )
        return author_distribution

    def recover_author_field_distribution(self, author_distribution, author_field_name):
        """
        Given a dict of author id to message count,
        produces a dict of author field values to message counts.

        If there are multiple authors with the same field value,
        their message counts will be added.
        """
        field_distribution = {}
        for pid, pcount in author_distribution.iteritems():
            author = corpus_models.Person.objects.get(id=pid)

            field_val = getattr(author, author_field_name)
            if field_val not in field_distribution:
                field_distribution[field_val] = 0

            field_distribution[field_val] += pcount

        return field_distribution

    def test_author_name_distribution(self):
        """Count messages by author name"""
        dataset = self.generate_authors('username', ['username_%d' % d for d in xrange(5)])
        author_distribution = self.distibute_messages_to_authors(dataset)
        author_name_distribution = self.recover_author_field_distribution(author_distribution, 'username')

        calculator = distributions.CategoricalDistribution()

        # Calculate the categorical distribution over the field name
        result = calculator.group_by(dataset, field_name='sender__username')
        self.assertDistributionsEqual(result, author_name_distribution)

    def test_author_count_distribution(self):
        """Can count messages for different author message_counts"""
        dataset = self.generate_authors('message_count', [5, 10, 15, 20, 25])
        author_distribution = self.distibute_messages_to_authors(dataset)
        author_count_distribution = self.recover_author_field_distribution(author_distribution, 'message_count')

        calculator = distributions.PersonQuantitativeDistribution()

        # Calculate the categorical distribution over the field name
        result = calculator.group_by(dataset, field_name='message_count')
        self.assertDistributionsEqual(result, author_count_distribution)

    def test_author_count_distribution_with_duplicates(self):
        """Multiple authors with the same message_count."""
        dataset = self.generate_authors('message_count', [5, 10, 15, 20, 25, 5, 10, 15])
        author_distribution = self.distibute_messages_to_authors(dataset)
        author_count_distribution = self.recover_author_field_distribution(author_distribution, 'message_count')

        calculator = distributions.PersonQuantitativeDistribution()

        # Calculate the categorical distribution over the field name
        result = calculator.group_by(dataset, field_name='message_count')
        self.assertDistributionsEqual(result, author_count_distribution)
