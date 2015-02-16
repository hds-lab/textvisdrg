import operator
import math

from django.db import models
from django.db.models import query
from django.db.models import Q
from django.conf import settings

from msgvis.apps.corpus import models as corpus_models


QUANTITATIVE_DIMENSION_BINS = getattr(settings, 'QUANTITATIVE_DIMENSION_BINS', 50)


def add_metadata(queryset, **kwargs):
    for key, value in kwargs.iteritems():
        setattr(queryset, key, value)
    return queryset


def db_vendor():
    from django.db import connection

    return connection.vendor


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
        self.field_map = kwargs.get('field_map', {})

    @classmethod
    def create_from(cls, values_query_set, field_map):
        """Create a MappedValueQuerySet with a field name mapping dictionary."""
        return values_query_set._clone(cls, field_map=field_map)

    def _clone(self, klass=None, setup=False, **kwargs):
        c = super(MappedValuesQuerySet, self)._clone(klass, setup, **kwargs)
        c.field_map = self.field_map
        return c

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

    def get_range(self, messages):
        """
        Find a min and max for this dimension, as a tuple.
        If there isn't one, (None, None) is returned.

        Calling this multiple times on the same queryset object will
        use a cached value.
        """

        if self._cached_range_queryset_id == id(messages):
            return self._cached_range

        dim_range = messages.aggregate(min=models.Min(self.field_name),
                                       max=models.Max(self.field_name))

        self._cached_range_queryset_id = id(messages)
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

    def _render_grouping_expression(self, bin_size):
        return self.grouping_expressions[db_vendor()].format(
            field_name=self.field_name,
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
            return self._render_grouping_expression(bin_size)
        else:
            # No need for binning
            return self.field_name

    def _attach_grouping_expression(self, queryset, grouping_expression, grouping_key):
        """
        Make sure the queryset selects the grouping expression, aliased to grouping_key.
        """
        # This is a workaround for QuerySet.extra(select={})
        # because it doesn't work if the value you are selecting
        # contains a %s -- even though Sqlite uses %s as a time format
        # string.

        # Copy the queryset first to avoid problems
        queryset = queryset._clone()
        queryset.query.extra.update({
            grouping_key: (grouping_expression, ())
        })
        return queryset

    def group_by(self, queryset, grouping_key=None, bins=None, bin_size=None):
        """
        Return a ValuesQuerySet that has been grouped by this dimension.
        The group value will be available as grouping_key in the dictionaries.

        The grouping key defaults to the dimension key.

        If num_bins or bin_size is not provided, an estimate will be used.

        .. code-block:: python

            messages = dim.group_by(messages, 'value', 100)
            distribution = messages.annotate(count=Count('id'))
            print distribution[0]
            # { 'value': 'hello', 'count': 5 }
        """
        expression = self.get_grouping_expression(queryset, bins=bins, bin_size=bin_size)

        if expression == self.field_name:

            # We still have to map back to the requested grouping_key
            return MappedValuesQuerySet.create_from(queryset.values(expression), {
                expression: grouping_key
            })

        else:
            # Sometimes this step gets complicated
            queryset = self._attach_grouping_expression(queryset, expression, grouping_key)

            # Then use values to group by the grouping key.
            return queryset.values(grouping_key)

    def get_distribution(self, dataset, value_key='value', bins=None, **kwargs):
        """
        On the given :class:`.Dataset`, calculate a binned distribution.
        A desired number of bins may be provided.
        The results will be keyed by value_key.
        """
        if bins is None:
            bins = self.default_bins

        # Get the min and max
        if isinstance(dataset, corpus_models.Dataset):
            queryset = dataset.message_set.all()
        else:
            queryset = dataset

        min_val, max_val = self.get_range(queryset)
        if min_val is None:
            return []

        # Get a good bin size
        bin_size = self._get_bin_size(min_val, max_val, bins)

        # Group by that bin size
        queryset = self.group_by(queryset, value_key, bin_size=bin_size)

        # Count the messages in each group
        queryset = queryset.annotate(count=models.Count('id'))

        # Store the bin info on the queryset
        return add_metadata(queryset,
                            bins=bins,
                            bin_size=bin_size,
                            min_val=min_val,
                            max_val=max_val)


class RelatedQuantitativeDimension(QuantitativeDimension):
    """A quantitative dimension on a related model, e.g. sender message count."""

    # Expressions for grouping when we have to join tables
    grouping_expressions_joined = {
        'mysql': '{bin_size} * FLOOR(`{to_table}`.`{target_field_name}` / {bin_size})',
        'sqlite': '{bin_size} * CAST(`{to_table}`.`{target_field_name}` / {bin_size} AS INTEGER)',
    }

    def __init__(self, key, name=None, description=None, field_name=None, default_bins=QUANTITATIVE_DIMENSION_BINS,
                 min_bin_size=1):
        super(RelatedQuantitativeDimension, self).__init__(key, name, description, field_name, default_bins,
                                                           min_bin_size)

        # e.g. (sender, username)
        self.local_field_name, self.target_field_name = self.field_name.split('__')

    @property
    def _path_info(self):
        if not hasattr(self, '_path_info_cache'):
            model = corpus_models.Message

            # Get the django.db.models.related.PathInfo for this relation
            path_infos = model._meta.get_field(self.local_field_name).get_path_info()
            assert len(path_infos) == 1, "I cannot handle long path_infos!"

            setattr(self, '_path_info_cache', path_infos[0])

        return getattr(self, '_path_info_cache')

    def _get_join_condition(self):
        """
        Return a join condition like "`table1`.`field` = `table2`.`field`"

        """
        pi = self._path_info
        assert len(pi.target_fields) == 1, "Complex multi-field joins not supported"
        target_field = pi.target_fields[0]

        return "`{from_table}`.`{from_field}` = `{to_table}`.`{to_field}`".format(
            from_table=pi.from_opts.db_table,
            from_field=pi.join_field.column,
            to_table=pi.to_opts.db_table,
            to_field=target_field.column,
        )

    def _add_manual_join(self, queryset):
        """Add a join to the queryset"""
        to_table = self._path_info.to_opts.db_table
        return queryset.extra(
            tables=[to_table],
            where=[self._get_join_condition()]
        )

    def _render_grouping_expression(self, bin_size):
        """Render the grouping expression, with support for manually joined tables"""

        if bin_size == self.min_bin_size:
            # Fall back because we're not even grouping anyway
            return super(RelatedQuantitativeDimension, self)._render_grouping_expression(bin_size)
        else:
            to_table = self._path_info.to_opts.db_table
            return self.grouping_expressions_joined[db_vendor()].format(
                to_table=to_table,
                target_field_name=self.target_field_name,
                bin_size=bin_size
            )

    def _attach_grouping_expression(self, queryset, grouping_expression, grouping_key):
        queryset = super(RelatedQuantitativeDimension, self)._attach_grouping_expression(
            queryset,
            grouping_expression,
            grouping_key)

        # We also need to specify the join manually :( :( :(
        queryset = self._add_manual_join(queryset)

        return queryset


class TimeDimension(QuantitativeDimension):
    """A dimension for time fields on Message"""

    def filter(self, queryset, filter):
        queryset = self.exact_filter(queryset, filter)
        if filter.get('min_time'):
            queryset = queryset.filter(Q((self.field_name + "__gte", filter['min_time'])))
        if filter.get('max_time'):
            queryset = queryset.filter(Q((self.field_name + "__lte", filter['max_time'])))
        return queryset

    # Convert to unix timestamp. Divide by bin size. Floor. Multiply by bin size. Convert to datetime.
    grouping_expressions = {
        'mysql': r"FROM_UNIXTIME({bin_size} * FLOOR(UNIX_TIMESTAMP(`{field_name}`) / {bin_size}))",
        'sqlite': r"DATETIME({bin_size} * CAST(STRFTIME('%%s', `{field_name}`) / {bin_size} AS INTEGER), 'unixepoch')"
    }

    # A range of human-friendly time bin sizes
    # https://github.com/mbostock/d3/blob/master/src/time/scale.js
    # NOTE: these are in milliseconds! (JS uses millis)
    d3_time_scaleSteps = [
        1e3,  # 1-second
        5e3,  # 5-second
        15e3,  # 15-second
        3e4,  # 30-second
        6e4,  # 1-minute
        3e5,  # 5-minute
        9e5,  # 15-minute
        18e5,  # 30-minute
        36e5,  # 1-hour
        108e5,  # 3-hour
        216e5,  # 6-hour
        432e5,  # 12-hour
        864e5,  # 1-day
        1728e5,  # 2-day
        6048e5,  # 1-week
        2592e6,  # 1-month
        7776e6,  # 3-month
        31536e6  # 1-year
    ]

    def _get_bin_size(self, min_val, max_val, desired_bins):
        """
        Determines a bin size for the time interval
        that supplies at least as many bins as minimum_bins,
        unless the time interval spans fewer than minimum_bins seconds.
        """

        extent = max_val - min_val
        bin_size = extent / desired_bins

        bin_size_seconds = bin_size.total_seconds()

        bin_size_millis = 1000 * bin_size_seconds

        # Find the first human-friendly bin size that isn't bigger than bin_size_seconds
        best_bin_millis = self.d3_time_scaleSteps[0]
        for step in self.d3_time_scaleSteps:
            if step <= bin_size_millis:
                best_bin_millis = step
            else:
                break

        return best_bin_millis / 1000


class RelatedCategoricalDimension(CategoricalDimension):
    """A categorical dimension where the values are in a related table, e.g. sender name."""


class TextDimension(CategoricalDimension):
    """A dimension based on the words in a text field."""
    distribution = None
