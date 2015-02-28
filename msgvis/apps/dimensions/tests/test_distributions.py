"""Test that the registered dimensions can get their distributions"""

from django.test import TestCase

from msgvis.apps.dimensions import registry
from msgvis.apps.corpus import models as corpus_models
from msgvis.apps.base.tests import DistributionTestCaseMixins

from django.conf import settings
from django.utils import timezone as tz
from django.utils import dateparse


class CategoricalDimensionsRegistryTest(DistributionTestCaseMixins, TestCase):
    def test_related_categorical_distribution(self):
        """
        Checks that the distribution of a categorical related model field,
        in this case Sentiment, can be calculated correctly.
        """

        # Create some language labels
        language_ids = self.create_test_languages()
        language_distribution = self.get_distribution(language_ids)
        language_code_distribution = self.recover_related_field_distribution(language_distribution,
                                                                               corpus_models.Language, 'code')

        dataset = self.generate_messages_for_distribution(
            field_name='language_id',
            distribution=language_distribution,
        )

        dimension = registry.get_dimension('language')

        # Calculate the categorical distribution over the field name
        result = dimension.get_distribution(dataset.message_set.all())

        self.assertDistributionsEqual(result['counts'], language_code_distribution)

    def test_many_related_model_distribution(self):
        """
        Checks that the distribution of a categorical many-to-many related model field,
        in this case Hashtags, can be calculated correctly.
        """

        hashtag_ids = self.create_test_hashtags()
        hashtag_distribution = self.get_distribution(hashtag_ids)
        hashtag_text_distribution = self.recover_related_field_distribution(hashtag_distribution,
                                                                            corpus_models.Hashtag, 'text')

        dataset = self.generate_messages_for_distribution(
            field_name='hashtags',
            distribution=hashtag_distribution,
            many=True,
        )

        dimension = registry.get_dimension('hashtags')

        # Calculate the categorical distribution over the field name
        result = dimension.get_distribution(dataset.message_set.all())
        self.assertDistributionsEqual(result['counts'], hashtag_text_distribution)

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

        dimension = registry.get_dimension('contains_url')
        result = dimension.get_distribution(dataset.message_set.all())
        self.assertDistributionsEqual(result['counts'], bool_distribution)

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

        dimension = registry.get_dimension('contains_url')
        result = dimension.get_distribution(dataset.message_set.all())
        self.assertDistributionsEqual(result['counts'], bool_distribution)

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

        dimension = registry.get_dimension('contains_url')
        result = dimension.get_distribution(dataset.message_set.all())
        self.assertDistributionsEqual(result['counts'], bool_distribution)


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

        dimension = registry.get_dimension('shares')
        result = dimension.get_distribution(dataset.message_set.all())

        self.assertDistributionsEqual(result['counts'], shared_count_distribution)

        self.assertEquals(result['bin_size'], 1)
        self.assertEquals(result['bins'], 50)
        self.assertEquals(result['min_val'], 0)
        self.assertEquals(result['max_val'], 11)
        self.assertEquals(result['min_bin'], 0)
        self.assertEquals(result['max_bin'], 11)

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

        dimension = registry.get_dimension('shares')
        result = dimension.get_distribution(dataset.message_set.all(), bins=5)

        self.assertEquals(result['bin_size'], 20)
        self.assertEquals(result['bins'], 5)
        self.assertEquals(result['min_val'], 1)
        self.assertEquals(result['max_val'], 101)
        self.assertEquals(result['min_bin'], 0)
        self.assertEquals(result['max_bin'], 100)
        self.assertDistributionsEqual(result['counts'], binned_distribution)


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

        dimension = registry.get_dimension('shares')
        result = dimension.get_distribution(dataset.message_set.all(), bins=50)

        self.assertDistributionsEqual(result['counts'], shared_count_distribution)

        self.assertEquals(result['bin_size'], 1)
        self.assertEquals(result['bins'], 50)
        self.assertEquals(result['min_val'], 1)
        self.assertEquals(result['max_val'], 3)
        self.assertEquals(result['min_bin'], 1)
        self.assertEquals(result['max_bin'], 3)


class TimeDistributionsTest(DistributionTestCaseMixins, TestCase):
    def setUp(self):
        # Get an arbitrary time to work with
        self.base_time = tz.datetime(2012, 5, 2, 20, 10, 2, 0)

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

        times = list(self.generate_times(self.base_time, 'minutes', [2, 5, 10, 12, 1]))
        time_distribution = self.get_distribution(times)

        dataset = self.generate_messages_for_distribution(
            field_name='time',
            distribution=time_distribution,
        )

        dimension = registry.get_dimension('time')
        result = dimension.get_distribution(dataset, bins=2000)

        self.fix_datetimes(result['counts'])
        self.assertDistributionsEqual(result['counts'], time_distribution)

        self.assertEquals(result['bin_size'], 1)
        self.assertEquals(result['bins'], 2000)
        self.assertEquals(result['min_val'], times[0])
        self.assertEquals(result['max_val'], times[len(times) - 1])
        self.assertEquals(result['min_bin'], times[0])
        self.assertEquals(result['max_bin'], times[len(times) - 1])

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

        dimension = registry.get_dimension('time')
        result = dimension.get_distribution(dataset, bins=4)

        self.fix_datetimes(result['counts'])
        self.assertDistributionsEqual(result['counts'], binned_distribution)

        self.assertEquals(result['bin_size'], 24 * 60 * 60)
        self.assertEquals(result['bins'], 4)
        self.assertEquals(result['min_val'], times[0])
        self.assertEquals(result['max_val'], times[len(times) - 1])
        self.assertEquals(result['min_bin'], day1)
        self.assertEquals(result['max_bin'], day2)

    def run_time_bin_test(self, delta, desired_bins, expected_bin_size):
        """Run a generic time bin test."""
        t0 = self.base_time
        t1 = t0 + delta
        dimension = registry.get_dimension('time')
        self.assertEquals(dimension._get_bin_size(t0, t1, desired_bins), expected_bin_size)

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


    def test_author_name_distribution(self):
        """Count messages by author name"""
        dataset = self.create_authors_with_values('username', ['username_%d' % d for d in xrange(5)])
        author_distribution = self.distibute_messages_to_authors(dataset)
        author_name_distribution = self.recover_related_field_distribution(author_distribution, corpus_models.Person,
                                                                           'username')

        dimension = registry.get_dimension('sender_name')

        # Calculate the categorical distribution over the field name
        result = dimension.get_distribution(dataset.message_set.all())
        self.assertDistributionsEqual(result['counts'], author_name_distribution)

    def test_author_count_distribution(self):
        """Can count messages for different author message_counts"""
        dataset = self.create_authors_with_values('message_count', [5, 10, 15, 20, 25])
        author_distribution = self.distibute_messages_to_authors(dataset)
        author_count_distribution = self.recover_related_field_distribution(author_distribution, corpus_models.Person,
                                                                            'message_count')

        dimension = registry.get_dimension('sender_message_count')
        result = dimension.get_distribution(dataset)
        self.assertDistributionsEqual(result['counts'], author_count_distribution)

    def test_author_count_distribution_with_duplicates(self):
        """Multiple authors with the same message_count."""
        dataset = self.create_authors_with_values('message_count', [5, 10, 15, 20, 25, 5, 10, 15])
        author_distribution = self.distibute_messages_to_authors(dataset)
        author_count_distribution = self.recover_related_field_distribution(author_distribution, corpus_models.Person,
                                                                            'message_count')

        dimension = registry.get_dimension('sender_message_count')
        result = dimension.get_distribution(dataset)
        self.assertDistributionsEqual(result['counts'], author_count_distribution)


    def test_wide_author_count_distribution(self):
        """
        If the range of the counts is very large,
        they should come out binned.
        """
        dataset = self.create_authors_with_values('message_count', [5, 10, 2005])
        author_distribution = self.distibute_messages_to_authors(dataset)
        author_count_distribution = self.recover_related_field_distribution(author_distribution, corpus_models.Person,
                                                                            'message_count')
        binned_distribution = {
            0: author_count_distribution[5] + author_count_distribution[10],
            2000: author_count_distribution[2005]
        }

        dimension = registry.get_dimension('sender_message_count')
        result = dimension.get_distribution(dataset, bins=2)

        self.assertDistributionsEqual(result['counts'], binned_distribution)

        self.assertEquals(result['bin_size'], 1000)
        self.assertEquals(result['bins'], 2)
        self.assertEquals(result['min_val'], 5)
        self.assertEquals(result['max_val'], 2005)
        self.assertEquals(result['min_bin'], 0)
        self.assertEquals(result['max_bin'], 2000)


    def test_narrow_author_count_distribution(self):
        """
        If the range is very small but we ask for a lot of bins,
        we should get a bin size of 1.
        """

        dataset = self.create_authors_with_values('message_count', [5, 6, 7])
        author_distribution = self.distibute_messages_to_authors(dataset)
        author_count_distribution = self.recover_related_field_distribution(author_distribution, corpus_models.Person,
                                                                            'message_count')

        dimension = registry.get_dimension('sender_message_count')
        result = dimension.get_distribution(dataset.message_set.all(), bins=50)

        self.assertDistributionsEqual(result['counts'], author_count_distribution)

        self.assertEquals(result['bin_size'], 1)
        self.assertEquals(result['bins'], 50)
        self.assertEquals(result['min_val'], 5)
        self.assertEquals(result['max_val'], 7)
        self.assertEquals(result['min_bin'], 5)
        self.assertEquals(result['max_bin'], 7)
