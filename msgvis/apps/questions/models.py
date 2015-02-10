from django.db import models


class Article(models.Model):
    """
    A published research article.
    """


class Question(models.Model):
    """
    A research question from an :class:`Article`.
    """

