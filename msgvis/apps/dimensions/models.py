from django.db import models
from django.db.models import query

from django.db.models import Q
import operator
from msgvis.apps.corpus import models as corpus_models
from msgvis.apps.dimensions import distributions

from django.conf import settings
import math
import collections

QUANTITATIVE_DIMENSION_BINS = getattr(settings, 'QUANTITATIVE_DIMENSION_BINS', 50)


class BinnedValuesQuerySet(query.ValuesQuerySet):
    """
    A class for storing binned values queryset results with
    bin_size, min_val, and max_val metadata as fields.
    """

    def __init__(self, *args, **kwargs):
        super(BinnedValuesQuerySet, self).__init__(*args, **kwargs)
        self.bin_size = kwargs.get('bin_size', None)
        self.min_val = kwargs.get('min_val', None)
        self.max_val = kwargs.get('max_val', None)

    @classmethod
    def create_from(cls, queryset, bin_size=None, min_val=None, max_val=None):
        """Create a MappedValueQuerySet with a field name mapping dictionary."""
        return queryset._clone(cls, bin_size=bin_size, min_val=min_val, max_val=max_val)


class MappedValuesQuerySet(query.ValuesQuerySet):
    """
    A special ValuesQuerySet that can re-map the dictionary keys
    while they are bing iterated over.

    .. code-block:: python

        valuesQuerySet = queryset.values('some__ugly__field__expression')
        mapped = MappedQuerySet.create_from(valuesQuerySet, {
            'some__ugly__field__expression': 'nice_expression'
        })
        mapped[0]
        # { 'nice_expression': 5 }

    """

    def __init__(self, *args, **kwargs):
        super(MappedValuesQuerySet, self).__init__(*args, **kwargs)
        self.field_map = {}

    @classmethod
    def create_from(cls, values_query_set, field_map):
        """Create a MappedValueQuerySet with a field name mapping dictionary."""
        return values_query_set._clone(cls, field_map=field_map)

    def _clone(self, klass=None, setup=False, **kwargs):
        return super(MappedValuesQuerySet, self)._clone(klass, setup, field_map=self.field_map, **kwargs)

    def iterator(self):
        # Purge any extra columns that haven't been explicitly asked for
        extra_names = list(self.query.extra_select)
        field_names = self.field_names
        aggregate_names = list(self.query.aggregate_select)

        names = extra_names + field_names + aggregate_names

        # Remap the fields, but fall back on regular name
        names = [self.field_map.get(name, name) for name in names]

        for row in self.query.get_compiler(self.db).results_iter():
            yield dict(zip(names, row))


class CategoricalDimension(object):
    """
    A basic categorical dimension class.

    Attributes:
        key (str): A string id for the dimension (e.g. 'time')
        name (str): A nicely-formatted name for the dimension (e.g. 'Number of Tweets')
        description (str): A longer explanation for the dimension (e.g. "The total number of tweets produced by this author.")
        field_name (str): The name of the field in the database for this dimension (defaults to the key)
                          Related to the Message model: if you want sender name, use sender__name.
    """

    def __init__(self, key, name=None, description=None, field_name=None):
        self.key = key
        self.name = name
        self.description = description
        self.field_name = field_name if field_name is not None else key

    def exact_filter(self, queryset, filter):
        """Filtering for exact value"""
        if filter.get('value'):
            queryset = queryset.filter(Q((self.field_name, filter['value'])))
        return queryset

    def filter(self, queryset, filter):
        """Apply a filter to a queryset and return the new queryset."""
        queryset = self.exact_filter(queryset, filter)
        if filter.get('levels'):
            filter_ors = []
            for level in filter.get('levels'):
                filter_ors.append((self.field_name, level))
            queryset = queryset.filter(reduce(operator.or_, [Q(x) for x in filter_ors]))
        return queryset

    def group_by(self, queryset, grouping_key=None):
        """
        Return a ValuesQuerySet that has been grouped by this dimension.
        The group value will be available as grouping_key in the dictionaries.

        The grouping key defaults to the dimension key.

        .. code-block:: python

            messages = dim.group_by(messages, 'value')
            distribution = messages.annotate(count=Count('id'))
            print distribution[0]
            # { 'value': 'hello', 'count': 5 }
        """

        if grouping_key is None:
            grouping_key = self.key

        # Get the expression that groups this dimension for this queryset
        grouping_expression = self.get_grouping_expression(queryset)

        # Group the data
        queryset = queryset.values(grouping_expression)

        if grouping_key != grouping_expression:
            # We need to transform the output to match the requested grouping key
            # queryset = queryset.extra(select={grouping_key: grouping_expression})
            queryset = MappedValuesQuerySet.create_from(queryset, {
                grouping_expression: grouping_key
            })

        return queryset

    def get_distribution(self, queryset, value_key='value', **kwargs):
        """Get the distribution of the dimension within the dataset."""

        # Use 'values' to group the queryset
        queryset = self.group_by(queryset, value_key)

        # Count the messages in each group
        return queryset.annotate(count=models.Count('id'))

    def get_grouping_expression(self, queryset, **kwargs):
        """
        Given a set of messages (possibly filtered),
        returns a string that could be used with QuerySet.values() to
        group the messages by this dimension.
        """
        return self.field_name


class QuantitativeDimension(CategoricalDimension):
    """
    A generic quantitative dimension.
    This works for fields on Message or on related fields,
    e.g. field_name=sender__message_count
    """
    distribution = distributions.QuantitativeDistribution()

    grouping_expressions = {
        'mysql': '{bin_size} * FLOOR(`{field_name}` / {bin_size})',
        'sqlite': '{bin_size} * CAST(`{field_name}` / {bin_size} AS INTEGER)',
    }

    def __init__(self, key, name=None, description=None, field_name=None,
                 default_bins=QUANTITATIVE_DIMENSION_BINS,
                 min_bin_size=1):
        super(QuantitativeDimension, self).__init__(key, name, description, field_name)
        self.default_bins = default_bins
        self.min_bin_size = min_bin_size
        self._cached_range_queryset_id = None
        self._cached_range = None

    def filter(self, queryset, filter):
        queryset = self.exact_filter(queryset, filter)
        if filter.get('min'):
            queryset = queryset.filter(Q((self.field_name + "__gte", filter['min'])))
        if filter.get('max'):
            queryset = queryset.filter(Q((self.field_name + "__lte", filter['max'])))
        return queryset

    def get_range(self, queryset):
        """
        Find a min and max for this dimension, as a tuple.
        If there isn't one, (None, None) is returned.

        Calling this multiple times on the same queryset object will
        use a cached value.
        """

        if self._cached_range_queryset_id == id(queryset):
            return self._cached_range

        dim_range = queryset.aggregate(min=models.Min(self.field_name),
                                       max=models.Max(self.field_name))

        self._cached_range_queryset_id = id(queryset)
        self._cached_range = dim_range

        if dim_range is None:
            return None, None

        return dim_range['min'], dim_range['max']

    def _get_bin_size(self, min_val, max_val, desired_bins):
        """
        Given the provided min and max, and the desired minimum number of bins,
        return a nice bin size that is at least at least the
        ``min_bin_size`` for this dimension
        """

        bin_size = max(self.min_bin_size,
                       math.floor(float(max_val - min_val) / desired_bins))

        return bin_size

    def _render_grouping_expression(self, field_name, bin_size):
        from django.db import connection

        return self.grouping_expressions[connection.vendor].format(
            field_name=field_name,
            bin_size=bin_size
        )

    def get_grouping_expression(self, queryset, bins=None, bin_size=None, **kwargs):
        """
        Generate a SQL expression for grouping this dimension.
        If you already know the bin size you want, you may provide it.
        Or the number of bins.
        """
        if bin_size is None:
            if bins is None:
                bins = self.default_bins

            min_val, max_val = self.get_range(queryset)
            if min_val is None:
                return None

            bin_size = self._get_bin_size(min_val, max_val, bins)

        # Determine a bin size for this field
        if bin_size > self.min_bin_size:
            return self._render_grouping_expression(self.field_name, bin_size)
        else:
            # No need for binning
            return super(QuantitativeDimension, self).get_grouping_expression(queryset)

    def _add_grouping_value(self, queryset, grouping_expression, value_key):
        # We can's just use items.extra() because of a bug in Django < 1.8.
        # Sqlite uses %s to convert to unix timestamps.
        # Django's QuerySet.extra() thinks that any %s needs to have a
        # param so if we don't provide one, it errors.
        # If we do provide one, the Sqlite engine complains because it knows better.

        # Copy the queryset to avoid problems
        queryset = queryset._clone()
        queryset.query.extra.update({
            value_key: (grouping_expression, ())
        })

        return queryset

    def _count_messages(self, queryset):
        return queryset.annotate(count=models.Count('id'))

    def get_distribution(self, queryset, value_key='value', bins=None, **kwargs):
        if bins is None:
            bins = self.default_bins

        # Get the min and max
        min_val, max_val = self.get_range(queryset)
        if min_val is None:
            return []

        # Get a good bin size
        bin_size = self._get_bin_size(min_val, max_val, bins)

        # Calculate a grouping value
        grouping_expression = self.get_grouping_expression(queryset, bin_size=bin_size)
        queryset = self._add_grouping_value(queryset, grouping_expression, value_key)

        # Group by it
        queryset = queryset.values(value_key)

        # Count the messages in each group
        queryset = self._count_messages(queryset)

        return BinnedValuesQuerySet.create_from(queryset,
                                                bin_size=bin_size,
                                                min_val=min_val,
                                                max_val=max_val)


class TimeDimension(QuantitativeDimension):
    """A dimension for time fields on Message"""
    distribution = distributions.TimeDistribution()

    def filter(self, queryset, filter):
        queryset = self.exact_filter(queryset, filter)
        if filter.get('min_time'):
            queryset = queryset.filter(Q((self.field_name + "__gte", filter['min_time'])))
        if filter.get('max_time'):
            queryset = queryset.filter(Q((self.field_name + "__lte", filter['max_time'])))
        return queryset


class RelatedCategoricalDimension(CategoricalDimension):
    """A categorical dimension where the values are in a related table, e.g. sender name."""


class TextDimension(CategoricalDimension):
    """A dimension based on the words in a text field."""
    distribution = None
