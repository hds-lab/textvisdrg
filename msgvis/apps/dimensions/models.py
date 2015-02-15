from django.db import models
from django.db.models import Q
import operator
from msgvis.apps.corpus import models as corpus_models
from msgvis.apps.dimensions import distributions


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

    def __init__(self, key, name, description, field_name=None):
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

        if grouping_key != grouping_expression:
            # We need to add this expression as a calculated field
            # because otherwise Django just uses the expression itself as the
            # grouping variable name.
            queryset = queryset.extra(select={grouping_key: grouping_expression})

        # Then group by the grouping field
        return queryset.values(grouping_key)

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


class TextDimension(CategoricalDimension):
    """A dimension based on the words in a text field."""
    distribution = None
