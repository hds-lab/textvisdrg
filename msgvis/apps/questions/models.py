from django.db import models

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

    @staticmethod
    def get_dimension_key_model(key):
        return registry.get_dimension(key).get_key_model()

    def add_dimension(self, key):
        self.dimensions.add(self.get_dimension_key_model(key))

    def __unicode__(self):
        return self.text

def get_sample_questions(dimension_list):
    """
    Given dimensions, return sample research questions.
    """

    questions = Question.objects.all()
    for dimension in dimension_list:
        questions = questions.filter(dimensions__key=dimension)

    if questions.count() == 0:
        questions = Question.objects.all()
        """Consider the case that no dimension in the existing questions matches"""
        #TODO: may need a better way to handle this

    return questions[:10]