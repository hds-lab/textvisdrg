from django.db import models

from msgvis.apps.dimensions import registry as dimensions


class Article(models.Model):
    """
    A published research article.
    """

    year = models.PositiveIntegerField(null=True, default=None, blank=True)
    """The publication year for the article."""

    authors = models.CharField(max_length=250, default=None, blank=True)
    """A plain-text author list."""

    link = models.CharField(max_length=250, default=None, blank=True)
    """A url to the article."""

    title = models.CharField(max_length=250, default=None, blank=True)
    """The title of the article."""

    venue = models.CharField(max_length=250, default=None, blank=True)
    """The venue where the article was published."""


class Dimension(models.Model):
    """
    Dimension names for research questions.
    """

    key = models.CharField(max_length=20, unique=True)
    """The id of the dimension"""

    def get_dimension(self):
        """Get the actual dimension object that can do stuff."""
        return dimensions.get_dimension(self.key)


class Question(models.Model):
    """
    A research question from an :class:`Article`.
    May be associated with a number of :class:`.Dimension` objects.
    """

    source = models.ForeignKey(Article, null=True, default=None)
    """The source article for the question."""

    text = models.TextField()
    """The text of the question."""

    dimensions = models.ManyToManyField(Dimension)
    """A set of dimensions related to the question."""
