from django.db import models

# Create your models here.
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
