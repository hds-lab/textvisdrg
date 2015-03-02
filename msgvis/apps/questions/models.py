from django.db import models
from msgvis.apps.dimensions.models import DimensionKey


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

    dimensions = models.ManyToManyField("dimensions.DimensionKey", through="QuestionDimensionConnection")
    """A set of dimensions related to the question."""


    def add_dimension(self, key):
        count = self.dimensions.count()
        dimension_key, created = DimensionKey.objects.get_or_create(key=key)
        connection = QuestionDimensionConnection(question=self, dimension=dimension_key, count=count + 1)
        connection.save()

    def __unicode__(self):
        return self.text

    @classmethod
    def get_sample_questions(cls, *dimension_list):
        """
        Given dimensions, return sample research questions.
        """
        final_questions = []
        questions = cls.objects.all()
        total_questions_count = 6

        if len(dimension_list) == 1:
            questions = questions.filter(dimensions__key=dimension_list[0])
            final_questions.extend(questions.order_by('?')[:total_questions_count])

        elif len(dimension_list) == 2:

            questions = questions.filter(dimensions__key=dimension_list[0])
            questions = questions.filter(dimensions__key=dimension_list[1])
            count = int(total_questions_count / 2)
            final_questions.extend(questions.order_by('?')[:count])

            questions = cls.objects.all()
            questions = questions.filter(dimensions__key=dimension_list[0])
            questions = questions.exclude(dimensions__key=dimension_list[1])
            count = int((total_questions_count - len(final_questions)) / 2)
            final_questions.extend(questions.order_by('?')[:count])

            questions = cls.objects.all()
            questions = questions.filter(dimensions__key=dimension_list[1])
            questions = questions.exclude(dimensions__key=dimension_list[0])
            count = total_questions_count - len(final_questions)
            final_questions.extend(questions.order_by('?')[:count])

        if len(final_questions) == 0:
            questions = cls.objects.all()
            final_questions.extend(questions.order_by('?')[:total_questions_count])
            """Consider the case that no dimension in the existing questions matches"""


        return final_questions

    @property
    def ordered_dimensions(self):
        dimensions = self.dimensions.all()
        #dimensions = dimensions.order_by('questions_question_dimensions.id')
        return dimensions

class QuestionDimensionConnection(models.Model):
    question = models.ForeignKey(Question)
    dimension = models.ForeignKey(DimensionKey)
    count = models.IntegerField()

    class Meta:
        ordering = ["count"]