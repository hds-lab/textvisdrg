from django.test import TestCase
from msgvis.apps.datatable import models
from msgvis.apps.corpus import models as corpus_models
from msgvis.apps.dimensions.models import CategoricalDimension
from msgvis.apps.dimensions import registry
import mock

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
            (6, 60000): quant_distribution[values[2]] + quant_distribution[values[3]]
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

