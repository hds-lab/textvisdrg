from django.test import TestCase
from msgvis.apps.corpus import models as corpus_models
from msgvis.apps.datatable import models
from msgvis.apps.dimensions.models import CategoricalDimension
from msgvis.apps.dimensions import registry
import mock

from msgvis.apps.base.tests import DistributionTestCaseMixins

# Create your tests here.
class TestDataTable(DistributionTestCaseMixins, TestCase):
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


    def test_render_single_categorical(self):
        """Can produce a datatable with a single categorical dimensions."""

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

    def generate_messages_for_multi_distribution(self, field_names, distribution, dataset=None):
        if dataset is None:
            dataset = corpus_models.Dataset.objects.create(
                name="Test %s distribution" % ':'.join(field_names),
                description="Created by create_multi_distribution",
            )

        num = 0
        for value_tuple, count in distribution.iteritems():
            for i in range(count):
                field_values = dict(zip(field_names, value_tuple))

                field_values['text'] = "Message %d: '%s'" % (num, str(field_values))
                msg = dataset.message_set.create(**field_values)

                num += 1

        return dataset

    def assertMultiDistributionsEqual(self, result, desired_distribution, field_names, measure_key='count'):
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
            # Each row should have the measure and levels for each field
            self.assertIn(measure_key, row)
            for fname in field_names:
                self.assertIn(fname, row)

            values = row.copy()
            values.pop(measure_key)
            # A list of the field values in order
            unzipped_values = tuple(values[fname] for fname in field_names)
            count = row[measure_key]

            # Check that this combo of levels was expected
            self.assertIn(unzipped_values, desired_distribution)
            # check the count is actually correct
            self.assertEquals(count, desired_distribution[unzipped_values])

            if count == 0:
                # It was zero but was included anyway
                del zeros[unzipped_values]

        # Should match the length of the distribution
        self.assertEquals(len(result), len(desired_distribution) - len(zeros))

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
