from django.db import models
from msgvis.apps.corpus import utils
from msgvis.apps.corpus import models as corpus_models
from msgvis.apps.enhance import models as enhance_models
import operator

class Group(models.Model):
    """
    A group of messages, created by inclusive and exclusive keywords.
    """

    name = models.CharField(max_length=250, default=None, blank=True)
    """The group name."""

    dataset = models.ForeignKey(corpus_models.Dataset, related_name='groups')
    """Which :class:`corpus_models.Dataset` this group belongs to"""

    created_at = models.DateTimeField(auto_now_add=True)
    """Creation time"""

    keywords = models.TextField(default="", blank=True)
    """keywords for including / excluding messages."""

    include_types = models.ManyToManyField(corpus_models.MessageType, null=True, blank=True, default=None)
    """include tweets/retweets/replies"""

    deleted = models.BooleanField(default=False)

    #messages = models.ManyToManyField(corpus_models.Message, null=True, blank=True, default=None, related_name='groups')
    #"""The set of :class:`corpus_models.Message` that belong to this group."""


    @property
    def messages(self):
        return self.dataset.get_advanced_search_results(self.keywords, self.include_types.all())

    @property
    def message_count(self):
        return self.messages.count()


    def __repr__(self):
        return self.name

    def __unicode__(self):
        return self.__repr__()

