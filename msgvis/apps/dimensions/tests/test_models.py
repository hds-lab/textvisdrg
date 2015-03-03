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

class QuantitativeDimensionTest(TestCase):

    def test_get_range_empty(self):
        """If there is no data, get_range returns none"""

        queryset = mock.Mock()
        queryset.aggregate.return_value = None

        dimension = models.QuantitativeDimension(
            key='shares',
            name='Count of shares',
            description='Count of shares',
            field_name='shared_count',
        )

        min_val, max_val = dimension.get_range(queryset)

        self.assertIsNone(min_val)
        self.assertIsNone(max_val)

    def test_grouping_expression_empty(self):
        """If there is no range in the data, returns no grouping expression"""

        class TestQuantDimension(models.QuantitativeDimension):
            """A quant dimension that returns no range"""

            def __init__(self, *args, **kwargs):
                super(TestQuantDimension, self).__init__(*args, **kwargs)
                self._get_range_calls = 0

            def get_range(self, queryset):
                self._get_range_calls += 1
                return None, None

        dimension = TestQuantDimension(
            key='shares',
            name='Count of shares',
            description='Count of shares',
            field_name='shared_count',
        )

        queryset = mock.Mock()
        expression = dimension.get_grouping_expression(queryset)

        self.assertIsNone(expression)
        self.assertEquals(dimension._get_range_calls, 1)


    def test_group_by_empty(self):
        """If there is no data, group by returns an empty values queryset"""

        class TestQuantDimension(models.QuantitativeDimension):
            """A quant dimension that returns no grouping expression"""
            def __init__(self, *args, **kwargs):
                super(TestQuantDimension, self).__init__(*args, **kwargs)
                self._get_grouping_expression_calls = 0

            def get_grouping_expression(self, queryset, bins=None, bin_size=None, **kwargs):
                self._get_grouping_expression_calls += 1
                return None

        dimension = TestQuantDimension(
            key='shares',
            name='Count of shares',
            description='Count of shares',
            field_name='shared_count',
        )

        queryset = mock.Mock()
        expected_result = queryset.values.return_value

        result = dimension.group_by(queryset)

        self.assertEquals(result, expected_result)
        queryset.values.assert_called_once_with()
        self.assertEquals(dimension._get_grouping_expression_calls, 1)
