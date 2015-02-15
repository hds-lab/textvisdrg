from django.db import models
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


class QuantitativeDimension(BaseDimension):
    """A generic quantitative dimension"""
    distribution = distributions.QuantitativeDistribution()


class TimeDimension(QuantitativeDimension):
    """A dimension for time variables"""
    distribution = distributions.TimeDistribution()


class CategoricalDimension(BaseDimension):
    """A generic categorical dimension"""
    distribution = distributions.CategoricalDistribution()


class ForeignKeyDimension(CategoricalDimension):
    """A categorical dimension where the values are in a related table."""
    distribution = distributions.ForeignKeyDistribution()

class TextDimension(CategoricalDimension):
    """A dimension based on the words in a text field."""
    distribution = distributions.CategoricalDistribution()
