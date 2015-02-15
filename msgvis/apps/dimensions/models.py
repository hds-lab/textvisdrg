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

    def exact_filter(self, dataset, filter):
        """Filtering for exact value"""
        if filter.get('value'):
            dataset = dataset.filter(Q((self.field_name, filter['value'])))
        return dataset

    def filter(self, dataset, filter):
        """Filtering dataset with one filter"""
        return self.exact_filter(dataset, filter)


class QuantitativeDimension(BaseDimension):
    """A generic quantitative dimension"""
    distribution = distributions.QuantitativeDistribution()

    def filter(self, dataset, filter):
        dataset = self.exact_filter(dataset, filter)
        if filter.get('min'):
            dataset = dataset.filter(Q((self.field_name + "__gte", filter['min'])))
        if filter.get('max'):
            dataset = dataset.filter(Q((self.field_name + "__lte", filter['max'])))
        return dataset

class TimeDimension(QuantitativeDimension):
    """A dimension for time variables"""
    distribution = distributions.TimeDistribution()

    def filter(self, dataset, filter):
        dataset = self.exact_filter(dataset, filter)
        if filter.get('min_time'):
            dataset = dataset.filter(Q((self.field_name + "__gte", filter['min_time'])))
        if filter.get('max_time'):
            dataset = dataset.filter(Q((self.field_name + "__lte", filter['max_time'])))
        return dataset

class CategoricalDimension(BaseDimension):
    """A generic categorical dimension"""
    distribution = distributions.CategoricalDistribution()

    def filter(self, dataset, filter):
        dataset = self.exact_filter(dataset, filter)
        if filter.get('levels'):
            filter_ors = []
            for level in filter.get('levels'):
                filter_ors.append((self.field_name, level))
            dataset = dataset.filter(reduce(operator.or_, [Q(x) for x in filter_ors]))
        return dataset


class ForeignKeyDimension(CategoricalDimension):
    """A categorical dimension where the values are in a related table."""
    distribution = distributions.ForeignKeyDistribution()


class TextDimension(CategoricalDimension):
    """A dimension based on the words in a text field."""
    distribution = None
