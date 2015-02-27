"""Some basic tests of the dimension class, independent of configuration."""

from django.test import TestCase
import mock

from msgvis.apps.dimensions import models


class MappedValuesQuerySetTest(TestCase):
    def setUp(self):
        # Query against django.contrib.auth.models.Permissions just for fun
        from django.contrib.auth.models import Permission

        self.values_query_set = Permission.objects.values('content_type_id')
        self.original_dict = self.values_query_set[0]

    def test_maps_values(self):
        # Just making sure...
        self.assertIn('content_type_id', self.original_dict)

        mapped = models.MappedValuesQuerySet.create_from(self.values_query_set, {
            'content_type_id': 'cti'
        })

        # Check the queryset type
        self.assertIsInstance(mapped, models.MappedValuesQuerySet)
        # Check the length
        self.assertEquals(len(mapped), len(self.values_query_set))
        # Check the mapping
        self.assertTrue('cti' in mapped[0])
        self.assertTrue('content_type_id' not in mapped[0])

    def test_leaves_unmapped_values(self):
        mapped = models.MappedValuesQuerySet.create_from(self.values_query_set, {
            'some_random_field': 'whatever'
        })

        # Should not do anything in this case
        self.assertFalse('whatever' in mapped[0])
        self.assertFalse('some_random_field' in mapped[0])
        self.assertTrue('content_type_id' in mapped[0])


class CategoricalDimensionTest(TestCase):
    def test_can_get_distribution(self):
        """Just check that the Dimension.get_distribution method runs"""

        dimension = models.CategoricalDimension(
            key='contains_url',
            name='Contains a url',
            description='Contains a url',
            field_name='contains_url',
        )

        queryset = mock.Mock()
        grouped_queryset = mock.Mock()

        group_by = mock.Mock()
        group_by.return_value = grouped_queryset

        grouped_queryset.annotate.return_value = 'hello!'

        # Mock the Django count class
        Count = mock.Mock()
        Count.return_value = 5

        with mock.patch.object(dimension, 'group_by', group_by), \
             mock.patch('django.db.models.Count', Count):
            result = dimension.get_distribution(queryset)
            self.assertEquals(result['counts'], grouped_queryset.annotate.return_value)

        # We should be grouping with the key field aliased to value
        group_by.assert_called_once_with(queryset, grouping_key='value')

        # And then we should aggregate by Count('id')
        Count.assert_called_once_with('id')
        grouped_queryset.annotate.assert_called_once_with(count=Count.return_value)


    def test_get_grouping_expression(self):
        """Check that the grouping expression equals the field name"""

        field_name = 'i_am_a_field_name'
        dimension = models.CategoricalDimension(
            key='contains_url',
            name='Contains a url',
            description='Contains a url',
            field_name=field_name,
        )

        self.assertEquals(dimension.get_grouping_expression(mock.Mock()), field_name)

    @mock.patch('msgvis.apps.dimensions.models.MappedValuesQuerySet')
    def test_group_by_default_to_dimension_key(self, MappedValuesQuerySet):
        """
        If you don't call group_by with a desired group key name, it should
        fall back to the dimension key.
        """
        dimension_key = 'iamacat'

        dimension = models.CategoricalDimension(
            key=dimension_key,
            name='Contains a url',
            description='Contains a url',
            field_name='contains_url',
        )

        queryset = mock.Mock()
        queryset.values.return_value = 'values query set'
        MappedValuesQuerySet.create_from.return_value = 'hello'

        get_grouping_expression = mock.Mock()
        get_grouping_expression.return_value = 'grouping_expression'

        with mock.patch.object(dimension, 'get_grouping_expression', get_grouping_expression):
            result = dimension.group_by(queryset)

            # Should get a mapped values queryset out
            self.assertEquals(result, MappedValuesQuerySet.create_from.return_value)

        # Should group by the grouping expression
        queryset.values.assert_called_once_with(get_grouping_expression.return_value)

        # Since the dimension key is different from what we're actually grouping on,
        # the mapped queryset should be used to change the variables
        MappedValuesQuerySet.create_from.assert_called_once_with(
            queryset.values.return_value,
            {get_grouping_expression.return_value: dimension_key}
        )

    @mock.patch('msgvis.apps.dimensions.models.MappedValuesQuerySet')
    def test_group_by_key_equals_field_name(self, MappedValuesQuerySet):
        """When the grouping key equals grouping expression, it should not do any remapping"""

        dimension = models.CategoricalDimension(
            key='contains_url',
            name='Contains a url',
            description='Contains a url',
            field_name='whatever',
        )

        queryset = mock.Mock()
        values_query_set = mock.Mock()
        queryset.values.return_value = values_query_set

        grouping_key = 'iamacat'

        get_grouping_expression = mock.Mock()
        get_grouping_expression.return_value = grouping_key

        with mock.patch.object(dimension, 'get_grouping_expression', get_grouping_expression):
            result = dimension.group_by(queryset, grouping_key)

            # It should not be a mapped values queryset
            self.assertEquals(result, values_query_set)

        self.assertEquals(MappedValuesQuerySet.create_from.call_count, 0)

    def test_select_grouping_quantitative_no_grouping(self):
        """When the grouping expression equals the dimension field name, nothing fancy necessary."""

        dimension = models.QuantitativeDimension(
            key='shares',
            name='Count of shares',
            description='Count of shares',
            field_name='shared_count',
        )

        queryset = mock.Mock()

        result, internal_key = dimension.select_grouping_expression(queryset, dimension.field_name)

        # It should't need a different internal key in this simple case
        self.assertEquals(internal_key, dimension.field_name)
        self.assertEquals(result, queryset)
