from django.db import models


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


class Question(models.Model):
    """
    A research question from an :class:`Article`.
    May be associated with a number of :class:`.Dimension` objects.
    """

    source = models.ForeignKey(Article, null=True, default=None)
    """The source article for the question."""

    text = models.TextField()
    """The text of the question."""

    dimensions = models.ManyToManyField('dimensions.Dimension')
    """A set of dimensions related to the question."""
