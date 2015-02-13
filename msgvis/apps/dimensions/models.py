from django.db import models
from msgvis.apps.corpus import models as corpus_models
from msgvis.apps.dimensions import distributions


class Dimension(models.Model):
    """
    A dimension of the message data.
    The dimension model describes metadata about the dimension.
    """

    slug = models.SlugField()
    """A short uniquely identifying key for the dimension"""

    name = models.CharField(max_length=100)
    """Human-readable name for the dimension"""

    description = models.TextField()
    """A longer description of the dimension"""

    SCOPE_OPEN_ENDED = 'O'
    SCOPE_CLOSED_ENDED = 'C'
    SCOPE_CHOICES = (
        (SCOPE_OPEN_ENDED, 'Open-ended'),
        (SCOPE_CLOSED_ENDED, 'Closed-ended'),
    )

    scope = models.CharField(max_length=1, choices=SCOPE_CHOICES)
    """The scope of the dimension, e.g. open/closed"""

    TYPE_QUANTITATIVE = 'Q'
    TYPE_CATEGORICAL = 'C'
    TYPE_CHOICES = (
        (TYPE_QUANTITATIVE, 'Quantitative'),
        (TYPE_CATEGORICAL, 'Categorical'),
    )

    type = models.CharField(max_length=1, choices=TYPE_CHOICES)
    """The type of the dimension, e.g. quantitative/categorical"""

    field_name = models.CharField(max_length=50)
    """The name of the underlying Message field that stores this dimension"""

    def __unicode__(self):
        return self.slug

    def get_distribution(self, dataset):
        """Get the distribution of the dimension within the dataset."""

        field_attr = getattr(corpus_models.Message, self.field_name, None)
        if field_attr is None:
            raise AttributeError("Field %s is not on the Message model" % self.field_name)

        field_name, db_field = field_attr.field.get_attname_column()

        dist = None
        if self.type == self.TYPE_CATEGORICAL:
            dist = distributions.CategoricalDistribution(db_field)
        else:
            raise NotImplementedError("Distributions not yet implemented for the %s dimension." % self.name)

        result = dist.group_by(dataset.message_set.all())

        # We might want to look up related models somehow, e.g. for Sentiment

        return result
