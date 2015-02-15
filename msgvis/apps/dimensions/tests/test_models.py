from django.test import TestCase
import mock

from msgvis.apps.dimensions import models


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

        with mock.patch.object(dimension, 'group_by', group_by),\
             mock.patch('django.db.models.Count', Count):
            result = dimension.get_distribution(queryset)
            self.assertEquals(result, grouped_queryset.annotate.return_value)

        # We should be grouping with the key field aliased to value
        group_by.assert_called_once_with(queryset, 'value')

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

    def test_group_by_default_to_dimension_key(self):
        dimension_key = 'iamacat'
        dimension = models.CategoricalDimension(
            key=dimension_key,
            name='Contains a url',
            description='Contains a url',
            field_name='contains_url',
        )

        queryset = mock.Mock()
        extra_queryset = mock.Mock()
        queryset.extra.return_value = extra_queryset
        extra_queryset.values.return_value = 'hello!'

        get_grouping_expression = mock.Mock()
        get_grouping_expression.return_value = 'grouping_expression'

        with mock.patch.object(dimension, 'get_grouping_expression', get_grouping_expression):
            result = dimension.group_by(queryset)
            self.assertEquals(result, extra_queryset.values.return_value)

        # Since the dimension key is different from what we're actually grouping on,
        # it should have also called extra on it
        queryset.extra.assert_called_once_with(select={dimension_key: get_grouping_expression.return_value})

        # We want to get the dimension key in the ValuesQuerySet so this should be what values was called with
        extra_queryset.values.assert_called_once_with(dimension_key)


    def test_group_by_key_equals_field_name(self):
        """When the grouping key equals the field name, does not use QuerySet.extra()"""

        dimension = models.CategoricalDimension(
            key='contains_url',
            name='Contains a url',
            description='Contains a url',
            field_name='whatever',
            )

        queryset = mock.Mock()
        grouping_key = 'iamacat'

        get_grouping_expression = mock.Mock()
        get_grouping_expression.return_value = grouping_key

        with mock.patch.object(dimension, 'get_grouping_expression', get_grouping_expression):
            dimension.group_by(queryset, grouping_key)

        # Since the grouping_key equals the grouping expression, no extras necessary
        self.assertEquals(queryset.extra.call_count, 0)

