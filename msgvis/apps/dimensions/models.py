from django.db import models
from django.db.models import Q
import operator
from msgvis.apps.corpus import models as corpus_models
from msgvis.apps.dimensions import distributions


class BaseDimension(object):
    """
    The abstract dimension class.

    Attributes:
        key (str): a string id for the dimension (e.g. 'time')
        name (str): a nicely-formatted name for the dimension (e.g. 'Number of Tweets')
        description (str): a longer explanation for the dimension (e.g. "The total number of tweets produced by this author.")
        field_name (str): the name of the field in the database for this dimension (defaults to the key)
    """

    distribution = None

    def __init__(self, key, name, description, field_name=None):
        self.key = key
        self.name = name
        self.description = description
        self.field_name = field_name if field_name is not None else key

    def get_distribution(self, dataset):
        """Get the distribution of the dimension within the dataset."""

        if self.distribution is None:
            raise AttributeError("Dimension %s does not know how to calculate a distribution" % self.key)

        field_object, model, direct, m2m = corpus_models.Message._meta.get_field_by_name(self.field_name)

        return self.distribution.group_by(dataset, self.field_name)

    def exact_filter(self, queryset, filter):
        """Filtering for exact value"""
        if filter.get('value'):
            queryset = queryset.filter(Q((self.field_name, filter['value'])))
        return queryset

    def filter(self, queryset, filter):
        """Filtering dataset with one filter"""
        return self.exact_filter(queryset, filter)

    def get_grouping_expression(self, queryset):
        """
        Given a set of messages (possibly filtered),
        returns a string that could be used with QuerySet.values() to
        group the messages by this dimension.
        """


class QuantitativeDimension(BaseDimension):
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

class CategoricalDimension(BaseDimension):
    """A generic categorical dimension"""
    distribution = distributions.CategoricalDistribution()

    def filter(self, queryset, filter):
        queryset = self.exact_filter(queryset, filter)
        if filter.get('levels'):
            filter_ors = []
            for level in filter.get('levels'):
                filter_ors.append((self.field_name, level))
            queryset = queryset.filter(reduce(operator.or_, [Q(x) for x in filter_ors]))
        return queryset


class RelatedCategoricalDimension(CategoricalDimension):
    """A categorical dimension where the values are in a related table."""
    distribution = distributions.CategoricalDistribution()


class TextDimension(CategoricalDimension):
    """A dimension based on the words in a text field."""
    distribution = None
