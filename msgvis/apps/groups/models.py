from django.db import models
from msgvis.apps.corpus import utils
from msgvis.apps.corpus import models as corpus_models
from msgvis.apps.enhance import models as enhance_models
from django.contrib.auth.models import User
import operator
from django.utils import timezone

class Group(models.Model):
    """
    A group of messages, created by inclusive and exclusive keywords.
    """

    owner = models.ForeignKey(User, default=None, null=True)
    """User"""

    order = models.IntegerField(default=0)
    """The order in a user's group set"""

    name = models.CharField(max_length=250, default=None, blank=True)
    """The group name."""

    dataset = models.ForeignKey(corpus_models.Dataset, related_name='groups')
    """Which :class:`corpus_models.Dataset` this group belongs to"""

    created_at = models.DateTimeField(auto_now_add=True)
    """The group created time"""

    keywords = models.TextField(default="", blank=True)
    """keywords for including / excluding messages."""

    include_types = models.ManyToManyField(corpus_models.MessageType, null=True, blank=True, default=None)
    """include tweets/retweets/replies"""

    is_search_record = models.BooleanField(default=False)

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

class ActionHistory(models.Model):
    """
    A model to record history
    """

    owner = models.ForeignKey(User, default=None, null=True)

    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    """Created time"""

    from_server = models.BooleanField(default=False)

    type = models.CharField(max_length=100, default="", blank=True, db_index=True)

    contents = models.TextField(default="", blank=True)