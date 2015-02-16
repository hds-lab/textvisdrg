from django.db import models
from django.db.models import query
from django.db.models import Q
import operator
from msgvis.apps.corpus import models as corpus_models
from msgvis.apps.dimensions import distributions


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

    distribution = distributions.CategoricalDistribution()

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

    def get_distribution(self, queryset):
        """Get the distribution of the dimension within the dataset."""
        if self.distribution is None:
            raise AttributeError("Dimension %s does not know how to calculate a distribution" % self.key)

        # Use 'values' to group the queryset
        queryset = self.group_by(queryset, 'value')

        # Count the messages in each group
        return queryset.annotate(count=models.Count('id'))


    def get_grouping_expression(self, queryset):
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

    def filter(self, queryset, filter):
        queryset = self.exact_filter(queryset, filter)
        if filter.get('min'):
            queryset = queryset.filter(Q((self.field_name + "__gte", filter['min'])))
        if filter.get('max'):
            queryset = queryset.filter(Q((self.field_name + "__lte", filter['max'])))
        return queryset


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
    """A categorical dimension where the values are in a related table."""

    def get_distribution(self, queryset):
        """Get the distribution of the dimension within the dataset."""
        if self.distribution is None:
            raise AttributeError("Dimension %s does not know how to calculate a distribution" % self.key)

        # Use 'values' to group the queryset
        queryset = self.group_by(queryset, 'value')

        # Count the messages in each group
        return queryset.annotate(count=models.Count('id'))


class TextDimension(CategoricalDimension):
    """A dimension based on the words in a text field."""
    distribution = None
