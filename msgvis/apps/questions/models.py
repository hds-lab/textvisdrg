from django.db import models
from msgvis.apps.dimensions.models import DimensionKey

from msgvis.apps.dimensions import registry

from django.db.models import Q


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

    def __unicode__(self):
        return self.title

class Question(models.Model):
    """
    A research question from an :class:`Article`.
    May be associated with a number of :class:`.DimensionKey` objects.
    """

    source = models.ForeignKey(Article, null=True, default=None)
    """The source article for the question."""

    text = models.TextField()
    """The text of the question."""

    dimensions = models.ManyToManyField("dimensions.DimensionKey")
    """A set of dimensions related to the question."""


    def add_dimension(self, key):
        dimension_key, created = DimensionKey.objects.get_or_create(key=key)
        self.dimensions.add(dimension_key)

    def __unicode__(self):
        return self.text

    @classmethod
    def get_sample_questions(cls, *dimension_list):
        """
        Given dimensions, return sample research questions.
        """

        questions = cls.objects.all()
        for dimension in dimension_list:
            questions = questions.filter(dimensions__key=dimension)
        exclude_dimensions = ['location', 'codes', 'age', 'gender', 'media']
        for ed in exclude_dimensions:
            questions = questions.exclude(dimensions__key=ed)

        if questions.count() == 0:
            questions = cls.objects.all()
            """Consider the case that no dimension in the existing questions matches"""
            #TODO: may need a better way to handle this

        return questions[:10]
