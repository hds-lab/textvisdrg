from django.test import TestCase
from django.conf import settings
from django.utils import timezone as tz
from django.utils import dateparse
import mock

from msgvis.apps.datatable import models
from msgvis.apps.corpus import models as corpus_models
from msgvis.apps.dimensions.models import CategoricalDimension
from msgvis.apps.dimensions import registry
from msgvis.apps.base.tests import DistributionTestCaseMixins


class TestDataTable(DistributionTestCaseMixins, TestCase):
    """Some basic functionality tests"""

    @mock.patch('msgvis.apps.dimensions.registry.get_dimension')
    def test_create_with_keys(self, get_dimension):
        """If given strings, finds the matching dimensions."""
        datatable = models.DataTable('foo', 'bar')

        get_dimension.assert_has_calls([
                                           mock.call('foo'),
                                           mock.call('bar')
                                       ], any_order=True)

    @mock.patch('msgvis.apps.dimensions.registry.get_dimension')
    def test_create_with_dimensions(self, get_dimension):
        """Accepts arguments that are dimensions"""
        d1 = mock.Mock(spec=CategoricalDimension)
        d2 = mock.Mock(spec=CategoricalDimension)
        datatable = models.DataTable(d1, d2)
        self.assertEquals(get_dimension.call_count, 0)

    def test_create_with_one_dimension(self):
        """Can be created with only one dimension"""
        d1 = mock.Mock(spec=CategoricalDimension)
        datatable = models.DataTable(d1)
        self.assertIsNone(datatable.secondary_dimension)


class TestCategoricalDataTable(DistributionTestCaseMixins, TestCase):
    """Tests for categorical dimensions only, on the Message object"""

    def test_render_single_categorical(self):
        """Can produce a datatable with a single categorical dimension."""

        values = [True, False]
        bool_distribution = self.get_distribution(values)

        dataset = self.generate_messages_for_distribution(
            field_name='contains_url',
            distribution=bool_distribution,
        )

        dimension = registry.get_dimension('contains_url')

        datatable = models.DataTable(dimension)
        result = datatable.render(dataset)

        self.assertDistributionsEqual(result, bool_distribution, level_key='contains_url', measure_key='value')

    def test_render_double_categorical(self):
        """Can produce a datatable with a two categorical dimensions."""

        field_names = ('contains_url', 'contains_mention')
        values = [(True, True), (True, False), (False, True), (False, False)]
        bi_bool_distribution = self.get_distribution(values)

        dataset = self.generate_messages_for_multi_distribution(
            field_names=field_names,
            distribution=bi_bool_distribution,
        )

        d1 = registry.get_dimension(field_names[0])
        d2 = registry.get_dimension(field_names[1])

        datatable = models.DataTable(d1, d2)
        result = datatable.render(dataset)

        self.assertMultiDistributionsEqual(result, bi_bool_distribution, field_names, measure_key='value')


class TestQuantitativeDataTable(DistributionTestCaseMixins, TestCase):
    """Tests for quantitative dimensions only, on the Message object"""

    def test_render_single_quantitative_narrow(self):
        """
        Can produce a datatable with only a single quantitative dimension.
        The distribution is small enough no binning is needed.
        """

        values = [0, 2, 3, 4, 6]
        quant_distribution = self.get_distribution(values)

        dataset = self.generate_messages_for_distribution(
            field_name='shared_count',
            distribution=quant_distribution,
        )

        dimension = registry.get_dimension('shares')

        datatable = models.DataTable(dimension)
        result = datatable.render(dataset)

        self.assertDistributionsEqual(result, quant_distribution, level_key='shares', measure_key='value')

    def test_render_single_quantitative_wide(self):
        """
        Can produce a datatable with only a single quantitative dimension.
        The distribution is very wide and binning must be used.
        """

        values = [0, 2, 3, 4, 60000]
        quant_distribution = self.get_distribution(values)

        dataset = self.generate_messages_for_distribution(
            field_name='shared_count',
            distribution=quant_distribution,
        )

        binned_distribution = {
            0: sum(quant_distribution[value] for value in values[:4]),
            60000: quant_distribution[values[4]],
        }

        dimension = registry.get_dimension('shares')

        datatable = models.DataTable(dimension)
        result = datatable.render(dataset, desired_primary_bins=5)

        self.assertDistributionsEqual(result, binned_distribution, level_key='shares', measure_key='value')


    def test_double_quantitative_narrow(self):
        """Can it render two quantitative dimensions when binning is not needed."""
        values = [(0, 1), (2, 3), (3, 2), (4, 5), (6, 7)]
        quant_distribution = self.get_distribution(values)

        dataset = self.generate_messages_for_multi_distribution(
            ('shared_count', 'replied_to_count'),
            quant_distribution)

        d1 = registry.get_dimension('shares')
        d2 = registry.get_dimension('replies')

        datatable = models.DataTable(d1, d2)
        result = datatable.render(dataset)

        self.assertMultiDistributionsEqual(result, quant_distribution, ('shares', 'replies'), measure_key='value')

    def test_double_quantitative_one_wide(self):
        """Can it render two quant dimensions, when one requires binning?"""
        values = [(0, 1), (2, 3), (6, 59999), (6, 60000)]
        quant_distribution = self.get_distribution(values)

        dataset = self.generate_messages_for_multi_distribution(
            ('shared_count', 'replied_to_count'),
            quant_distribution)

        binned_distribution = {
            (0, 0): quant_distribution[values[0]],
            (2, 0): quant_distribution[values[1]],
            (6, 59995): quant_distribution[values[2]] + quant_distribution[values[3]]
        }

        d1 = registry.get_dimension('shares')
        d2 = registry.get_dimension('replies')

        datatable = models.DataTable(d1, d2)
        result = datatable.render(dataset, desired_secondary_bins=5)

        self.assertMultiDistributionsEqual(result, binned_distribution, ('shares', 'replies'), measure_key='value')


class TestRelatedCategoricalDataTable(DistributionTestCaseMixins, TestCase):
    """Tests for categorical dimensions only, on a related table."""

    def test_render_single_related_categorical(self):
        """Can produce a datatable with a single related categorical dimension."""

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

        datatable = models.DataTable(dimension)
        result = datatable.render(dataset)

        self.assertDistributionsEqual(result, language_code_distribution, level_key='language', measure_key='value')

    def test_render_two_related_categorical(self):
        """Can produce a datatable with two related categorical dimensions."""

        # Create some language labels
        language_ids = self.create_test_languages()
        dataset = self.create_authors_with_values('username', ['username_%d' % d for d in xrange(5)])
        author_ids = dataset.person_set.values_list('id', flat=True).distinct()

        # create language/person pairs
        value_pairs = []
        for lang in language_ids:
            for author in author_ids:
                # skip cases where both are even, just so's there's gaps
                if lang % 2 == 0 and author % 2 == 0:
                    continue

                value_pairs.append((lang, author))

        # Distribute some messages
        id_distribution = self.get_distribution(value_pairs)
        self.generate_messages_for_multi_distribution(('language_id', 'sender_id'), id_distribution, dataset=dataset)

        # Get the actual expected distribution
        value_distribution = self.convert_id_distribution_to_related(id_distribution,
                                                                     (corpus_models.Language, corpus_models.Person),
                                                                     ('code', 'username'))

        d1 = registry.get_dimension('language')
        d2 = registry.get_dimension('sender_name')

        datatable = models.DataTable(d1, d2)
        result = datatable.render(dataset)

        self.assertMultiDistributionsEqual(result, value_distribution, ('language', 'sender_name'), measure_key='value')


class CategoricalDimensionsRegistryTest(DistributionTestCaseMixins, TestCase):
    """Tests transplanted from the dimension distribution tests"""

    def doCategoricalDistributionTest(self, dimension_key, dataset, distribution):
        dimension = registry.get_dimension(dimension_key)
        datatable = models.DataTable(dimension)

        # Calculate the categorical distribution over the field name
        result = datatable.render(dataset.message_set.all())
        self.assertDistributionsEqual(result, distribution, level_key=dimension.key, measure_key='value')

    def test_related_categorical_distribution(self):
        """
        Checks that the distribution of a categorical related model field,
        in this case Language, can be calculated correctly.
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

        self.doCategoricalDistributionTest('language', dataset, language_code_distribution)

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

        self.doCategoricalDistributionTest('hashtags', dataset, hashtag_text_distribution)

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

        self.doCategoricalDistributionTest('contains_url', dataset, bool_distribution)

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

        self.doCategoricalDistributionTest('contains_url', dataset, bool_distribution)

    def test_empty_boolean_distribution(self):
        """
        Checks that we can calculate a distribution with no messages.
        """

        bool_distribution = {True: 0, False: 0}

        dataset = self.generate_messages_for_distribution(
            field_name='contains_url',
            distribution=bool_distribution,
        )

        self.doCategoricalDistributionTest('contains_url', dataset, bool_distribution)


class QuantitativeDistributionsTest(DistributionTestCaseMixins, TestCase):
    """Ported from the dimension distribution tests"""

    def doQuantitativeDimensionsTest(self, dimension_key, dataset, distribution, **kwargs):
        dimension = registry.get_dimension(dimension_key)
        datatable = models.DataTable(dimension)

        # Calculate the categorical distribution over the field name
        result = datatable.render(dataset.message_set.all(), **kwargs)
        self.assertDistributionsEqual(result, distribution, level_key=dimension.key, measure_key='value')

    def test_count_distribution(self):
        """
        Checks that the distribution of a count field,
        in this case shared_count, can be calculated correctly.
        """
        shared_counts = range(0, 5)
        shared_count_distribution = self.get_distribution(shared_counts)
        dataset = self.generate_messages_for_distribution(
            field_name='shared_count',
            distribution=shared_count_distribution,
        )

        self.doQuantitativeDimensionsTest('shares', dataset, shared_count_distribution, desired_primary_bins=50)

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

        self.doQuantitativeDimensionsTest('shares', dataset, binned_distribution, desired_primary_bins=5)


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
            timeval = row['time']
            count = row['value']

            if isinstance(timeval, basestring):

                timeval = dateparse.parse_datetime(timeval)
                if settings.USE_TZ:
                    timeval = timeval.replace(tzinfo=tz.utc)
                row['time'] = timeval


    def doTimeDimensionsTest(self, dataset, distribution, **kwargs):
        dimension_key = 'time'
        dimension = registry.get_dimension(dimension_key)
        datatable = models.DataTable(dimension)

        # Calculate the categorical distribution over the field name
        result = datatable.render(dataset.message_set.all(), **kwargs)
        self.fix_datetimes(result)
        self.assertDistributionsEqual(result, distribution, level_key=dimension.key, measure_key='value')


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

        self.doTimeDimensionsTest(dataset, time_distribution, desired_primary_bins=2000)


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

        self.doTimeDimensionsTest(dataset, binned_distribution, desired_primary_bins=4)


class AuthorFieldDistributionsTest(DistributionTestCaseMixins, TestCase):

    def doDistributionTest(self, dimension_key, dataset, distribution, **kwargs):
        dimension = registry.get_dimension(dimension_key)

        # Calculate the categorical distribution over the field name
        datatable = models.DataTable(dimension)
        result = datatable.render(dataset.message_set.all(), **kwargs)
        self.assertDistributionsEqual(result, distribution, level_key=dimension_key, measure_key='value')

    def test_author_name_distribution(self):
        """Count messages by author name"""
        dataset = self.create_authors_with_values('username', ['username_%d' % d for d in xrange(5)])
        author_distribution = self.distibute_messages_to_authors(dataset)
        author_name_distribution = self.recover_related_field_distribution(author_distribution, corpus_models.Person,
                                                                           'username')

        self.doDistributionTest('sender_name', dataset, author_name_distribution)

    def test_author_count_distribution(self):
        """Can count messages for different author message_counts"""
        dataset = self.create_authors_with_values('message_count', [5, 10, 15, 20, 25])
        author_distribution = self.distibute_messages_to_authors(dataset)
        author_count_distribution = self.recover_related_field_distribution(author_distribution, corpus_models.Person,
                                                                            'message_count')

        self.doDistributionTest('sender_message_count', dataset, author_count_distribution)

    def test_author_count_distribution_with_duplicates(self):
        """Multiple authors with the same message_count."""
        dataset = self.create_authors_with_values('message_count', [5, 10, 15, 20, 25, 5, 10, 15])
        author_distribution = self.distibute_messages_to_authors(dataset)
        author_count_distribution = self.recover_related_field_distribution(author_distribution, corpus_models.Person,
                                                                            'message_count')

        self.doDistributionTest('sender_message_count', dataset, author_count_distribution)

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

        self.doDistributionTest('sender_message_count', dataset, binned_distribution, desired_primary_bins=2)

    def test_narrow_author_count_distribution(self):
        """
        If the range is very small but we ask for a lot of bins,
        we should get a bin size of 1.
        """

        dataset = self.create_authors_with_values('message_count', [5, 6, 7])
        author_distribution = self.distibute_messages_to_authors(dataset)
        author_count_distribution = self.recover_related_field_distribution(author_distribution, corpus_models.Person,
                                                                            'message_count')

        self.doDistributionTest('sender_message_count', dataset, author_count_distribution, desired_primary_bins=50)


class GenerateDataTableTest(DistributionTestCaseMixins, TestCase):
    """Test the combined data table generation routine"""

    def test_generate(self):
        """It should render a data table"""

        dataset = self.create_empty_dataset()

        render_calls = []
        class MockDataTable(models.DataTable):
            def render(self, *args, **kwargs):
                render_calls.append((args, kwargs))

        datatable = MockDataTable(primary_dimension='time')
        datatable.generate(dataset)
        self.assertEquals(len(render_calls), 1)

